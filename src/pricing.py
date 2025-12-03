import json
import os
from rich import print
from rich.panel import Panel

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config_precios.json")

def load_prices():

    """
    Carga las tarifas desde el archivo de configuración y permite seleccionar un modo de precio.
    Devuelve un diccionario con dos claves: 'stopped' y 'moving', que indican el coste por segundo.
    """
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            
            prices = json.load(file)# declaramos la variable prices y con esa funcion lo convierte en un diccionario
            
    except FileNotFoundError:
        print("❌ config_precios.json not found.")
        exit()
        
    print("\nAvailable pricing modes:")
    for mode in prices:
        print(f"- {mode}")
    
    selected_mode = input("Choose pricing mode: ").strip()
    
    if selected_mode not in prices:
        print("❌ Invalid pricing mode.")
        exit()
        
    return prices[selected_mode]