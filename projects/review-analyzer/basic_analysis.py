import pandas as pd
from pathlib import Path


def cargar_csv_limpio(ruta_csv):
    """
    Carga el CSV limpio de reseñas.
    """

    ruta_csv = Path(ruta_csv)

    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

    df = pd.read_csv(ruta_csv)

    return df


def calcular_metricas_generales(df):
    """
    Calcula métricas generales sobre las reseñas.
    """

    total_reviews = len(df)

    rating_medio = round(df["rating"].mean(), 2)

    reviews_con_texto = int(df["has_text"].sum()) if "has_text" in df.columns else 0

    reviews_con_respuesta = (
        int(df["has_owner_response"].sum())
        if "has_owner_response" in df.columns
        else 0
    )

    porcentaje_con_respuesta = round((reviews_con_respuesta / total_reviews) * 100, 2)

    positivas = int((df["rating"] >= 4).sum())
    neutrales = int((df["rating"] == 3).sum())
    negativas = int((df["rating"] <= 2).sum())

    porcentaje_positivas = round((positivas / total_reviews) * 100, 2)
    porcentaje_neutrales = round((neutrales / total_reviews) * 100, 2)
    porcentaje_negativas = round((negativas / total_reviews) * 100, 2)

    metricas = {
        "total_reviews": total_reviews,
        "rating_medio": rating_medio,
        "reviews_con_texto": reviews_con_texto,
        "reviews_con_respuesta": reviews_con_respuesta,
        "porcentaje_con_respuesta": porcentaje_con_respuesta,
        "positivas": positivas,
        "neutrales": neutrales,
        "negativas": negativas,
        "porcentaje_positivas": porcentaje_positivas,
        "porcentaje_neutrales": porcentaje_neutrales,
        "porcentaje_negativas": porcentaje_negativas,
    }

    return metricas


def distribucion_estrellas(df):
    """
    Calcula cuántas reseñas hay por cada número de estrellas.
    """

    distribucion = df["rating"].value_counts().sort_index()

    return distribucion


def obtener_reviews_destacadas(df):
    """
    Obtiene algunas reseñas positivas y negativas con texto.
    """

    df_texto = df[df["content"].notna()]
    df_texto = df_texto[df_texto["content"].astype(str).str.strip() != ""]

    reviews_negativas = df_texto[df_texto["rating"] <= 2].sort_values(
        by="reviewed_at_date",
        ascending=False
    )

    reviews_positivas = df_texto[df_texto["rating"] >= 4].sort_values(
        by="reviewed_at_date",
        ascending=False
    )

    return reviews_positivas.head(5), reviews_negativas.head(5)


def mostrar_metricas(metricas):
    """
    Muestra las métricas por pantalla.
    """

    print("\nANÁLISIS GENERAL DE RESEÑAS")
    print("---------------------------")
    print(f"Total de reseñas: {metricas['total_reviews']}")
    print(f"Rating medio: {metricas['rating_medio']}")
    print(f"Reseñas con texto: {metricas['reviews_con_texto']}")
    print(f"Reseñas respondidas por el negocio: {metricas['reviews_con_respuesta']}")
    print(f"Porcentaje de respuesta: {metricas['porcentaje_con_respuesta']}%")

    print("\nDistribución por sentimiento según estrellas")
    print("--------------------------------------------")
    print(f"Positivas: {metricas['positivas']} ({metricas['porcentaje_positivas']}%)")
    print(f"Neutrales: {metricas['neutrales']} ({metricas['porcentaje_neutrales']}%)")
    print(f"Negativas: {metricas['negativas']} ({metricas['porcentaje_negativas']}%)")


def mostrar_distribucion_estrellas(distribucion):
    """
    Muestra la distribución de estrellas.
    """

    print("\nDistribución por estrellas")
    print("--------------------------")

    for estrellas, cantidad in distribucion.items():
        print(f"{int(estrellas)} estrellas: {cantidad}")


def mostrar_reviews_destacadas(reviews_positivas, reviews_negativas):
    """
    Muestra ejemplos de reseñas positivas y negativas.
    """

    print("\nÚltimas reseñas positivas con texto")
    print("----------------------------------")

    for _, row in reviews_positivas.iterrows():
        print(f"\nRating: {row['rating']}")
        print(f"Fecha: {row.get('reviewed_at_date', '')}")
        print(f"Texto: {row['content']}")

    print("\nÚltimas reseñas negativas con texto")
    print("----------------------------------")

    for _, row in reviews_negativas.iterrows():
        print(f"\nRating: {row['rating']}")
        print(f"Fecha: {row.get('reviewed_at_date', '')}")
        print(f"Texto: {row['content']}")


if __name__ == "__main__":
    input_csv = "reviews_clean.csv"

    df_reviews = cargar_csv_limpio(input_csv)

    metricas = calcular_metricas_generales(df_reviews)
    distribucion = distribucion_estrellas(df_reviews)
    reviews_positivas, reviews_negativas = obtener_reviews_destacadas(df_reviews)

    mostrar_metricas(metricas)
    mostrar_distribucion_estrellas(distribucion)
    mostrar_reviews_destacadas(reviews_positivas, reviews_negativas)