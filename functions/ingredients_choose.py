import streamlit as st
import pandas as pd

# ---- Интерфейс выбора ингредиентов пользователем для корректировки состава корма

all_nutrs=['moisture_per', 'protein_per', 'carbohydrate_per', 'fats_per',
		   'ash_g', 'fiber_g', 'cholesterol_mg', 'total_sugar_g',
           'choline_mg', 'selenium_mcg', 'iodine_mcg', 'linoleic_acid_g','alpha_linolenic_acid_g', 'arachidonic_acid_g', 'epa_g', 'dha_g',
           'calcium_mg', 'phosphorus_mg', 'magnesium_mg', 'sodium_mg', 'potassium_mg', 'iron_mg', 'copper_mg', 'zinc_mg', 'manganese_mg',
           'vitamin_a_mcg', 'vitamin_e_mg', 'vitamin_d_mcg', 'vitamin_b1_mg', 'vitamin_b2_mg', 'vitamin_b3_mg', 'vitamin_b5_mg', 
		   'vitamin_b6_mg', 'vitamin_b9_mcg', 'vitamin_b12_mcg', 'vitamin_c_mg', 'vitamin_k_mcg']


def ingredients_choose(ingredirents_df,finish_ingr_list):

   # --- Список заполняется рекомендованными ингредиентами	
   if len(st.session_state.selected_ingredients) == 0:
      st.session_state.selected_ingredients = set(finish_ingr_list)
	   
   # --- Инструмент добавления ингредиентов в состав корма (раскрывающиеся списки)
   # --- Иерархия выбора: категория -> ингредиент -> разновидность (подчасть) 
   st.title("🍲 Выбор ингредиентов")
   for category in ingredirents_df['category_ru'].dropna().unique():    # --- Основные категории (мясо, крупы, жиры и др.)
      with st.expander(f"{category}"):                                   
         df_cat = ingredirents_df[ingredirents_df['category_ru'] == category]
         for ingredient in df_cat['full_name_ingredient'].dropna().unique():   # --- Ингредиенты внутри категории
			ingredient_name_ru = (df_cat.loc[df_cat["full_name_ingredient"] == ingredient,"name_ingredient_ru"].iloc[0])

            df_ing = df_cat[df_cat['name_ingredient_ru'] == ingredient_name_ru]
            unique_descs = df_ing['format_ingredient_ru'].dropna().unique()
			 
			# --- Сочетание "ингредиент — разновидность" (если разновидность указана)
			# --- С одной разновиднотстью
            non_regular_descs = [desc for desc in unique_descs if desc.lower() != "обыкновенный"] 

			# --- Для ингредиентов с одной разновидностью создаётся отдельная кнопка выбора
            if len(unique_descs) == 1 and unique_descs[0].lower() != "обыкновенный":
               desc = unique_descs[0]
			   label=ingredient
               key = f"{category}_{ingredient}_{desc}"
               text = f"{ingredient} — {desc}" if desc != "Обыкновенный" else f"{ingredient}"  
               if st.button(text, key=key):
				  st.session_state.selected_ingredients.add(label)
                  st.session_state.show_result_2 = False
				   

			# --- Для ингредиентов с несколькими разновидностями создаётся вложенный список выбора
            elif non_regular_descs:
               with st.expander(f"{ingredient}"):           # --- подчасть ингредиента или его разновидность
                  for desc in non_regular_descs:
					 label = (df_ing.loc[df_ing["format_ingredient_ru"] == desc,"full_name_ingredient"].iloc[0])
                     key = f"{category}_{ingredient}_{desc}"
                     if st.button(f"{desc}", key=key):
						st.session_state.selected_ingredients.add(label)
                        st.session_state.show_result_2 = False

			# --- Ингредиенты c одной разновидностью (формат = "Обыкновенный")  
            regular_descs = [desc for desc in unique_descs if desc.lower() == "обыкновенный"]
            for desc in regular_descs:
			   label = (df_ing.loc[df_ing["format_ingredient_ru"] == desc,"full_name_ingredient"].iloc[0])
               key = f"{category}_{ingredient}_{desc}_reg"
               text = f"{ingredient}"  
               if st.button(text, key=key):
				  st.session_state.selected_ingredients.add(label)
                  st.session_state.show_result_2 = False

   
   # --- Отображение текущего списка ингредиентов для расчёта рецептуры
   st.markdown("### ✅ Выбранные ингредиенты:")
   if "to_remove" not in st.session_state:
      st.session_state.to_remove = None
   for i in sorted(st.session_state.selected_ingredients):
      col1, col2 = st.columns([5, 1])
	  i_ru=(ingredirents_df.loc[ingredirents_df["full_name_ingredient"] == i,"ingredient_format_cat"].iloc[0])
      col1.write(i_ru.replace(" — Обыкновенный", ""))
      if col2.button("❌", key=f"remove_{i}"):     # --- Кнопка удаления ингредиента из списка
         st.session_state.to_remove = i
   if st.session_state.to_remove:           # --- Удаление ингредиента при нажатии кнопки
	  st.session_state.selected_ingredients.discard(st.session_state.to_remove) 
      st.session_state.to_remove = None
      st.rerun()

   # --- Формирование финального списка ингредиентов для расчёта	
   ingredient_names = list(st.session_state.selected_ingredients)
	
   return  ingredient_names
	  
