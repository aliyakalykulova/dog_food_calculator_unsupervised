import pandas as pd
import numpy as np

nutrient_cols = [    'moisture_per',    'protein_per',    'carbohydrate_per',    'fats_per',    'ash_g',    'fiber_g',
    'cholesterol_mg',    'total_sugar_g',
    'calcium_mg',    'phosphorus_mg',    'magnesium_mg',    'sodium_mg',    'potassium_mg',    'iron_mg',    'copper_mg',    'zinc_mg',    'manganese_mg',
    'selenium_mcg',    'iodine_mcg',    'choline_mg',
    'vitamin_a_mcg',    'vitamin_e_mg',   'vitamin_d_mcg',    'vitamin_b1_mg',    'vitamin_b2_mg',    'vitamin_b3_mg',    'vitamin_b5_mg',
    'vitamin_b6_mg',    'vitamin_b9_mcg',    'vitamin_b12_mcg',    'vitamin_c_mg',    'vitamin_k_mcg',
    'alpha_carotene_mcg',    'beta_carotene_mcg',    'beta_cryptoxanthin_mcg',    'lutein_zeaxanthin_mcg',    'lycopene_mcg',    'retinol_mcg',
    'linoleic_acid_g',    'alpha_linolenic_acid_g',    'arachidonic_acid_g',    'epa_g',    'dha_g',"omega_3","omega_6"
]

def cliffs_delta(x1, x2):
    x1 = x1.dropna()
    x2 = x2.dropna()
    if len(x1) < 2 or len(x2) < 2:
        return 0
    x1 = x1.values
    x2 = x2.values
    n1, n2 = len(x1), len(x2)
    more = 0
    less = 0
    for a in x1:
        for b in x2:
            if a > b:
                more += 1
            elif a < b:
                less += 1
    return (more - less) / (n1 * n2 + 1e-9)


def nutrient_cliff(high_df, low_df):
    high_nutr = []
    low_nutr = []
    for col in nutrient_cols:
        delta = cliffs_delta(high_df[col], low_df[col])
        if delta > 0.2:
            high_nutr.append({"name": col, "effect": float(delta)})
        elif delta < -0.2:
            low_nutr.append({"name": col,"effect": float(delta)})
    return high_nutr, low_nutr
  
group_results = {}
for group in df_tsne["category_ru"].dropna().unique():
    high_df = df_tsne[df_tsne["category_ru"] == group]
    low_df = df_tsne[df_tsne["category_ru"] != group]
    cliff_feats = {}

    for col in nutrient_cols:
        c = cliffs_delta(high_df[col], low_df[col])
        if c > 0.2:
            cliff_feats[col] = round(float(c),3)
    group_results[group]=sorted(cliff_feats.items(), key=lambda x: (x[0]))

df_category_nutrients = pd.DataFrame(results)


