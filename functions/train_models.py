import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge, RidgeClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import hstack, csr_matrix
from collections import Counter

# ---- Обучение моделей рекомендаций ингредиентов и нутриентов на основе размера породы, возрастного периода и заболевания

# ----Преобразование текстового описания кормов для собак в векторное представление
@st.cache_resource(show_spinner=False)
def build_text_pipeline(corpus, n_components=100):
   vect = TfidfVectorizer(stop_words="english", max_features=5000)
   X_tfidf = vect.fit_transform(corpus)
   svd = TruncatedSVD(n_components=n_components, random_state=42)
   X_reduced = svd.fit_transform(X_tfidf)
   return vect, svd, X_reduced

# ---- Векторизация категориальных признаков (размер породы, возрастная категория)
@st.cache_resource(show_spinner=False)
def build_categorical_encoder(df):
   cats = df[["breed_size", "life_stage"]]
   enc = OneHotEncoder(sparse_output=True, handle_unknown="ignore")
   enc.fit(cats)
   X = enc.transform(cats)
   return enc, X

# ---- Объединение текстового вектора описания корма и категориального вектора 
@st.cache_resource(show_spinner=False)
def combine_features(text_reduced, _cat_matrix):
   X_sparse_text = csr_matrix(text_reduced)
   return hstack([X_sparse_text, _cat_matrix])

# ---- Модификация категориальных векторов: если указано "-", устанавливается 1 для всех категорий (универсальная применимость)
def apply_category_masks(X, encoder):
   X = X.toarray()
   feature_names = encoder.get_feature_names_out()
   idx = {name: i for i, name in enumerate(feature_names)}
   if "breed_size_-" in idx:                                      # --- Обработка признака "размер породы"
      mask = X[:, idx["breed_size_-"]] == 1
      for k in ["breed_size_s", "breed_size_m", "breed_size_l"]:
         if k in idx:
            X[mask, idx[k]] = 1
              
   if "life_stage_-" in idx:                                       # --- Обработка признака "возрастная категория"
      mask = X[:, idx["life_stage_-"]] == 1
      for k in ["life_stage_puppy", "life_stage_adult", "life_stage_senior"]:
         if k in idx:
            X[mask, idx[k]] = 1
             
   return csr_matrix(X)

# ---- Обучение модели рекомендации ингредиентов (RidgeClassifier)
@st.cache_resource(show_spinner=False)
def train_ingredient_models(food, _X):
   parsed_ings = []
   for txt in food["ingredients"].dropna():
      tokens = (txt.split(", ") )
      parsed_ings.append(set(tokens))
      
   # --- Формирование списка уникальных ингредиентов
   all_ings = [ing for s in parsed_ings for ing in s]    
   frequent = list(set(all_ings))
   
   # --- Формирование бинарных таргетов
   targets = {}                                         
   parsed_series = food["ingredients"].fillna("").apply(
      lambda txt: set(txt.split(", ")) if txt else set())
   for ing in frequent:
      targets[ing] = parsed_series.apply(lambda s: int(ing in s)).values
      
   # --- Обучение модели
   ing_models = {}                    
   for ing, y in targets.items():
      clf = RidgeClassifier()
      clf.fit(_X, y)
      ing_models[ing] = clf
   return ing_models, frequent

# ---- Обучение модели рекомендации количества нутриентов
@st.cache_resource(show_spinner=False)
def train_nutrient_models(food, _X):
   nutrient_models = {}
   scalers = {}
   nutrients = ['moisture', 'protein', 'fats', 'carbohydrate']
   for nutrient in nutrients:
      y = food[nutrient].fillna(food[nutrient].median()).values.reshape(-1, 1)
      scaler = None
      y_scaled = y.ravel()
      X_train, _, y_train, _ = train_test_split(_X, y_scaled, test_size=0.2, random_state=42)
      base = Ridge()
      search = GridSearchCV( base,  param_grid = {"alpha": [0.1, 1.0]}, scoring="r2", cv=2, n_jobs=-1)
      search.fit(X_train, y_train)
      nutrient_models[nutrient] = search.best_estimator_
      scalers[nutrient] = scaler

   return nutrient_models, scalers

