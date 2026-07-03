# utils/embeddings.py
import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')   # since we have low load right now and it is fast and free on groq when scaling increasing we can shift to higher models

def create_embeddings(chunks: list[str]) -> np.ndarray:
    return model.encode(chunks, convert_to_numpy=True)