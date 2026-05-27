import json
import pandas as pd
from pathlib import Path
from html import escape


def cargar_reviews_limpias(ruta_csv):
    ruta_csv = Path(ruta_csv)

    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_csv}")

    return pd.read_csv(ruta_csv)


def cargar_analisis_ia(ruta_json):
    ruta_json = Path(ruta_json)

    if not ruta_json.exists():
        print("No se encontró ai_analysis.json. El informe se generará sin sección de IA.")
        return None

    with open(ruta_json, "r", encoding="utf-8") as file:
        return json.load(file)


def calcular_metricas(df):
    total_reviews = len(df)

    rating_medio = round(df["rating"].mean(), 2)

    positivas = int((df["rating"] >= 4).sum())
    neutrales = int((df["rating"] == 3).sum())
    negativas = int((df["rating"] <= 2).sum())

    porcentaje_positivas = round((positivas / total_reviews) * 100, 2)
    porcentaje_neutrales = round((neutrales / total_reviews) * 100, 2)
    porcentaje_negativas = round((negativas / total_reviews) * 100, 2)

    reviews_con_texto = int(df["has_text"].sum()) if "has_text" in df.columns else 0
    reviews_con_respuesta = int(df["has_owner_response"].sum()) if "has_owner_response" in df.columns else 0

    porcentaje_respuesta = round((reviews_con_respuesta / total_reviews) * 100, 2)

    place_name = df["place_name"].dropna().iloc[0] if "place_name" in df.columns and df["place_name"].notna().any() else "Negocio"
    city = df["city"].dropna().iloc[0] if "city" in df.columns and df["city"].notna().any() else ""
    category = df["category"].dropna().iloc[0] if "category" in df.columns and df["category"].notna().any() else ""

    return {
        "place_name": place_name,
        "city": city,
        "category": category,
        "total_reviews": total_reviews,
        "rating_medio": rating_medio,
        "positivas": positivas,
        "neutrales": neutrales,
        "negativas": negativas,
        "porcentaje_positivas": porcentaje_positivas,
        "porcentaje_neutrales": porcentaje_neutrales,
        "porcentaje_negativas": porcentaje_negativas,
        "reviews_con_texto": reviews_con_texto,
        "reviews_con_respuesta": reviews_con_respuesta,
        "porcentaje_respuesta": porcentaje_respuesta,
    }


def obtener_reseñas_destacadas(df):
    df_texto = df.copy()

    df_texto["content"] = df_texto["content"].fillna("").astype(str).str.strip()
    df_texto = df_texto[df_texto["content"] != ""]

    positivas = df_texto[df_texto["rating"] >= 4].sort_values(
        by="reviewed_at_date",
        ascending=False
    ).head(5)

    negativas = df_texto[df_texto["rating"] <= 2].sort_values(
        by="reviewed_at_date",
        ascending=False
    ).head(5)

    return positivas, negativas


def generar_bloque_reseñas(df):
    html = ""

    for _, row in df.iterrows():
        rating = escape(str(row.get("rating", "")))
        fecha = escape(str(row.get("reviewed_at_date", "")))
        contenido = escape(str(row.get("content", "")))

        html += f"""
        <div class="review-card">
            <div class="review-rating">{rating} estrellas</div>
            <div class="review-date">{fecha}</div>
            <p>{contenido}</p>
        </div>
        """

    if html == "":
        html = "<p>No hay reseñas disponibles para esta sección.</p>"

    return html


def generar_lista_simple(items, clave_titulo, clave_descripcion=None):
    if not items:
        return "<p>No hay información suficiente para esta sección.</p>"

    html = ""

    for item in items:
        titulo = escape(str(item.get(clave_titulo, "")))

        descripcion = ""
        if clave_descripcion:
            descripcion = escape(str(item.get(clave_descripcion, "")))

        html += f"""
        <div class="ai-item">
            <h4>{titulo}</h4>
            <p>{descripcion}</p>
        </div>
        """

    return html


def generar_bloque_quejas(quejas):
    if not quejas:
        return "<p>No se detectaron quejas relevantes en la muestra analizada.</p>"

    html = ""

    for queja in quejas:
        problema = escape(str(queja.get("problema", "")))
        explicacion = escape(str(queja.get("explicacion", "")))
        gravedad = escape(str(queja.get("gravedad", "")))
        evidencia = escape(str(queja.get("evidencia", "")))

        html += f"""
        <div class="ai-item danger">
            <h4>{problema}</h4>
            <p>{explicacion}</p>
            <p><strong>Gravedad:</strong> {gravedad}</p>
            <p><strong>Evidencia:</strong> {evidencia}</p>
        </div>
        """

    return html


def generar_bloque_oportunidades(oportunidades):
    if not oportunidades:
        return "<p>No se detectaron oportunidades específicas en la muestra analizada.</p>"

    html = ""

    for oportunidad in oportunidades:
        titulo = escape(str(oportunidad.get("oportunidad", "")))
        accion = escape(str(oportunidad.get("accion_recomendada", "")))
        impacto = escape(str(oportunidad.get("impacto_estimado", "")))

        html += f"""
        <div class="ai-item opportunity">
            <h4>{titulo}</h4>
            <p>{accion}</p>
            <p><strong>Impacto estimado:</strong> {impacto}</p>
        </div>
        """

    return html


def generar_bloque_acciones(acciones):
    if not acciones:
        return "<p>No hay acciones prioritarias disponibles.</p>"

    html = ""

    for accion in acciones:
        titulo = escape(str(accion.get("accion", "")))
        prioridad = escape(str(accion.get("prioridad", "")))
        motivo = escape(str(accion.get("motivo", "")))

        html += f"""
        <div class="ai-item action">
            <h4>{titulo}</h4>
            <p><strong>Prioridad:</strong> {prioridad}</p>
            <p>{motivo}</p>
        </div>
        """

    return html


def generar_seccion_ia(analisis_ia):
    if analisis_ia is None:
        return """
        <div class="section">
            <h2>Análisis inteligente</h2>
            <p>
                Todavía no se ha generado el análisis con Gemini.
                Ejecuta primero <strong>python ai_analysis.py</strong>.
            </p>
        </div>
        """

    if "respuesta_bruta" in analisis_ia:
        respuesta = escape(str(analisis_ia["respuesta_bruta"]))
        return f"""
        <div class="section">
            <h2>Análisis inteligente</h2>
            <p>La respuesta de Gemini no se pudo convertir correctamente a JSON.</p>
            <pre>{respuesta}</pre>
        </div>
        """

    resumen = escape(str(analisis_ia.get("resumen_ejecutivo", "")))
    diagnostico = escape(str(analisis_ia.get("diagnostico_general", "")))
    frase_demo = escape(str(analisis_ia.get("frase_comercial_para_demo", "")))
    conclusion = escape(str(analisis_ia.get("conclusion", "")))

    aspectos_positivos = generar_lista_simple(
        analisis_ia.get("aspectos_positivos", []),
        "tema",
        "explicacion"
    )

    quejas = generar_bloque_quejas(
        analisis_ia.get("principales_quejas", [])
    )

    oportunidades = generar_bloque_oportunidades(
        analisis_ia.get("oportunidades_de_mejora", [])
    )

    acciones = generar_bloque_acciones(
        analisis_ia.get("acciones_prioritarias", [])
    )

    html = f"""
    <div class="section ai-section">
        <h2>Análisis inteligente con IA</h2>

        <div class="highlight-box">
            <h3>Resumen ejecutivo</h3>
            <p>{resumen}</p>
        </div>

        <h3>Diagnóstico general</h3>
        <p>{diagnostico}</p>

        <h3>Aspectos positivos detectados</h3>
        {aspectos_positivos}

        <h3>Principales quejas</h3>
        {quejas}

        <h3>Oportunidades de mejora</h3>
        {oportunidades}

        <h3>Acciones prioritarias recomendadas</h3>
        {acciones}

        <div class="highlight-box">
            <h3>Frase para presentar al negocio</h3>
            <p>{frase_demo}</p>
        </div>

        <h3>Conclusión</h3>
        <p>{conclusion}</p>
    </div>
    """

    return html


def generar_html(metricas, reviews_positivas, reviews_negativas, analisis_ia):
    bloque_positivas = generar_bloque_reseñas(reviews_positivas)
    bloque_negativas = generar_bloque_reseñas(reviews_negativas)
    bloque_ia = generar_seccion_ia(analisis_ia)

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Informe de reseñas - {escape(str(metricas["place_name"]))}</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                color: #222;
            }}

            .container {{
                max-width: 1100px;
                margin: 0 auto;
                padding: 40px 20px;
            }}

            .header {{
                background-color: #111827;
                color: white;
                padding: 35px;
                border-radius: 18px;
                margin-bottom: 30px;
            }}

            .header h1 {{
                margin: 0;
                font-size: 34px;
            }}

            .header p {{
                margin-top: 10px;
                font-size: 16px;
                color: #d1d5db;
            }}

            .grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 18px;
                margin-bottom: 30px;
            }}

            .card {{
                background-color: white;
                padding: 24px;
                border-radius: 16px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
            }}

            .card-title {{
                font-size: 14px;
                color: #6b7280;
                margin-bottom: 8px;
            }}

            .card-value {{
                font-size: 30px;
                font-weight: bold;
            }}

            .section {{
                background-color: white;
                padding: 30px;
                border-radius: 18px;
                margin-bottom: 30px;
                box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
            }}

            .section h2 {{
                margin-top: 0;
                font-size: 24px;
            }}

            .section h3 {{
                margin-top: 28px;
                font-size: 20px;
            }}

            .bar-container {{
                background-color: #e5e7eb;
                border-radius: 999px;
                height: 22px;
                overflow: hidden;
                margin-bottom: 15px;
            }}

            .bar-positive {{
                height: 100%;
                background-color: #22c55e;
                width: {metricas["porcentaje_positivas"]}%;
            }}

            .bar-neutral {{
                height: 100%;
                background-color: #facc15;
                width: {metricas["porcentaje_neutrales"]}%;
            }}

            .bar-negative {{
                height: 100%;
                background-color: #ef4444;
                width: {metricas["porcentaje_negativas"]}%;
            }}

            .review-card {{
                border-left: 5px solid #111827;
                padding: 16px;
                margin-bottom: 16px;
                background-color: #f9fafb;
                border-radius: 12px;
            }}

            .review-rating {{
                font-weight: bold;
                margin-bottom: 4px;
            }}

            .review-date {{
                font-size: 13px;
                color: #6b7280;
                margin-bottom: 8px;
            }}

            .ai-section {{
                border-top: 8px solid #111827;
            }}

            .ai-item {{
                padding: 18px;
                background-color: #f9fafb;
                border-radius: 12px;
                margin-bottom: 14px;
                border-left: 5px solid #111827;
            }}

            .ai-item h4 {{
                margin-top: 0;
                margin-bottom: 8px;
            }}

            .ai-item p {{
                margin-bottom: 6px;
            }}

            .danger {{
                border-left-color: #ef4444;
            }}

            .opportunity {{
                border-left-color: #2563eb;
            }}

            .action {{
                border-left-color: #22c55e;
            }}

            .highlight-box {{
                background-color: #eef2ff;
                padding: 22px;
                border-radius: 14px;
                margin-bottom: 22px;
            }}

            .highlight-box h3 {{
                margin-top: 0;
            }}

            .footer {{
                text-align: center;
                color: #6b7280;
                margin-top: 30px;
                font-size: 14px;
            }}

            pre {{
                white-space: pre-wrap;
                background-color: #111827;
                color: white;
                padding: 16px;
                border-radius: 12px;
                overflow-x: auto;
            }}

            @media (max-width: 800px) {{
                .grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}

            @media (max-width: 500px) {{
                .grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>

    <body>
        <div class="container">

            <div class="header">
                <h1>Análisis automático de reseñas</h1>
                <p>{escape(str(metricas["place_name"]))} · {escape(str(metricas["city"]))} · {escape(str(metricas["category"]))}</p>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="card-title">Total de reseñas</div>
                    <div class="card-value">{metricas["total_reviews"]}</div>
                </div>

                <div class="card">
                    <div class="card-title">Rating medio</div>
                    <div class="card-value">{metricas["rating_medio"]}</div>
                </div>

                <div class="card">
                    <div class="card-title">Reseñas con texto</div>
                    <div class="card-value">{metricas["reviews_con_texto"]}</div>
                </div>

                <div class="card">
                    <div class="card-title">Reseñas respondidas</div>
                    <div class="card-value">{metricas["porcentaje_respuesta"]}%</div>
                </div>
            </div>

            {bloque_ia}

            <div class="section">
                <h2>Distribución general</h2>

                <p><strong>Positivas:</strong> {metricas["positivas"]} reseñas ({metricas["porcentaje_positivas"]}%)</p>
                <div class="bar-container">
                    <div class="bar-positive"></div>
                </div>

                <p><strong>Neutrales:</strong> {metricas["neutrales"]} reseñas ({metricas["porcentaje_neutrales"]}%)</p>
                <div class="bar-container">
                    <div class="bar-neutral"></div>
                </div>

                <p><strong>Negativas:</strong> {metricas["negativas"]} reseñas ({metricas["porcentaje_negativas"]}%)</p>
                <div class="bar-container">
                    <div class="bar-negative"></div>
                </div>
            </div>

            <div class="section">
                <h2>Últimas reseñas positivas destacadas</h2>
                {bloque_positivas}
            </div>

            <div class="section">
                <h2>Últimas reseñas negativas destacadas</h2>
                {bloque_negativas}
            </div>

            <div class="footer">
                Informe generado automáticamente por ProcessAI Studio
            </div>

        </div>
    </body>
    </html>
    """

    return html


def guardar_informe(html, ruta_salida):
    ruta_salida = Path(ruta_salida)

    with open(ruta_salida, "w", encoding="utf-8") as file:
        file.write(html)

    print(f"Informe generado correctamente: {ruta_salida}")


if __name__ == "__main__":
    input_csv = "reviews_clean.csv"
    input_ai_json = "ai_analysis.json"
    output_html = "review_report.html"

    df_reviews = cargar_reviews_limpias(input_csv)
    analisis_ia = cargar_analisis_ia(input_ai_json)

    metricas = calcular_metricas(df_reviews)
    reviews_positivas, reviews_negativas = obtener_reseñas_destacadas(df_reviews)

    html = generar_html(
        metricas=metricas,
        reviews_positivas=reviews_positivas,
        reviews_negativas=reviews_negativas,
        analisis_ia=analisis_ia
    )

    guardar_informe(html, output_html)