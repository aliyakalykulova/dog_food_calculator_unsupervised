import numpy as np
import pandas as pd
from collections import Counter

nutrient_cols = ['moisture_per', 'protein_per', 'fats_per',
       'carbohydrate_per', 'dha_g', 'epa_g', 'epa_dha', 'omega_3', 'omega_6',
       'linoleic_acid_g', 'alpha_linolenic_acid_g', 'essential_fatty_acids',
       'taurine', 'l_arginine', 'l_lysine', 'glutamine_glutamate',
       'dl_methionine_l_cystine', 'bcaa_total', 'hydroxyproline',
       'beta_carotene_mcg', 'l_carnitine', 'glucosamine',
       'chondroitin_sulfate', 'calcium_mg', 'phosphorus_mg', 'potassium_mg',
       'sodium_mg', 'magnesium_mg', 'iron_mg', 'copper_mg', 'zinc_mg',
       'chloride', 'sulphur', 'vitamin_a_mcg', 'vitamin_c_mg', 'vitamin_d_mcg',
       'vitamin_e_mg', 'vitamin_k_mcg', 'vitamin_b1_mg', 'vitamin_b2_mg',
       'vitamin_b3_mg', 'vitamin_b5_mg', 'vitamin_b6_mg', 'vitamin_b7',
       'vitamin_b9_mcg', 'vitamin_b12_mcg']

def ingredient_freq(series):
    cnt = Counter()
    for text in series.dropna():
        for ing in text.split(","):
            ing = ing.strip().lower()
            if ing:
                cnt[ing] += 1
    return cnt

def compute_ingredient_lift(high_cnt, low_cnt, n_high, n_low):
    rows = []
    all_ingredients = set(high_cnt) | set(low_cnt)
    for ing in all_ingredients:
        p_high = high_cnt.get(ing, 0) / max(n_high, 1)
        p_low = low_cnt.get(ing, 0) / max(n_low, 1)
        lift = (p_high + 1e-9) / (p_low + 1e-9)
        rows.append({"ingredient": ing,"lift": float(lift),"high_freq": float(p_high),"low_freq": float(p_low)})
    df = pd.DataFrame(rows)
    return df.sort_values("lift", ascending=False)

def cliffs_delta(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    greater = 0
    less = 0
    for xi in x:
        greater += np.sum(xi > y)
        less += np.sum(xi < y)
    delta = (greater - less) / (len(x) * len(y))
    return float(delta)

def nutrient_cliff(high_df, low_df):
    high_nutr = []
    low_nutr = []
    for col in nutrient_cols:
        delta = cliffs_delta(high_df[col],low_df[col])
        if delta > 0.2:
            high_nutr.append({"name": col, "effect": float(delta) })
        elif delta < -0.2:
            low_nutr.append({"name": col,"effect": float(delta)})
    return high_nutr, low_nutr

def ingr_nutr_food_find(query, model,df,corpus_embeddings):
    query_embedding = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    df["score"] = scores.cpu().numpy()
    df_pos = df[df["score"] > 0].copy()
    df_pos["score_norm"] = ( (df_pos["score"] - df_pos["score"].min()) /(df_pos["score"].max() - df_pos["score"].min() + 1e-9) )

    result = df_pos.sort_values("score_norm", ascending=False)
    cluster_id = result["spectral_cluster"].iloc[:2].tolist()

    high = result[result["spectral_cluster"].isin(cluster_id)]
    low = result[~result["spectral_cluster"].isin(cluster_id)]

    high_nutr, low_nutr = nutrient_cliff(high, low)

    high_cnt = ingredient_freq(high["ingredients"])
    low_cnt = ingredient_freq(low["ingredients"])

    ingredient_df = compute_ingredient_lift(high_cnt, low_cnt,len(high), len(low))
    ingredient_df = ingredient_df[ingredient_df["lift"] > 2]

    high_nutrients =  [ {"name": n, "effect": d} for n, d in high_nutr ]
    low_nutrients =  [ {"name": n, "effect": d} for n, d in low_nutr]
    ingredients = [  {"name": r["ingredient"], "lift": r["lift"]} for _, r in ingredient_df.iterrows() ]
       
    return high_nutrients, low_nutrients ingredients

def ingredients_category_nutrient_analysis(ingredirents_df):
   results = []
   for group in ingredirents_df["category_ru"].dropna().unique():
      high_df = ingredirents_df[ingredirents_df["category_ru"] == group]
      low_df = ingredirents_df[ingredirents_df["category_ru"] != group]
      cliff_feats = {}
      for col in nutrient_cols:
          c = cliffs_delta(high_df[col], low_df[col])
          if c > 0.2:
              cliff_feats[col] = round(float(c),3)
      results.append({"category": group, "cliff": dict(sorted(cliff_feats.items(), key=lambda x: (x[0]))),})
      df_category_nutrients = pd.DataFrame(results)
      return df_category_nutrients


