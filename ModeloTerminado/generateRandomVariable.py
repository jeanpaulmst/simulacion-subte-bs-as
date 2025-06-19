from dataIngresos import ingresos_lineaA

import numpy as np
from scipy.stats import rv_discrete

# Cache de distribuciones ya calculadas
_distribuciones_cache = {}

def generar_ingreso_pasajeros(nombre_estacion: str) -> int:
    """
    Devuelve un valor aleatorio de ingreso de pasajeros para la estación dada,
    según una distribución empírica construida a partir de datos reales.
    """

    if nombre_estacion not in ingresos_lineaA:
        raise ValueError(f"No hay datos cargados para la estación: {nombre_estacion}")

    # Si ya se construyó la distribución para esta estación, reutilizarla
    if nombre_estacion not in _distribuciones_cache:
        datos = ingresos_lineaA[nombre_estacion]
        
        # Construcción de histograma
        num_bins = 20
        hist, bin_edges = np.histogram(datos, bins=num_bins, density=True, range=(min(datos), max(datos)))
        valores = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        probabilidades = hist / hist.sum()

        print("conteo: ", hist)
        print("bordes: ", bin_edges)

        # Crear distribución y guardar en cache
        distribucion = rv_discrete(name=nombre_estacion, values=(valores, probabilidades))
        _distribuciones_cache[nombre_estacion] = distribucion

    # Generar un valor aleatorio
    return int(_distribuciones_cache[nombre_estacion].rvs())

# Generar 10 valores de variable aleatoria
print("\n\n")
for i in range(0,50):
    aleatorio = generar_ingreso_pasajeros("Plaza de Mayo")
    print("Variable Aleatoria: ", aleatorio)