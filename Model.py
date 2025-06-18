import mesa

import random

from funciones.auxiliarData import linea_a_stations 

class Pasajero(mesa.Agent):
    def __init__(self, model, partida, destino):
        super().__init__( model)
        self.partida = partida
        self.destino = destino
        self.estado = "en_partida"
        self.distancia = abs(model.estaciones.index(destino) - model.estaciones.index(partida))

    def step(self):
        if self.estado == "en_partida":
            self.estado = "en_viaje"
        elif self.estado == "en_viaje":
            self.distancia -= 1
            if self.distancia <= 0:
                self.estado = "en_destino"

class Estacion:
    def __init__(self, nombre):
        self.nombre = nombre
        self.pasajeros_actuales = 0

class ModeloSubte(mesa.Model):
    def __init__(self):
        self.estaciones = linea_a_stations
        self.estaciones_objs = {nombre: Estacion(nombre) for nombre in self.estaciones}
        self.pasajeros = []

    def crear_pasajeros_en_estaciones(self):
        for nombre in self.estaciones:
            cantidad = random.randint(0, 3)  # variable aleatoria simple - Cambiar por variable aleatoria generada para cada estación
            for _ in range(cantidad):
                destino = random.choice([e for e in self.estaciones if e != nombre])
                pasajero = Pasajero(self, nombre, destino)
                self.pasajeros.append(pasajero)
                

    def step(self):
        # 1. Crear nuevos pasajeros
        self.crear_pasajeros_en_estaciones()

        # 2. Avanzar estado de cada pasajero
        for p in self.pasajeros:
            p.step()

        # 3. Contar pasajeros por estación
        conteo = {nombre: 0 for nombre in self.estaciones}
        for p in self.pasajeros:
            if p.estado == "en_partida" and p.partida in conteo:
                conteo[p.partida] += 1
            elif p.estado == "en_destino" and p.destino in conteo:
                conteo[p.destino] += 1

        print("Cantidad de pasajeros por estación:")
        for nombre, cant in conteo.items():
            print(f"{nombre}: {cant}")
        print("")

# Ejecutar el modelo por 5 pasos
modelo = ModeloSubte()

for i in range(5):
    print(f"--- STEP {i+1} ---")
    modelo.step()
