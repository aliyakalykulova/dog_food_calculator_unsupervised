import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import SpectralClustering

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)

def cluster_food(df):
    corpus = df["description"].fillna("").tolist()
    corpus_embeddings = model.encode( corpus,
                                      convert_to_tensor=True,
                                      normalize_embeddings=True,
                                      show_progress_bar=True)
    X = corpus_embeddings  
    sc = SpectralClustering( n_clusters=45,
                             affinity="nearest_neighbors",
                             n_neighbors=15,
                             random_state=42 )
    labels = sc.fit_predict(X)
    df["spectral_cluster"] = labels
    return df
  


