import streamlit as st
import pandas as pd
import sqlite3
from sklearn.preprocessing import MinMaxScaler

numeric_cols = ['moisture', 'protein', 'fat','carbohydrate', 'dha', 'epa', 'epa_dha', 
                'omega_3', 'omega_6','linoleic_acid', 'alpha_linolenic_acid', 
                'essential_fatty_acids','taurine', 'l_arginine', 'l_lysine', 
                'glutamine_glutamate', 'dl_methionine_l_cystine', 'bcaa_total', 
                'hydroxyproline', 'beta_carotene', 'l_carnitine', 'glucosamine', 
                'chondroitin_sulfate', 'calcium', 'phospohorus', 'potassium', 'sodium', 
                'magnesium', 'iron', 'copper', 'zinc', 'chloride', 'sulphur', 
                'vitamin_a', 'vitamin_c', 'vitamin_d', 'vitamin_e', 'vitamin_k', 
                'vitamin_b1', 'vitamin_b2','vitamin_b3', 'vitamin_b5', 
                'vitamin_b6', 'vitamin_b7', 'vitamin_b9', 'vitamin_b12' ]

def prepocess_data(food):
    numeric_cols_up = [col for col in numeric_cols if col in food.columns]
    # Масштабирование отдельно для dry и wet
    scaler = MinMaxScaler()
    
    for food_type in food['food_form'].dropna().unique():
       mask = food['food_form'] == food_type
       food.loc[mask, numeric_cols_up] = scaler.fit_transform( food.loc[mask, numeric_cols_up])
    food = food.rename(
    columns={"moisture":"moisture_per",
             'protein': 'protein_per',
             'fat': 'fats_per',
             'carbohydrate': 'carbohydrate_per',
             'calcium': 'calcium_mg',
             'phospohorus': 'phosphorus_mg',
             'potassium': 'potassium_mg',
             'sodium': 'sodium_mg',
             'magnesium': 'magnesium_mg',
             'iron': 'iron_mg',
             'copper': 'copper_mg',
             'zinc': 'zinc_mg',
             'vitamin_a': 'vitamin_a_mcg',
             'vitamin_c': 'vitamin_c_mg',
             'vitamin_d': 'vitamin_d_mcg',
             'vitamin_e': 'vitamin_e_mg',
             'vitamin_k': 'vitamin_k_mcg',
             'vitamin_b1': 'vitamin_b1_mg',
             'vitamin_b2': 'vitamin_b2_mg',
             'vitamin_b6': 'vitamin_b6_mg',
             'vitamin_b9': 'vitamin_b9_mcg',
             'vitamin_b3':'vitamin_b3_mg',
             'vitamin_b5':'vitamin_b5_mg',
             'vitamin_b12':'vitamin_b12_mcg',
             'beta_carotene': 'beta_carotene_mcg',
             'linoleic_acid': 'linoleic_acid_g',
             'alpha_linolenic_acid': 'alpha_linolenic_acid_g',
             'epa': 'epa_g',
             'dha': 'dha_g'})
    return food

@st.cache_data(show_spinner=False)
def load_data():

    # --- Данные о кормах для собак и их рецептурах
    conn = sqlite3.connect("data_base/pet_food.db")
    food=pd.read_sql("""SELECT df.id_dog_food,df.source, df.name_product,df.description,   df.ingredients, bs.breed_size,  ls.life_stage, ff.food_form, dfc.flavour, GROUP_CONCAT(DISTINCT c.category) AS category,  
                        nm.calories, nm.moisture, nm.protein, nm.fat, nm.carbohydrate, 
                        nm.crude_fibre, nm.crude_ash, nm.soluble_fibre, nm.total_dietary_fiber, nm.insoluble_fibre, nm.starch, 

                        m.calcium, m.phospohorus, m.potassium, m.sodium, m.magnesium, m.iron, m.copper, m.zinc, m.chloride, m.sulphur, 

                        v.vitamin_a, v.vitamin_c, v.vitamin_d, v.vitamin_e, v.vitamin_k, v.vitamin_b1, v.vitamin_b2, v.vitamin_b3, v.vitamin_b5, 
                        v.vitamin_b6, v.vitamin_b7, v.vitamin_b9, v.vitamin_b12, 

                        fa.dha, fa.epa, fa.epa_dha, fa.omega_3, fa.omega_6, fa.linoleic_acid, fa.alpha_linolenic_acid, fa.essential_fatty_acids, 

                        bc.taurine, bc.l_arginine, bc.l_lysine, bc.glutamine_glutamate, bc.dl_methionine_l_cystine, bc.bcaa_total, bc.hydroxyproline, 
                        bc.beta_carotene, bc.l_carnitine, bc.glucosamine, bc.chondroitin_sulfate  

                        FROM dog_food df  
                        LEFT JOIN dog_food_characteristics dfc ON df.id_dog_food = dfc.id_dog_food  
                        LEFT JOIN breed_size bs ON dfc.id_breed_size = bs.id_breed_size  
                        LEFT JOIN life_stage ls ON dfc.id_life_stage = ls.id_life_stage  
                        LEFT JOIN food_form ff ON dfc.id_food_form = ff.id_food_form  
                        LEFT JOIN food_category_connect fcc ON df.id_dog_food = fcc.id_dog_food  
                        LEFT JOIN category c ON fcc.id_category = c.id_category  
                        LEFT JOIN nutrient_macro nm ON df.id_dog_food = nm.id_dog_food  
                        LEFT JOIN minerals m ON df.id_dog_food = m.id_dog_food  
                        LEFT JOIN vitamins v ON df.id_dog_food = v.id_dog_food  
                        LEFT JOIN fatty_acid fa ON df.id_dog_food = fa.id_dog_food  
                        LEFT JOIN bioactive_compounds bc ON df.id_dog_food = bc.id_dog_food  
                        GROUP BY df.id_dog_food""", conn)
    food["category"] = (food["category"].fillna("").str.split(",").apply(lambda x: [i.strip() for i in x if i.strip()]))
    food=prepocess_data(food)

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

    ingredirents_df["omega_3"] = ( ingredirents_df["epa_g"].fillna(0) + ingredirents_df["dha_g"].fillna(0) + ingredirents_df["alpha_linolenic_acid_g"].fillna(0))
    ingredirents_df["omega_6"] = ( ingredirents_df["linoleic_acid_g"].fillna(0) + ingredirents_df["arachidonic_acid_g"].fillna(0))
    ingredirents_df['epa_dha'] = ingredirents_df['epa_g']*0.5 + ingredirents_df['dha_g']*0.5

    return food, disease, standart, ingredirents_df,nutrients_transl
  
