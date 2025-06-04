import pandas as pd
import csv

# Leer archivo CSV
file_path = "202401_PAX15min-ABC.csv"

try:
    df = pd.read_csv(file_path, sep=';', encoding='utf-8', quoting=csv.QUOTE_NONE)

except FileNotFoundError:
    print(f"Error: El archivo {file_path} no se encontró.")
    df = pd.DataFrame()



#Contar la cantidad de gente que se sube (POR estación, por hora)
class LineaData:
    def __init__(self, nombre):
        self.nombre = nombre
        self.estaciones = {}  # Diccionario de estaciones por nombre

    def agregar_estacion(self, estacion):
        self.estaciones[estacion.nombre] = estacion

    def obtener_estacion(self, nombre):
        return self.estaciones.get(nombre, None)

class EstacionData:
    def __init__(self, nombre, ingresos, egresos):
        self.nombre = nombre
        self.ingresos = ingresos   #Lista de cantidad de gente que ingresa a la estación cada 15 min
        self.egresos = egresos   #Lista de cantidad de gente que sale de la estación cada 15 min


#Cantidad de gente que ingresa a cada estacion cada 15 minutos
df_agrupado = df.groupby(['DESDE', 'HASTA', 'LINEA', 'ESTACION'])['pax_pagos'].sum().reset_index()
print(df_agrupado.head())

#Obtener todas las distintas líneas y crear un objeto LineaData para cada una
lineas_unicas = df['LINEA'].unique()
lineas = [LineaData(nombre_linea) for nombre_linea in lineas_unicas]

#Por cada Linea, obtener todas las estaciones y crear un objeto EstacionData para cada una
for linea in lineas:
    estaciones_por_linea = df[df['LINEA'] == linea.nombre]['ESTACION'].unique()
    for nombre_estacion in estaciones_por_linea:

        subidas = [valor for valor in df_agrupado[df_agrupado['ESTACION'] == nombre_estacion]['pax_pagos']]
        
        estacion = EstacionData(nombre_estacion, ingresos=subidas, egresos=[])
        linea.agregar_estacion(estacion)

print(len(df['DESDE'].unique()))  # Imprimir la cantidad de horas únicas
print(len(lineas[0].estaciones["Dorrego"].ingresos))  # Imprimir las estaciones de la primera línea
#print(df_agrupado.head())


# cantidad de mediciones de ingresos por estación por día
for estacion in lineas[0].estaciones.values():
    print(estacion.nombre + ": " + str(len(estacion.ingresos)))