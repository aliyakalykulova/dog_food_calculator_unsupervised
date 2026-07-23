import streamlit as st
import pandas as pd
from ctypes import create_string_buffer
import itertools
import matplotlib.pyplot as plt
import textwrap
from functions.norm_kcal_nutr import nutrient_norm

# ---- Вывод результатов расчета рецептуры: соотношение ингредиентов и нутриентный профиль

main_nutrs=['moisture_per', 'protein_per', 'carbohydrate_per', 'fats_per']
other_nutrients_1=['ash_g', 'fiber_g', 'cholesterol_mg', 'total_sugar_g']
other_nutrients_2 = ['choline_mg', 'selenium_mcg', 'iodine_mcg', 'linoleic_acid_g','alpha_linolenic_acid_g', 'arachidonic_acid_g', 'epa_g', 'dha_g']
other_nutrients=other_nutrients_1+other_nutrients_2
major_minerals=['calcium_mg', 'phosphorus_mg', 'magnesium_mg', 'sodium_mg', 'potassium_mg', 'iron_mg', 'copper_mg', 'zinc_mg', 'manganese_mg']
vitamins=['vitamin_a_mcg', 'vitamin_e_mg', 'vitamin_d_mcg', 'vitamin_b1_mg', 'vitamin_b2_mg', 'vitamin_b3_mg', 'vitamin_b5_mg', 
          'vitamin_b6_mg', 'vitamin_b9_mcg', 'vitamin_b12_mcg', 'vitamin_c_mg', 'vitamin_k_mcg']

# ---- Вывод графика нутриентов: сравнение нормы потребления и содержания в рассчитанной рецептуре корма 
def bar_print(total_norm,current_value,name_ing,mg):
   maxi_dat = total_norm if total_norm>current_value else current_value
   norma = 100 if maxi_dat== total_norm else (total_norm/current_value)*100
   curr =  100 if maxi_dat== current_value else (current_value/total_norm)*100
   maxi_lin = 100*1.2
   diff = current_value - total_norm
   fig, ax = plt.subplots(figsize=(5, 1))
   ax.axis('off')
   ax.set_xlim(-60, maxi_lin+8)
   ax.set_ylim(-0.5, 0.5)
   ax.plot([0, maxi_lin], [0, 0], color='#e0e0e0', linewidth=10, solid_capstyle='round', alpha=0.8)
   fixed_space = -10 
   wrapped_text = "\n".join(textwrap.wrap(name_ing, width=15))
   ax.text(fixed_space, 0, wrapped_text, ha='right', va='center', fontsize=13)
   if current_value < total_norm:
      ax.plot([0, norma], [0, 0], color='green', linewidth=10, solid_capstyle='round')
      ax.plot([0, curr], [0, 0], color='purple', linewidth=10, solid_capstyle='round')
   else:
      ax.plot([0, curr], [0, 0], color='darkgray', linewidth=10, solid_capstyle='round')
      ax.plot([0, norma], [0, 0], color='green', linewidth=10, solid_capstyle='round')
   if diff < 0:
      ax.text(maxi_lin+10, 0, f"Дефицит: {round(abs(diff),2)} {mg}", ha='left', va='center', fontsize=13, color='black')
   else:
      ax.text(maxi_lin+10, 0,"                            ", ha='left', va='center', fontsize=13, color='black')
   ax.text(curr, 0.2, f"Текущее\n{round(current_value,2)}", color='purple', ha='center', va='bottom', fontsize=9)
   ax.text(norma, -0.2,  f"Норма\n{round(total_norm,2)}", color='green', ha='center', va='top', fontsize=9)
   return fig
         
# ---- Вывод содержания нутриентов в рассчитанной рецептуре 
def show_nutr_content(count_all_nutr, nutrients_transl, kkal_sel, age_type_categ, weight_sel, select_reproductive_status):
   other_nutrient_norms = nutrient_norm(kkal_sel, age_type_categ, weight_sel, select_reproductive_status)
   for i in range(0, len(other_nutrients), 2):
      cols = st.columns(2)
      for j, col in enumerate(cols):
         if i + j < len(other_nutrients):
            nutris = (other_nutrients)[i + j]
            nutr_text=nutrients_transl.loc[nutrients_transl["name_in_database"] == nutris,"name_ru"].iloc[0].split(",")    
            emg=""
            if len(nutr_text)>1:
                  emg=nutr_text[-1].strip() if "%" not in nutr_text[-1] else "g"
            else:
               emg="g"
            with col:
               st.markdown(f"**{nutr_text[0]}**: {count_all_nutr.get(nutris, '')} {emg}")

   coli, colii=st.columns([6,3])
   with coli:
      for i in range(0, len(other_nutrients_2)):
         nutris = other_nutrients_2[i]
         nutr_text=nutrients_transl.loc[nutrients_transl["name_in_database"] == nutris,"name_ru"].iloc[0].split(",") 
        
         emg = nutr_text[-1].strip() if len(nutr_text)>1 and "%" not in nutr_text[-1] else "g"
         if nutr_text[0] in other_nutrient_norms:
            norma = other_nutrient_norms[nutr_text[0]]
            st.pyplot(bar_print(norma, count_all_nutr.get(nutris, ''), nutr_text[0]+", "+ emg, str(emg)))
                               
   st.markdown("#### 🔹 Минералы")
   coli, colii=st.columns([6,3])
   with coli:
      for i in range(0, len(major_minerals)):
         nutris = major_minerals[i]
         nutr_text=nutrients_transl.loc[nutrients_transl["name_in_database"] == nutris,"name_ru"].iloc[0].split(",") 
         emg = nutr_text[-1].strip() if len(nutr_text)>1 and "%" not in nutr_text[-1] else "g"
         if nutris in other_nutrient_norms:
            norma = other_nutrient_norms[nutris]
            st.pyplot(bar_print(norma, count_all_nutr.get(nutris, ''), nutr_text[0]+", "+ emg, str(emg)))
                                                  
   st.markdown("#### 🍊 Витамины")
   coli, colii=st.columns([6,3])
   with coli:
      for i in range(0, len(vitamins)):
         nutris = vitamins[i]
         nutr_text=nutrients_transl.loc[nutrients_transl["name_in_database"] == nutris,"name_ru"].iloc[0].split(",") 
         emg = nutr_text[-1].strip() if len(nutr_text)>1 and "%" not in nutr_text[-1] else "g"
         if nutris in other_nutrient_norms:
            norma = other_nutrient_norms[nutris]
            st.pyplot(bar_print(norma, count_all_nutr.get(nutris, ''), nutr_text[0]+", "+ emg, str(emg)))

   # ---- Вывод недостающих нутриентов и их количества, которое необходимо добавить в корм для достижения суточной нормы     
   st.markdown("### Необходимо добавить")
   for name,amount in count_all_nutr.items():
      if name in other_nutrient_norms:
         diff=other_nutrient_norms[name] - amount
         if diff>0:
            name_n=nutrients_transl.loc[nutrients_transl["name_in_database"] == name,"name_ru"].iloc[0].split(",") 
            emg = name_n[-1].strip() if len(name_n)>1 and "%" not in name_n[-1] else "g"
            st.write(f"**{name_n[0]}:** {round(diff,2)} {emg}")
                                        
# ---- Вывод графика сравнения установленных пользователем лимитов и содержания ингредиентов и нутриентов в рассчитанной рецептуре
def show_figures_ingr_nutr(ingr_ranges, nutr_ranges, ingredients_combo, nutrients_combo, nutrients_transl):
   # --- График для ингредиентов     
   ingredient_names = list(ingredients_combo.keys())
   fig1, ax1 = plt.subplots(figsize=(10, 6))
   ingr_vals = [ingredients_combo[i] for i in ingredient_names]
   ingr_lims = ingr_ranges
   wrapped_ingredients = [  '\n'.join(textwrap.wrap(label.replace(" — Обыкновенный", ""), 10))
                             for label in ingredient_names]

   for i, (val, (low, high)) in enumerate(zip(ingr_vals, ingr_lims)):
      if i == 0:
         ax1.plot([i, i], [low, high], color='#1E90FF',linewidth=4,alpha=0.5,label="Установленные лимиты")
         ax1.plot(i, val,'o',color='#FF4B4B',label="Количество в рецептуре")
      else:
         ax1.plot([i, i], [low, high],color='#1E90FF',linewidth=4,alpha=0.5)
         ax1.plot(i, val,'o',color='#FF4B4B')
   ax1.set_xticks(range(len(wrapped_ingredients)))
   ax1.set_xticklabels(wrapped_ingredients, rotation=0)
   ax1.set_ylabel("Значение")
   ax1.set_title("Ингредиенты: значения и ограничения")
   ax1.set_ylim(0, 100)
   ax1.legend()          
   ax1.grid(True, axis='y', linestyle='-', color='#e6e6e6', alpha=0.7)
   ax1.spines['top'].set_color('white')
   ax1.spines['right'].set_visible(False)
   st.pyplot(fig1)

   # --- График для нутриентов    
   fig2, ax2 = plt.subplots(figsize=(10, 6))
   nutrients = list(nutr_ranges.keys())
   nutr_vals = [nutrients_combo[n] for n in nutrients]
   nutr_lims = [nutr_ranges[n] for n in nutrients]
   for i, (nutrient, val, (low, high)) in enumerate(zip(nutrients, nutr_vals, nutr_lims)):
      if i==0:
         ax2.plot([i, i], [low, high], color='#1E90FF', linewidth=4, alpha=0.5,label="Установленные лимиты")
         ax2.plot(i, val, 'o', color='#FF4B4B',label="Количество в рецептуре") 
      else: 
         ax2.plot([i, i], [low, high], color='#1E90FF', linewidth=4, alpha=0.5)
         ax2.plot(i, val, 'o', color='#FF4B4B')                              
   ax2.set_xticks(range(len(nutrients)))
   ax2.set_xticklabels([nutrients_transl.loc[nutrients_transl["name_in_database"] == nutr,"name_ru"].iloc[0].split(",")[0] for nutr in  nutrients], rotation=0)
   ax2.set_ylabel("Значение")
   ax2.set_title("Питательные вещества: значения и допустимые границы")
   ax2.set_ylim(0, 100)
   ax2.legend()  
   ax2.grid(True, axis='y', linestyle='-', color='#e6e6e6', alpha=0.7)
   ax2.spines['top'].set_color('white')
   ax2.spines['right'].set_visible(False)
   st.pyplot(fig2)

# ---- Вывод рассчитанной рецептуры: соотношение количества ингредиентов и содержания основных нутриентов
def show_resuts_success(best_recipe,food,nutrients_transl,metobolic_energy, age_type_categ, ingredient_names, ingr_ranges,nutr_ranges):
   kkal_sel = st.session_state.kkal_sel
   weight_sel = st.session_state.weight_sel
   select_reproductive_status = st.session_state.select_reproductive_status
   ingredients_combo, nutrients_combo = best_recipe

   # --- Соотношение ингредиентов и количество нутриентов на 100 г корма        
   st.markdown("### 📦 Состав (в граммах на 100 г):")
   for ingredient, value in ingredients_combo.items():
      if int(round(value,0))!=0:
         st.write(f"{ingredient.replace(" — Обыкновенный", "")}: **{int(round(value,0))} г**")
           
   st.markdown("### 💪 Питательная ценность на 100 г:")
   for nutrient, value in nutrients_combo.items():
      nutrient_trl = nutrients_transl.loc[nutrients_transl["name_in_database"] == nutrient,"name_ru"].iloc[0].split(",")[0]
      st.write(f"**{nutrient_trl}:** {int(round(value,0))} г")
           
   en_nutr_100=int(round(3.5*nutrients_combo["protein_per"]+8.5*nutrients_combo["fats_per"]+3.5*nutrients_combo["carbohydrate_per"],0))
   st.write(f"**Энергетическая ценность:** {en_nutr_100} ккал")
   st.write(f"****") 
          
   count_all_nutr_100 = {nutr: round(sum(amount * food[ingredient][nutr]/100 for ingredient, amount in ingredients_combo.items()), 2)
                                for nutr in main_nutrs+other_nutrients+major_minerals+vitamins}
   for i in range(0, len(other_nutrients+major_minerals+vitamins), 2):
      cols = st.columns(2)
      for j, col in enumerate(cols):
         if i + j < len(other_nutrients+major_minerals+vitamins):
            nutris = (other_nutrients+major_minerals+vitamins)[i + j]
            nutr_text=nutrients_transl.loc[nutrients_transl["name_in_database"] == nutris,"name_ru"].iloc[0].split(",")    
            emg=""
            if len(nutr_text)>1:
                  emg=nutr_text[-1].strip() if "%" not in nutr_text[-1] else "g"
            else:
               emg="g"
            with col:
               st.markdown(f"**{nutr_text[0]}**: {count_all_nutr_100.get(nutris, '')} {emg}")

   # --- Необходимое количество корма и ингредиентов для удовлетворения суточной потребности в калориях       
   st.markdown(f"### Сколько нужно в граммах корма и ингредиентов на {metobolic_energy} ккал") 
  
   needed_feed_g = int(round((metobolic_energy * 100) / en_nutr_100 , 0))
   st.write(f"📌 Корм: {needed_feed_g} г")
   ingredients_required = { name: int(round((weight * needed_feed_g / 100),0))
                                  for name, weight in ingredients_combo.items() }  
   st.write("🧾 Количество ингредиентов для этой порции:")
   for ingredient, value in ingredients_required.items():
      if int(round(value,0))!=0:
         st.write(f" - {ingredient.replace(" — Обыкновенный", "")}: {value} г")
         
   count_all_nutr = {nutr: round(sum(amount * food[ingredient][nutr]/100 for ingredient, amount in ingredients_required.items()), 2)
                                for nutr in main_nutrs+other_nutrients+major_minerals+vitamins}
  
   st.markdown(f"### 💪 Питательная ценность на {needed_feed_g} г:")
  
   for nutrient in main_nutrs:
      nutrient_trl=nutrients_transl.loc[nutrients_transl["name_in_database"] == nutrient,"name_ru"].iloc[0].split(",")[0]
      st.write(f"**{nutrient_trl}:** {int(round(count_all_nutr[nutrient], 0))} г")

   # ---  Вывод содержания нутриентов в рассчитанной рецептуре на дневную порцию    
   st.write(f"****") 
   show_nutr_content(count_all_nutr, nutrients_transl, kkal_sel, age_type_categ, weight_sel, select_reproductive_status)
   show_figures_ingr_nutr(ingr_ranges, nutr_ranges, ingredients_combo, nutrients_combo, nutrients_transl)

