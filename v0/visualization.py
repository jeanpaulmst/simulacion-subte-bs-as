import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from subway_simulation import run_simulation

def create_visualizations(results):
    """Crea visualizaciones de los resultados de la simulación"""
    
    model_data = results['model_data']
    stations_data = results['stations_data']
    
    # Configurar estilo
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análisis de Simulación - Línea A Subte Buenos Aires', fontsize=16, fontweight='bold')
    
    # 1. Evolución temporal de pasajeros
    axes[0, 0].plot(model_data.index, model_data['Total_Passengers'], 'b-', linewidth=2, label='Total')
    axes[0, 0].plot(model_data.index, model_data['Passengers_En_Partida'], 'g--', label='En Partida')
    axes[0, 0].plot(model_data.index, model_data['Passengers_En_Viaje'], 'r--', label='En Viaje')
    axes[0, 0].plot(model_data.index, model_data['Passengers_En_Destino'], 'm--', label='En Destino')
    axes[0, 0].set_title('Evolución Temporal de Pasajeros')
    axes[0, 0].set_xlabel('Steps')
    axes[0, 0].set_ylabel('Cantidad de Pasajeros')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Distribución por estados (gráfico de torta)
    final_counts = [
        model_data['Passengers_En_Partida'].iloc[-1],
        model_data['Passengers_En_Viaje'].iloc[-1],
        model_data['Passengers_En_Destino'].iloc[-1]
    ]
    labels = ['En Partida', 'En Viaje', 'En Destino']
    colors = ['#2ecc71', '#e74c3c', '#9b59b6']
    
    axes[0, 1].pie(final_counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    axes[0, 1].set_title('Distribución Final por Estados')
    
    # 3. Pasajeros por estación
    stations = list(stations_data.keys())
    totals = [stations_data[station]['total'] for station in stations]
    partida = [stations_data[station]['en_partida'] for station in stations]
    destino = [stations_data[station]['en_destino'] for station in stations]
    
    x = range(len(stations))
    width = 0.35
    
    axes[1, 0].bar([i - width/2 for i in x], partida, width, label='En Partida', color='#3498db', alpha=0.8)
    axes[1, 0].bar([i + width/2 for i in x], destino, width, label='En Destino', color='#e67e22', alpha=0.8)
    
    axes[1, 0].set_title('Pasajeros por Estación')
    axes[1, 0].set_xlabel('Estaciones')
    axes[1, 0].set_ylabel('Cantidad de Pasajeros')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(stations, rotation=45, ha='right')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Heatmap de flujo entre estaciones (simulado)
    # Crear matriz de flujo simulada
    n_stations = len(stations)
    flow_matrix = [[0 for _ in range(n_stations)] for _ in range(n_stations)]
    
    # Simular algunos flujos basados en los datos
    for i, origin in enumerate(stations):
        for j, dest in enumerate(stations):
            if i != j:
                # Simular flujo basado en la distancia y popularidad de las estaciones
                distance = abs(i - j)
                flow = max(0, 10 - distance + (totals[i] + totals[j]) / 20)
                flow_matrix[i][j] = flow
    
    im = axes[1, 1].imshow(flow_matrix, cmap='YlOrRd', aspect='auto')
    axes[1, 1].set_title('Matriz de Flujo Entre Estaciones')
    axes[1, 1].set_xticks(range(n_stations))
    axes[1, 1].set_yticks(range(n_stations))
    axes[1, 1].set_xticklabels([s[:10] + '...' if len(s) > 10 else s for s in stations], rotation=45, ha='right')
    axes[1, 1].set_yticklabels([s[:10] + '...' if len(s) > 10 else s for s in stations])
    
    # Agregar colorbar
    plt.colorbar(im, ax=axes[1, 1], shrink=0.8)
    
    plt.tight_layout()
    plt.show()
    
    # Crear reporte estadístico
    print("\n" + "="*60)
    print("REPORTE ESTADÍSTICO DE LA SIMULACIÓN")
    print("="*60)
    
    print(f"\nEstadísticas Generales:")
    print(f"- Promedio de pasajeros totales: {model_data['Total_Passengers'].mean():.1f}")
    print(f"- Máximo de pasajeros simultáneos: {model_data['Total_Passengers'].max()}")
    print(f"- Desviación estándar: {model_data['Total_Passengers'].std():.1f}")
    
    print(f"\nDistribución Promedio por Estados:")
    print(f"- En Partida: {model_data['Passengers_En_Partida'].mean():.1f} ({model_data['Passengers_En_Partida'].mean()/model_data['Total_Passengers'].mean()*100:.1f}%)")
    print(f"- En Viaje: {model_data['Passengers_En_Viaje'].mean():.1f} ({model_data['Passengers_En_Viaje'].mean()/model_data['Total_Passengers'].mean()*100:.1f}%)")
    print(f"- En Destino: {model_data['Passengers_En_Destino'].mean():.1f} ({model_data['Passengers_En_Destino'].mean()/model_data['Total_Passengers'].mean()*100:.1f}%)")
    
    print(f"\nTop 5 Estaciones más Concurridas:")
    station_totals = [(station, data['total']) for station, data in stations_data.items()]
    station_totals.sort(key=lambda x: x[1], reverse=True)
    for i, (station, total) in enumerate(station_totals[:5]):
        print(f"{i+1}. {station}: {total} pasajeros")

if __name__ == "__main__":
    # Ejecutar simulación con visualizaciones
    print("Ejecutando simulación...")
    results = run_simulation(steps=100)
    
    print("Creando visualizaciones...")
    create_visualizations(results)
