# ProcessAI Review Analyzer

Demo de análisis automático de reseñas de Google Maps usando Python, Apify y Gemini.

Este proyecto permite extraer reseñas públicas de un negocio en Google Maps, limpiarlas, analizarlas con inteligencia artificial y generar un informe HTML con métricas generales, puntos fuertes, quejas recurrentes y acciones recomendadas.

El objetivo de esta demo es mostrar cómo un negocio local puede transformar sus reseñas en información útil para tomar decisiones.

---

## Funcionalidades principales

- Extracción automática de reseñas desde Google Maps mediante Apify.
- Limpieza y normalización de los datos en formato CSV.
- Cálculo de métricas básicas:
  - número total de reseñas;
  - rating medio;
  - porcentaje de reseñas positivas, neutras y negativas;
  - porcentaje de reseñas respondidas por el negocio.
- Análisis inteligente con Gemini:
  - resumen ejecutivo;
  - diagnóstico general;
  - aspectos positivos más repetidos;
  - principales quejas;
  - oportunidades de mejora;
  - acciones prioritarias recomendadas.
- Generación automática de un informe HTML visual y presentable.

---

## Estructura del proyecto

```text
processai-review-analyzer/
│
├── main.py
├── clean_reviews.py
├── ai_analysis.py
├── report_generator.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md