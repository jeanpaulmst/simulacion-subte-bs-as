
# Simulación del Tráfico de Pasajeros en la Línea A del Subte de Buenos Aires

## Proyecto de la materia Simulación  
**Universidad Tecnológica Nacional (UTN)**

### Autores
- Hsin Yu Lin  
- Masuet Juan Pablo  
- Ramiro de Coninck

## Pasos para ejecutar 
1- Clonar el repo localmente    
    ```git clone https://github.com/jeanpaulmst/simulacion-subte-bs-as.git```  
    ```cd ModeloTerminado```   

2- Crear un entorno virtual  
```python -m venv env``` 

3- Activar el entorno virtual  
```.\env\Scripts\activate``` (para Windows)  
```source env/bin/activate``` (para Linux)  


4- Instalar dependencias  
```pip install -r requirements.txt```  

5- Ejecuta la app con streamlit  
```streamlit run app.py```  



## Descripción

Este proyecto es un modelo de simulación basado en agentes que representa el flujo de pasajeros en las estaciones de la **Línea A** del subte de la Ciudad Autónoma de Buenos Aires.  
El modelo fue desarrollado con la librería **Mesa** de Python.

El objetivo es estudiar el comportamiento del tráfico de pasajeros entre estaciones en distintos momentos del tiempo.


## Tecnologías

- Python 3.x
- Librería [Mesa](https://mesa.readthedocs.io/en/stable/) (version 2.1.5) para simulaciones basadas en agentes
- UI con `streamlit` 

## Explicación del Modelo

### Agente: Pasajero

Cada **Pasajero** realiza un viaje entre dos estaciones, con los siguientes atributos:

- `partida`: estación de origen
- `destino`: estación de llegada
- `estado`: puede ser:
  - `en_partida`
  - `en_viaje`
  - `en_destino`
- `longitud`: cantidad de estaciones a recorrer

### Funcionamiento

1 - Cada estación genera una cantidad n de pasajeros en cada `step`. Esto se hace a través  
2 - A cada pasajero se le asigna una estación destino aleatoria (diferente a la partida).  
3 - Se calcula la longitud del recorrido según la distancia entre partida y destino.  
4 - En el primer `step`, el pasajero está `en_partida` y se contabiliza en la estación de origen.  
5 - En el siguiente `step`, pasa a `en_viaje` y la longitud disminuye en 1 por cada paso.  
6 - Cuando la longitud llega a 0, pasa a estado `en_destino` y se contabiliza en la estación de destino.



