import fitz
import re

def leer_cotizacion_sap(ruta_pdf):
    try:
        doc = fitz.open(ruta_pdf)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        doc.close()

        lineas = [l.strip() for l in texto.split('\n')]

        datos = {
            "numero_cotizacion": "",
            "fecha": "",
            "cliente": "",
            "rut": "",
            "codigo_sap": "",
            "ejecutivo": "",
            "condicion_pago": "",
            "tipo_despacho": "",
            "email_cliente": "",
            "total_neto": "",
            "iva": "",
            "total": "",
            "productos": []
        }

        # Número de cotización
        for i, linea in enumerate(lineas):
            if linea.startswith("N°"):
                datos["numero_cotizacion"] = linea.replace("N°", "").strip()
                break

        # Fecha
        match = re.search(r'Fecha Cotiz\.\:\s*(\d{2}\.\d{2}\.\d{4})', texto)
        if match:
            datos["fecha"] = match.group(1).replace(".", "/")

        # Cliente y RUT
        for i, linea in enumerate(lineas):
            if linea.startswith("RUT:"):
                datos["cliente"] = lineas[i - 1].strip()
                datos["rut"] = linea.replace("RUT:", "").strip()
                break

        # Código SAP cliente
        match = re.search(r'Cod\.Cliente:\s*(\d+)', texto)
        if match:
            datos["codigo_sap"] = match.group(1)

        # Ejecutivo — línea después de "Cond. de Pago"
        for i, linea in enumerate(lineas):
            if linea == "Cond. de Pago":
                if i + 1 < len(lineas):
                    datos["ejecutivo"] = lineas[i + 1].strip()
                break

        # Condición de pago — buscar "Contado" u otro valor después del ejecutivo
        for i, linea in enumerate(lineas):
            if linea == "Cond. de Pago":
                for j in range(i + 2, min(i + 8, len(lineas))):
                    candidato = lineas[j].strip()
                    if (candidato and
                        not candidato.startswith("Fono") and
                        not candidato.startswith("Email") and
                        candidato != ""):
                        datos["condicion_pago"] = candidato
                        break
                break

        # Tipo despacho
        for i, linea in enumerate(lineas):
            if linea == "Tipo Despacho":
                if i + 1 < len(lineas):
                    datos["tipo_despacho"] = lineas[i + 1].strip()
                break

        # Email cliente
        match = re.search(r'Email:([\w\.\@]+)', texto)
        if match:
            datos["email_cliente"] = match.group(1).strip()

        # Total neto
        match = re.search(r'Valor neto\s+([\d\.\s]+)', texto)
        if match:
            datos["total_neto"] = "$" + match.group(1).strip().replace(" ", "")

        # IVA
        match = re.search(r'19% IVA Ventas\s+([\d\.\s]+)', texto)
        if match:
            datos["iva"] = "$" + match.group(1).strip().replace(" ", "")

        # Total
        match = re.search(r'TOTAL\s*:\s*([\d\.\s]+)', texto)
        if match:
            datos["total"] = "$" + match.group(1).strip().replace(" ", "")

        # ─────────────────────────────────────
        # PRODUCTOS
        # Estructura exacta SAP BathCenter:
        # [CODIGO]         → código alfanumérico largo
        # [NOMBRE línea 1] → texto
        # [NOMBRE línea 2] → texto opcional (si tiene 2 líneas)
        # [CENTRO]         → 4 dígitos
        # [CANTIDAD]       → número
        # [UNIDAD]         → "Unidad"
        # [PRECIO UNIT]    → número con espacios
        # [TOTAL]          → número con espacios
        # ─────────────────────────────────────

        def es_codigo_producto(s):
            return bool(re.match(r'^[A-Z]{2}[A-Z0-9]{5,}$', s))

        def es_centro(s):
            return bool(re.match(r'^\d{4}$', s))

        def es_precio(s):
            return bool(re.match(r'^[\d\s\.]+$', s)) and len(s.replace(" ", "")) > 2

        i = 0
        while i < len(lineas):
            if es_codigo_producto(lineas[i]):
                codigo = lineas[i]
                i += 1
                nombre_partes = []

                # Recoger nombre hasta encontrar el centro (4 dígitos)
                while i < len(lineas) and not es_centro(lineas[i]):
                    parte = lineas[i].strip()
                    if parte:
                        nombre_partes.append(parte)
                    i += 1

                nombre = " ".join(nombre_partes)

                # Centro — saltar
                i += 1

                # Cantidad
                cantidad = lineas[i].strip() if i < len(lineas) else ""
                i += 1

                # Unidad — saltar
                i += 1

                # Precio unitario
                precio_unit = ""
                if i < len(lineas) and es_precio(lineas[i]):
                    precio_unit = "$" + lineas[i].strip().replace(" ", "")
                i += 1

                # Total producto
                total_prod = ""
                if i < len(lineas) and es_precio(lineas[i]):
                    total_prod = "$" + lineas[i].strip().replace(" ", "")
                i += 1

                if codigo:
                    datos["productos"].append({
                        "codigo": codigo,
                        "nombre": nombre,
                        "cantidad": cantidad,
                        "precio_unitario": precio_unit,
                        "total": total_prod
                    })
                continue

            i += 1

        return datos

    except Exception as e:
        return {"error": str(e)}