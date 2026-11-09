"""Meta (Facebook/Instagram) product catalog feed.

Public RSS 2.0 feed with the Google/Meta ``g:`` namespace, consumed by
Commerce Manager -> Catalog -> Data sources (scheduled fetch).

The ``g:id`` MUST match the ``content_ids`` the Meta Pixel sends from the
front (``id_product``); that is how Meta links pixel events to catalog items.

Product images live in S3 as WebP served as ``application/octet-stream``,
which Meta's catalog does not accept, so ``image_link`` points to
``meta_catalog_image``: it converts them to JPEG on the fly. That endpoint
only takes product/image ids (never a raw S3 key) because the same bucket
also stores private store documents.
"""
import io
import logging
import xml.etree.ElementTree as ET
from decimal import Decimal

from PIL import Image as PILImage
from django.core.cache import cache
from django.http import Http404, HttpResponse
from django.utils.html import strip_tags
from django.views.decorators.http import require_GET

from ..models import Images, Products

logger = logging.getLogger(__name__)

SITE_URL = 'https://interamericana.store'
PRODUCT_URL = SITE_URL + '/interamericana/products/accessories/{id}'
IMAGE_URL = SITE_URL + '/api/feed/img/{product_id}.jpg'
GALLERY_IMAGE_URL = SITE_URL + '/api/feed/img/{product_id}/{image_id}.jpg'
CURRENCY = 'COP'
G_NS = 'http://base.google.com/ns/1.0'
MAX_ADDITIONAL_IMAGES = 10
MAX_DESCRIPTION = 5000
MIN_IMAGE_SIDE = 500  # Meta catalog minimum
MAX_IMAGE_SIDE = 2048
IMAGE_CACHE_SECONDS = 60 * 60 * 24

ET.register_namespace('g', G_NS)


def _public_products():
    """Same visibility rules as the store front."""
    return Products.objects.filter(published=True, state_id=2)


def _read_from_bucket(key):
    """Read through the same S3 storage the Images model uses.

    Don't build URLs from settings.AWS_URL_BUCKET_DOCS: in prod it points to
    the wrong region (S3 answers 301 + XML), and the storage also keeps
    working if the bucket ever becomes private.
    """
    storage = Images._meta.get_field('image').storage
    with storage.open(key, 'rb') as f:
        return f.read()


def _price(value):
    return '{:.2f} {}'.format(Decimal(value), CURRENCY)


def _description(product):
    text = ' '.join(strip_tags(product.description_product or '').split())
    return (text or product.name_product)[:MAX_DESCRIPTION]


def _add(item, tag, value):
    el = ET.SubElement(item, '{%s}%s' % (G_NS, tag))
    el.text = str(value)


def _gallery(product):
    """Gallery images that are not the main image."""
    main = str(product.image or '')
    return [img for img in product.rel_product.all()
            if img.image and img.image.name and img.image.name != main]


def _build_item(channel, product):
    gallery = _gallery(product)
    if product.image:
        image_link = IMAGE_URL.format(product_id=product.id_product)
    elif gallery:
        first = gallery.pop(0)
        image_link = GALLERY_IMAGE_URL.format(product_id=product.id_product, image_id=first.id)
    else:
        return  # Meta rejects items without image

    in_stock = product.availability and (product.stock or 0) > 0

    item = ET.SubElement(channel, 'item')
    _add(item, 'id', product.id_product)
    _add(item, 'title', product.name_product[:200])
    _add(item, 'description', _description(product))
    _add(item, 'availability', 'in stock' if in_stock else 'out of stock')
    _add(item, 'condition', 'new')
    _add(item, 'price', _price(product.total_price))
    if product.discount_price and Decimal(0) < product.discount_price < product.total_price:
        _add(item, 'sale_price', _price(product.discount_price))
    _add(item, 'link', PRODUCT_URL.format(id=product.id_product))
    _add(item, 'image_link', image_link)
    for img in gallery[:MAX_ADDITIONAL_IMAGES]:
        _add(item, 'additional_image_link',
             GALLERY_IMAGE_URL.format(product_id=product.id_product, image_id=img.id))
    _add(item, 'brand', product.brand or 'Interamericana')
    if product.product_code:
        _add(item, 'mpn', product.product_code)
    if product.stock is not None:
        _add(item, 'quantity_to_sell_on_facebook', max(product.stock, 0))
    if product.subcategory_id:
        _add(item, 'product_type', product.subcategory)


@require_GET
def meta_catalog_feed(request):
    """GET /api/feed/meta-catalog.xml"""
    products = (_public_products()
                .select_related('subcategory')
                .prefetch_related('rel_product')
                .order_by('id_product'))

    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = 'Interamericana'
    ET.SubElement(channel, 'link').text = SITE_URL
    ET.SubElement(channel, 'description').text = 'Catálogo de productos Interamericana'

    for product in products:
        _build_item(channel, product)

    body = ET.tostring(rss, encoding='utf-8', xml_declaration=True)
    response = HttpResponse(body, content_type='application/xml; charset=utf-8')
    response['Cache-Control'] = 'public, max-age=3600'
    return response


def _to_jpeg(raw):
    img = PILImage.open(io.BytesIO(raw))
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
        background = PILImage.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])
        img = background
    else:
        img = img.convert('RGB')

    width, height = img.size
    scale = 1.0
    if min(width, height) < MIN_IMAGE_SIDE:
        scale = MIN_IMAGE_SIDE / float(min(width, height))
    elif max(width, height) > MAX_IMAGE_SIDE:
        scale = MAX_IMAGE_SIDE / float(max(width, height))
    if scale != 1.0:
        img = img.resize((round(width * scale), round(height * scale)), PILImage.LANCZOS)

    out = io.BytesIO()
    img.save(out, format='JPEG', quality=88, optimize=True)
    return out.getvalue()


@require_GET
def meta_catalog_image(request, product_id, image_id=None):
    """GET /api/feed/img/<product_id>.jpg and /api/feed/img/<product_id>/<image_id>.jpg"""
    product = _public_products().filter(id_product=product_id).first()
    if product is None:
        raise Http404

    if image_id is None:
        key = str(product.image or '')
    else:
        gallery = Images.objects.filter(id=image_id, product_id=product.id_product).first()
        key = gallery.image.name if gallery and gallery.image else ''
    if not key:
        raise Http404

    cache_key = 'meta_feed_img:' + key
    jpeg = cache.get(cache_key)
    if jpeg is None:
        try:
            jpeg = _to_jpeg(_read_from_bucket(key))
        except Exception:
            logger.exception('Meta feed image conversion failed for %s', key)
            raise Http404
        cache.set(cache_key, jpeg, IMAGE_CACHE_SECONDS)

    response = HttpResponse(jpeg, content_type='image/jpeg')
    response['Cache-Control'] = 'public, max-age=86400'
    return response
