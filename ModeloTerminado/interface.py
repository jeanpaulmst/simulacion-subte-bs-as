import streamlit as st
import mesa
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum
from typing import List, Dict
import time
from Model import ModeloSubte

def plot_data(data, estaciones):
    df = pd.DataFrame(data)

    # Create two columns for the plots
    col1, col2 = st.columns(2)

    # Plot individual station graphs
    for index, estacion in enumerate(estaciones):
        fig, ax = plt.subplots()
        ax.plot(df[estacion], label=estacion, alpha=0.7)
        ax.set_xlabel('Step')
        ax.set_ylabel('Numbero de Pasajeros')
        ax.legend()
        ax.set_title(f'{estacion}')

        # Place each plot in one of the two columns alternately
        if index % 2 == 0:
            col1.pyplot(fig)
        else:
            col2.pyplot(fig)

    # Gráfico del conjunto de todas las estaciones
    st.write("### Gráfico del conjunto de todas las estaciones")
    fig_combined, ax_combined = plt.subplots(figsize=(12, 8))
    for estacion in estaciones:
        ax_combined.plot(df[estacion], label=estacion, alpha=0.7)

    ax_combined.set_xlabel('Step')
    ax_combined.set_ylabel('Numbero de Pasajeros')
    ax_combined.legend(loc='center left', bbox_to_anchor=(1, 0.5))
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


