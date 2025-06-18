from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from modelo_subte import ModeloSubte, Estacion

def portrayal_estacion(agent):
    if not isinstance(agent, Estacion):
        return

    porcentaje = agent.pasajeros_actuales / agent.capacidad_maxima
    if porcentaje < 0.5:
        color = "green"
    elif porcentaje < 0.9:
        color = "yellow"
    else:
        color = "red"

    return {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "Filled": "true",
        "Layer": 0,
        "Color": color,
        "text": f"{agent.nombre}\n{agent.pasajeros_actuales}",
        "text_color": "black",
    }

num_estaciones = len(ModeloSubte().estaciones)
grid = CanvasGrid(portrayal_estacion, num_estaciones, 1, 40 * num_estaciones, 80)

server = ModularServer(
    ModeloSubte,
    [grid],
    "Simulación del Subte (Línea A)",
    {}
)

server.port = 8521
server.launch()
