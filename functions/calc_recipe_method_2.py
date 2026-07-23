import streamlit as st
import numpy as np
import itertools

# ---- Расчёт соотношения ингредиентов альтернативным методом
# ---- Метод перебора всех возможных соотношений ингредиентов с выбором варианта с минимальным отклонением от нутриентных показателей

main_nutrs=['moisture_per', 'protein_per', 'carbohydrate_per', 'fats_per']

def calc_recipe(ingr_ranges,nutr_ranges,ingredient_names,food):
   st.error("❌ Не удалось найти оптимальное решение. Попробуйте другие параметры.")
   with st.spinner("🔄 Ищем по другому методу..."):
      # --- Вычисление всех возможных соотношений ингредиентов
      step = 1  
      variants = []
      ranges = [np.arange(low, high + step, step) for (low, high) in ingr_ranges]
      for combo in itertools.product(*ranges):
         if abs(sum(combo) - 100) < 1e-6:
            variants.append(combo)
      best_recipe = None

      # --- Поиск соотношения ингредиентов с минимальным отклонением от заданных нутриентных норм
      min_penalty = float("inf")
      for combo in variants:
         ingredients_combo = dict(zip(ingredient_names, combo))
         nutrients_combo = {nutr: 0.0 for nutr in main_nutrs}
         for i, ingr in enumerate(ingredient_names):
            for nutr in main_nutrs:
               nutrients_combo[nutr] += ingredients_combo[ingr] * food[ingr][nutr]/100
         penalty = 0
         for nutr in main_nutrs:
            val = nutrients_combo[nutr]
            min_val = nutr_ranges[nutr][0]
            max_val = nutr_ranges[nutr][1]
            if val < min_val:
               penalty += min_val - val
            elif val > max_val:
               penalty += val - max_val
         if penalty < min_penalty:
            min_penalty = penalty
            best_recipe = (ingredients_combo, nutrients_combo)
   return best_recipe
