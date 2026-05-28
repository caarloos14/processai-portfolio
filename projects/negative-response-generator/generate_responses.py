# generate_responses.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
import pandas as pd

load_dotenv()


def generar_respuestas_gemini(df_negativas, max_reviews=50):
    """
    Genera respuestas automáticas a reseñas negativas usando Gemini.
    
    Args:
        df_negativas (DataFrame): DataFrame con las reseñas negativas.
        max_reviews (int): Número máximo de reseñas a procesar en un batch.
        
    Returns:
        List[str]: Lista de respuestas generadas por la IA.
    """
    
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    if not api_key:
        raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")
    
    client = genai.Client(api_key=api_key)
    
    # Tomamos solo las últimas reseñas negativas
    df = df_negativas.copy()
    df = df.sort_values("reviewed_at_date", ascending=False)
    df = df.head(max_reviews)
    
    respuestas = []
    
    for idx, row in df.iterrows():
        review_text = row.get("content", "")
        business_name = row.get("place_name", "el negocio")
        
        prompt = f"""
Eres un asistente profesional encargado de generar respuestas amables y útiles
a reseñas negativas de clientes en Google Maps para {business_name}.

Reseña del cliente:
\"\"\"{review_text}\"\"\"

Genera una respuesta profesional, empática y que busque resolver la situación.
Devuelve SOLO el texto de la respuesta.
No inventes datos ni nombres de clientes.
"""
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="text/plain"
            )
        )
        
        respuesta_text = response.text.strip()
        respuestas.append(respuesta_text)
    
    return respuestas


def guardar_respuestas(df_negativas, respuestas, path_salida="respuestas_negativas.csv"):
    """
    Guarda las reseñas negativas junto con las respuestas generadas en CSV.
    
    Args:
        df_negativas (DataFrame)
        respuestas (List[str])
        path_salida (str)
    """
    df_result = df_negativas.copy().reset_index(drop=True)
    df_result["respuesta_sugerida"] = respuestas
    df_result.to_csv(path_salida, index=False, encoding="utf-8-sig")
    print(f"Respuestas automáticas guardadas en {path_salida}")