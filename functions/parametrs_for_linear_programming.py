import streamlit as st
import pandas as pd
import numpy as np

# ---- Подготовка параметров для расчёта оптимального соотношения ингредиентов с использованием метода линейного программирования

main_nutrs=['moisture_per', 'protein_per', 'carbohydrate_per', 'fats_per']

# ---- Функция рекомендации нутриентов для максимизации (целевая функция)
def maximize_function(food_df, nutrient_preds):
   df_wet = (food_df[(food_df["food_form"] == "wet food") & (food_df["moisture"] > 50)].copy()).explode("category")
   maximize = [ i for i in main_nutrs  if nutrient_preds[i.replace("_per","")] > df_wet[i.replace("_per","")].mean()]
   return  maximize

# ---- Установка ограничений (min, max) на ингредиенты
# ---- Ограничения зависят от их роли как преимущественного источника нутриента
# ---- Отображение ограничений в виде ползунков (пользователь может корректировать вручную)
def ingredients_limits(ingredirents_df, ingredient_names):

   # --- Формирование списков ингредиентов по источникам основных нутриентов 	
   proteins=ingredirents_df[ingredirents_df["category_ru"].isin(["Яйца и молочные продукты", "Мясо"])]["ingredient_format_cat"].tolist()
   oils=ingredirents_df[ingredirents_df["category_ru"].isin([ "Масло и жир"])]["ingredient_format_cat"].tolist()
   carbonates_cer=ingredirents_df[ingredirents_df["category_ru"].isin(["Крупы"])]["ingredient_format_cat"].tolist()
   carbonates_veg=ingredirents_df[ingredirents_df["category_ru"].isin(["Зелень и специи","Овощи и фрукты"])]["ingredient_format_cat"].tolist()
   other=ingredirents_df[ingredirents_df["category_ru"].isin(["Вода, соль и сахар","Дополнительные пищевые компоненты"])]["ingredient_format_cat"].tolist()

   st.subheader("Ограничения по количеству ингредиентов (в % от 100 г):")
   ingr_ranges = []	
   for ingr in ingredient_names:
      if ingr in proteins:
         ingr_ranges.append(st.slider(f"{ingr.replace(" — Обыкновенный", "")}", 0, 100, (40,60)))
      elif ingr in oils:
         ingr_ranges.append(st.slider(f"{ingr.replace(" — Обыкновенный", "")}", 0, 100, (1,10)))
      elif ingr in carbonates_cer:
         ingr_ranges.append(st.slider(f"{ingr.replace(" — Обыкновенный", "")}", 0, 100, (5,35)))
      elif ingr in carbonates_veg:
         ingr_ranges.append(st.slider(f"{ingr.replace(" — Обыкновенный", "")}", 0, 100, (5,25)))
      elif "Вода" in ingr:
         ingr_ranges.append(st.slider(f"{ingr.replace(" — Обыкновенный", "")}", 0, 100, (0,30)))
      elif ingr in other:
         ingr_ranges.append(st.slider(f"{ingr.replace(" — Обыкновенный", "")}", 0, 100, (1,3)))
   return ingr_ranges

# ---- Установка ограничений (min, max) для основных нутриентов
# ---- Отображение ограничений в виде ползунков (ручная корректировка пользователем)
def nutrients_limits(nutrient_preds):
   st.subheader("Ограничения по нутриентам:")
   nutr_ranges = {}
   nutr_ranges['moisture_per'] = st.slider(f"{'Влага'}", 0, 100, (int(nutrient_preds["moisture"]-5), int(nutrient_preds["moisture"]+5)))
   nutr_ranges['protein_per'] = st.slider(f"{'Белки'}", 0, 100, (int(nutrient_preds["protein"]-3), int(nutrient_preds["protein"]+6)))
   nutr_ranges['carbohydrate_per'] = st.slider(f"{'Углеводы'}", 0, 100, (int(nutrient_preds["carbohydrate"]-4), int(nutrient_preds["carbohydrate"]+4)))
   nutr_ranges['fats_per'] = st.slider(f"{'Жиры'}", 0, 100, (int(nutrient_preds["fats"]-1), int(nutrient_preds["fats"]+1)) )
   return nutr_ranges				               

# ---- Подготовка параметров задачи линейного программирования
def lin_prog_parametrs(food,ingredient_names,nutr_ranges,ingr_ranges,maximaze_nutrs,nutrients_transl):

   # --- Матрица A: Столбцы — ингредиенты, Строки — нутриенты, Элемент A[i, j] — содержание i-го нутриента в j-м ингредиенте
   # --- Для каждого нутриента формируются отдельные строки для min и max ограничений 
   A = [ [food[ing][nutr]/100 if val > 0 else -food[ing][nutr]/100
          for ing in ingredient_names]
          for nutr in nutr_ranges
          for val in (-nutr_ranges[nutr][0], nutr_ranges[nutr][1]) ]
   # --- Вектор b: Содержит граничные значения по нутриентам. Каждый элемент соответствует строке матрицы A
   b = [ val / 100 for nutr in nutr_ranges
         for val in (-nutr_ranges[nutr][0], nutr_ranges[nutr][1]) ]
	
   # --- Ограничение суммы ингредиентов: Сумма долей всех ингредиентов = 1 (или 100%)
   A_eq = [[1 for _ in ingredient_names]]
   b_eq = [1.0]
	
   # --- Дополнительные ограничения: индивидуальные лимиты на каждый ингредиент (min, max)
   bounds = [(low/100, high/100) for (low, high) in ingr_ranges]

   # --- Интерфейс выбора нутриента(ов) для максимизации
   st.subheader("Что максимизировать?")
   selected_maximize = st.multiselect(
	            "Выберите нутриенты для максимизации:",
                [ nutrients_transl.loc[nutrients_transl["name_in_database"] == nutr,"name_ru"].iloc[0].split(",")[0] 
				  for nutr in main_nutrs],
                default=[ nutrients_transl.loc[nutrients_transl["name_in_database"] == nutr,"name_ru"].iloc[0].split(",")[0]  
						     for nutr in maximaze_nutrs]  )
   # --- Инициализация глобальной переменной списка нутриентов для максимизации
   if "prev_selected_maximize" not in st.session_state:
      st.session_state.prev_selected_maximize = [nutrients_transl.loc[nutrients_transl["name_in_database"] == nutr,"name_ru"].iloc[0].split(",")[0] 
												 for nutr in main_nutrs]
   # --- При изменении списка нутриентов для максимизации сбрасывается рассчитанная рецептура 	   
   if selected_maximize != st.session_state.prev_selected_maximize:
      st.session_state.show_result_2 = False
      st.session_state.prev_selected_maximize = selected_maximize.copy()
   selected_maximize=[nutrients_transl.loc[nutrients_transl["name_ru"].str.contains(nutr, na=False),"name_in_database"].iloc[0] for nutr in selected_maximize]

   # --- Преобразование списка нутриентов в вектор коэффициентов целевой функции
   f = [-sum(food[i][nutr] for nutr in selected_maximize) for i in ingredient_names]
   return A, b, A_eq, b_eq,selected_maximize,f,bounds
