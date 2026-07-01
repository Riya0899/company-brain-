# utils/embeddings.py
import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embeddings(chunks: list[str]) -> np.ndarray:
    return model.encode(chunks, convert_to_numpy=True)