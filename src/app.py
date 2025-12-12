import streamlit as st
import time                        # mide tiempos
import json                        # lee el json de la tarifa
import os                          # constuye rutas
from oop_taximeter import Taximeter # mi archivo con la logica
import pandas as pd
import textwrap


def generar_ticket_html(modo, parado, marcha, total):
    """Genera el código HTML del ticket."""
    fecha = time.strftime("%d/%m/%Y")
    hora = time.strftime("%H:%M")
    
    
    html = f"""
    <div style="background-color: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); font-family: 'Courier New', monospace; color: #333; max-width: 450px; margin: 30px auto;">
        <div style="text-align: center;">
            <h2 style="margin: 0; color: #000;">🚖 TAXI F5</h2>
            <p style="font-size: 12px; color: #666; margin: 5px 0;">Servicio Oficial</p>
            <hr style="border-top: 2px dashed #bbb; margin: 10px 0;">
        </div>
        <p style="margin: 5px 0;"><strong>📅 Fecha:</strong> {fecha}</p>
        <p style="margin: 5px 0;"><strong>🕒 Hora:</strong> {hora}</p>
        <p style="margin: 5px 0;"><strong>🏷️ Tarifa:</strong> {modo.upper()}</p>
        <hr style="border-top: 1px solid #eee; margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>Tiempo Parado:</span> <span>{parado:.1f} s</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>Tiempo Marcha:</span> <span>{marcha:.1f} s</span>
        </div>
        <hr style="border-top: 2px dashed #bbb; margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 18px; font-weight: bold;">TOTAL:</span>
            <span style="font-size: 24px; font-weight: bold; color: #000;">€ {total:.2f}</span>
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <p style="font-size: 12px; margin: 0;">¡Gracias por su visita!</p>
        </div>
    </div>
    """
    return html

# --- CONFIGURACIÓN DE PÁGINA ---
# st.set_page_config configura la pestaña del navegador antes de dibujar nada.
st.set_page_config(
    page_title="Taxímetro Profesional", # Título en la pestaña del navegador
    page_icon="🚖",                     # Icono en la pestaña
    layout="centered"                   # "centered" centra todo en una columna bonita (antes ocupaba todo el ancho y se veía desparramado)
)
LOGO_PATH = "src/assets/logo_taxi3.png"

def load_all_prices():
    """
    Lee el archivo JSON de tarifas y devuelve un diccionario.
    """
    # Ruta del archivo JSON: subimos un nivel desde src/ hasta la raíz y buscamos config_precios.json
    config_path = os.path.join(os.path.dirname(__file__), "..", "config_prices.json")
    try: 
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: No encuentro el archivo config_prices.json")
        st.stop() # Si falla, paramos la app para que no dé errores raros después
        
       
 # Inicializar variables en session_state (memoria de la sesión)
if "taximeter" not in st.session_state:
        st.session_state.taximeter = None  # se guarda el objeto taximeter
        st.session_state.mode = None # se guarda el modo de la tarifa (normal,night etc.
        st.session_state.is_running = False # hay un viaje en marcha empieza en False
        st.session_state.status = "Sin Iniciar" # Texto del estado actual
        st.session_state.ticket_html = None # memoria para el tikect
# El selector de tarifa a la izquierda (sidebar).
with st.sidebar:
    st.header("Elige Tarifa")
    # --- Cargar datos ---
    all_prices = load_all_prices()
    modes = list(all_prices.keys())
    
    st.write("---") # Una línea separadora
    
    selected_mode = st.selectbox("Tarifa:", modes)
    
    # Usamos 'expander' para que la tabla se pueda ocultar y no moleste.
    with st.expander("Ver precios (€/s)"):
        # Mostramos el diccionario de precios en una tabla bonita
        st.table(all_prices[selected_mode])
    
    # --- Botón de Cargar ---
    # 'use_container_width=True' hace que el botón ocupe todo el ancho.
    if st.button("🔄 Cargar Tarifa", use_container_width=True):
        # creamos el objeto con los precios elegidos
        selected_prices = all_prices[selected_mode]
        st.session_state.taximeter = Taximeter(selected_prices)
        st.session_state.mode = selected_mode
        
        # Reseteamos estados
        st.session_state.is_running = False
        st.session_state.status = "✅ Lista para iniciar"
        
        # 'toast' saca un mensajito flotante temporal en la esquina
        st.toast(f"¡Tarifa {selected_mode} cargada!", icon="🚕")
        
#Creamos columnas para centrar la imagen
#El '3' y '1' son proporciones. Las columnas 1 y 3 tendrán 1 partes de espacio,
# y la columna 2 tendrá 3 parte donde se centra el contenido.
col1, col2, col3 = st.columns([1, 3, 1])
# Título principal
with col2:
    st.image(LOGO_PATH, width=300)
# Mostramos el estado actual en texto pequeño (Markdown)
st.markdown(f"**Estado actual:** `{st.session_state.status}`")

st.divider() # Una línea gris elegante para separar

# --- LÓGICA DE VISUALIZACIÓN EN TIEMPO REAL ---
# Los segundos correr en pantalla.
# Así que calculamos el tiempo "extra" que ha pasado desde el último cambio de estado.
# Muestra el estado actual

taxi = st.session_state.taximeter

# Variables para mostrar en pantalla (empiezan en 0)
display_stopped = 0.0
display_moving = 0.0
display_total = 0.0

if taxi is not None:
    # 1. Cogemos lo que ya tiene guardado el taxímetro
    display_stopped = taxi.stopped_time
    display_moving = taxi.moving_time
    # 2. Si está corriendo, sumamos el tiempo que ha pasado "ahora mismo"
    if st.session_state.is_running and taxi.state is not None:
        tiempo_ahora = time.time()
        # Tiempo transcurrido = Ahora - Cuando empezó el estado
        duracion_extra = tiempo_ahora - taxi.state_start_time
        
        if taxi.state == "stopped":
            display_stopped += duracion_extra
        elif taxi.state == "moving":
            display_moving += duracion_extra
    # 3. Calculamos el precio total para mostrarlo
    precio_parado = display_stopped * taxi.stopped_price
    precio_marcha = display_moving * taxi.moving_price
    display_total = precio_parado + precio_marcha
    

# Usamos st.metric. Son tarjetas con números grandes.
# Dividimos la pantalla en 3 columnas.
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

col_kpi1.metric(
    label="⏱️ Tiempo Parado", 
    value=f"{display_stopped:.1f} s", # .1f significa "1 decimal"
    delta="Tarifa Stop" if taxi and taxi.state == "stopped" else None
)

col_kpi2.metric(
    label="🚕 Tiempo Marcha", 
    value=f"{display_moving:.1f} s",
    delta="Tarifa Move" if taxi and taxi.state == "moving" else None,
    delta_color="inverse" # Pone la flechita en otro color
)

col_kpi3.metric(
    label="💶 PRECIO TOTAL", 
    value=f"€ {display_total:.2f}" # .2f para 2 decimales (euros)
)

st.divider()

# -----------------------------------------------------------------------------
#  PANEL DE CONTROL (BOTONES)
# Usamos 4 columnas para poner los botones en fila horizontal.
# -----------------------------------------------------------------------------
st.subheader("Panel de Control")

b1, b2, b3, b4 = st.columns(4)

with b1:
    if st.button("▶️ INICIAR", use_container_width=True):
        if st.session_state.taximeter is None:
            st.error("¡Primero carga una tarifa en la izquierda!")
        else:
            try:
                st.session_state.taximeter.start_trip()
                st.session_state.is_running = True
                st.session_state.status = "🟢 En espera (Parado)"
                st.session_state.ticket_html = None # (Borra ticket anterior)
                st.rerun() # Recargamos página para ver cambios al instante
            except ValueError as e:
                st.error(str(e))

with b2:
    if st.button("💨 MARCHA", use_container_width=True):
        taxi = st.session_state.taximeter
        # Solo dejamos pulsar si el taxi existe y está corriendo
        if taxi and st.session_state.is_running:
            taxi.change_state("moving")
            st.session_state.status = "🚕 En movimiento..."
            st.rerun()

with b3:
    if st.button("🛑 PARAR", use_container_width=True):
        taxi = st.session_state.taximeter
        if taxi and st.session_state.is_running:
            taxi.change_state("stopped")
            st.session_state.status = "🔴 Detenido (Semáforo)"
            st.rerun()

with b4:
    # type="primary" pone el botón rojo para destacar que es el final
    if st.button("🏁 FINALIZAR", type="primary", use_container_width=True):
        taxi = st.session_state.taximeter
        if taxi and st.session_state.is_running:
            resumen = taxi.finish_trip()
            st.session_state.is_running = False
            st.session_state.status = "🏁 Viaje terminado"
            
            # --- Animación y Resultado ---
            st.balloons() # ¡Globos!
            
            # --- Generar y Mostrar Ticket ---
            # Llamamos a la función que hemos creado arriba
            html_code = generar_ticket_html(
                st.session_state.mode, 
                resumen['stopped_time'], 
                resumen['moving_time'], 
                resumen['total_fare']
            )
            
            st.session_state.ticket_html = html_code
# Pintamos el tikect           
if st.session_state.ticket_html:
    st.markdown(st.session_state.ticket_html, unsafe_allow_html=True)
            
           ##REFRESCO AUTOMÁTICO 
# Esto es lo que hace que los números se muevan solos.
# Si el taxi está encendido, esperamos medio segundo y recargamos la página.
# -----------------------------------------------------------------------------
if st.session_state.is_running:
    time.sleep(0.5)
    st.rerun()
