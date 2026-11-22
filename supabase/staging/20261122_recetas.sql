insert into public.fitness_recipes
  (is_global,title,category,description,prep_minutes,servings,ingredients,steps,kcal_per_serving,protein_g,carbs_g,fat_g)
select true,title,category,'Valores aproximados por porción.',minutes,1,ingredients::jsonb,steps::jsonb,kcal,p,c,g
from (values
 ('Avena nocturna con frutillas','Desayuno',5,'["40 g de avena","170 g de yogur griego natural","80 g de frutillas"]','["Mezclá la avena y el yogur.","Tapá y refrigerá al menos cuatro horas. Serví con las frutillas."]',310,20,40,8),
 ('Bowl tibio de pollo y choclo','Almuerzo',15,'["120 g de pollo cocido","150 g de arroz cocido","60 g de choclo","5 g de aceite de oliva","Limón"]','["Cortá el pollo en cubos.","Calentá con el arroz y el choclo. Condimentá con limón y aceite."]',488,42,55,11),
 ('Tostadas de ricota y pera','Merienda',5,'["60 g de pan integral","80 g de ricota magra","100 g de pera","Canela"]','["Tostá el pan y untá la ricota.","Sumá la pera en láminas y espolvoreá con canela."]',307,15,46,7),
 ('Tortilla de papa y espinaca','Cena',20,'["180 g de papa cocida","2 huevos","60 g de espinaca","5 g de aceite"]','["Picá la espinaca y cortá la papa en cubos.","Mezclá con los huevos batidos. Cociná en sartén aceitada hasta que el huevo esté firme."]',345,18,34,16)
) r(title,category,minutes,ingredients,steps,kcal,p,c,g)
where not exists(select 1 from public.fitness_recipes f where f.is_global and f.title=r.title);
