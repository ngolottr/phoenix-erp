import os
from serpapi import GoogleSearch
import re

def buscar_prospectos(rubro, ciudad="Santiago", cantidad=10):
    """
    Busca prospectos reales en Google usando SerpApi.
    """

    API_KEY = os.environ["SERPAPI_KEY"]

    rubros_queries = {
        "constructoras": f"constructoras en {ciudad} Chile contacto teléfono",
        "hoteles": f"hoteles en {ciudad} Chile contacto teléfono",
        "inmobiliarias": f"inmobiliarias en {ciudad} Chile contacto",
        "gasfiteres": f"gasfiteres instaladores sanitarios {ciudad} Chile",
        "ferreterias": f"ferreterías materiales construcción {ciudad} Chile",
        "clinicas": f"clínicas hospitales {ciudad} Chile contacto",
        "colegios": f"colegios universidades {ciudad} Chile contacto",
        "restaurantes": f"restaurantes {ciudad} Chile contacto teléfono",
        "empresas": f"empresas corporativas {ciudad} Chile contacto",
        "todos": f"empresas constructoras hoteles inmobiliarias {ciudad} Chile"
    }

    query = rubros_queries.get(rubro, f"{rubro} {ciudad} Chile contacto")

    try:
        params = {
            "engine": "google",
            "q": query,
            "location": "Santiago, Chile",
            "hl": "es",
            "gl": "cl",
            "num": cantidad,
            "api_key": API_KEY
        }

        search = GoogleSearch(params)
        resultados = search.get_dict()
        prospectos = []

        # Resultados orgánicos
        for r in resultados.get("organic_results", []):
            nombre = r.get("title", "")
            # Limpiar nombre
            nombre = re.sub(r'\s*[-|]\s*.*$', '', nombre).strip()
            if len(nombre) > 50:
                nombre = nombre[:50] + "..."

            url = r.get("link", "")
            descripcion = r.get("snippet", "")

            # Extraer teléfono del snippet
            telefono = ""
            tel_match = re.search(
                r'(?:\+56|56)?[\s\-]?(?:2|9)[\s\-]?\d{4}[\s\-]?\d{4}',
                descripcion
            )
            if tel_match:
                telefono = tel_match.group().strip()

            # Extraer email del snippet
            email = ""
            email_match = re.search(r'[\w\.\-]+@[\w\.\-]+\.\w+', descripcion)
            if email_match:
                email = email_match.group()

            prospectos.append({
                "nombre": nombre,
                "telefono": telefono,
                "email": email,
                "url": url[:40] if url else "",
                "motivo": descripcion[:80] + "..." if len(descripcion) > 80 else descripcion,
                "estado": "🟡 Por contactar"
            })

        # Resultados locales (Google Maps)
        for r in resultados.get("local_results", {}).get("places", []):
            nombre = r.get("title", "")
            telefono = r.get("phone", "")
            direccion = r.get("address", "")
            rating = r.get("rating", "")

            prospectos.append({
                "nombre": nombre,
                "telefono": telefono,
                "email": "",
                "url": direccion[:40],
                "motivo": f"⭐ {rating} | {direccion}" if rating else direccion,
                "estado": "🟡 Por contactar"
            })

        return prospectos[:cantidad]

    except Exception as e:
        return {"error": str(e)}