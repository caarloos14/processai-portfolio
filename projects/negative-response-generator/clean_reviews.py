import json
from pathlib import Path
import pandas as pd


def cargar_reviews(ruta_json):
    """
    Carga el archivo JSON generado por Apify y devuelve una lista de reseñas.
    """

    ruta_json = Path(ruta_json)

    if not ruta_json.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_json}")

    with open(ruta_json, "r", encoding="utf-8") as file:
        reviews = json.load(file)

    return reviews


def limpiar_reviews(reviews):
    """
    Recibe la lista de reseñas en bruto y devuelve un DataFrame limpio
    con solo las columnas importantes para el análisis.
    """

    filas = []

    for review in reviews:
        fila = {
            # Datos de la reseña
            "review_id": review.get("review_id"),
            "review_url": review.get("review_url"),
            "rating": review.get("rating"),
            "content": review.get("content"),
            "content_language": review.get("content_language"),
            "content_translated": review.get("content_translated"),
            "likes_count": review.get("likes_count"),
            "reviewed_at": review.get("reviewed_at"),
            "reviewed_at_date": review.get("reviewed_at_date"),

            # Respuesta del negocio
            "owner_response": review.get("owner_response"),
            "owner_response_translated": review.get("owner_response_translated"),
            "owner_response_at": review.get("owner_response_at"),

            # Datos del negocio
            "place_name": review.get("place_name"),
            "place_id": review.get("place_id"),
            "place_rating": review.get("place_rating"),
            "place_reviews_count": review.get("place_reviews_count"),
            "category": review.get("category"),
            "city": review.get("city"),
            "state": review.get("state"),
            "country": review.get("country"),
            "full_address": review.get("full_address"),
            "website": review.get("website"),
            "phone": review.get("phone"),

            # Datos del usuario, sin información personal sensible
            "reviewer_reviews_count": review.get("reviewer_reviews_count"),
            "reviewer_photos_count": review.get("reviewer_photos_count"),
            "is_local_guide": review.get("is_local_guide"),

            # Metadatos
            "source": review.get("source"),
            "scraped_at": review.get("scraped_at"),
        }

        filas.append(fila)

    df = pd.DataFrame(filas)

    # Convertir rating a número
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    # Convertir likes_count a número
    df["likes_count"] = pd.to_numeric(df["likes_count"], errors="coerce").fillna(0).astype(int)

    # Limpiar textos vacíos
    df["content"] = df["content"].fillna("").astype(str).str.strip()
    df["owner_response"] = df["owner_response"].fillna("").astype(str).str.strip()

    # Crear columna auxiliar: tiene texto o no
    df["has_text"] = df["content"] != ""

    # Crear columna auxiliar: tiene respuesta del negocio o no
    df["has_owner_response"] = df["owner_response"] != ""

    # Crear columna de sentimiento básico según estrellas
    df["sentiment_by_rating"] = df["rating"].apply(clasificar_sentimiento_por_rating)

    # Eliminar reseñas completamente vacías, si las hubiera
    df = df.dropna(subset=["rating"])

    return df


def clasificar_sentimiento_por_rating(rating):
    """
    Clasifica la reseña de forma básica según la puntuación.
    Más adelante esto lo mejoraremos con IA.
    """

    if pd.isna(rating):
        return "desconocido"

    if rating >= 4:
        return "positivo"
    elif rating == 3:
        return "neutral"
    else:
        return "negativo"


def guardar_csv(df, ruta_salida):
    """projects/review-analyzer/clean_reviews.py
    Guarda el DataFrame limpio en formato CSV.
    """

    ruta_salida = Path(ruta_salida)

    df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")

    print(f"CSV limpio guardado en: {ruta_salida}")


def mostrar_resumen(df):
    """
    Muestra un pequeño resumen para comprobar que todo está bien.
    """

    print("\nResumen del archivo limpio")
    print("--------------------------")
    print(f"Número total de reprojects/review-analyzer/clean_reviews.pyseñas: {len(df)}")
    print(f"Rating medio: {round(df['rating'].mean(), 2)}")
    print(f"Reseñas con texto: {df['has_text'].sum()}")
    print(f"Reseñas con respuesta del negocio: {df['has_owner_response'].sum()}")

    print("\nDistribución por sentimiento:")
    print(df["sentiment_by_rating"].value_counts())

    print("\nPrimeras filas:")
    print(df.head())


def filtrar_negativas(df):

    """
    Vamos a quedarnos solamente con las reseñas negativas
    """

    df_negativas = df[df["rating"]<=2].copy()

    return df_negativas 

if __name__ == "__main__":
    input_json = "reviews.json"
    output_csv = "reviews_clean.csv"

    reviews = cargar_reviews(input_json)

    df_reviews = limpiar_reviews(reviews)

    guardar_csv(df_reviews, output_csv)

    mostrar_resumen(df_reviews)