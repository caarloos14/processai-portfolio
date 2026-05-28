# main.py
from dotenv import load_dotenv
import os
import pandas as pd
from pathlib import Path
from apify_client import ApifyClient
import json

from clean_reviews import cargar_reviews, limpiar_reviews, filtrar_negativas
from generate_responses import generar_respuestas_gemini, guardar_respuestas

load_dotenv()

def ejecutar_pipeline():
    # 1. Extraer reseñas con Apify (igual que review-analyzer)
    print("Extraer reseñas con Apify... (usa tu scraper actual)")
    # Aqui iría el código de Apify que ya tienes, guardando reviews.json

    def ejecutar_scraper():
        """
        Ejecuta el scraper de Apify y guarda las reseñas en reviews.json.
        """

        apify_token = os.getenv("APIFY_TOKEN")

        if not apify_token:
            raise ValueError("No se encontró APIFY_TOKEN en el archivo .env")

        client = ApifyClient(apify_token)

        actor_id = "web_wanderer/google-reviews-scraper"

        run_input = {
        "include_personal": False,
        "place_ids": [
            "ChIJoTXWl8dbwokRpKA2BJFVsGA",
            "0x53554f38893bbb89:0x222e4f25f9ee250"
        ],
        "place_urls": [
            "https://maps.app.goo.gl/L9prRQmVR3DWymDt6"
        ]
    }

        print("\n[1/4] Ejecutando scraper de Apify...")

        run = client.actor(actor_id).call(run_input=run_input)

        dataset_id = run.default_dataset_id

        items = list(
            client.dataset(dataset_id).iterate_items()
        )

        output_path = Path("reviews.json")

        output_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )

        print(f"Reseñas guardadas: {len(items)}")
        print(f"Archivo generado: {output_path}")



        # 2. Cargar y limpiar todas las reseñas
    reviews = cargar_reviews("reviews.json")
    df_limpio = limpiar_reviews(reviews)

    # 3. Filtrar solo reseñas negativas
    df_negativas = filtrar_negativas(df_limpio)

    # 4. Generar respuestas automáticas con Gemini
    respuestas = generar_respuestas_gemini(df_negativas)

    # 5. Guardar respuestas en CSV o JSON
    guardar_respuestas(df_negativas, respuestas, "respuestas_negativas.csv")

    print("Pipeline de respuestas automáticas finalizado.")

if __name__ == "__main__":
    ejecutar_pipeline()