drop view v_get_product_list;
CREATE OR REPLACE VIEW public.v_get_product_list
as
select pr.*, st.name_store, cat.name_category from api_products pr join api_stores st on st.id_store = pr.store_id join api_categories cat on cat.id = pr.category_id;