# utils/embeddings.py
import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np

@st.cache_resource  # it caches the model so it doesnot reload everytime
def _load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = _load_model()

def create_embeddings(chunks: list[str]) -> np.ndarray:
    return model.encode(chunks, convert_to_numpy=True)