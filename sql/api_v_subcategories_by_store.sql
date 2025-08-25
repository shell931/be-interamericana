create or replace view public.api_v_subcategories_by_store
as
select store_id, cat.id as category_id, cat.name_category, pr.subcategory_id, sub.name_subcategory
from api_products pr
left join api_subcategories sub on sub.id = pr.subcategory_id
left join api_categories cat on cat.id = sub.category_id
group by store_id, cat.id, cat.name_category, pr.subcategory_id, sub.name_subcategory
order by store_id desc;