import sqlite3
from datetime import datetime, timedelta

def conectar():
    conn = sqlite3.connect("phoenix_erp.db")
    return conn

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    # Clientes CRM
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            empresa TEXT,
            rut TEXT,
            telefono TEXT,
            correo TEXT,
            origen TEXT,
            fecha_registro TEXT
        )
    """)

    # Cotizaciones SAP
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            fecha TEXT,
            cliente TEXT,
            rut TEXT,
            codigo_sap TEXT,
            ejecutivo TEXT,
            condicion_pago TEXT,
            tipo_despacho TEXT,
            email_cliente TEXT,
            total_neto TEXT,
            iva TEXT,
            total TEXT,
            fecha_importacion TEXT
        )
    """)

    # Productos de cotizaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos_cotizacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cotizacion_numero TEXT,
            codigo TEXT,
            nombre TEXT,
            cantidad TEXT,
            precio_unitario TEXT,
            total TEXT
        )
    """)

    # Prospectos — flujo comercial completo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prospectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            web TEXT,
            motivo TEXT,
            ejecutivo TEXT,
            estado TEXT DEFAULT 'nuevo',
            intentos_llamada INTEGER DEFAULT 0,
            fecha_busqueda TEXT,
            fecha_email TEXT,
            fecha_ultima_llamada TEXT,
            fecha_interes TEXT,
            fecha_cotizacion TEXT,
            fecha_cierre TEXT,
            proximo_contacto TEXT,
            notas TEXT
        )
    """)

    # Actividades por prospecto
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prospecto_id INTEGER,
            tipo TEXT,
            descripcion TEXT,
            fecha TEXT,
            FOREIGN KEY (prospecto_id) REFERENCES prospectos(id)
        )
    """)

    # Cotizaciones asociadas a prospectos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones_prospecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prospecto_id INTEGER,
            nombre_archivo TEXT,
            ruta_archivo TEXT,
            numero_cotizacion TEXT,
            total TEXT,
            fecha_importacion TEXT,
            FOREIGN KEY (prospecto_id) REFERENCES prospectos(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Base de datos lista")

# ─────────────────────────────────────
# CLIENTES
# ─────────────────────────────────────
def guardar_cliente(nombre, empresa, rut, telefono, correo, origen):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (nombre, empresa, rut, telefono, correo, origen, fecha_registro)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre, empresa, rut, telefono, correo, origen,
          datetime.now().strftime("%d/%m/%Y")))
    conn.commit()
    conn.close()

def obtener_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

# ─────────────────────────────────────
# COTIZACIONES SAP
# ─────────────────────────────────────
def guardar_cotizacion(datos):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cotizaciones WHERE numero = ?",
                   (datos["numero_cotizacion"],))
    if cursor.fetchone():
        conn.close()
        return False
    cursor.execute("""
        INSERT INTO cotizaciones (
            numero, fecha, cliente, rut, codigo_sap,
            ejecutivo, condicion_pago, tipo_despacho,
            email_cliente, total_neto, iva, total, fecha_importacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos["numero_cotizacion"], datos["fecha"], datos["cliente"],
        datos["rut"], datos["codigo_sap"], datos["ejecutivo"],
        datos["condicion_pago"], datos["tipo_despacho"], datos["email_cliente"],
        datos["total_neto"], datos["iva"], datos["total"],
        datetime.now().strftime("%d/%m/%Y %H:%M")
    ))
    for p in datos.get("productos", []):
        cursor.execute("""
            INSERT INTO productos_cotizacion
            (cotizacion_numero, codigo, nombre, cantidad, precio_unitario, total)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datos["numero_cotizacion"], p["codigo"], p["nombre"],
              p["cantidad"], p["precio_unitario"], p["total"]))
    conn.commit()
    conn.close()
    return True

def obtener_cotizaciones():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT numero, fecha, cliente, total, fecha_importacion
        FROM cotizaciones ORDER BY id DESC
    """)
    cotizaciones = cursor.fetchall()
    conn.close()
    return cotizaciones

# ─────────────────────────────────────
# PROSPECTOS
# ─────────────────────────────────────
def guardar_prospecto(nombre, telefono, email, web, motivo, ejecutivo="Nicolas Golott"):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM prospectos WHERE nombre = ? AND email = ?",
                   (nombre, email))
    if cursor.fetchone():
        conn.close()
        return None
    cursor.execute("""
        INSERT INTO prospectos (nombre, telefono, email, web, motivo, ejecutivo,
                                estado, fecha_busqueda)
        VALUES (?, ?, ?, ?, ?, ?, 'nuevo', ?)
    """, (nombre, telefono, email, web, motivo, ejecutivo,
          datetime.now().strftime("%d/%m/%Y %H:%M")))
    prospecto_id = cursor.lastrowid
    cursor.execute("""
        INSERT INTO actividades (prospecto_id, tipo, descripcion, fecha)
        VALUES (?, 'busqueda', 'Prospecto encontrado en búsqueda Google', ?)
    """, (prospecto_id, datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()
    return prospecto_id

def obtener_prospectos(estado=None):
    conn = conectar()
    cursor = conn.cursor()
    if estado:
        cursor.execute("""
            SELECT * FROM prospectos WHERE estado = ?
            ORDER BY id DESC
        """, (estado,))
    else:
        cursor.execute("""
            SELECT * FROM prospectos
            WHERE estado NOT IN ('ganado', 'perdido', 'archivado')
            ORDER BY id DESC
        """)
    prospectos = cursor.fetchall()
    conn.close()
    return prospectos

def actualizar_estado_prospecto(prospecto_id, nuevo_estado, notas=""):
    conn = conectar()
    cursor = conn.cursor()
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

    campos = {"estado": nuevo_estado}

    if nuevo_estado == "email_enviado":
        campos["fecha_email"] = ahora
        campos["proximo_contacto"] = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")
        descripcion = "Email de presentación enviado"
    elif nuevo_estado == "llamada_contestada":
        campos["fecha_ultima_llamada"] = ahora
        descripcion = "Cliente contactado por teléfono"
    elif nuevo_estado == "no_contesto":
        cursor.execute("SELECT intentos_llamada FROM prospectos WHERE id = ?",
                       (prospecto_id,))
        intentos = cursor.fetchone()[0] + 1
        campos["intentos_llamada"] = intentos
        campos["fecha_ultima_llamada"] = ahora
        dias = {1: 2, 2: 3, 3: 5}.get(intentos, 0)
        if dias:
            campos["proximo_contacto"] = (datetime.now() + timedelta(days=dias)).strftime("%d/%m/%Y")
            descripcion = f"No contestó (intento {intentos}) - Próximo contacto en {dias} días"
        else:
            campos["estado"] = "archivado"
            descripcion = "Sin respuesta tras 4 intentos - Archivado"
    elif nuevo_estado == "interesado":
        campos["fecha_interes"] = ahora
        descripcion = "Cliente interesado en productos BathCenter"
    elif nuevo_estado == "cotizacion_enviada":
        campos["fecha_cotizacion"] = ahora
        descripcion = "Cotización SAP enviada al cliente"
    elif nuevo_estado == "ganado":
        campos["fecha_cierre"] = ahora
        descripcion = "¡Cliente ganado! 🏆"
    elif nuevo_estado == "perdido":
        campos["fecha_cierre"] = ahora
        descripcion = f"Cliente no interesado. {notas}"
    else:
        descripcion = notas or nuevo_estado

    set_clause = ", ".join([f"{k} = ?" for k in campos])
    valores = list(campos.values()) + [prospecto_id]
    cursor.execute(f"UPDATE prospectos SET {set_clause} WHERE id = ?", valores)

    cursor.execute("""
        INSERT INTO actividades (prospecto_id, tipo, descripcion, fecha)
        VALUES (?, ?, ?, ?)
    """, (prospecto_id, nuevo_estado, descripcion, ahora))

    conn.commit()
    conn.close()

def obtener_tareas_pendientes():
    conn = conectar()
    cursor = conn.cursor()
    hoy = datetime.now().strftime("%d/%m/%Y")
    tareas = []

    # Nuevos sin contactar
    cursor.execute("""
        SELECT id, nombre FROM prospectos WHERE estado = 'nuevo'
    """)
    for p in cursor.fetchall():
        tareas.append({
            "prospecto_id": p[0],
            "empresa": p[1],
            "tarea": "📧 Enviar email de presentación",
            "prioridad": 1
        })

    # Por llamar
    cursor.execute("""
        SELECT id, nombre, intentos_llamada FROM prospectos
        WHERE estado IN ('email_enviado', 'no_contesto')
        AND (proximo_contacto <= ? OR proximo_contacto IS NULL)
    """, (hoy,))
    for p in cursor.fetchall():
        intentos = p[2]
        if intentos > 0:
            tarea = f"📞 Llamar (intento {intentos + 1} de 4)"
        else:
            tarea = "📞 Llamar por primera vez"
        tareas.append({
            "prospecto_id": p[0],
            "empresa": p[1],
            "tarea": tarea,
            "prioridad": 2
        })

    # Interesados sin cotización
    cursor.execute("""
        SELECT id, nombre FROM prospectos WHERE estado = 'interesado'
    """)
    for p in cursor.fetchall():
        tareas.append({
            "prospecto_id": p[0],
            "empresa": p[1],
            "tarea": "🔥 Preparar cotización en SAP",
            "prioridad": 1
        })

    # Cotización enviada sin cierre
    cursor.execute("""
        SELECT id, nombre FROM prospectos WHERE estado = 'cotizacion_enviada'
    """)
    for p in cursor.fetchall():
        tareas.append({
            "prospecto_id": p[0],
            "empresa": p[1],
            "tarea": "📄 Hacer seguimiento de cotización",
            "prioridad": 2
        })

    conn.close()
    tareas.sort(key=lambda x: x["prioridad"])
    return tareas

def obtener_actividades_prospecto(prospecto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tipo, descripcion, fecha FROM actividades
        WHERE prospecto_id = ? ORDER BY id ASC
    """, (prospecto_id,))
    actividades = cursor.fetchall()
    conn.close()
    return actividades

def guardar_cotizacion_prospecto(prospecto_id, nombre_archivo, ruta, numero, total):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cotizaciones_prospecto
        (prospecto_id, nombre_archivo, ruta_archivo, numero_cotizacion, total, fecha_importacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (prospecto_id, nombre_archivo, ruta, numero, total,
          datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()

def obtener_cotizaciones_prospecto(prospecto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre_archivo, numero_cotizacion, total, fecha_importacion
        FROM cotizaciones_prospecto WHERE prospecto_id = ?
        ORDER BY id DESC
    """, (prospecto_id,))
    cotizaciones = cursor.fetchall()
    conn.close()
    return cotizaciones

def obtener_stats():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cotizaciones")
    total_cotizaciones = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM prospectos WHERE estado NOT IN ('archivado','perdido')")
    total_prospectos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM prospectos WHERE estado = 'ganado'")
    ganados = cursor.fetchone()[0]
    cursor.execute("SELECT total FROM cotizaciones")
    totales = cursor.fetchall()
    monto_total = 0
    for t in totales:
        try:
            monto = t[0].replace("$", "").replace(".", "").strip()
            monto_total += int(monto)
        except:
            pass
    conn.close()
    return {
        "cotizaciones": total_cotizaciones,
        "clientes": total_clientes,
        "prospectos": total_prospectos,
        "ganados": ganados,
        "monto_total": f"${monto_total:,}".replace(",", ".")
    }