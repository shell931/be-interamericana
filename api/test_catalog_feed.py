import io
import xml.etree.ElementTree as ET
from decimal import Decimal
from unittest import mock

from PIL import Image as PILImage
from django.core.cache import cache
from django.test import TestCase

from .models import Categories, Images, ProductState, Products, SubCategories

G = '{http://base.google.com/ns/1.0}'


def _webp_bytes(size=(300, 200), mode='RGBA'):
    out = io.BytesIO()
    PILImage.new(mode, size, (255, 0, 0, 128) if mode == 'RGBA' else (255, 0, 0)).save(out, format='WEBP')
    return out.getvalue()


class MetaCatalogFeedTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        approved, _ = ProductState.objects.get_or_create(id=2, defaults={'name_state': 'Aprobado'})
        pending, _ = ProductState.objects.get_or_create(id=1, defaults={'name_state': 'Pendiente'})
        category = Categories.objects.create(name_category='Rodamientos')
        cls.subcategory = SubCategories.objects.create(name_subcategory='Rodamientos de bola', category=category)

        def make(**kwargs):
            data = dict(name_product='Rodamiento 6201-RS',
                        description_product='<p>Rodamiento\n6201-RS</p>',
                        product_code='6201-RS', total_price=Decimal('4200.00'),
                        stock=1000, subcategory=cls.subcategory, state=approved,
                        image='6-229-1.webp', brand='Sin marca')
            data.update(kwargs)
            return Products.objects.create(**data)

        cls.product = make()
        cls.on_sale = make(name_product='Escobilla', discount_price=Decimal('3000.00'), stock=0)
        cls.unpublished = make(name_product='Oculto', published=False)
        cls.not_approved = make(name_product='Pendiente', state=pending)
        cls.no_image = make(name_product='Sin imagen', image=None)
        cls.gallery = Images(product=cls.product, image_name='6-229-2.webp')
        cls.gallery.image.name = '6-229-2.webp'
        Images.objects.bulk_create([cls.gallery])
        cls.gallery = Images.objects.get(product=cls.product)

    def setUp(self):
        cache.clear()

    def _items(self):
        response = self.client.get('/api/feed/meta-catalog.xml')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/xml'))
        root = ET.fromstring(response.content)
        return {item.find(G + 'id').text: item for item in root.iter('item')}

    def test_feed_only_lists_public_products_with_image(self):
        items = self._items()
        self.assertEqual(set(items), {str(self.product.id_product), str(self.on_sale.id_product)})

    def test_item_fields_match_pixel_and_store(self):
        item = self._items()[str(self.product.id_product)]
        pid = self.product.id_product
        self.assertEqual(item.find(G + 'price').text, '4200.00 COP')
        self.assertEqual(item.find(G + 'availability').text, 'in stock')
        self.assertEqual(item.find(G + 'condition').text, 'new')
        self.assertEqual(item.find(G + 'description').text, 'Rodamiento 6201-RS')
        self.assertEqual(item.find(G + 'link').text,
                         'https://interamericana.store/interamericana/products/accessories/%d' % pid)
        self.assertEqual(item.find(G + 'image_link').text,
                         'https://interamericana.store/api/feed/img/%d.jpg' % pid)
        self.assertEqual(item.find(G + 'additional_image_link').text,
                         'https://interamericana.store/api/feed/img/%d/%d.jpg' % (pid, self.gallery.id))
        self.assertEqual(item.find(G + 'product_type').text, 'Rodamientos de bola')
        self.assertIsNone(item.find(G + 'sale_price'))

    def test_sale_price_and_out_of_stock(self):
        item = self._items()[str(self.on_sale.id_product)]
        self.assertEqual(item.find(G + 'sale_price').text, '3000.00 COP')
        self.assertEqual(item.find(G + 'availability').text, 'out of stock')

    @mock.patch('api.views.catalog_feed.requests.get')
    def test_image_is_converted_to_jpeg_and_upscaled(self, get):
        get.return_value = mock.Mock(content=_webp_bytes(), raise_for_status=lambda: None)
        response = self.client.get('/api/feed/img/%d.jpg' % self.product.id_product)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        img = PILImage.open(io.BytesIO(response.content))
        self.assertEqual(img.format, 'JPEG')
        self.assertGreaterEqual(min(img.size), 500)
        get.assert_called_once_with('https://market-docus-v2.s3.us-east-2.amazonaws.com/6-229-1.webp', timeout=15)

        self.client.get('/api/feed/img/%d.jpg' % self.product.id_product)
        get.assert_called_once()  # second hit served from cache

    @mock.patch('api.views.catalog_feed.requests.get')
    def test_gallery_image(self, get):
        get.return_value = mock.Mock(content=_webp_bytes(mode='RGB'), raise_for_status=lambda: None)
        response = self.client.get('/api/feed/img/%d/%d.jpg' % (self.product.id_product, self.gallery.id))
        self.assertEqual(response.status_code, 200)
        get.assert_called_once_with('https://market-docus-v2.s3.us-east-2.amazonaws.com/6-229-2.webp', timeout=15)

    @mock.patch('api.views.catalog_feed.requests.get')
    def test_image_endpoint_never_exposes_non_public_files(self, get):
        for url in ('/api/feed/img/%d.jpg' % self.unpublished.id_product,
                    '/api/feed/img/%d.jpg' % self.not_approved.id_product,
                    '/api/feed/img/%d.jpg' % self.no_image.id_product,
                    '/api/feed/img/999999.jpg',
                    # gallery image that belongs to another product
                    '/api/feed/img/%d/%d.jpg' % (self.on_sale.id_product, self.gallery.id)):
            self.assertEqual(self.client.get(url).status_code, 404, url)
        get.assert_not_called()

    @mock.patch('api.views.catalog_feed.requests.get', side_effect=Exception('s3 down'))
    def test_image_upstream_failure_is_404(self, get):
        with self.assertLogs('api.views.catalog_feed', level='ERROR'):
            response = self.client.get('/api/feed/img/%d.jpg' % self.product.id_product)
        self.assertEqual(response.status_code, 404)
