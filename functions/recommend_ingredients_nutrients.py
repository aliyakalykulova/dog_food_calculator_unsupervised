import pandas as pd



def ingredient_recommendation(ingredirents_df,ingredient_names):
   proteins=ingredirents_df[ingredirents_df["category_ru"].isin(["Яйца и молочные продукты", "Мясо"])]["full_name_ingredient"].tolist()
   oils=ingredirents_df[ingredirents_df["category_ru"].isin([ "Масло и жир"])]["full_name_ingredient"].tolist()
   carbonates_cer=ingredirents_df[ingredirents_df["category_ru"].isin(["Крупы"])]["full_name_ingredient"].tolist()
   carbonates_veg=ingredirents_df[ingredirents_df["category_ru"].isin(["Овощи и фрукты"])]["full_name_ingredient"].tolist()
   carbonates_grace=ingredirents_df[ingredirents_df["category_ru"].isin(["Зелень и специи"])]["full_name_ingredient"].tolist()
   other=ingredirents_df[ingredirents_df["category_ru"].isin(["Вода, соль и сахар"])]["full_name_ingredient"].tolist()

   ingr_ranges = []
   for ingr in ingredient_names:

      if ingr in proteins:
         ingr_ranges.append((50,90))
      elif ingr in oils:
         ingr_ranges.append((1,10))
      elif ingr in carbonates_cer:
         ingr_ranges.append((5,35))
      elif ingr in carbonates_veg:
         ingr_ranges.append((5,25))
      elif ingr in carbonates_grace:
         ingr_ranges.append((1,15))
      elif "WATER" in ingr:
         ingr_ranges.append((0,30))
      elif ingr in other:
         ingr_ranges.append((1,3))

   # --- Вывод списка рекомендованных ингредиентов
	
	   
   st.subheader("🌿 Рекомендуемые ингредиенты")
   for ing in ingredient_names:
      st.write("• " + ing.replace("— Обыкновенный",""))
   return ingr_ranges

# ---- Функция рекомендации количества нутриентов
def nutrients_recommendation(food_df):
        nutr_ranges=dict()
        nutr_ranges['moisture_per']=[65,95]

        s = food_df[(food_df["food_form"] == "wet food") &(food_df["moisture_per"] > 0.5) ]["protein_per"]
        protein_min=(100-nutr_ranges['moisture_per'][0])*0.25
        protein_min=protein_min if protein_min > s.mean()-s.std() else s.mean()-s.std()
        nutr_ranges['protein_per']=[protein_min , 30]

        s = food_df[(food_df["food_form"] == "wet food") &(food_df["moisture_per"] > 0.5) ]["fats_per"]
        fats_min= (100-nutr_ranges['moisture_per'][0])*0.085
        fats_min=fats_min if fats_min > s.mean()-s.std() else s.mean()-s.std()
        nutr_ranges['fats_per']=[fats_min, 15]

        nutr_ranges['carbohydrate_per']=[5 , 100-nutr_ranges['protein_per'][0]-nutr_ranges['fats_per'][0]-nutr_ranges['moisture_per'][0]]
	
   return nutr_ranges




