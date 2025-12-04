import json
import os
from rich import print
from rich.panel import Panel

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "config_prices.json")

def load_prices():

    """
    Carga las tarifas desde el archivo de configuración y permite seleccionar un modo de precio.
    Devuelve un diccionario con dos claves: 'stopped' y 'moving', que indican el coste por segundo.
    """
    try:
        print("Buscando archivo en:", CONFIG_FILE)

        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            
            prices = json.load(file)# declaramos la variable prices y con esa funcion lo convierte en un diccionario
            
    except FileNotFoundError:
        print(Panel("[bold red]No se encontró el archivo config_precios.json[/bold red]", title="ERROR"))
        exit()
    
    #Se meuestran los modos disponibles
    print(Panel("[bold cyan]Modos de tarifa disponibles:[/bold cyan]", title="CONFIGURACIÓN"))
    for mode in prices:
        print(f"[yellow]{mode}[/yellow]")
    
    selected_mode = input("Choose pricing mode: ").strip()
    
    if selected_mode not in prices:
        print(Panel("[bold red]Modo de tarifa no válido[/bold red]", title="ERROR"))
        exit()
        
    print(Panel(
        f"[green]Modo seleccionado:[/green] [bold]{selected_mode}[/bold]",
        title="OK",
        border_style="green"
    ))
        
    return prices[selected_mode]