"use client"

import { useState, useEffect } from "react"
import { Play, Pause, RotateCcw, Settings, Train } from "lucide-react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts"

// Estaciones de la Línea A del Subte de Buenos Aires
const STATIONS = [
  "San Pedrito",
  "Piedra Buena",
  "Varela",
  "Medalla Milagrosa",
  "Acoyte",
  "Primera Junta",
  "Puan",
  "Carabobo",
  "Río de Janeiro",
  "Castro Barros",
  "Loria",
  "Plaza Miserere",
  "Alberti",
  "Pasco",
  "Congreso",
  "Sáenz Peña",
  "Lima",
  "Piedras",
  "Perú",
  "Plaza de Mayo",
]

interface PassengerData {
  id: string
  origin: string
  destination: string
  state: "en_partida" | "en_viaje" | "en_destino"
  travelLength: number
  step: number
  creationStep: number
}

interface StationData {
  name: string
  passengers: number
  departing: number
  arriving: number
  generationRate: number
}

interface SimulationData {
  step: number
  totalPassengers: number
  enPartida: number
  enViaje: number
  enDestino: number
}

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"]

export default function SubwaySimulation() {
  const [isRunning, setIsRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [simulationData, setSimulationData] = useState<SimulationData[]>([])
  const [currentStationData, setCurrentStationData] = useState<StationData[]>([])
  const [selectedStation, setSelectedStation] = useState<string>(STATIONS[0])
  const [allPassengers, setAllPassengers] = useState<PassengerData[]>([])
  const [speed, setSpeed] = useState(1000) // milliseconds

  // Inicializar datos de estaciones con tasas de generación
  useEffect(() => {
    const initialStationData: StationData[] = STATIONS.map((station) => ({
      name: station,
      passengers: 0,
      departing: 0,
      arriving: 0,
      generationRate: getStationGenerationRate(station),
    }))
    setCurrentStationData(initialStationData)
  }, [])

  // Obtener tasa de generación específica por estación
  const getStationGenerationRate = (station: string): number => {
    const rates: Record<string, number> = {
      "Plaza de Mayo": 25.0,
      Congreso: 20.0,
      "Plaza Miserere": 22.0,
      "Primera Junta": 18.0,
      "San Pedrito": 12.0,
    }
    return rates[station] || 15.0
  }

  // Generar pasajeros usando distribución de Poisson simulada
  const generatePassengers = (station: string, step: number): PassengerData[] => {
    const rate = getStationGenerationRate(station)
    // Simulación simple de Poisson usando aproximación normal para valores grandes
    const lambda = rate
    const passengerCount = Math.max(0, Math.floor(Math.random() * lambda + Math.random() * Math.sqrt(lambda)))

    const passengers: PassengerData[] = []

    for (let i = 0; i < passengerCount; i++) {
      const originIndex = STATIONS.indexOf(station)
      let destinationIndex = Math.floor(Math.random() * STATIONS.length)

      // Asegurar que el destino sea diferente al origen
      while (destinationIndex === originIndex) {
        destinationIndex = Math.floor(Math.random() * STATIONS.length)
      }

      const travelLength = Math.abs(destinationIndex - originIndex)

      passengers.push({
        id: `${station}-${step}-${i}`,
        origin: station,
        destination: STATIONS[destinationIndex],
        state: "en_partida",
        travelLength,
        step,
        creationStep: step,
      })
    }

    return passengers
  }

  // Actualizar estado de pasajeros existentes
  const updatePassengers = (passengers: PassengerData[], currentStep: number): PassengerData[] => {
    return passengers
      .map((passenger) => {
        if (passenger.state === "en_partida") {
          return { ...passenger, state: "en_viaje" as const }
        } else if (passenger.state === "en_viaje") {
          const newTravelLength = passenger.travelLength - 1
          if (newTravelLength <= 0) {
            return { ...passenger, state: "en_destino" as const, travelLength: 0 }
          }
          return { ...passenger, travelLength: newTravelLength }
        }
        return passenger
      })
      .filter((passenger) => {
        // Remover pasajeros que han estado en destino por más de 3 steps
        if (passenger.state === "en_destino") {
          const stepsInDestination =
            currentStep -
            passenger.creationStep -
            Math.abs(STATIONS.indexOf(passenger.destination) - STATIONS.indexOf(passenger.origin))
          return stepsInDestination <= 3
        }
        return true
      })
  }

  // Calcular datos de estaciones
  const calculateStationData = (passengers: PassengerData[]): StationData[] => {
    return STATIONS.map((station) => {
      const departing = passengers.filter((p) => p.origin === station && p.state === "en_partida").length
      const arriving = passengers.filter((p) => p.destination === station && p.state === "en_destino").length

      return {
        name: station,
        passengers: departing + arriving,
        departing,
        arriving,
        generationRate: getStationGenerationRate(station),
      }
    })
  }

  // Simular un step
  const simulateStep = () => {
    setCurrentStep((prevStep) => {
      const newStep = prevStep + 1

      setAllPassengers((prevPassengers) => {
        // 1. Generar nuevos pasajeros para cada estación
        const newPassengers: PassengerData[] = []
        STATIONS.forEach((station) => {
          newPassengers.push(...generatePassengers(station, newStep))
        })

        // 2. Actualizar pasajeros existentes
        const updatedPassengers = updatePassengers(prevPassengers, newStep)

        // 3. Combinar todos los pasajeros
        const allCurrentPassengers = [...updatedPassengers, ...newPassengers]

        // 4. Calcular datos de estaciones
        const stationData = calculateStationData(allCurrentPassengers)
        setCurrentStationData(stationData)

        // 5. Calcular datos de simulación
        const enPartida = allCurrentPassengers.filter((p) => p.state === "en_partida").length
        const enViaje = allCurrentPassengers.filter((p) => p.state === "en_viaje").length
        const enDestino = allCurrentPassengers.filter((p) => p.state === "en_destino").length

        const newSimulationData: SimulationData = {
          step: newStep,
          totalPassengers: allCurrentPassengers.length,
          enPartida,
          enViaje,
          enDestino,
        }

        setSimulationData((prev) => [...prev.slice(-49), newSimulationData])

        return allCurrentPassengers
      })

      return newStep
    })
  }

  // Control de simulación
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isRunning) {
      interval = setInterval(simulateStep, speed)
    }
    return () => clearInterval(interval)
  }, [isRunning, speed])

  const resetSimulation = () => {
    setIsRunning(false)
    setCurrentStep(0)
    setSimulationData([])
    setAllPassengers([])
    const resetStationData: StationData[] = STATIONS.map((station) => ({
      name: station,
      passengers: 0,
      departing: 0,
      arriving: 0,
      generationRate: getStationGenerationRate(station),
    }))
    setCurrentStationData(resetStationData)
  }

  const selectedStationData = currentStationData.find((s) => s.name === selectedStation)
  const currentSimData = simulationData[simulationData.length - 1]

  const pieData = currentSimData
    ? [
        { name: "En Partida", value: currentSimData.enPartida },
        { name: "En Viaje", value: currentSimData.enViaje },
        { name: "En Destino", value: currentSimData.enDestino },
      ]
    : []

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Train className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Simulación de Tráfico - Línea A Subte Buenos Aires</h1>
          </div>
          <p className="text-gray-600">
            Sistema de simulación basado en agentes para el análisis de flujo de pasajeros
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Controles de Simulación
            </h2>
          </div>
          <div className="flex items-center gap-4 flex-wrap">
            <button
              onClick={() => setIsRunning(!isRunning)}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-colors ${
                isRunning ? "bg-red-500 hover:bg-red-600 text-white" : "bg-blue-500 hover:bg-blue-600 text-white"
              }`}
            >
              {isRunning ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              {isRunning ? "Pausar" : "Iniciar"}
            </button>

            <button
              onClick={resetSimulation}
              className="flex items-center gap-2 px-4 py-2 rounded-md border border-gray-300 hover:bg-gray-50 transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
              Reiniciar
            </button>

            <div className="flex items-center gap-4">
              <span className="bg-gray-100 px-3 py-1 rounded-md font-medium">Step: {currentStep}</span>
              <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-md font-medium">
                Total Pasajeros: {currentSimData?.totalPassengers || 0}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-sm font-medium">Velocidad:</label>
              <select
                value={speed}
                onChange={(e) => setSpeed(Number(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1 text-sm"
              >
                <option value={2000}>Lenta (2s)</option>
                <option value={1000}>Normal (1s)</option>
                <option value={500}>Rápida (0.5s)</option>
                <option value={200}>Muy Rápida (0.2s)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Station Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Mapa de Estaciones - Línea A</h2>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {STATIONS.map((station, index) => {
                const stationData = currentStationData.find((s) => s.name === station)
                const passengers = stationData?.passengers || 0
                const isSelected = station === selectedStation

                return (
                  <div
                    key={station}
                    onClick={() => setSelectedStation(station)}
                    className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-4 h-4 rounded-full ${
                          passengers > 50 ? "bg-red-500" : passengers > 25 ? "bg-yellow-500" : "bg-green-500"
                        }`}
                      />
                      <span className="font-medium text-sm">{station}</span>
                    </div>
                    <div className="flex gap-2">
                      <span className="bg-gray-100 px-2 py-1 rounded text-xs font-medium">{passengers}</span>
                      {stationData && (
                        <>
                          <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs">
                            ↑{stationData.departing}
                          </span>
                          <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs">
                            ↓{stationData.arriving}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Detalles de Estación: {selectedStation}</h2>
            {selectedStationData ? (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{selectedStationData.passengers}</div>
                    <div className="text-sm text-gray-600">Total Pasajeros</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{selectedStationData.departing}</div>
                    <div className="text-sm text-gray-600">En Partida</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{selectedStationData.arriving}</div>
                    <div className="text-sm text-gray-600">En Destino</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-semibold">Información de la Estación:</h4>
                  <div className="text-sm text-gray-600">
                    <p>Tasa de generación: {selectedStationData.generationRate} pasajeros/step</p>
                    <p>
                      Posición en línea: {STATIONS.indexOf(selectedStation) + 1} de {STATIONS.length}
                    </p>
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs">En Partida</span>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">En Viaje</span>
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">En Destino</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">Inicie la simulación para ver los datos</div>
            )}
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Evolución Temporal de Pasajeros</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={simulationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="step" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="totalPassengers" stroke="#3b82f6" strokeWidth={2} name="Total" />
                  <Line type="monotone" dataKey="enPartida" stroke="#10b981" strokeWidth={2} name="En Partida" />
                  <Line type="monotone" dataKey="enViaje" stroke="#f59e0b" strokeWidth={2} name="En Viaje" />
                  <Line type="monotone" dataKey="enDestino" stroke="#8b5cf6" strokeWidth={2} name="En Destino" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Distribución por Estados</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Distribución Actual por Estación</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={currentStationData} margin={{ bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={10} interval={0} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="passengers" fill="#3b82f6" name="Total" />
                <Bar dataKey="departing" fill="#10b981" name="Partida" />
                <Bar dataKey="arriving" fill="#8b5cf6" name="Destino" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Statistics */}
        {currentSimData && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Estadísticas de la Simulación</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-700">{simulationData.length}</div>
                <div className="text-sm text-gray-600">Steps Ejecutados</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {simulationData.length > 0
                    ? Math.round(simulationData.reduce((sum, d) => sum + d.totalPassengers, 0) / simulationData.length)
                    : 0}
                </div>
                <div className="text-sm text-gray-600">Promedio Pasajeros</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {Math.max(...simulationData.map((d) => d.totalPassengers), 0)}
                </div>
                <div className="text-sm text-gray-600">Máximo Simultáneo</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {currentStationData.reduce((max, station) => Math.max(max, station.passengers), 0)}
                </div>
                <div className="text-sm text-gray-600">Estación más Concurrida</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
