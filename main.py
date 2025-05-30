import mesa
import random
import numpy as np

class Pasajero(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.partida = None
        self.destino = None

    def step(self):
        # Lógica para mover al pasajero hacia su destino
        pass

class Estacion:
    def __init__(self, importance):
        self.importance = importance
        self.passengers = []

    def add_passenger(self, passenger):
        self.passengers.append(passenger)

    def step(self):
        # Lógica para manejar a los pasajeros en la estación
        pass

class LineaSubte(mesa.Agent):
    def __init__(self, stations):
        self.stations = list(stations)

    def add_station(self, station):
        self.stations.append(station)

    def step(self):
        # Lógica para manejar el movimiento de trenes a lo largo de la línea
        pass

class ModeloSubte(mesa.Model):
    def __init__(self, N):
        self.num_agents = N
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

# Crear y ejecutar el modelo

N = 900000 #Numero de pasajeros máximo en toda la red

model = ModeloSubte(50)
for i in range(10):
    model.step()
