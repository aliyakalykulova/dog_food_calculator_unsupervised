import streamlit as st
import pandas as pd
from scipy.optimize import linprog  
import numpy as np

from functions.init_global import init_global
from functions.connect_database import  load_data

from functions.train_models import build_text_pipeline
from functions.train_models import build_categorical_encoder
from functions.train_models import combine_features
from functions.train_models import train_ingredient_models
from functions.train_models import train_nutrient_models
from functions.train_models import  apply_category_masks

from functions.choose_dog_characteristics import choose_dog_characteristics

from functions.norm_kcal_nutr import kcal_calculate

from functions.recommend_ingredients_nutrients import ingredient_recommendation
from functions.recommend_ingredients_nutrients import nutrients_recommendation
from functions.ingredients_choose import ingredients_choose  

from functions.parametrs_for_linear_programming import maximize_function
from functions.parametrs_for_linear_programming import ingredients_limits 
from functions.parametrs_for_linear_programming import nutrients_limits 
from functions.parametrs_for_linear_programming import lin_prog_parametrs

from functions.calc_recipe_method_2 import calc_recipe
from functions.show_results import show_resuts_success


main_nutrs=['moisture_per', 'protein_per', 'carbohydrate_per', 'fats_per']

# ---- Загрузка данных из базы данных (connect_database.py)
food_df, disease_df, df_standart, ingredirents_df,nutrients_transl= load_data()

# ---- Обучение модели рекомендации ингредиентов (train_models.py)
vectorizer, svd, X_text_reduced = build_text_pipeline(food_df["description"], n_components=100)
encoder, X_categorical = build_categorical_encoder(food_df)
X_categorical=apply_category_masks(X_categorical,encoder)
X_combined = combine_features(X_text_reduced, X_categorical)
ingredient_models, frequent_ingredients = train_ingredient_models(food_df, X_combined)

# ---- Обучение модели расчёта количества нутриентов (только влажные корма) (train_models.py)
vectorizer_wet, svd_wet, X_text_reduced_wet = build_text_pipeline(food_df[food_df["food_form"]=="wet food"]["description"], n_components=100)
encoder_wet, X_categorical_wet = build_categorical_encoder(food_df[food_df["food_form"]=="wet food"])
X_categorical_wet=apply_category_masks(X_categorical_wet,encoder_wet)
X_combined_wet = combine_features(X_text_reduced_wet, X_categorical_wet)
ridge_models, scalers = train_nutrient_models(food_df[food_df["food_form"]=="wet food"], X_combined_wet)

# ---- Инициализация глобальных переменных (init_global.py)
init_global()

# ---- Ввод характеристик собаки (choose_dog_characteristics.py)
user_breed, breed_size, avg_wight, age_type_categ = choose_dog_characteristics(disease_df)

standard_care_map = {
    "puppy": "Уход за щенками",
    "adult": "Уход за взрослыми",
    "senior": "Уход за пожилыми"
}
st_c = standard_care_map.get(age_type_categ)

if user_breed:
   info = disease_df[disease_df["name_breed"] == user_breed]
   if not info.empty:
	  # ---- Вывод списка возможных заболеваний в зависимости от породы
      diseases = [  dis for dis in info["name_disease"].unique().tolist()
                    if dis not in standard_care_map.values() or dis == st_c]
      selected_disease = st.selectbox("Заболевание:", diseases)
      match = info.loc[info["name_disease"] == selected_disease, "name_disorder"]
      disorder_type = match.iloc[0] if not match.empty else selected_disease

	  # ---- При изменении данных о собаке (порода, заболевание) сбрасываются текущие рекомендации корма 
      if user_breed != st.session_state.user_breed or selected_disease!= st.session_state.disorder:
         st.session_state.user_breed = user_breed
         st.session_state.disorder = selected_disease
         st.session_state.show_result_1 = False
         st.session_state.show_result_2 = False
            
      # ---- Кнопка расчёта рекомендаций корма (калории, ингредиенты, нутриенты)
      if st.button("Составить рекомендации"):
         st.session_state.show_result_1 = True
	 
      if st.session_state.show_result_1:
	     # ---- Расчёт суточной потребности в калориях по формулам FEDIAF (norm_kcal_nutr.py)
         kcal =kcal_calculate( age_type_categ, avg_wight)
         metobolic_energy = int(round(st.number_input("Киллокаллории в день", min_value=0.0, step=0.1,  value=round(kcal,1) ),1))
		 
		 # --- При изменении значения калорий сбрасывается рассчитанная рецептура корма	
         if st.session_state.kkal_sel!=metobolic_energy:
            st.session_state.kkal_sel=metobolic_energy
            st.session_state.show_result_1 = True
            st.session_state.show_result_2 = False

		 # --- Вычисление рекомендаций ингредиентов и количества нутриентов с помощью обученных моделей (recommend_ingredients_nutrients.py)
         ingredients_finish,keywords=ingredient_recommendation(ingredient_models,breed_size, age_type_categ,disorder_type, selected_disease,vectorizer,svd,encoder, df_standart)
         nutrient_preds = nutrients_recommendation(vectorizer_wet,keywords,svd_wet,encoder_wet, breed_size, age_type_categ, ridge_models,scalers )
         
         if len(ingredients_finish)>0: 
			# ---- Интерфейс для редактирования списка ингредиентов пользователем (ingredients_choose.py)
            ingredirents_df, ingredient_names,food = ingredients_choose(ingredirents_df,ingredients_finish)
			 
			# ---- Выбор нутриентов для максимизации в корме (параметры линейного программирования) (parametrs_for_linear_programming.py) 
            maximaze_nutrs = maximize_function(food_df, nutrient_preds)
			 
            if ingredient_names:
			   # ---- Установка пределов (min, max) содержания ингредиентов и нутриентов в корме (parametrs_for_linear_programming.py)
               ingr_ranges= ingredients_limits(ingredirents_df, ingredient_names)
               nutr_ranges = nutrients_limits(nutrient_preds)
				
			   # --- При изменении пределов содержания ингредиентов и нутриентов сбрасывается рассчитанная рецептура корма
               if ingr_ranges != st.session_state.prev_ingr_ranges:
                  st.session_state.show_result_2 = False
                  st.session_state.prev_ingr_ranges = ingr_ranges.copy()
               if nutr_ranges != st.session_state.prev_nutr_ranges:
                  st.session_state.show_result_2 = False
                  st.session_state.prev_nutr_ranges = nutr_ranges.copy()
	  
			   # ---- Проверка соотношения ингредиентов и пропорциональная корректировка минимальных и максимальных пределов при нарушении условий
			   # ---- Проверка условия: сумма минимальных долей ингредиентов < 100, сумма максимальных долей > 100
               lowest=sum([low for (low, high) in ingr_ranges])
               highest=sum([high for (low, high) in ingr_ranges])
               ingr_ranges_2=ingr_ranges
               if lowest>100:
                  st.write("Минимальные доли ингредиентов превышают 100%. Значения были пропорционально уменьшены.")
                  factor=99/lowest
                  ingr_ranges_2=[(low*factor, high) for (low, high) in ingr_ranges]
               elif highest<100:
                  st.write("Максимальные доли ингредиентов меньше 100%. Значения были пропорционально увеличены.")
                  factor=101/highest
                  ingr_ranges_2=[(low, high*factor) for (low, high) in ingr_ranges]
				
			   # --- Подготовка параметров на основе заданных условий для расчёта рецептуры методом линейного программирования (parameters_for_linear_programming.py) 	   
               A, b, A_eq, b_eq,selected_maximize,f,bounds = lin_prog_parametrs(food,ingredient_names,nutr_ranges,ingr_ranges_2,maximaze_nutrs,nutrients_transl)
             
			   # --- Кнопка расчёта рецептуры	
               if st.button("🔍 Рассчитать оптимальный состав"):
                  st.session_state.show_result_2 = True

			
               if st.session_state.show_result_2:
				  # --- Расчёт рецептуры методом линейного программирования
                  res = linprog(f, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

				  # --- Если решение найдено методом линейного программирования  
                  if res.success:
                     st.success("✅ Решение найдено!")
					  
					 # ---- Приведение результатов к удобному формату отображения (общее содержание нутриентов и соотношение ингредиентов)
                     nutrients_combo = {nutr: int(round(sum(res.x[i] * food[name][nutr]/100 for i, name in enumerate(ingredient_names)) * 100, 0))
                                       for nutr in main_nutrs}
                     ingredients_combo={name: int(round(val * 100, 0)) for name, val in zip(ingredient_names,res.x)}
                     best_recipe= (ingredients_combo,nutrients_combo)

					 # ---- Отображение результатов (show_results.py)
                     show_resuts_success(best_recipe,food,nutrients_transl,metobolic_energy, age_type_categ,
                                        ingredient_names, ingr_ranges,nutr_ranges)                         
                  else:
					 # ---- Если решение не найдено, используется комбинаторный метод
					 # ---- Расчёт рецептуры комбинаторным методом с выбором варианта с минимальным отклонением от нутриентных лимитов (calc_recipe_method_2.py)	 
                     best_recipe=calc_recipe(ingr_ranges_2,nutr_ranges,ingredient_names,food)
                     if best_recipe:
                        st.success("⚙️ Найден состав перебором:")
					    # ---- Отображение результатов (show_results.py)
                        show_resuts_success(best_recipe, food, nutrients_transl, metobolic_energy, age_type_categ,
                                            ingredient_names, ingr_ranges,nutr_ranges)
                     else:
                        st.error("🚫 Измените соотношение ингредиентов и/или нутриентов")
         else:
            st.info("👈 Пожалуйста, выберите хотя бы один ингредиент.")
