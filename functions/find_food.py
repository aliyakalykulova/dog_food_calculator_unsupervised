from collections import Counter
import numpy as np

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

def cohens_d(x1, x2):
    x1 = x1.dropna()
    x2 = x2.dropna()
    pooled_std = np.sqrt( ((len(x1)-1)*x1.var() + (len(x2)-1)*x2.var()) /  (len(x1)+len(x2)-2))
    if pooled_std < 0.01:
        return 0
    return (x1.mean() - x2.mean()) / pooled_std

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
        rows.append({
            "ingredient": ing,
            "lift": float(lift),
            "high_freq": float(p_high),
            "low_freq": float(p_low)
        })
    df = pd.DataFrame(rows)
    return df.sort_values("lift", ascending=False)

def nutrient_signal(high_df, low_df):
    if len(high_df) < 2 or len(low_df) < 2:
        return [], []
    high_nutr = []
    low_nutr = []
    for col in nutrient_cols:
        d = cohens_d(high_df[col], low_df[col])
        if d > 0.2:
            high_nutr.append((col, float(d)))
        if d < -0.5:
            low_nutr.append((col, float(d)))
    return high_nutr, low_nutr


def find_clusters_food(query, model,corpus_embeddings, df):
    query_embedding = model.encode(query,
                                   convert_to_tensor=True,
                                   normalize_embeddings=True )
    scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    df["score"] = scores.cpu().numpy()
    df_pos = df[df["score"] > 0].copy()
    df_pos["score_norm"] = (  (df_pos["score"] - df_pos["score"].min()) /
                              (df_pos["score"].max() - df_pos["score"].min() + 1e-9)  )
    
    result = df_pos.sort_values("score_norm", ascending=False)
    cluster_id = result["spectral_cluster"].iloc[0]
  
    high = result[result["spectral_cluster"] == cluster_id]
    low = result[result["spectral_cluster"] != cluster_id]
    
    high_nutr, low_nutr = nutrient_signal(high, low)
    high_cnt = ingredient_freq(high["ingredients"])
    low_cnt = ingredient_freq(low["ingredients"])
    
    ingredient_df = compute_ingredient_lift( high_cnt, low_cnt, len(high), len(low))
    ingredient_df = ingredient_df[ingredient_df["lift"] > 2]
  
    cluster = result["spectral_cluster"].iloc[:3].tolist()
    high_nutrients = [ {"name": n, "effect": d} for n, d in high_nutr]
    low_nutrients = [ {"name": n, "effect": d} for n, d in low_nutr ]
    ingredients = [ {"name": r["ingredient"], "lift": r["lift"]}  for _, r in ingredient_df.iterrows()]
    return cluster, high_nutrients, low_nutrients, ingredients


