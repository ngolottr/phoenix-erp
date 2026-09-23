import os

def cargar_env():
    """Lee .env (junto a este archivo) y carga sus variables si aún no están
    definidas en el entorno. Sin dependencias nuevas: alcanza con un archivo
    de una línea por variable, KEY=valor."""
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(ruta):
        return
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip())
