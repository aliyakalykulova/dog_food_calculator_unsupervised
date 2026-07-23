import streamlit as st
import pandas as pd
import sqlite3

# ---- Загрузка данных из базы данных и преобразование в формат DataFrame

@st.cache_data(show_spinner=False)
def load_data():

	# --- Данные о кормах для собак и их рецептурах
    conn = sqlite3.connect("data_base/pet_food.db")
    food=pd.read_sql("""SELECT name_product, description, ingredients, GROUP_CONCAT(category.category) AS category,
                        food_form.food_form,  breed_size.breed_size,  life_stage.life_stage, 
                        moisture, protein, fat as fats, carbohydrate 
                        FROM dog_food 
                        INNER JOIN dog_food_characteristics ON dog_food_characteristics.id_dog_food = dog_food.id_dog_food 
                        INNER JOIN breed_size ON dog_food_characteristics.id_breed_size = breed_size.id_breed_size
                        INNER JOIN life_stage ON dog_food_characteristics.id_life_stage = life_stage.id_life_stage 
                        INNER JOIN food_form ON dog_food_characteristics.id_food_form = food_form.id_food_form 
                        INNER JOIN food_category_connect ON food_category_connect.id_dog_food = dog_food.id_dog_food 
                        INNER JOIN category ON food_category_connect.id_category = category.id_category 
                        INNER JOIN nutrient_macro ON nutrient_macro.id_dog_food = dog_food.id_dog_food 
                        GROUP BY dog_food.id_dog_food""", conn)
    food["category"] = (food["category"].astype(str).str.split(", "))

	# --- Данные о породах собак и связанных заболеваниях
    conn= sqlite3.connect("data_base/dog_breed_disease.db")
    disease = pd.read_sql("""SELECT breed_name.name_ru as name_breed,  min_weight, max_weight, disease.name_ru as name_disease, name_disorder
                             FROM breed 
                             INNER JOIN breed_name ON breed.id_breed = breed_name.id_breed
                             INNER JOIN breed_disease ON breed.id_breed = breed_disease.id_breed
                             INNER JOIN disease ON disease.id_disease= breed_disease.id_disease
                             INNER JOIN disease_disorder ON disease.id_disease= disease_disorder.id_disease
                             INNER JOIN disorder ON disorder.id_disorder=disease_disorder.id_disorder""", conn)
	
	# --- Данные для стандартизации названий ингредиентов между рецептурами кормов и общей базой ингредиентов
    conn=sqlite3.connect("data_base/ingredients.db")
    standart = pd.read_sql("""SELECT name_feed_ingredient,  ingredients_translation.name_ru || " — " || format_ingredients_translation.name_ru AS ingredient_full_ru, 
                              ingredient_category.name_ru as category_ru     
                              FROM  ingredient_mapping
                              INNER JOIN ingredient ON ingredient.id_ingredient	= ingredient_mapping.id_ingredient
                              INNER JOIN ingredients_translation ON ingredients_translation.id_name_ingredient=ingredient.id_name_ingredient
                              INNER JOIN format_ingredients_translation ON format_ingredients_translation.id_format_ingredient = ingredient.id_format_ingredient
                              INNER JOIN ingredient_category ON ingredient_category.id_category = ingredient.id_category""", conn)
    
	# --- Данные об ингредиентах и их нутриентном составе
    ingredirents_df =  pd.read_sql("""SELECT full_name_ingredient, ingredients_translation.name_ru as name_ingredient_ru , 
                                      format_ingredients_translation.name_ru as format_ingredient_ru, ingredient_category.name_ru as category_ru, 
                                      ingredients_translation.name_ru || " — " || format_ingredients_translation.name_ru AS ingredient_format_cat,
                                     
                                      calories_kcal, moisture_per, protein_per, carbohydrate_per,fats_per, ash_g, fiber_g, cholesterol_mg, total_sugar_g,
                                      calcium_mg, phosphorus_mg, magnesium_mg, sodium_mg, potassium_mg, iron_mg, copper_mg, zinc_mg, manganese_mg, 
                                      selenium_mcg, iodine_mcg, choline_mg,
                      
                                      vitamin_a_mcg,  vitamin_e_mg,  vitamin_d_mcg, vitamin_b1_mg, vitamin_b2_mg,vitamin_b3_mg, 
                                      vitamin_b5_mg, vitamin_b6_mg,vitamin_b9_mcg,vitamin_b12_mcg, vitamin_c_mg, vitamin_k_mcg,
                                      alpha_carotene_mcg,beta_carotene_mcg, beta_cryptoxanthin_mcg, lutein_zeaxanthin_mcg, lycopene_mcg, retinol_mcg, 
                                      linoleic_acid_g, alpha_linolenic_acid_g , arachidonic_acid_g ,epa_g, dha_g
                      
                                      FROM  ingredient
                                      INNER JOIN ingredients_translation on ingredient.id_name_ingredient=ingredients_translation.id_name_ingredient
                                      INNER JOIN format_ingredients_translation on format_ingredients_translation.id_format_ingredient=ingredient.id_format_ingredient
                                      INNER JOIN ingredient_category on ingredient_category.id_category= ingredient.id_category

                                      INNER JOIN nutrient_macro ON nutrient_macro.id_ingredient=ingredient.id_ingredient
                                      INNER JOIN nutrient_micro ON nutrient_micro.id_ingredient=ingredient.id_ingredient
                                      INNER JOIN vitamin ON vitamin.id_ingredient=ingredient.id_ingredient
                                      INNER JOIN vitamin_a_related_compounds ON vitamin_a_related_compounds.id_ingredient=ingredient.id_ingredient
                                      INNER JOIN fatty_acids ON fatty_acids.id_ingredient=ingredient.id_ingredient""", conn)
    
	# --- Данные для стандартизации названий нутриентов
    nutrients_transl= pd.read_sql("""SELECT name_in_database, name_ru FROM  nutrients_names """, conn)
  
    return food, disease, standart, ingredirents_df,nutrients_transl
  
