import time                      
from pricing import load_prices   # Importamos la función que carga las tarifas desde config_precios.json



class Taximeter:
    """
    Clase que representa un taxímetro.
    Aquí guardamos el estado del viaje (tiempos, modo, precios)
    y definimos las acciones que puede hacer (empezar, cambiar estado, terminar).
    """
    def __init__(self, prices: dict):
         """
        El constructor de la clase.
        Se ejecuta cuando hacemos Taximeter(prices).
        :param prices: diccionario con las tarifas del modo elegido.
                       Ejemplo: {"stopped": 0.02, "moving": 0.05}
        """
         # Guardamos el diccionario de precios dentro del objeto
      
         self.prices = prices
         # Extraemos los precios concretos para mayor comodidad
         self.stopped_price = prices["stopped"]# precio por segundo parado
         self.moving_price = prices["moving"] # precio por segundo en moviemiento
         # Estado inicial del taxímetro (sin viaje activo)
         self.trip_active = False  # ¿Hay un viaje en marcha? empieza en false 
         self.state= None # el estado empieza en nada para luego poner "stopped", "moving"
         self.state_start_time = None    # Momento en el que empezó el estado actual
         # Tiempos acumulados en segundos
         self.stopped_time = 0.0  # Total de tiempo parado
         self.moving_time = 0.0    # Total de tiempo en movimiento empizan siemore en 0
         
    def start_trip (self):
        """
        Inicia un nuevo viaje.
        Reinicia tiempos y pone el estado en 'stopped'.
        """
        if self.trip_active:
            # Si ya hay un viaje activo, no dejamos empezar otro
            raise ValueError("Trip already active")
        
        self.trip_active = True # marcamos un viaje activo
        self.stopped_time = 0.0 # reiniciamos el tiempo parado
        self.moving_time = 0.0 # reiniciamos el tiempo en movimiento
        self.state = "stopped" # estado comenzamos en parado
        self.state_start_time = time.time() # # Guardamos el momento de inicio del estado
        
        
    def _update_current_state_time(self):
        """
        Método interno (empieza con _) para actualizar el tiempo
        del estado actual ('stopped' o 'moving').

        Calcula cuánto tiempo ha pasado desde state_start_time
        y lo suma al contador correspondiente.
        """
        if not self.trip_active or self.state is None:
            # Si no hay viaje activo o no hay estado, no hacemos nada no seguimos para  guardar nada en duration
            return
         # Calculamos cuánto tiempo ha pasado desde que entramos en este estado
        duration = time.time() - self.state_start_time
        # Sumamos ese tiempo al acumulador correspondiente
        if self.state == "stopped":
            self.stopped_time += duration 
        else:
            self.moving_time += duration
    
    def change_state(self, new_state: str):
        """
        Cambia el estado del taxímetro a 'stopped' o 'moving'.

        :param new_state: cadena con el nuevo estado ('stopped' o 'moving')
        """
        if not self.trip_active:
            # No se puede cambiar de estado si no hay viaje activo
            raise ValueError("No active trip")
        
        if new_state not in ("stopped", "moving"):
            # Validamos que el nuevo estado sea correcto
            raise ValueError("Invalid state")
       
        # Antes de cambiar de estado, actualizamos el tiempo del estado anterior
        self._update_current_state_time()
        
        self.state = new_state #cambiamos al nuevo estado
        # Guardamos el instante en el que empieza este nuevo estado
        self.state_start_time = time.time()

    def finish_trip(self):
        """
        Termina el viaje actual.

        - Actualiza el último tramo de tiempo según el estado actual.
        - Calcula la tarifa total.
        - Marca el viaje como no activo.
        - Devuelve un diccionario con el resumen.
        """
        if not self.trip_active:
          # No se puede terminar un viaje que no existe
            raise ValueError("No active trip to finish")
        
        # Actualizamos el tiempo del último estado
        self._update_current_state_time()
        # Calculamos la tarifa total usando los tiempos acumulados y las tarifas
        total_fare = self.calculate_fare()
         # Guardamos el resumen en un diccionario para devolverlo
        summary = {
            "stopped_time": self.stopped_time,
            "moving_time": self.moving_time,
            "total_fare": total_fare
            
        }
        # Marcamos que ya no hay viaje activo
        self.trip_active = False
        self.state = None
        self.state_start_time = None
        
        # retornamos el resumen del viaje
        return summary
    
    def calculate_fare(self) -> float:
        """
        Calcula el precio total del viaje usando:
        - tiempo parado * tarifa parada
        - tiempo en movimiento * tarifa movimiento
        """
        fare = self.stopped_time * self.stopped_price + self.moving_time * self.moving_price

        return fare

