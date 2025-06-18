import mesa
import random
import numpy as np
from enum import Enum
from typing import List, Dict, Optional

class PassengerState(Enum):
    EN_PARTIDA = "en_partida"
    EN_VIAJE = "en_viaje" 
    EN_DESTINO = "en_destino"

class Passenger(mesa.Agent):
    """Agente Pasajero que representa a una persona viajando en el subte"""
    
    def __init__(self, unique_id: int, model, origin_station: str, destination_station: str):
        super().__init__(unique_id, model)
        self.origin_station = origin_station
        self.destination_station = destination_station
        self.state = PassengerState.EN_PARTIDA
        self.travel_length = self.calculate_travel_length()
        self.creation_step = model.schedule.steps
        
    def calculate_travel_length(self) -> int:
        """Calcula la longitud del viaje basado en la distancia entre estaciones"""
        stations = self.model.stations_list
        origin_idx = stations.index(self.origin_station)
        dest_idx = stations.index(self.destination_station)
        return abs(dest_idx - origin_idx)
    
    def step(self):
        """Ejecuta un paso de la simulación para este pasajero"""
        if self.state == PassengerState.EN_PARTIDA:
            # Cambiar a estado "en viaje" en el siguiente step
            self.state = PassengerState.EN_VIAJE
            
        elif self.state == PassengerState.EN_VIAJE:
            # Reducir la longitud del viaje
            self.travel_length -= 1
            
            # Si llegó al destino, cambiar estado
            if self.travel_length <= 0:
                self.state = PassengerState.EN_DESTINO
                
        # Los pasajeros en destino se mantienen en ese estado

class Station:
    """Representa una estación del subte"""
    
    def __init__(self, name: str, passenger_generation_rate: float = 15.0):
        self.name = name
        self.passenger_generation_rate = passenger_generation_rate
        
    def generate_passengers_count(self) -> int:
        """Genera la cantidad de pasajeros usando una distribución de Poisson"""
        return np.random.poisson(self.passenger_generation_rate)

class SubwayModel(mesa.Model):
    """Modelo principal de simulación del subte"""
    
    def __init__(self, stations_data: Optional[Dict[str, float]] = None):
        super().__init__()
        
        # Estaciones de la Línea A
        self.stations_list = [
            'San Pedrito', 'Piedra Buena', 'Varela', 'Medalla Milagrosa',
            'Acoyte', 'Primera Junta', 'Puan', 'Carabobo', 'Río de Janeiro',
            'Castro Barros', 'Loria', 'Plaza Miserere', 'Alberti', 'Pasco',
            'Congreso', 'Sáenz Peña', 'Lima', 'Piedras', 'Perú', 'Plaza de Mayo'
        ]
        
        # Crear objetos Station con tasas de generación específicas o por defecto
        self.stations = {}
        for station_name in self.stations_list:
            rate = stations_data.get(station_name, 15.0) if stations_data else 15.0
            self.stations[station_name] = Station(station_name, rate)
        
        # Scheduler para los agentes
        self.schedule = mesa.time.RandomActivation(self)
        
        # Contador de IDs únicos para pasajeros
        self.passenger_id_counter = 0
        
        # Recolector de datos
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Total_Passengers": self.count_total_passengers,
                "Passengers_En_Partida": self.count_passengers_en_partida,
                "Passengers_En_Viaje": self.count_passengers_en_viaje,
                "Passengers_En_Destino": self.count_passengers_en_destino,
            },
            agent_reporters={
                "State": "state",
                "Origin": "origin_station",
                "Destination": "destination_station",
                "Travel_Length": "travel_length"
            }
        )
        
    def create_passenger(self, origin_station: str) -> Passenger:
        """Crea un nuevo pasajero con destino aleatorio"""
        # Seleccionar destino aleatorio diferente al origen
        available_destinations = [s for s in self.stations_list if s != origin_station]
        destination = random.choice(available_destinations)
        
        # Crear pasajero
        passenger = Passenger(
            unique_id=self.passenger_id_counter,
            model=self,
            origin_station=origin_station,
            destination_station=destination
        )
        
        self.passenger_id_counter += 1
        self.schedule.add(passenger)
        
        return passenger
    
    def step(self):
        """Ejecuta un paso de la simulación"""
        # 1. Generar nuevos pasajeros en cada estación
        for station_name, station in self.stations.items():
            passenger_count = station.generate_passengers_count()
            
            for _ in range(passenger_count):
                self.create_passenger(station_name)
        
        # 2. Ejecutar step para todos los pasajeros existentes
        self.schedule.step()
        
        # 3. Recolectar datos
        self.datacollector.collect(self)
        
        # 4. Remover pasajeros que han estado en destino por más de 3 steps
        passengers_to_remove = []
        for agent in self.schedule.agents:
            if (agent.state == PassengerState.EN_DESTINO and 
                self.schedule.steps - agent.creation_step > agent.calculate_travel_length() + 3):
                passengers_to_remove.append(agent)
        
        for passenger in passengers_to_remove:
            self.schedule.remove(passenger)
    
    def count_passengers_in_station(self, station_name: str) -> Dict[str, int]:
        """Cuenta los pasajeros en una estación específica"""
        en_partida = 0
        en_destino = 0
        
        for agent in self.schedule.agents:
            # Pasajeros en partida desde esta estación
            if (agent.origin_station == station_name and 
                agent.state == PassengerState.EN_PARTIDA):
                en_partida += 1
            
            # Pasajeros que llegaron a esta estación
            if (agent.destination_station == station_name and 
                agent.state == PassengerState.EN_DESTINO and 
                agent.travel_length == 0):
                en_destino += 1
        
        return {
            'en_partida': en_partida,
            'en_destino': en_destino,
            'total': en_partida + en_destino
        }
    
    def get_all_stations_data(self) -> Dict[str, Dict[str, int]]:
        """Obtiene datos de todas las estaciones"""
        return {station: self.count_passengers_in_station(station) 
                for station in self.stations_list}
    
    # Métodos para el DataCollector
    def count_total_passengers(self):
        return len(self.schedule.agents)
    
    def count_passengers_en_partida(self):
        return len([a for a in self.schedule.agents if a.state == PassengerState.EN_PARTIDA])
    
    def count_passengers_en_viaje(self):
        return len([a for a in self.schedule.agents if a.state == PassengerState.EN_VIAJE])
    
    def count_passengers_en_destino(self):
        return len([a for a in self.schedule.agents if a.state == PassengerState.EN_DESTINO])

def run_simulation(steps: int = 100, stations_data: Optional[Dict[str, float]] = None):
    """Ejecuta la simulación y retorna los resultados"""
    
    # Crear modelo
    model = SubwayModel(stations_data)
    
    # Ejecutar simulación
    print(f"Iniciando simulación por {steps} steps...")
    
    for step in range(steps):
        model.step()
        
        if step % 10 == 0:
            total_passengers = model.count_total_passengers()
            print(f"Step {step}: {total_passengers} pasajeros totales")
    
    # Obtener datos finales
    model_data = model.datacollector.get_model_vars_dataframe()
    agent_data = model.datacollector.get_agent_vars_dataframe()
    stations_data = model.get_all_stations_data()
    
    print("\n=== RESULTADOS FINALES ===")
    print(f"Total de pasajeros: {model.count_total_passengers()}")
    print(f"En partida: {model.count_passengers_en_partida()}")
    print(f"En viaje: {model.count_passengers_en_viaje()}")
    print(f"En destino: {model.count_passengers_en_destino()}")
    
    print("\n=== PASAJEROS POR ESTACIÓN ===")
    for station, data in stations_data.items():
        print(f"{station}: {data['total']} total ({data['en_partida']} partida, {data['en_destino']} destino)")
    
    return {
        'model_data': model_data,
        'agent_data': agent_data,
        'stations_data': stations_data,
        'model': model
    }

# Ejemplo de uso
if __name__ == "__main__":
    # Datos de ejemplo con diferentes tasas de generación por estación
    station_rates = {
        'Plaza de Mayo': 25.0,  # Estación muy concurrida
        'Congreso': 20.0,
        'Plaza Miserere': 22.0,
        'Primera Junta': 18.0,
        'San Pedrito': 12.0,    # Estación menos concurrida
    }
    
    # Ejecutar simulación
    results = run_simulation(steps=50, stations_data=station_rates)
    
    # Los resultados están disponibles en results['model_data'], results['agent_data'], etc.
