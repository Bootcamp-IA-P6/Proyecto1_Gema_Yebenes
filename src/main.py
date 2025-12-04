import time
import logging
import os
from datetime import datetime
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from pricing import load_prices # funcion del archivo princing para elegir tarifa

console = Console()
TRIPS_HISTORY_FILE = os.path.join("data", "trips_history.txt")

# Configuración básica de logging
logging.basicConfig (
    level= logging.INFO, #esto es el nivel minimo que se registrara (INFO.WARNING,ERRORES ...)
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename= "logs/taximeter.log",
    filemode="a",
)

def calculate_fare(seconds_stopped, seconds_moving, prices):
    """
    Calcular la tarifa total en euros, segun los precios que hay en mi json
    nornal
    - Stopped: 0.02 €/s
    - Moving: 0.05 €/s
    night
      - Stopped: 0.03 €/s
     - Moving: 0.06 €/s . etc
    """
    #declaro dos variables
    stopped_price = prices["stopped"]
    moving_price = prices["moving"]
    
    fare = seconds_stopped * stopped_price + seconds_moving * moving_price
    
    # print(f"Este es el total: {fare}")
    print(f":euro: [bold green]Total so far: €{fare:.2f}[/bold green]")

    return fare

def save_trip_hstory(stopped_time, moving_time, total_fare ):
    """
    Guarda un registro del viaje en un archivo de texto plano.
    Cada línea representa un viaje.
    """
    timestamp =datetime.now().strftime("%Y-%m-%d %H:%M:%S")#fecha y hora con texto bonito
    
    line = (
        f"{timestamp} | "
        f"stopped={stopped_time:.1f}s  | "
        f"moving={moving_time: .1f}s | " 
        f"total={total_fare: .2f}\n | "
        
    )
    
    with open(TRIPS_HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(line)

def taximeter():
    """
    Función para manejar y mostrar las opciones del taxímetro.
    """
    logging.info("Taximeter program started")
    
    prices = load_prices()
    
    print(Panel("Welcome to the F5 TAXIMETER", title="🚕 TAXIMETER", border_style="yellow"))
    print("[bold cyan]Commands:[/bold cyan]")
    print(":play_button: [green]start[/green]")
    print(":pause_button: [blue]stop[/blue]")
    print(":taxi: [yellow]move[/yellow]")
    print(":check_mark: [green]finish[/green]")
    print(":cross_mark: [red]exit[/red]\n")
    
   
    
    trip_active = False
    start_time = 0
    stopped_time = 0
    moving_time = 0
    state = None  # 'stopped' o 'moving'
    state_start_time = 0

    while True:
        command = input("> ").strip().lower()

        if command == "start":
            if trip_active:
                print("warning: [bold red] Trip is already in progress! [bold red]")
                logging.warning("User tried to start a trip, but a trip is already active")
                continue
            trip_active = True
            start_time = time.time()
            stopped_time = 0
            moving_time = 0
            state = 'stopped'  # Iniciamos en estado 'stopped'
            state_start_time = time.time()
            print(":play_button: [bold green]Trip started![/bold green]")
            print(":pause_button: [cyan]Initial state: STOPPED[/cyan]")


        elif command in ("stop", "move"):
            if not trip_active:
                print(":x: [bold red]No active trip. Use START first![/bold red]")
                logging.warning(f"Command '{command}' used without active trip")
                continue
            # Calcula el tiempo del estado anterior
            duration = time.time() - state_start_time
            if state == 'stopped':
                stopped_time += duration
            else:
                moving_time += duration

            # Cambia el estado
            previous_state = state
            state = 'stopped' if command == "stop" else 'moving'
            state_start_time = time.time()
            
            logging.info(f"State changed from {previous_state} to {state} (duration of previous state: {duration:.1f} seconds)")
            
            if state == "moving":
              print(":taxi: [yellow]Taxi is MOVING[/yellow]")
            else:
              print(":pause_button: [cyan]Taxi is STOPPED[/cyan]")

        elif command == "finish":
            if not trip_active:
                print(":warning: [bold red]No trip to finish[/bold red]")
                logging.warning("User tried to finish a trip, but no active trip")
                continue
            # Agrega tiempo del último estado
            duration = time.time() - state_start_time
            if state == 'stopped':
                stopped_time += duration
            else:
                moving_time += duration

            # Calcula la tarifa total y muestra el resumen del viaje
            total_fare = calculate_fare(stopped_time, moving_time, prices)
            logging.info(
             f"Trip finished. Stopped: {stopped_time:.1f}s, Moving: {moving_time:.1f}s, Total fare: €{total_fare:.2f}" )
            #guardamos el viaje en el historico llamamos a la funcion que hemos echo antes
            save_trip_hstory(stopped_time, moving_time,total_fare)

            table = Table(title="🚕 Trip Summary", show_header=True, header_style="bold magenta")
            table.add_column("State", style="cyan")
            table.add_column("Time (seconds)", justify="right")
            table.add_column("Cost (€)", justify="right", style="green")
            
            table.add_row("Stopped", f"{stopped_time:.1f}", f"{stopped_time * prices["stopped"]:.2f}")
            table.add_row("Moving", f"{moving_time:.1f}", f"{moving_time * prices["moving"]:.2f}")
            table.add_row("TOTAL", "", f"{total_fare:.2f}")

            console.print(table)

            print(":check_mark: [bold green]Trip finished successfully![/bold green]\n")


            # Reset las variables para el próximo viaje
            trip_active = False
            state = None

        elif command == "exit":
            logging.info("User exited the program")
            print("Exiting the program. Goodbye!")
            break

        else:
            print(":question: [yellow]Unknown command[/yellow] → use start, stop, move, finish or exit.")
            logging.warning(f"Unknown command received: '{command}'")


if __name__ == "__main__":
    taximeter()