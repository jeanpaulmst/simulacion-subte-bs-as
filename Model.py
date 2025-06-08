import mesa
import random
import numpy as np

from getStats import LineaData, EstacionData
from auxiliarData import lineas_aux_data

## --- Definición de las clases del modelo de subte --- ##




class Pasajero(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.partida = None
        self.destino = None

    def step(self):
        # Lógica para mover al pasajero hacia su destino
        pass

class Estacion:
    def __init__(self, indice):
        self.indice = indice
        self.pasajeros_en_espera  = []

    def add_passenger(self, passenger):
        self.pasajeros_en_espera.append(passenger)

    def step(self):
        # Lógica para manejar a los pasajeros en la estación
        pass

class LineaSubte(mesa.Agent):
    def __init__(self, name, stations):
        self.name = name
        self.stations = list(stations)

    def step(self):
        # Lógica para manejar el movimiento de trenes a lo largo de la línea
        pass

class ModeloSubte(mesa.Model):
    def __init__(self):
        self.schedule = mesa.time.RandomActivation(self)
        self.lines = []

        # Crear líneas de subte
        line = LineaSubte(1, self)
        self.schedule.add(line)
        self.lines.append(line)

        # Crear estaciones
        for i in range(2):
            station = Estacion(i, self, random.random())
            line.add_station(station)
            self.schedule.add(station)

        # Crear pasajeros
        for i in range(self.num_agents):
            passenger = Pasajero(i, self)
            self.schedule.add(passenger)
            # Asignar una estación aleatoria como destino
            passenger.destination = random.choice(line.stations)
            passenger.destination.add_passenger(passenger)

    def step(self):
        self.schedule.step()
        print(f"Paso del modelo: {self.schedule.time}")

# Crear y ejecutar el modelo

N = 900000 #Numero de pasajeros máximo en toda la red

model = ModeloSubte()

for i in range(96):
    model.step()
