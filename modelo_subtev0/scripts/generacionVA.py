from dataIngresos import ingresos_lineaA

import numpy as np
from scipy.interpolate import interp1d

def create_intensity_function(data, original_step=15, new_step=5):
    # Asegúrate de que el nuevo step sea un divisor del original
    if original_step % new_step != 0:
        raise ValueError("El nuevo step debe ser un divisor del step original.")

    # Factor de división
    factor = original_step // new_step

    # Redistribuye los datos a los nuevos intervalos
    redistributed_data = np.repeat([(elem / factor) for elem in data], factor)

    # Tiempo en minutos para cada nuevo intervalo
    time_intervals = np.arange(0, len(redistributed_data) * new_step, new_step)

    # Crea una función de interpolación lineal para la tasa de llegada
    intensity_function = interp1d(time_intervals, redistributed_data, kind='linear', fill_value="extrapolate")

    return intensity_function

# Ejemplo de uso
intensity_function = create_intensity_function(ingresos_lineaA["Flores"])

# Ejemplo de cómo obtener la tasa en un tiempo específico
time = 30  # minutos
rate = intensity_function(time)

for i in range(0, 1000):
    rate = intensity_function(i)
    print(np.random.poisson(rate))
