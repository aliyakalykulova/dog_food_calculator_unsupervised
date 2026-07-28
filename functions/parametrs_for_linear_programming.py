import streamlit as st
import pandas as pd
import numpy as np

# ---- Подготовка параметров для расчёта оптимального соотношения ингредиентов с использованием метода линейного программирования

main_nutrs=['moisture_per', 'protein_per', 'carbohydrate_per', 'fats_per']



# ---- Установка ограничений (min, max) на ингредиенты
# ---- Ограничения зависят от их роли как преимущественного источника нутриента
# ---- Отображение ограничений в виде ползунков (пользователь может корректировать вручную)
def ingredients_limits(ingredirents_df, ingredient_names,finish_ingr_list):
   st.subheader("🌿 Рекомендуемые ингредиенты")
   for ing in finish_ingr_list:
      ing_ru=(ingredirents_df.loc[ingredirents_df["full_name_ingredient"] == ing,"ingredient_format_cat"].iloc[0])
      st.write("• " + ing_ru.replace("— Обыкновенный",""))
      
   proteins=ingredirents_df[ingredirents_df["category_ru"].isin(["Яйца и молочные продукты", "Мясо"])]["full_name_ingredient"].tolist()
   oils=ingredirents_df[ingredirents_df["category_ru"].isin([ "Масло и жир"])]["full_name_ingredient"].tolist()
   carbonates_cer=ingredirents_df[ingredirents_df["category_ru"].isin(["Крупы"])]["full_name_ingredient"].tolist()
   carbonates_veg=ingredirents_df[ingredirents_df["category_ru"].isin(["Овощи и фрукты"])]["full_name_ingredient"].tolist()
   carbonates_grace=ingredirents_df[ingredirents_df["category_ru"].isin(["Зелень и специи"])]["full_name_ingredient"].tolist()
   other=ingredirents_df[ingredirents_df["category_ru"].isin(["Вода, соль и сахар"])]["full_name_ingredient"].tolist()
   
   st.subheader("Ограничения по количеству ингредиентов (в % от 100 г):")
   ingr_ranges = []
   for ingr in ingredient_names:
      ingr_ru=(ingredirents_df.loc[ingredirents_df["full_name_ingredient"] == ingr,"ingredient_format_cat"].iloc[0])
      if ingr in proteins:
         ingr_ranges.append(st.slider(f"{ingr_ru.replace(" — Обыкновенный", "")}", 0, 100, (50,90)))
      elif ingr in oils:
         ingr_ranges.append(st.slider(f"{ingr_ru.replace(" — Обыкновенный", "")}", 0, 100, (1,10)))
      elif ingr in carbonates_cer:
         ingr_ranges.append(st.slider(f"{ingr_ru.replace(" — Обыкновенный", "")}", 0, 100, (5,35)))
      elif ingr in carbonates_veg:
         ingr_ranges.append(st.slider(f"{ingr_ru.replace(" — Обыкновенный", "")}", 0, 100, (5,25)))
      elif "WATER" in ingr:
         ingr_ranges.append(st.slider(f"{ingr_ru.replace(" — Обыкновенный", "")}", 0, 100, (0,30)))
      else:
         ingr_ranges.append(st.slider(f"{ingr_ru.replace(" — Обыкновенный", "")}", 0, 100, (1,3)))
   return ingr_ranges


# ---- Установка ограничений (min, max) для основных нутриентов
# ---- Отображение ограничений в виде ползунков (ручная корректировка пользователем)
def nutrients_limits(food_df):
   st.subheader("Ограничения по нутриентам:")
   nutr_ranges = {}
   nutr_ranges['moisture_per'] = st.slider(f"{'Влага'}", 0, 100, (65, 95))
   
   s = food_df[(food_df["food_form"] == "wet food") &(food_df["moisture_per"] > 0.5) ]["protein_per"]
   protein_min=(100-nutr_ranges['moisture_per'][0])*0.25
   protein_min=protein_min if protein_min > s.mean()-s.std() else s.mean()-s.std()
   nutr_ranges['protein_per'] = st.slider(f"{'Белки'}", 0, 100, (int(protein_min), 30))
   
   s = food_df[(food_df["food_form"] == "wet food") &(food_df["moisture_per"] > 0.5) ]["fats_per"]
   fats_min= (100-nutr_ranges['moisture_per'][0])*0.085
   fats_min=fats_min if fats_min > s.mean()-s.std() else s.mean()-s.std()
   nutr_ranges['fats_per'] = st.slider(f"{'Жиры'}", 0, 100, (int(fats_min),15) )
   
   carb_max=100-nutr_ranges['protein_per'][0]-nutr_ranges['fats_per'][0]-nutr_ranges['moisture_per'][0]
   nutr_ranges['carbohydrate_per'] = st.slider(f"{'Углеводы'}", 0, 100, (5, int(carb_max)))
   
   return nutr_ranges


# ---- Подготовка параметров задачи линейного программирования
def lin_prog_parametrs(food,ingredient_names,nutr_ranges,ingr_ranges,selected_maximize):

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


   # --- Преобразование списка нутриентов в вектор коэффициентов целевой функции
   f = [-sum(food[i][nutr] for nutr in selected_maximize) for i in ingredient_names]
   return A, b, A_eq, b_eq,f,bounds
