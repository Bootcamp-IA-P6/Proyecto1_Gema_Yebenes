import tkinter as tk               # Librería estándar de Python para crear interfaces gráficas
from tkinter import messagebox     # Para mostrar mensajes tipo popup
import json
import os
from oop_taximeter import Taximeter  # Importamos la clase


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config_prices.json")

def load_all_prices():
    """
    Carga TODO el archivo JSON de tarifas.
    No pide nada por consola, solo lee el fichero.
    Devuelve un diccionario con todos los modos de tarifa.
    """
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Si no encontramos el archivo, mostramos un error y cerramos la app
        messagebox.showerror("Error", "No se encontró config_precios.json")
        # exit() cierra el programa
        exit()
        
try:
    all_prices = load_all_prices()
    print("Prices loaded:", all_prices)
except Exception as e:
    messagebox.showerror("ERROR", f"Error loading prices:\n{e}")
    exit()


# Creamos la ventana principal
root = tk.Tk()
#si se ponen los titulos
root.title("🚕 Taxímetro - GUI")
# tamaño inicial de la ventana
root.geometry("450x550")


#VARIABLES GLOBALES DE TKINTER
#selected_mode guardará el modo elegido en los Radiobuttons (normal, night, etc.)
selected_mode = tk.StringVar()

# taximeter será nuestro objeto Taximeter, pero empezamos sin crear ninguno
taximeter = None   # Hasta que el usuario elija una tarifa, esto vale None (nada)


#  ETIQUETAS (LABELS) - SE CREAN ANTES DE LAS FUNCIONES
title = tk.Label(root, text="🚕 TAXÍMETRO", font=("Arial", 50, "bold"), bg="yellow")
title.pack(pady=10)
# Aquí mostraremos qué tarifa está seleccionada
label_mode= tk.Label(root, text="Tarifa no selecionada", font=("Arial", 10))
title.pack(pady=10)

label_state = tk.Label(root, text="Estado: SIN VIAJE", font=("Arial", 30))
label_state.pack(pady=5)

label_info = tk.Label(root, text="", font=("Arial", 10))
label_info.pack(pady=5)


# FUNCIONES QUE VAN A LOS BOTONES
btn_start = None
btn_stop = None
btn_move = None
btn_finish = None


def select_pricing_mode():
    """
    Función que se ejecuta cuando pulsamos el botón "Confirmar tarifa".
    - Lee el modo seleccionado (normal, night, etc.)
    - Crea un objeto Taximeter con los precios de ese modo
    - Activa los botones de START/STOP/MOVE/FINISH
    """
    
    global taximeter  # Indicamos que vamos a modificar la variable global taximeter
    
    mode = selected_mode.get()  # Obtenemos el texto de la tarifa elegida
    
    if not mode:
        # Si no se ha elegido nada, avisamos al usuario
        messagebox.showwarning("Atención", "Elige un modo de tarifa primero")
        return
    # Obtenemos las tarifas de ese modo del diccionario all_prices
    prices= all_prices[mode]
    # Creamos el objeto Taximeter con esas tarifas
    taximeter = Taximeter(prices)
       
     # Actualizamos los textos de la interfaz
    label_mode.config(text=f"Tarifa Selecionada: {mode.upper()}")
    label_state.config(text="Estado: SIN VIAJE")
    label_info.config(text="Tarifa cargada")
    
    # Activamos los botones del viaje, ahora que ya tenemos taximeter
    btn_start.config(state=tk.NORMAL)
    btn_stop.config(state=tk.NORMAL)
    btn_move.config(state=tk.NORMAL)
    btn_finish.config(state=tk.NORMAL)


def start_trip():
    try:
        taximeter.start_trip()
        label_state.config(text="Estado: STOPPED")
        label_info.config(text="Viaje iniciado")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        
def stop_trip():
    """Cambia el estado a parado."""
    try:
        taximeter.change_state("stopped")
        label_state.config(text="Estado: STOPPED")
        label_info.config(text="Taxi Parado")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        
def move_trip():
    """Cambia el estado a parado."""
    try:
        taximeter.change_state("moving")
        label_state.config(text= "Estado: MOVING")
        label_info.config(text= "Taxi en Movimiento")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        
def finish_trip():
    """Termina el viaje y muestra un resumen."""
    try:
        summary= taximeter.finish_trip()
        
        stopped = summary["stopped_time"]
        moving = summary["moving_time"]
        total = summary["total_fare"]
        
        messagebox.showinfo(
            "Resumen de su Viaje",
            f"Parado:{stopped:.1f}s\n"
            f"En movimiento:{moving: .1f}s\n\n"
            f"Total Viaje:{total: .2f}"    
        )
        
        label_state.config(text="Estado: SIN VIAJE")
        label_info.config(text="Viaje finalizado")
    
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        
    
#  SELECTOR DE TARIFA (RADIObuttons)
frame_mode= tk.LabelFrame(
    root,
    text="Elige Tarifa",
    padx=50,     # espacio interno horizontal
    pady=40,     # espacio interno vertical
    font=("Arial", 20, "bold"))
frame_mode.pack(pady=10)
    
    # Creamos un radiobutton por cada modo de tarifa del JSON
for mode in all_prices:
        tk.Radiobutton(
            frame_mode,
            text=mode, # lo que se ve (normal, night, high_demand)
            variable=selected_mode, # variable compartida declarada arriba
            value=mode,  # valor que toma selected_mode cuando se selecciona este botón
            font=("Arial", 20),
            padx=10,
            pady=4,
        ).pack(anchor="w")
        
        #Botón para confirmar la tarifa elegida
btn_select= tk.Button(
    root, 
    text="Confirmar Tarifa",
    width=20,
    height=2,
    font=("Arial", 15 , "bold" ),  
    command=select_pricing_mode,
    )
btn_select.pack(pady=5)
        
       
btn_start = tk.Button(
    root, 
    text="START", 
    width=20,
    height=2,
    font=("Arial", 15 , "bold" ), 
    command=start_trip,
    bg="green", 
    fg="white",
    state=tk.DISABLED)
btn_start.pack(pady=5)

btn_move = tk.Button(
    root, 
    text="MOVE", 
    width=20,
    height=2,
    font=("Arial", 15 , "bold" ), 
    command=move_trip, 
    bg="yellow", 
    fg="white",
    state=tk.DISABLED)
btn_move.pack(pady=5)

btn_stop = tk.Button(
    root, 
    text="STOP", 
    width=20,
    height=2,
    font=("Arial", 15 , "bold" ), 
    command=stop_trip, 
    bg="red", 
    fg="white",
    state=tk.DISABLED)
btn_stop.pack(pady=5)

btn_finish = tk.Button(root, text="FINISH", width=15, command=finish_trip, bg="lightblue", state=tk.DISABLED)
btn_finish.pack(pady=5)
    


    #INICIAR EL BUCLE DE LA VENTANA
root.mainloop()
        
