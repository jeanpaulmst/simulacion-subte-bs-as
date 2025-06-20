import mesa
import random
import numpy as np
from enum import Enum
from typing import List, Dict
import os
import time

from auxiliarData import linea_a_stations
from dataIngresos import ingresos_lineaA
from generateRandomVariable2 import create_intensity_function

class EstadoPasajero(Enum):
    EN_PARTIDA = "en_partida"
    EN_VIAJE = "en_viaje"
    EN_DESTINO = "en_destino"

class Pasajero(mesa.Agent):
    """Agente Pasajero que viaja por la línea A del subte"""
    
    def __init__(self, unique_id, model, estacion_partida, estacion_destino):
        super().__init__(unique_id, model)
        self.estacion_partida = estacion_partida
        self.estacion_destino = estacion_destino
        self.estado = EstadoPasajero.EN_PARTIDA
        self.longitud_viaje = self.calcular_longitud_viaje()
        self.step_creacion = model.schedule.steps
        
    def calcular_longitud_viaje(self):
        """Calcula la distancia entre estación de partida y destino"""
        estaciones = self.model.estaciones
        idx_partida = linea_a_stations[self.estacion_partida]
        idx_destino = linea_a_stations[self.estacion_destino]
        return abs(idx_destino - idx_partida)
    
    def step(self):
        """Actualiza el estado del pasajero en cada step"""
        if self.estado == EstadoPasajero.EN_PARTIDA:
            self.estado = EstadoPasajero.EN_VIAJE
            
        elif self.estado == EstadoPasajero.EN_VIAJE:
            self.longitud_viaje -= 1
            
            if self.longitud_viaje <= 0:
                self.estado = EstadoPasajero.EN_DESTINO

class Estacion:
    """Representa una estación de la línea A"""
    
    def __init__(self, nombre, indice, model):
        self.nombre = nombre
        self.indice = indice
        self.model = model
        self.intensity_function = create_intensity_function(list(ingresos_lineaA[nombre]))
        
    def generar_cantidad_pasajeros(self):
        """Genera cantidad aleatoria de pasajeros usando distribución de Poisson"""
        rate = self.intensity_function[self.model.schedule.steps]   
        return np.random.poisson(rate)
    
    def crear_pasajeros(self):
        """Crea pasajeros en esta estación"""
        cantidad = self.generar_cantidad_pasajeros()
        
        for _ in range(cantidad):
            # Asignar destino aleatorio (diferente a la estación de partida)
            destinos_posibles = [est for est in self.model.estaciones if est != self.nombre]
            destino = random.choice(destinos_posibles)
            
            # Crear pasajero
            self.model.contador_pasajeros += 1
            pasajero = Pasajero(
                unique_id=self.model.contador_pasajeros,
                model=self.model,
                estacion_partida=self.nombre,
                estacion_destino=destino
            )
            
            # Agregar al scheduler
            self.model.schedule.add(pasajero)
    
    def contar_pasajeros(self):
        """Cuenta pasajeros en esta estación según las reglas especificadas"""
        count = 0
        
        for agente in self.model.schedule.agents:
            if isinstance(agente, Pasajero):
                # Pasajeros en partida desde esta estación
                if (agente.estacion_partida == self.nombre and 
                    agente.estado == EstadoPasajero.EN_PARTIDA):
                    count += 1
                
                # Pasajeros que llegaron a destino en esta estación
                elif (agente.estacion_destino == self.nombre and 
                      agente.longitud_viaje == 0 and 
                      agente.estado == EstadoPasajero.EN_DESTINO):
                    count += 1
        
        return count

class ModeloSubte(mesa.Model):
    """Modelo principal de simulación del subte"""
    
    def __init__(self):
        super().__init__()

        self.estaciones = linea_a_stations
        
        # Crear objetos estación
        self.objetos_estaciones = {nombre: Estacion(nombre, indice, self) for nombre, indice in self.estaciones.items()}
        
        # Scheduler para los agentes
        self.schedule = mesa.time.RandomActivation(self)
        
        # Contador de pasajeros únicos
        self.contador_pasajeros = 0
        
        # Estadísticas simplificadas
        self.pasajeros_por_estacion = {estacion: 0 for estacion in list(self.estaciones.keys())}
        
        # Data collector simplificado - solo para mostrar en tiempo real
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Step": lambda m: m.schedule.steps,
                **{f"Estacion_{estacion}": lambda m, est=estacion: m.pasajeros_por_estacion[est] 
                   for estacion in list(self.estaciones.keys())}
            }
        )
        self.data = []
    
    def actualizar_estadisticas(self):
        """Actualiza estadísticas de pasajeros por estación"""
        for estacion_nombre, estacion_obj in self.objetos_estaciones.items():
            self.pasajeros_por_estacion[estacion_nombre] = estacion_obj.contar_pasajeros()

    
    def step(self):
        """Ejecuta un paso de la simulación"""
        # Crear pasajeros en todas las estaciones
        for estacion in self.objetos_estaciones.values():
            estacion.crear_pasajeros()
        
        # Actualizar todos los agentes
        self.schedule.step()
        
        # Actualizar estadísticas
        self.actualizar_estadisticas()
        
        # Recopilar datos
        self.datacollector.collect(self)
        
        # Limpiar pasajeros que completaron su viaje
        self.limpiar_pasajeros_finalizados()
        self.data.append(self.pasajeros_por_estacion.copy())
    
    def limpiar_pasajeros_finalizados(self):
        """Elimina pasajeros que han llegado a su destino (después de 1 step en destino)"""
        pasajeros_a_eliminar = []
        
        for agente in self.schedule.agents:
            if isinstance(agente, Pasajero):
                if (agente.estado == EstadoPasajero.EN_DESTINO and 
                    self.schedule.steps - agente.step_creacion > agente.calcular_longitud_viaje() + 1):
                    pasajeros_a_eliminar.append(agente)
        
        for pasajero in pasajeros_a_eliminar:
            self.schedule.remove(pasajero)

    def obtener_estado_tiempo_real(self):
        """Obtiene el estado actual para mostrar en tiempo real"""
        return {
            "step": self.schedule.steps,
            "pasajeros_por_estacion": self.pasajeros_por_estacion.copy()
        }

# Ejemplo de uso

""""
modelo = ModeloSubte()

print("Iniciando simulación de la Línea A del Subte...")
print("=" * 60)

time.sleep(1)
os.system('cls')

modelo.step()
estado = modelo.obtener_estado_tiempo_real()
estaciones = list(estado['pasajeros_por_estacion'].keys())


for i in range(1, 100):
    modelo.step()
    estado = modelo.obtener_estado_tiempo_real()
    
    os.system('cls')
    
    # Construir todo de una vez usando list comprehension
    lines = [f"\nStep {estado['step']}:", "-" * 40]
    lines.extend(f"  {est:<25}: {estado['pasajeros_por_estacion'][est]:>3} pasajeros" 
                for est in estaciones)
    lines.extend(["-" * 40, 
                 f"  {'TOTAL':<25}: {sum(estado['pasajeros_por_estacion'].values()):>3} pasajeros"])
    
    print('\n'.join(lines))
    time.sleep(1)

print("\n" + "=" * 60)
print("Simulación completada")
"""