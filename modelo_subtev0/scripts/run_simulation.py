import random
import numpy as np
from enum import Enum
from typing import List, Dict, Optional
import json

from generacionVA import create_intensity_function

class PassengerState(Enum):
    EN_PARTIDA = "en_partida"
    EN_VIAJE = "en_viaje" 
    EN_DESTINO = "en_destino"

class Passenger:
    """Agente Pasajero que representa a una persona viajando en el subte"""
    
    def __init__(self, unique_id: int, origin_station: str, destination_station: str, creation_step: int):
        self.unique_id = unique_id
        self.origin_station = origin_station
        self.destination_station = destination_station
        self.state = PassengerState.EN_PARTIDA
        self.travel_length = self.calculate_travel_length()
        self.creation_step = creation_step
        
    def calculate_travel_length(self) -> int:
        """Calcula la longitud del viaje basado en la distancia entre estaciones"""
        stations = [
            'San Pedrito', 'Piedra Buena', 'Varela', 'Medalla Milagrosa',
            'Acoyte', 'Primera Junta', 'Puan', 'Carabobo', 'Río de Janeiro',
            'Castro Barros', 'Loria', 'Plaza Miserere', 'Alberti', 'Pasco',
            'Congreso', 'Sáenz Peña', 'Lima', 'Piedras', 'Perú', 'Plaza de Mayo'
        ]
        origin_idx = stations.index(self.origin_station)
        dest_idx = stations.index(self.destination_station)
        return abs(dest_idx - origin_idx)
    
    def step(self):
        """Ejecuta un paso de la simulación para este pasajero"""
        if self.state == PassengerState.EN_PARTIDA:
            self.state = PassengerState.EN_VIAJE
            
        elif self.state == PassengerState.EN_VIAJE:
            self.travel_length -= 1
            
            if self.travel_length <= 0:
                self.state = PassengerState.EN_DESTINO

class Station:
    """Representa una estación del subte"""
    
    def __init__(self, name: str, passenger_generation_rate: float = 15.0):
        self.name = name
        self.passenger_generation_rate = passenger_generation_rate
        
    def generate_passengers_count(self, step) -> int:
        """Genera la cantidad de pasajeros usando una distribución de Poisson"""
        rate = create_intensity_function(step)
        return np.random.poisson(self.passenger_generation_rate)

class SubwayModel:
    """Modelo principal de simulación del subte"""
    
    def __init__(self, stations_data: Optional[Dict[str, float]] = None):
        # Estaciones de la Línea A
        self.stations_list = [
            'San Pedrito', 'Piedra Buena', 'Varela', 'Medalla Milagrosa',
            'Acoyte', 'Primera Junta', 'Puan', 'Carabobo', 'Río de Janeiro',
            'Castro Barros', 'Loria', 'Plaza Miserere', 'Alberti', 'Pasco',
            'Congreso', 'Sáenz Peña', 'Lima', 'Piedras', 'Perú', 'Plaza de Mayo'
        ]
        
        # Crear objetos Station
        self.stations = {}
        for station_name in self.stations_list:
            rate = stations_data.get(station_name, 15.0) if stations_data else 15.0
            self.stations[station_name] = Station(station_name, rate)
        
        # Lista de pasajeros activos
        self.passengers = []
        self.passenger_id_counter = 0
        self.current_step = 0
        
        # Datos de simulación
        self.simulation_data = []
        
    def create_passenger(self, origin_station: str) -> Passenger:
        """Crea un nuevo pasajero con destino aleatorio"""
        available_destinations = [s for s in self.stations_list if s != origin_station]
        destination = random.choice(available_destinations)
        
        passenger = Passenger(
            unique_id=self.passenger_id_counter,
            origin_station=origin_station,
            destination_station=destination,
            creation_step=self.current_step
        )
        
        self.passenger_id_counter += 1
        self.passengers.append(passenger)
        
        return passenger
    
    def step(self):
        """Ejecuta un paso de la simulación"""
        self.current_step += 1
        
        # 1. Generar nuevos pasajeros en cada estación
        for station_name, station in self.stations.items():
            passenger_count = station.generate_passengers_count(self.current_step)
            
            for _ in range(passenger_count):
                self.create_passenger(station_name)
        
        # 2. Ejecutar step para todos los pasajeros existentes
        for passenger in self.passengers:
            passenger.step()
        
        # 3. Remover pasajeros que han estado en destino por más de 3 steps
        passengers_to_remove = []
        for passenger in self.passengers:
            if (passenger.state == PassengerState.EN_DESTINO and 
                self.current_step - passenger.creation_step > passenger.calculate_travel_length() + 3):
                passengers_to_remove.append(passenger)
        
        for passenger in passengers_to_remove:
            self.passengers.remove(passenger)
        
        # 4. Recolectar datos
        step_data = {
            'step': self.current_step,
            'total_passengers': len(self.passengers),
            'en_partida': len([p for p in self.passengers if p.state == PassengerState.EN_PARTIDA]),
            'en_viaje': len([p for p in self.passengers if p.state == PassengerState.EN_VIAJE]),
            'en_destino': len([p for p in self.passengers if p.state == PassengerState.EN_DESTINO]),
            'stations_data': self.get_all_stations_data()
        }
        
        self.simulation_data.append(step_data)
    
    def get_all_stations_data(self) -> Dict[str, Dict[str, int]]:
        """Obtiene datos de todas las estaciones"""
        stations_data = {}
        
        for station in self.stations_list:
            en_partida = len([p for p in self.passengers 
                            if p.origin_station == station and p.state == PassengerState.EN_PARTIDA])
            
            en_destino = len([p for p in self.passengers 
                            if p.destination_station == station and p.state == PassengerState.EN_DESTINO])
            
            stations_data[station] = {
                'en_partida': en_partida,
                'en_destino': en_destino,
                'total': en_partida + en_destino
            }
        
        return stations_data

def run_simulation(steps: int = 50):
    """Ejecuta la simulación y retorna los resultados"""
    
    # Datos de ejemplo con diferentes tasas de generación por estación
    station_rates = {
        'Plaza de Mayo': 25.0,
        'Congreso': 20.0,
        'Plaza Miserere': 22.0,
        'Primera Junta': 18.0,
        'San Pedrito': 12.0,
    }
    
    # Crear modelo
    model = SubwayModel(station_rates)
    
    print(f"Iniciando simulación por {steps} steps...")
    
    for step in range(steps):
        model.step()
        
        if step % 10 == 0:
            total_passengers = len(model.passengers)
            print(f"Step {step}: {total_passengers} pasajeros totales")
    
    print("\n=== RESULTADOS FINALES ===")
    final_data = model.simulation_data[-1]
    print(f"Total de pasajeros: {final_data['total_passengers']}")
    print(f"En partida: {final_data['en_partida']}")
    print(f"En viaje: {final_data['en_viaje']}")
    print(f"En destino: {final_data['en_destino']}")
    
    print("\n=== PASAJEROS POR ESTACIÓN ===")
    for station, data in final_data['stations_data'].items():
        print(f"{station}: {data['total']} total ({data['en_partida']} partida, {data['en_destino']} destino)")
    
    # Guardar resultados en JSON para usar en el frontend
    with open('simulation_results.json', 'w', encoding='utf-8') as f:
        json.dump(model.simulation_data, f, ensure_ascii=False, indent=2)
    
    return model.simulation_data

if __name__ == "__main__":
    results = run_simulation(steps=50)
    print(f"\nSimulación completada. Datos guardados en simulation_results.json")
