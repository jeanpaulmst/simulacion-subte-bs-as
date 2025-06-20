import datetime
import streamlit as st
import mesa
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from enum import Enum
from typing import List, Dict
import time
from Model import ModeloSubte

def plot_data(data, estaciones):
    # Generate the list of datetime objects
    datetime_objects = [datetime.datetime(2024, 1, 1, 0) + datetime.timedelta(minutes=5 * i + 60 * 8) for i in range(len(data))]

    # Create a DataFrame with the datetime objects and the data
    df = pd.DataFrame(data, index=datetime_objects)

    # Create two columns for the plots
    col1, col2 = st.columns(2)

    # Plot individual station graphs
    for index, estacion in enumerate(estaciones):
        fig, ax = plt.subplots()
        ax.plot(df.index, df[estacion], label=estacion, alpha=0.7)
        ax.set_xlabel('Time')
        ax.set_ylabel('Number of Passengers')
        ax.legend()
        ax.set_title(f'{estacion}')

        # Format the x-axis to show only the time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)

        # Place each plot in one of the two columns alternately
        if index % 2 == 0:
            col1.pyplot(fig)
        else:
            col2.pyplot(fig)

    # Combined plot of all stations
    st.write("### Combined Plot of All Stations")
    fig_combined, ax_combined = plt.subplots(figsize=(12, 8))
    for estacion in estaciones:
        ax_combined.plot(df.index, df[estacion], label=estacion, alpha=0.7)

    ax_combined.set_xlabel('Time')
    ax_combined.set_ylabel('Number of Passengers')
    ax_combined.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # Format the x-axis to show only the time
    ax_combined.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)

    st.pyplot(fig_combined)

def main():
    st.title("Simulación de la Línea A del Subte")
    modelo = ModeloSubte()

    steps_input = st.text_input("Ingrese cantidad de steps a simular (cada step representa 5 min de la realidad):")

    if st.button("Iniciar Simulación"):
        progress_bar = st.progress(0)
        steps = int(steps_input)

        for i in range(steps):
            modelo.step()
            estado = modelo.obtener_estado_tiempo_real()
            progress_bar.progress((i + 1) / steps)

            # Mostrar resultados en una tabla
            st.write(f"### Paso {estado['step']}")
            df = pd.DataFrame(list(estado['pasajeros_por_estacion'].items()), columns=['Estación', 'Pasajeros'])
            st.table(df)
            st.write(f"Total: {sum(estado['pasajeros_por_estacion'].values())} pasajeros")

            time.sleep(0.1)

        st.success("Simulación completada")

        # Mostrar gráficos por estación en dos columnas y un gráfico conjunto al final
        st.write("### Evolución de Pasajeros por Estación")
        plot_data(modelo.data, modelo.estaciones)

if __name__ == "__main__":
    main()
