import customtkinter as ctk
from database import (crear_tablas, guardar_cliente, obtener_clientes,
                      guardar_cotizacion, obtener_cotizaciones,
                      guardar_prospecto, obtener_prospectos,
                      actualizar_estado_prospecto, obtener_tareas_pendientes,
                      obtener_actividades_prospecto, guardar_cotizacion_prospecto,
                      obtener_cotizaciones_prospecto, obtener_stats)
from lector_pdf import leer_cotizacion_sap
from tkinter import filedialog
import subprocess
import os

# Crear tablas al iniciar
crear_tablas()

# Configuración visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Ventana principal
ventana = ctk.CTk()
ventana.title("Proyecto Phoenix ERP")
ventana.geometry("1100x650")
ventana.resizable(False, False)

# ─────────────────────────────────────
# PANEL IZQUIERDO
# ─────────────────────────────────────
panel_izquierdo = ctk.CTkFrame(ventana, width=220, corner_radius=0)
panel_izquierdo.pack(side="left", fill="y")
panel_izquierdo.pack_propagate(False)

logo = ctk.CTkLabel(panel_izquierdo, text="🔥 Phoenix ERP",
                    font=("Arial", 20, "bold"))
logo.pack(pady=30)

# Panel derecho
panel_derecho = ctk.CTkFrame(ventana, corner_radius=0, fg_color="#1a1a2e")
panel_derecho.pack(side="right", fill="both", expand=True)

contenido_frame = ctk.CTkFrame(panel_derecho, fg_color="transparent")
contenido_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ─────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────
def limpiar_contenido():
    for widget in contenido_frame.winfo_children():
        widget.destroy()

def abrir_outlook(email, nombre_empresa):
    asunto = f"BathCenter La Florida - Productos para su empresa"
    cuerpo = f"""Estimado equipo de {nombre_empresa},

Mi nombre es Nicolás Golott, Jefe de Tienda de BathCenter La Florida.

Me pongo en contacto con ustedes para presentarles nuestra línea de productos sanitarios de las marcas Fanaloza y Briggs, líderes en el mercado chileno.

Contamos con:
- Lavamanos y pedestales
- Inodoros y wc
- Griferías y monos comando
- Duchas y accesorios
- Muebles de baño

Ofrecemos precios competitivos, atención personalizada y entrega inmediata desde nuestra tienda ubicada en La Florida 9660, Santiago.

Quedo a disposición para coordinar una visita o enviarles una cotización personalizada.

Saludos cordiales,

Nicolás Golott
Jefe de Tienda - BathCenter La Florida
Fono: +56 2 2351 5813
nicolas.golott@bathcenter.cl"""

    try:
        import urllib.parse
        asunto_enc = urllib.parse.quote(asunto)
        cuerpo_enc = urllib.parse.quote(cuerpo)
        mailto = f"mailto:{email}?subject={asunto_enc}&body={cuerpo_enc}"
        os.startfile(mailto)
        return True
    except Exception as e:
        return False

# ─────────────────────────────────────
# MÓDULO INICIO
# ─────────────────────────────────────
def mostrar_inicio():
    limpiar_contenido()

    # Notificaciones
    tareas = obtener_tareas_pendientes()

    if tareas:
        frame_notif = ctk.CTkFrame(contenido_frame, fg_color="#2a1a1a",
                                    corner_radius=10)
        frame_notif.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame_notif,
                     text=f"🔔 TIENES {len(tareas)} TAREAS PENDIENTES",
                     font=("Arial", 15, "bold"),
                     text_color="#ff6b6b").pack(pady=(15, 5))

        for tarea in tareas[:5]:
            ctk.CTkLabel(frame_notif,
                         text=f"{tarea['tarea']}  →  {tarea['empresa']}",
                         font=("Arial", 12),
                         text_color="white").pack(pady=2)

        if len(tareas) > 5:
            ctk.CTkLabel(frame_notif,
                         text=f"... y {len(tareas)-5} tareas más",
                         font=("Arial", 11),
                         text_color="gray").pack(pady=(2, 10))
        else:
            ctk.CTkLabel(frame_notif, text="").pack(pady=5)

    else:
        frame_notif = ctk.CTkFrame(contenido_frame, fg_color="#1a2a1a",
                                    corner_radius=10)
        frame_notif.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame_notif,
                     text="✅ Sin tareas pendientes por hoy",
                     font=("Arial", 14),
                     text_color="#6bff6b").pack(pady=20)

    # Stats
    stats = obtener_stats()
    frame_stats = ctk.CTkFrame(contenido_frame, fg_color="transparent")
    frame_stats.pack(fill="x", pady=10)

    kpis = [
        ("📄 Cotizaciones", str(stats["cotizaciones"]), "#1f6aa5"),
        ("👥 Clientes CRM", str(stats["clientes"]), "#2d8a4e"),
        ("🔍 Prospectos", str(stats["prospectos"]), "#8a4e2d"),
        ("🏆 Ganados", str(stats["ganados"]), "#6b2d8a"),
    ]

    for titulo, valor, color in kpis:
        card = ctk.CTkFrame(frame_stats, fg_color=color,
                             corner_radius=12, width=150, height=80)
        card.pack(side="left", padx=10)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=titulo, font=("Arial", 11),
                     text_color="white").pack(pady=(12, 2))
        ctk.CTkLabel(card, text=valor, font=("Arial", 22, "bold"),
                     text_color="white").pack()

    ctk.CTkLabel(contenido_frame,
                 text="Selecciona un módulo del menú lateral",
                 font=("Arial", 13), text_color="gray").pack(pady=20)

# ─────────────────────────────────────
# MÓDULO PROSPECTOS
# ─────────────────────────────────────
def mostrar_prospectos():
    limpiar_contenido()

    ctk.CTkLabel(contenido_frame, text="🔍 Buscador de Prospectos",
                 font=("Arial", 24, "bold")).pack(pady=10)

    frame_busqueda = ctk.CTkFrame(contenido_frame)
    frame_busqueda.pack(fill="x", padx=20, pady=5)

    ctk.CTkLabel(frame_busqueda, text="Rubro:",
                 font=("Arial", 13)).grid(row=0, column=0, padx=15, pady=10)

    rubro_var = ctk.StringVar(value="constructoras")
    ctk.CTkOptionMenu(frame_busqueda,
                      values=["constructoras", "hoteles", "inmobiliarias",
                               "gasfiteres", "ferreterias", "clinicas",
                               "colegios", "restaurantes", "empresas", "todos"],
                      variable=rubro_var, width=180).grid(row=0, column=1, padx=10)

    ctk.CTkLabel(frame_busqueda, text="Ciudad:",
                 font=("Arial", 13)).grid(row=0, column=2, padx=15)

    ciudad_entry = ctk.CTkEntry(frame_busqueda, width=130,
                                 placeholder_text="Santiago")
    ciudad_entry.grid(row=0, column=3, padx=10)
    ciudad_entry.insert(0, "Santiago")

    mensaje = ctk.CTkLabel(contenido_frame, text="",
                            font=("Arial", 12), text_color="gray")
    mensaje.pack(pady=3)

    resultado_frame = ctk.CTkScrollableFrame(contenido_frame, height=380)
    resultado_frame.pack(fill="x", padx=20, pady=5)

    def buscar():
        rubro = rubro_var.get()
        ciudad = ciudad_entry.get().strip() or "Santiago"
        mensaje.configure(text="🔍 Buscando...", text_color="yellow")
        contenido_frame.update()

        for widget in resultado_frame.winfo_children():
            widget.destroy()

        from buscador_prospectos import buscar_prospectos
        resultados = buscar_prospectos(rubro, ciudad, cantidad=10)

        if isinstance(resultados, dict) and "error" in resultados:
            mensaje.configure(text=f"❌ Error: {resultados['error']}",
                              text_color="red")
            return

        # Filtrar solo con email O teléfono
        filtrados = [r for r in resultados
                     if r.get("email") or r.get("telefono")]

        if not filtrados:
            mensaje.configure(text="⚠️ No se encontraron prospectos con contacto.",
                              text_color="orange")
            return

        mensaje.configure(
            text=f"✅ {len(filtrados)} prospectos con datos de contacto encontrados",
            text_color="green")

        # Encabezado
        header = ctk.CTkFrame(resultado_frame, fg_color="#2a2d36")
        header.pack(fill="x", pady=2)
        for col, ancho in [("Empresa", 220), ("Teléfono", 130),
                            ("Email", 190), ("Acciones", 200)]:
            ctk.CTkLabel(header, text=col, font=("Arial", 11, "bold"),
                         width=ancho, anchor="w").pack(side="left", padx=5)

        for p in filtrados:
            fila = ctk.CTkFrame(resultado_frame, fg_color="#16213e",
                                corner_radius=6)
            fila.pack(fill="x", pady=2, padx=2)

            ctk.CTkLabel(fila, text=p["nombre"][:30],
                         font=("Arial", 11), width=220,
                         anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(fila, text=p.get("telefono", "")[:18],
                         font=("Arial", 11), width=130,
                         anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(fila, text=p.get("email", "")[:25],
                         font=("Arial", 10), width=190,
                         anchor="w").pack(side="left", padx=5)

            # Botones de acción
            frame_botones = ctk.CTkFrame(fila, fg_color="transparent")
            frame_botones.pack(side="left", padx=5)

            ctk.CTkButton(frame_botones, text="➕ Agregar",
                          width=80, height=25, font=("Arial", 10),
                          command=lambda pr=p: agregar_y_contactar(pr, mensaje)
                          ).pack(side="left", padx=2)

    ctk.CTkButton(frame_busqueda, text="🔍 Buscar",
                  height=38, font=("Arial", 13, "bold"),
                  command=buscar).grid(row=0, column=4, padx=15)

def agregar_y_contactar(prospecto, mensaje_label):
    pid = guardar_prospecto(
        prospecto["nombre"],
        prospecto.get("telefono", ""),
        prospecto.get("email", ""),
        prospecto.get("url", ""),
        prospecto.get("motivo", ""),
        "Nicolas Golott"
    )
    if pid:
        mensaje_label.configure(
            text=f"✅ '{prospecto['nombre']}' agregado a Cartera. Ve a Cartera para contactarlo.",
            text_color="green")
    else:
        mensaje_label.configure(
            text=f"⚠️ '{prospecto['nombre']}' ya existe en la Cartera.",
            text_color="orange")

# ─────────────────────────────────────
# MÓDULO CARTERA DE CLIENTES
# ─────────────────────────────────────
def mostrar_cartera():
    limpiar_contenido()

    ctk.CTkLabel(contenido_frame, text="👤 Cartera de Clientes — Nicolás Golott",
                 font=("Arial", 22, "bold")).pack(pady=10)

    # Filtros por estado
    frame_filtros = ctk.CTkFrame(contenido_frame, fg_color="transparent")
    frame_filtros.pack(fill="x", padx=20, pady=5)

    estados = [
        ("Todos", None),
        ("🟡 Nuevos", "nuevo"),
        ("📧 Contactados", "email_enviado"),
        ("📞 En llamada", "no_contesto"),
        ("🔥 Interesados", "interesado"),
        ("📄 Cotizados", "cotizacion_enviada"),
        ("🏆 Ganados", "ganado"),
    ]

    filtro_actual = [None]
    lista_frame = [None]

    def cargar_lista(estado=None):
        filtro_actual[0] = estado
        if lista_frame[0]:
            lista_frame[0].destroy()

        frame = ctk.CTkScrollableFrame(contenido_frame, height=430)
        frame.pack(fill="x", padx=20, pady=5)
        lista_frame[0] = frame

        prospectos = obtener_prospectos(estado)

        if not prospectos:
            ctk.CTkLabel(frame, text="No hay prospectos en este estado.",
                         text_color="gray", font=("Arial", 13)).pack(pady=20)
            return

        # Encabezado
        header = ctk.CTkFrame(frame, fg_color="#2a2d36")
        header.pack(fill="x", pady=2)
        for col, ancho in [("Empresa", 200), ("Teléfono", 120),
                            ("Email", 170), ("Estado", 130), ("Acciones", 250)]:
            ctk.CTkLabel(header, text=col, font=("Arial", 11, "bold"),
                         width=ancho, anchor="w").pack(side="left", padx=5)

        estados_labels = {
            "nuevo": "🟡 Nuevo",
            "email_enviado": "📧 Email enviado",
            "no_contesto": "📞 No contestó",
            "llamada_contestada": "📞 Contactado",
            "interesado": "🔥 Interesado",
            "cotizacion_enviada": "📄 Cotización",
            "ganado": "🏆 Ganado",
            "perdido": "❌ Perdido",
            "archivado": "📁 Archivado"
        }

        for p in prospectos:
            pid = p[0]
            nombre = p[1]
            telefono = p[2] or ""
            email = p[3] or ""
            estado_actual = p[7] or "nuevo"

            fila = ctk.CTkFrame(frame, fg_color="#16213e", corner_radius=6)
            fila.pack(fill="x", pady=2, padx=2)

            ctk.CTkLabel(fila, text=nombre[:25], font=("Arial", 11),
                         width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(fila, text=telefono[:15], font=("Arial", 10),
                         width=120, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(fila, text=email[:22], font=("Arial", 10),
                         width=170, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(fila, text=estados_labels.get(estado_actual, estado_actual),
                         font=("Arial", 10), width=130,
                         anchor="w").pack(side="left", padx=5)

            # Botones según estado
            frame_btn = ctk.CTkFrame(fila, fg_color="transparent")
            frame_btn.pack(side="left", padx=3)

            if estado_actual == "nuevo":
                ctk.CTkButton(frame_btn, text="📧 Enviar Email",
                              width=110, height=25, font=("Arial", 10),
                              fg_color="#1f6aa5",
                              command=lambda i=pid, e=email, n=nombre: enviar_email_prospecto(i, e, n, lambda: cargar_lista(filtro_actual[0]))
                              ).pack(side="left", padx=2)

            elif estado_actual in ("email_enviado", "no_contesto"):
                intentos = p[8] or 0
                ctk.CTkButton(frame_btn, text="✅ Contestó",
                              width=90, height=25, font=("Arial", 10),
                              fg_color="#2d8a4e",
                              command=lambda i=pid: [actualizar_estado_prospecto(i, "llamada_contestada"), cargar_lista(filtro_actual[0])]
                              ).pack(side="left", padx=2)
                if intentos < 4:
                    ctk.CTkButton(frame_btn, text="❌ No contestó",
                                  width=100, height=25, font=("Arial", 10),
                                  fg_color="#8a2d2d",
                                  command=lambda i=pid: [actualizar_estado_prospecto(i, "no_contesto"), cargar_lista(filtro_actual[0])]
                                  ).pack(side="left", padx=2)

            elif estado_actual == "llamada_contestada":
                ctk.CTkButton(frame_btn, text="🔥 Le interesa",
                              width=100, height=25, font=("Arial", 10),
                              fg_color="#8a4e2d",
                              command=lambda i=pid: [actualizar_estado_prospecto(i, "interesado"), cargar_lista(filtro_actual[0])]
                              ).pack(side="left", padx=2)
                ctk.CTkButton(frame_btn, text="❌ No interesa",
                              width=100, height=25, font=("Arial", 10),
                              fg_color="#4a4a4a",
                              command=lambda i=pid: [actualizar_estado_prospecto(i, "perdido"), cargar_lista(filtro_actual[0])]
                              ).pack(side="left", padx=2)

            elif estado_actual == "interesado":
                ctk.CTkButton(frame_btn, text="📄 Cotización importada",
                              width=150, height=25, font=("Arial", 10),
                              fg_color="#6b2d8a",
                              command=lambda i=pid, n=nombre: importar_cotizacion_prospecto(i, n, lambda: cargar_lista(filtro_actual[0]))
                              ).pack(side="left", padx=2)

            elif estado_actual == "cotizacion_enviada":
                ctk.CTkButton(frame_btn, text="🏆 Ganado",
                              width=80, height=25, font=("Arial", 10),
                              fg_color="#2d8a4e",
                              command=lambda i=pid: [actualizar_estado_prospecto(i, "ganado"), cargar_lista(filtro_actual[0])]
                              ).pack(side="left", padx=2)
                ctk.CTkButton(frame_btn, text="❌ Perdido",
                              width=80, height=25, font=("Arial", 10),
                              fg_color="#8a2d2d",
                              command=lambda i=pid: [actualizar_estado_prospecto(i, "perdido"), cargar_lista(filtro_actual[0])]
                              ).pack(side="left", padx=2)

    for label, estado in estados:
        ctk.CTkButton(frame_filtros, text=label,
                      width=90, height=28, font=("Arial", 11),
                      fg_color="#2a2d36", hover_color="#3a3d46",
                      command=lambda e=estado: cargar_lista(e)
                      ).pack(side="left", padx=3)

    cargar_lista()

def enviar_email_prospecto(prospecto_id, email, nombre, callback):
    if not email:
        return
    exito = abrir_outlook(email, nombre)
    if exito:
        actualizar_estado_prospecto(prospecto_id, "email_enviado")
        callback()

def importar_cotizacion_prospecto(prospecto_id, nombre_empresa, callback):
    ruta = filedialog.askopenfilename(
        title=f"Seleccionar cotización SAP para {nombre_empresa}",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if not ruta:
        return

    datos = leer_cotizacion_sap(ruta)
    nombre_archivo = os.path.basename(ruta)
    numero = datos.get("numero_cotizacion", "")
    total = datos.get("total", "")

    guardar_cotizacion_prospecto(prospecto_id, nombre_archivo, ruta, numero, total)
    actualizar_estado_prospecto(prospecto_id, "cotizacion_enviada")
    callback()

# ─────────────────────────────────────
# MÓDULO CLIENTES CRM
# ─────────────────────────────────────
def mostrar_clientes():
    limpiar_contenido()

    ctk.CTkLabel(contenido_frame, text="👥 Clientes CRM",
                 font=("Arial", 24, "bold")).pack(pady=10)

    form = ctk.CTkFrame(contenido_frame)
    form.pack(pady=5, padx=20, fill="x")

    campos = {}
    etiquetas = ["Nombre", "Empresa", "RUT", "Teléfono", "Correo"]

    for i, campo in enumerate(etiquetas):
        ctk.CTkLabel(form, text=campo, font=("Arial", 13)).grid(
            row=i, column=0, padx=15, pady=5, sticky="w")
        entry = ctk.CTkEntry(form, width=280,
                             placeholder_text=f"Ingresa {campo.lower()}")
        entry.grid(row=i, column=1, padx=15, pady=5)
        campos[campo] = entry

    ctk.CTkLabel(form, text="Origen", font=("Arial", 13)).grid(
        row=5, column=0, padx=15, pady=5, sticky="w")
    origen_var = ctk.StringVar(value="Sala")
    ctk.CTkOptionMenu(form, values=["Sala", "WhatsApp", "Instagram",
                                     "Constructora", "SAP", "Prospecto Web"],
                      variable=origen_var, width=280).grid(row=5, column=1, padx=15, pady=5)

    mensaje = ctk.CTkLabel(contenido_frame, text="", font=("Arial", 13))
    mensaje.pack(pady=3)

    lista_frame = ctk.CTkScrollableFrame(contenido_frame, height=200)
    lista_frame.pack(fill="x", padx=20, pady=5)

    def actualizar_lista():
        for widget in lista_frame.winfo_children():
            widget.destroy()
        for c in obtener_clientes():
            ctk.CTkLabel(lista_frame,
                         text=f"👤 {c[1]}  |  {c[2]}  |  {c[3]}  |  {c[6]}  |  {c[7]}",
                         font=("Arial", 11), anchor="w").pack(fill="x", padx=10, pady=2)

    def guardar():
        nombre = campos["Nombre"].get().strip()
        if not nombre:
            mensaje.configure(text="⚠️ El nombre es obligatorio.", text_color="orange")
            return
        guardar_cliente(nombre, campos["Empresa"].get(), campos["RUT"].get(),
                        campos["Teléfono"].get(), campos["Correo"].get(), origen_var.get())
        for e in campos.values():
            e.delete(0, "end")
        mensaje.configure(text="✅ Cliente guardado.", text_color="green")
        actualizar_lista()

    ctk.CTkButton(contenido_frame, text="💾 Guardar Cliente",
                  command=guardar, height=38,
                  font=("Arial", 13, "bold")).pack(pady=5)
    actualizar_lista()

# ─────────────────────────────────────
# MÓDULO COTIZACIONES SAP
# ─────────────────────────────────────
def mostrar_cotizaciones():
    limpiar_contenido()

    ctk.CTkLabel(contenido_frame, text="📄 Cotizaciones SAP",
                 font=("Arial", 24, "bold")).pack(pady=10)

    ctk.CTkButton(contenido_frame, text="📂 Importar PDF de SAP",
                  height=42, font=("Arial", 13, "bold"),
                  command=importar_pdf).pack(pady=8)

    global resultado_frame
    resultado_frame = ctk.CTkScrollableFrame(contenido_frame, height=440)
    resultado_frame.pack(fill="x", padx=20, pady=5)

    ctk.CTkLabel(resultado_frame,
                 text="Presiona 'Importar PDF de SAP' para comenzar.",
                 text_color="gray", font=("Arial", 13)).pack(pady=20)

def importar_pdf():
    ruta = filedialog.askopenfilename(
        title="Seleccionar cotización SAP",
        filetypes=[("Archivos PDF", "*.pdf")]
    )
    if not ruta:
        return

    datos = leer_cotizacion_sap(ruta)

    for widget in resultado_frame.winfo_children():
        widget.destroy()

    if "error" in datos:
        ctk.CTkLabel(resultado_frame,
                     text=f"❌ Error: {datos['error']}",
                     text_color="red").pack(pady=10)
        return

    ctk.CTkLabel(resultado_frame, text="✅ Cotización detectada",
                 font=("Arial", 14, "bold"), text_color="green").pack(pady=5)

    info = [
        ("N° Cotización", datos["numero_cotizacion"]),
        ("Fecha", datos["fecha"]),
        ("Cliente", datos["cliente"]),
        ("RUT", datos["rut"]),
        ("Código SAP", datos["codigo_sap"]),
        ("Ejecutivo", datos["ejecutivo"]),
        ("Total", datos["total"]),
    ]

    frame_info = ctk.CTkFrame(resultado_frame)
    frame_info.pack(fill="x", padx=10, pady=5)

    for i, (etiqueta, valor) in enumerate(info):
        ctk.CTkLabel(frame_info, text=f"{etiqueta}:",
                     font=("Arial", 12, "bold"), width=140,
                     anchor="w").grid(row=i, column=0, padx=15, pady=3, sticky="w")
        ctk.CTkLabel(frame_info, text=valor or "No detectado",
                     font=("Arial", 12),
                     text_color="white" if valor else "gray").grid(
                         row=i, column=1, padx=10, pady=3, sticky="w")

    if datos["productos"]:
        ctk.CTkLabel(resultado_frame, text="📦 Productos:",
                     font=("Arial", 12, "bold")).pack(pady=5)
        for p in datos["productos"]:
            texto = f"• {p['codigo']}  |  {p['nombre']}  |  Cant: {p['cantidad']}  |  {p['precio_unitario']}  |  {p['total']}"
            ctk.CTkLabel(resultado_frame, text=texto,
                         font=("Arial", 10), anchor="w",
                         wraplength=700).pack(fill="x", padx=15, pady=2)

    ctk.CTkButton(resultado_frame, text="💾 Guardar en base de datos",
                  font=("Arial", 12, "bold"),
                  command=lambda: guardar_desde_pdf(datos)).pack(pady=10)

def guardar_desde_pdf(datos):
    guardado = guardar_cotizacion(datos)
    if guardado:
        if datos.get("cliente"):
            guardar_cliente(datos["cliente"], "", datos.get("rut", ""),
                            "", datos.get("email_cliente", ""), "SAP")
        ctk.CTkLabel(resultado_frame,
                     text="✅ Cotización guardada correctamente.",
                     text_color="green", font=("Arial", 12)).pack(pady=5)
    else:
        ctk.CTkLabel(resultado_frame,
                     text="⚠️ Esta cotización ya estaba registrada.",
                     text_color="orange", font=("Arial", 12)).pack(pady=5)

# ─────────────────────────────────────
# MÓDULO DASHBOARD
# ─────────────────────────────────────
def mostrar_dashboard():
    limpiar_contenido()

    ctk.CTkLabel(contenido_frame, text="📊 Dashboard",
                 font=("Arial", 24, "bold")).pack(pady=10)

    stats = obtener_stats()

    frame_kpis = ctk.CTkFrame(contenido_frame, fg_color="transparent")
    frame_kpis.pack(fill="x", padx=20, pady=10)

    kpis = [
        ("📄 Cotizaciones", str(stats["cotizaciones"]), "#1f6aa5"),
        ("👥 Clientes", str(stats["clientes"]), "#2d8a4e"),
        ("🔍 Prospectos", str(stats["prospectos"]), "#8a4e2d"),
        ("🏆 Ganados", str(stats["ganados"]), "#6b2d8a"),
        ("💰 Monto Total", stats["monto_total"], "#2d6b8a"),
    ]

    for titulo, valor, color in kpis:
        card = ctk.CTkFrame(frame_kpis, fg_color=color,
                             corner_radius=12, width=160, height=90)
        card.pack(side="left", padx=8)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=titulo, font=("Arial", 11),
                     text_color="white").pack(pady=(12, 2))
        ctk.CTkLabel(card, text=valor, font=("Arial", 20, "bold"),
                     text_color="white").pack()

    ctk.CTkLabel(contenido_frame, text="📋 Últimas Cotizaciones",
                 font=("Arial", 14, "bold")).pack(pady=(15, 5))

    tabla = ctk.CTkScrollableFrame(contenido_frame, height=320)
    tabla.pack(fill="x", padx=20, pady=5)

    header = ctk.CTkFrame(tabla, fg_color="#2a2d36")
    header.pack(fill="x", pady=2)
    for col, ancho in [("N° Cotización", 120), ("Fecha", 100),
                        ("Cliente", 280), ("Total", 100), ("Importada", 140)]:
        ctk.CTkLabel(header, text=col, font=("Arial", 11, "bold"),
                     width=ancho, anchor="w").pack(side="left", padx=5)

    for cot in obtener_cotizaciones():
        fila = ctk.CTkFrame(tabla, fg_color="transparent")
        fila.pack(fill="x", pady=1)
        for valor, ancho in zip(cot, [120, 100, 280, 100, 140]):
            ctk.CTkLabel(fila, text=str(valor or ""),
                         font=("Arial", 11), width=ancho,
                         anchor="w").pack(side="left", padx=5)

    ctk.CTkButton(contenido_frame, text="🔄 Actualizar",
                  command=mostrar_dashboard,
                  font=("Arial", 12)).pack(pady=8)

# ─────────────────────────────────────
# MENÚ LATERAL
# ─────────────────────────────────────
modulos = [
    ("🏠  Inicio",          mostrar_inicio),
    ("🔍  Prospectos",      mostrar_prospectos),
    ("👤  Cartera",         mostrar_cartera),
    ("👥  Clientes CRM",    mostrar_clientes),
    ("📄  Cotizaciones",    mostrar_cotizaciones),
    ("📊  Dashboard",       mostrar_dashboard),
]

for nombre, comando in modulos:
    ctk.CTkButton(panel_izquierdo, text=nombre, anchor="w",
                  height=45, font=("Arial", 13),
                  fg_color="transparent", hover_color="#2a2d36",
                  command=comando).pack(fill="x", padx=10, pady=3)

ctk.CTkLabel(panel_izquierdo,
             text="👤 Nicolás Golott\nJefe de Tienda",
             font=("Arial", 11), text_color="gray").pack(side="bottom", pady=20)

mostrar_inicio()
ventana.mainloop()