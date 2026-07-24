from collections import defaultdict
protein_source=['Мясо']
cerals=['Крупы']
veg_fruit=['Овощи и фрукты']
fat_oil=['Масло и жир']
water=['Вода, соль и сахар']
grace=['Зелень и специи']

finish_ingr_list=[]
sorce_categ=[protein_source,cerals,veg_fruit,fat_oil,grace]
main_nutr=["moisture_per","carbohydrate_per" ,"protein_per" ,"fats_per"]

def score_ingredient(row, high_dict, low_dict):
    score = 0.0
    for nutr, weight in high_dict.items():
        if nutr in row and pd.notna(row[nutr]):
            score += weight * row[nutr]
    for nutr, weight in low_dict.items():
        if nutr in row and pd.notna(row[nutr]):
            score += weight * row[nutr]
    return score

def find_ingredient(high_nutr_list, low_nutr_list, source_ingr_list):
    high_dict = {x["name"]: x["effect"] for x in high_nutr_list}
    low_dict = {x["name"]: x["effect"] for x in low_nutr_list}
    subset = ingredirents_df[ingredirents_df["full_name_ingredient"].isin(source_ingr_list)].copy()
    subset["score"] = subset.apply(score_ingredient, axis=1, args=(high_dict, low_dict))
    best_full_name = subset.sort_values("score", ascending=False).iloc[0]["full_name_ingredient"]
    return best_full_name

def output_name(best_full_name):
      best_full_name_result = (ingredirents_df.loc[ ingredirents_df["full_name_ingredient"] == best_full_name, ["name_ingredient_ru", "format_ingredient_ru"]].iloc[0] )
      answer = f"{best_full_name_result['name_ingredient_ru']}-{best_full_name_result['format_ingredient_ru']}"
      return answer 

def group_high_nutr_rec(high_nutr):
    grouped_high_nutr = defaultdict(list)
    for nutr in high_nutr:
        nutr_name = nutr["name"]
        found = False
        for category, nutrients in group_results.items():
            for nutr_full, score in nutrients:
                base_name = nutr_full
                if base_name == nutr_name:
                        grouped_high_nutr[category].append(nutr)
                        found = True
                        break
    return dict(grouped_high_nutr)

def group_ingr_rec(ingr_rec):
    name_to_full = (standart_updated.dropna(subset=["name_feed_ingredient", "full_name_ingredient"]).set_index("name_feed_ingredient")["full_name_ingredient"].to_dict())
    ingr_rec = sorted(ingr_rec,key=lambda x: x["lift"],reverse=True)
    ingr_rec_filtered = [{ **item,"name": name_to_full.get(item["name"].replace(" ", "_"), item["name"] ) }
        for item in ingr_rec if item["name"].replace(" ", "_") in name_to_full ]
    ingredient_to_category = ( standart_updated.drop_duplicates("full_name_ingredient").set_index("full_name_ingredient")["category_ru"].to_dict())
    grouped_ingredients = defaultdict(list)
    for item in ingr_rec_filtered:
        ingredient = item["name"]
        category = ingredient_to_category.get(ingredient,"Не определено")
        grouped_ingredients[category].append(ingredient)
    return  dict(grouped_ingredients)

def define_ingredients(high_nutr,low_nutr,ingr_rec,ingredirents_df):  #for index in range(len(df_results)):
    grouped_high_nutr=group_high_nutr_rec(high_nutr)
    grouped_ingredients=group_ingr_rec(ingr_rec)

    finish_ingr_list=[]
    finish_ingr_list_norm_name=[]
  
    maxim_main_nutr= [h_n["name"]  for h_n in high_nutr if h_n["name"]  in main_nutr]
    if len(maxim_main_nutr)==0:
      maxim_main_nutr=["moisture_per","protein_per"]
    minim_main_nutr =[h_n["name"]  for h_n in low_nutr if h_n["name"]  in main_nutr]

    for source in sorce_categ:
        source_ingr_list_1 = [ing for cat in source if cat in grouped_ingredients for ing in  grouped_ingredients[cat]]
        for cat in source:
            mask = ingredirents_df["category_ru"] == cat
            if cat in protein_source:
                mask &= ((ingredirents_df["protein_per"] > 10) &(ingredirents_df["moisture_per"] > 60) &(ingredirents_df["protein_per"] > ingredirents_df["fats_per"]))
            if cat in veg_fruit:
                mask &= ((ingredirents_df["carbohydrate_per"]< 20) &(ingredirents_df["moisture_per"] > 75))
            source_ingr_list_2.extend( ingredirents_df.loc[mask, "full_name_ingredient"].tolist())
        flat_list = [  item for items in grouped_high_nutr.values()  for item in items]
        source_high_nutr_list= [ing for cat in source if cat in grouped_high_nutr for ing in  grouped_high_nutr[cat]]
        high_nutr_list = ( source_high_nutr_list if len(source_high_nutr_list) > 0 else flat_list)
        source_ingr_list= source_ingr_list_1 if len(source_ingr_list_1)>1 else []
      
        if source==water or source==grace:
          if set(source).intersection(set(grouped_high_nutr.keys())):
              best_full_name = find_ingredient(high_nutr_list, low_nutr,source_ingr_list)
              best_full_name_answer=output_name(best_full_name)
              finish_ingr_list_norm_name.append(best_full_name_answer)
              finish_ingr_list.append(best_full_name)
        else:
          best_full_name = find_ingredient(high_nutr_list, low_nutr,source_ingr_list)
          best_full_name_answer=output_name(best_full_name)
          finish_ingr_list_norm_name.append(best_full_name_answer)
          finish_ingr_list.append(best_full_name)
    if "moisture_per" in maxim_main_nutr and "WATER,BTLD,GENERIC" not in finish_ingr_list:
          best_full_name = "WATER,BTLD,GENERIC"
          best_full_name_answer=output_name(best_full_name)
          finish_ingr_list_norm_name.append(best_full_name_answer)
          finish_ingr_list.append(best_full_name)
    return finish_ingr_list, finish_ingr_list_norm_name, maxim_main_nutr, minim_main_nutr
 



