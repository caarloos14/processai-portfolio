from apify_client import ApifyClient
from dotenv import load_dotenv
from pathlib import Path
import subprocess
import os
import json


load_dotenv()


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


def ejecutar_script(nombre_script, paso):
    """
    Ejecuta un script de Python como parte del pipeline.
    """

    script_path = Path(nombre_script)

    if not script_path.exists():
        raise FileNotFoundError(f"No se encontró el script: {nombre_script}")

    print(f"\n[{paso}] Ejecutando {nombre_script}...")

    resultado = subprocess.run(
        ["python", nombre_script],
        capture_output=True,
        text=True
    )

    if resultado.stdout:
        print(resultado.stdout)

    if resultado.stderr:
        print(resultado.stderr)

    if resultado.returncode != 0:
        raise RuntimeError(f"Falló la ejecución de {nombre_script}")

    print(f"{nombre_script} ejecutado correctamente.")


def ejecutar_pipeline():
    """
    Ejecuta todo el flujo completo:
    Apify → limpieza → análisis IA → informe HTML.
    """

    print("\nINICIANDO PIPELINE DE ANÁLISIS DE RESEÑAS")
    print("-----------------------------------------")

    ejecutar_scraper()

    ejecutar_script("clean_reviews.py", "2/4")

    ejecutar_script("ai_analysis.py", "3/4")

    ejecutar_script("report_generator.py", "4/4")

    print("\nPIPELINE FINALIZADO CORRECTAMENTE")
    print("---------------------------------")
    print("Archivos generados:")
    print("- reviews.json")
    print("- reviews_clean.csv")
    print("- ai_analysis.json")
    print("- review_report.html")
    print("\nAbre review_report.html en el navegador para ver el informe final.")


if __name__ == "__main__":
    ejecutar_pipeline()