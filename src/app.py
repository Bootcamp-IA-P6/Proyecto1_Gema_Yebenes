import streamlit as st
import time                        # mide tiempos
import json                        # lee el json de la tarifa
import os                          # constuye rutas
from oop_taximeter import Taximeter # mi archivo con la logica

def load_all_prices():
    """
    Lee el archivo JSON de tarifas y devuelve un diccionario.
    """
    # Ruta del archivo JSON: subimos un nivel desde src/ hasta la raíz y buscamos config_precios.json
    config_path = os.path.join(os.path.dirname(__file__), "..", "config_prices.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
    #  Configuración de la página Streamlit
st.set_page_config(page_title= "F5 Taximeter", page_icon="🚕")
    
st.title("🚕 F5 TAXIMETER")
st.write("Simulador de taxímetro en tiempo real con selección de tarifa.")
    
# Cargamos las tarifas
all_prices = load_all_prices()
modes = (all_prices.keys())
    
 # Inicializar variables en session_state (memoria de la sesión)
if "taximeter" not in st.session_state:
        st.session_state.taximeter = None  # se guarda el objeto taximeter
        st.session_state.mode = None # se guarda el modo de la tarifa (normal,night etc.
        st.session_state.is_running = False # hay un viaje en marcha empieza en False
        st.session_state.status = "Sin Iniciar" # Texto del estado actual
   
# selector de tarifa 
st.subheader ("Selecione la Tarifa")
    
selected_mode = st.selectbox("Tarifa:", modes)
    
if st.button("Usar esta tarifa"):
        # Cargamos los precios del modo elegido
        selected_prices = all_prices[selected_mode]
        # Creamos un nuevo taxímetro con esas tarifas
        st.session_state.taximeter = Taximeter(selected_prices)
        st.session_state.mode = selected_mode
        st.session_state.is_running = False
        st.session_state.status = f"Tarifa '{selected_mode}' cargada. Pulsa INICIAR"
        st.success(f"Tarifa '{selected_mode}' seleccionada correctamente")
# Muestra el estado actual
st.subheader("Estado del viaje")
st.info(f"Estado actual: {st.session_state.status}")
    
# Botones de control del viaje
st.subheader("Controles")
col1, col2, col3, col4 = st.columns(4)
    
# Boton INICIAR
with col1:
        if st.button("INICIAR"):
            if st.session_state.taximeter is None:
                st.warning("Primero selecciona y confirma una tarifa.")
            else:
                try:
                    st.session_state.taximeter.start_trip()
                    st.session_state.is_running = True
                    st.session_state.state = "PARADO (viaje iniciado)"
                except ValueError as e:
                    st.error(str(e))

# Boton Move o GO
with col2:
        if st.button("GO"):
            taxi = st.session_state.taximeter
            if taxi is None or not st.session_state.is_running:
                st.warning("No hay un viaje activo.")
            else:
                try:
                    taxi.change_state("moving")
                    st.session_state.status = "EN MARCHA"
                except ValueError as e:
                    st.error(str(e))
                    
# Boton STOP
with col3:
        if st.button("PARAR"):
            taxi = st.session_state.taximeter
            if taxi is None or not st.session_state.is_running:
                st.warning("No hay un viaje activo.")
            else:
                try:
                    taxi.change_state("stopped")        
                    st.session_state.status = "PARADO"
                except ValueError as e:
                    st.error(str(e))
# Boton FINISH
with col4:
        if st.button("FINALIZAR"):
            taxi = st.session_state.taximeter
            if taxi is None or not st.session_state.is_running:
                st.warning("No hay un viaje activo para finalizar.")
            else:
                try:
                    summary = taxi.finish_trip()
                    st.session_state.is_running = False
                    st.session_state.status = "FINALIZADO"
                    
                    st.success(f"Total del viaje: €{summary['total_fare']:.2f}")
                    st.write("Resumen del Viaje")
                    st.json(
                    
                            {
                             "Tiempo parado (s):" :round(summary["stopped_time"], 1),
                             "Tiempo en marcha (s):" :round(summary["moving_time"], 1),
                             "Total (€):" :round(summary ["total_fare"], 2),
                             "Tarifa:" : st.session_state.mode,
                             }
                    )
                except ValueError as e:
                   st.error(str(e))
#  Mostrar tiempos acumulados en pantalla
st.subheader("Tiempos del viaje")
taxi = st.session_state.taximeter
    
if taxi is None:
        st.write("Todavía no has iniciado ningún viaje.")
        st.stop()   #  Detiene la ejecución si no hay tarifa elegida
        # Calculamos tiempos "actuales" para mostrar (sin modificar el objeto)
stopped = taxi.stopped_time
moving = taxi.moving_time

if st.session_state.is_running and taxi.state is not None:
        now = time.time()
        # Sumamos el tiempo desde que empezó el estado actual solo para mostrar
        if taxi.state == "stopped":
            stopped += now -taxi.state_start_time
        elif taxi.state == "moving":
            moving += now - taxi.state_start_time
    
st.write(f"⏸ Tiempo parado: {stopped:.1f} segundos")
st.write(f"🚕 Tiempo en movimiento: {moving:.1f} segundos")