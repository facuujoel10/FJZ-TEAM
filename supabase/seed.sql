-- TEAM FJZ V22 synthetic seed only.
-- No production users, names, measurements, sessions, photos or credentials.

insert into public.food_library(
  id,created_by,is_global,name,category,kcal_100g,protein_100g,carbs_100g,fat_100g,
  default_portion_g,notes,unit_name,grams_per_unit,reference_source,reference_note
) values
('20000000-0000-4000-8000-000000000001',null,true,'QA Arroz cocido','Carbohidratos',130,2.7,28.0,0.3,100,'Dato ficticio para QA',null,null,'fixture','No usar como referencia nutricional real'),
('20000000-0000-4000-8000-000000000002',null,true,'QA Proteína ficticia','Proteínas',165,31.0,0.0,3.6,100,'Dato ficticio para QA',null,null,'fixture','No usar como referencia nutricional real'),
('20000000-0000-4000-8000-000000000003',null,true,'QA Yogur ficticio','Lácteos',75,8.0,6.0,2.0,100,'Dato ficticio para QA','unidad',180,'fixture','No usar como referencia nutricional real')
on conflict(id) do update set name=excluded.name;

insert into storage.buckets(id,name,public)
values
('progress-photos','progress-photos',false),
('profile-photos','profile-photos',false),
('exercise-videos','exercise-videos',false)
on conflict(id) do update set public=excluded.public;
