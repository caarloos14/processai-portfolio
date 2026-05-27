import os
import json
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


def cargar_reviews_limpias(ruta_csv):
    ruta_csv = Path(ruta_csv)

    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

    df = pd.read_csv(ruta_csv)
    return df


def obtener_datos_negocio(df):
    def valor_columna(columna, valor_defecto=""):
        if columna in df.columns and df[columna].notna().any():
            return str(df[columna].dropna().iloc[0])
        return valor_defecto

    datos = {
        "place_name": valor_columna("place_name", "Negocio"),
        "city": valor_columna("city", ""),
        "category": valor_columna("category", ""),
        "place_rating": valor_columna("place_rating", ""),
        "place_reviews_count": valor_columna("place_reviews_count", ""),
    }

    return datos


def preparar_reviews_para_ia(df, max_reviews=120):
    df = df.copy()

    df["content"] = df["content"].fillna("").astype(str).str.strip()
    df = df[df["content"] != ""]

    if "reviewed_at_date" in df.columns:
        df["reviewed_at_date"] = pd.to_datetime(df["reviewed_at_date"], errors="coerce")

    reviews_negativas = df[df["rating"] <= 2]
    reviews_neutrales = df[df["rating"] == 3]
    reviews_positivas = df[df["rating"] >= 4]

    if "reviewed_at_date" in df.columns:
        reviews_negativas = reviews_negativas.sort_values("reviewed_at_date", ascending=False)
        reviews_neutrales = reviews_neutrales.sort_values("reviewed_at_date", ascending=False)
        reviews_positivas = reviews_positivas.sort_values("reviewed_at_date", ascending=False)

    n_negativas = int(max_reviews * 0.45)
    n_neutrales = int(max_reviews * 0.20)
    n_positivas = max_reviews - n_negativas - n_neutrales

    muestra = pd.concat([
        reviews_negativas.head(n_negativas),
        reviews_neutrales.head(n_neutrales),
        reviews_positivas.head(n_positivas),
    ])

    reviews_formateadas = []

    for _, row in muestra.iterrows():
        review = {
            "rating": int(row["rating"]) if not pd.isna(row["rating"]) else None,
            "fecha": str(row.get("reviewed_at_date", "")),
            "contenido": row.get("content", ""),
            "respuesta_negocio": row.get("owner_response", ""),
        }

        reviews_formateadas.append(review)

    return reviews_formateadas


def construir_prompt(datos_negocio, reviews):
    prompt = f"""
Eres un analista de datos especializado en reputación online de negocios locales.

Vas a analizar reseñas de Google Maps de este negocio:

Nombre: {datos_negocio["place_name"]}
Ciudad: {datos_negocio["city"]}
Categoría: {datos_negocio["category"]}
Rating global en Google: {datos_negocio["place_rating"]}
Número total de reseñas en Google: {datos_negocio["place_reviews_count"]}

Tu tarea es analizar las reseñas y devolver un informe útil para el dueño del negocio.

Devuelve SOLO un JSON válido con esta estructura exacta:

{{
  "resumen_ejecutivo": "",
  "diagnostico_general": "",
  "aspectos_positivos": [
    {{
      "tema": "",
      "explicacion": "",
      "evidencia": ""
    }}
  ],
  "principales_quejas": [
    {{
      "problema": "",
      "explicacion": "",
      "gravedad": "baja | media | alta",
      "evidencia": ""
    }}
  ],
  "oportunidades_de_mejora": [
    {{
      "oportunidad": "",
      "accion_recomendada": "",
      "impacto_estimado": "bajo | medio | alto"
    }}
  ],
  "acciones_prioritarias": [
    {{
      "accion": "",
      "prioridad": "baja | media | alta",
      "motivo": ""
    }}
  ],
  "frase_comercial_para_demo": "",
  "conclusion": ""
}}

Reglas:
- No inventes datos.
- Basa el análisis únicamente en las reseñas proporcionadas.
- Escribe en español.
- Sé claro, profesional y orientado a negocio.
- No menciones que eres una IA.
- No incluyas datos personales de usuarios.
- La salida debe ser JSON válido.

Reseñas a analizar:
{json.dumps(reviews, ensure_ascii=False, indent=2)}
"""

    return prompt


def analizar_con_gemini(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise ValueError("No se encontró GEMINI_API_KEY en el archivo .env")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )

    return response.text


def convertir_respuesta_a_json(respuesta_texto):
    try:
        return json.loads(respuesta_texto)
    except json.JSONDecodeError:
        print("La respuesta no era JSON válido. Se guardará como texto bruto.")
        return {
            "respuesta_bruta": respuesta_texto
        }


def guardar_analisis(analisis, ruta_salida):
    ruta_salida = Path(ruta_salida)

    with open(ruta_salida, "w", encoding="utf-8") as file:
        json.dump(analisis, file, ensure_ascii=False, indent=4)

    print(f"Análisis con Gemini guardado en: {ruta_salida}")


def mostrar_resumen_ia(analisis):
    print("\nANÁLISIS CON GEMINI")
    print("-------------------")

    if "resumen_ejecutivo" in analisis:
        print("\nResumen ejecutivo:")
        print(analisis["resumen_ejecutivo"])

    if "principales_quejas" in analisis:
        print("\nPrincipales quejas:")
        for queja in analisis["principales_quejas"]:
            print(f"- {queja.get('problema', '')}: {queja.get('explicacion', '')}")

    if "acciones_prioritarias" in analisis:
        print("\nAcciones prioritarias:")
        for accion in analisis["acciones_prioritarias"]:
            print(f"- {accion.get('accion', '')}")


if __name__ == "__main__":
    input_csv = "reviews_clean.csv"
    output_json = "ai_analysis.json"

    df_reviews = cargar_reviews_limpias(input_csv)

    datos_negocio = obtener_datos_negocio(df_reviews)

    reviews_para_ia = preparar_reviews_para_ia(df_reviews, max_reviews=120)

    print(f"Reseñas enviadas a Gemini: {len(reviews_para_ia)}")

    prompt = construir_prompt(datos_negocio, reviews_para_ia)

    respuesta = analizar_con_gemini(prompt)

    analisis = convertir_respuesta_a_json(respuesta)

    guardar_analisis(analisis, output_json)

    mostrar_resumen_ia(analisis)