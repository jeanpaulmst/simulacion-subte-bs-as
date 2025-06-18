import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Play, Pause, RotateCcw, Settings } from "lucide-react"
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
}

interface StationData {
  name: string
  passengers: number
  departing: number
  arriving: number
}

interface SimulationData {
  step: number
  stations: StationData[]
  totalPassengers: number
}

export default function SubwaySimulation() {
  const [isRunning, setIsRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [simulationData, setSimulationData] = useState<SimulationData[]>([])
  const [currentStationData, setCurrentStationData] = useState<StationData[]>([])
  const [selectedStation, setSelectedStation] = useState<string>(STATIONS[0])

  // Simular generación de pasajeros basada en distribución aleatoria
  const generatePassengers = (station: string, step: number): PassengerData[] => {
    const baseRate = Math.random() * 20 + 5 // Entre 5 y 25 pasajeros por step
    const passengerCount = Math.floor(Math.random() * baseRate)
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
      })
    }

    return passengers
  }

  // Calcular datos de estaciones
  const calculateStationData = (allPassengers: PassengerData[]): StationData[] => {
    return STATIONS.map((station) => {
      const departing = allPassengers.filter((p) => p.origin === station && p.state === "en_partida").length

      const arriving = allPassengers.filter(
        (p) => p.destination === station && p.state === "en_destino" && p.travelLength === 0,
      ).length

      return {
        name: station,
        passengers: departing + arriving,
        departing,
        arriving,
      }
    })
  }

  // Simular un step
  const simulateStep = () => {
    setCurrentStep((prev) => {
      const newStep = prev + 1

      // Generar nuevos pasajeros para cada estación
      const newPassengers: PassengerData[] = []
      STATIONS.forEach((station) => {
        newPassengers.push(...generatePassengers(station, newStep))
      })

      // Actualizar pasajeros existentes
      const updatedPassengers =
        simulationData.length > 0
          ? simulationData[simulationData.length - 1].stations.flatMap((station) =>
              // Simular pasajeros en viaje
              Array.from({ length: Math.floor(Math.random() * 10) }, (_, i) => ({
                id: `traveling-${newStep}-${i}`,
                origin: station.name,
                destination: STATIONS[Math.floor(Math.random() * STATIONS.length)],
                state: "en_viaje" as const,
                travelLength: Math.max(0, Math.floor(Math.random() * 5)),
                step: newStep,
              })),
            )
          : []

      const allPassengers = [...newPassengers, ...updatedPassengers]
      const stationData = calculateStationData(allPassengers)

      setCurrentStationData(stationData)

      const newSimulationData: SimulationData = {
        step: newStep,
        stations: stationData,
        totalPassengers: allPassengers.length,
      }

      setSimulationData((prev) => [...prev.slice(-19), newSimulationData])

      return newStep
    })
  }

  // Control de simulación
  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isRunning) {
      interval = setInterval(simulateStep, 1000)
    }
    return () => clearInterval(interval)
  }, [isRunning, simulationData])

  const resetSimulation = () => {
    setIsRunning(false)
    setCurrentStep(0)
    setSimulationData([])
    setCurrentStationData([])
  }

  const selectedStationData = currentStationData.find((s) => s.name === selectedStation)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">Simulación de Tráfico - Línea A Subte Buenos Aires</h1>
          <p className="text-gray-600">
            Sistema de simulación basado en agentes para el análisis de flujo de pasajeros
          </p>
        </div>

        {/* Controls */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Controles de Simulación
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Button
                onClick={() => setIsRunning(!isRunning)}
                variant={isRunning ? "destructive" : "default"}
                className="flex items-center gap-2"
              >
                {isRunning ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                {isRunning ? "Pausar" : "Iniciar"}
              </Button>
              <Button onClick={resetSimulation} variant="outline" className="flex items-center gap-2">
                <RotateCcw className="h-4 w-4" />
                Reiniciar
              </Button>
              <Badge variant="secondary" className="text-lg px-4 py-2">
                Step: {currentStep}
              </Badge>
              <Badge variant="outline" className="text-lg px-4 py-2">
                Total Pasajeros: {currentStationData.reduce((sum, s) => sum + s.passengers, 0)}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Station Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Mapa de Estaciones - Línea A</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
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
                        <span className="font-medium">{station}</span>
                      </div>
                      <div className="flex gap-2">
                        <Badge variant="secondary">{passengers}</Badge>
                        {stationData && (
                          <>
                            <Badge variant="outline" className="text-green-600">
                              ↑{stationData.departing}
                            </Badge>
                            <Badge variant="outline" className="text-blue-600">
                              ↓{stationData.arriving}
                            </Badge>
                          </>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Detalles de Estación: {selectedStation}</CardTitle>
            </CardHeader>
            <CardContent>
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
                    <h4 className="font-semibold">Estados de Pasajeros:</h4>
                    <div className="flex gap-2">
                      <Badge className="bg-yellow-100 text-yellow-800">En Partida</Badge>
                      <Badge className="bg-blue-100 text-blue-800">En Viaje</Badge>
                      <Badge className="bg-green-100 text-green-800">En Destino</Badge>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">Inicie la simulación para ver los datos</div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Flujo de Pasajeros por Tiempo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={simulationData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="step" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="totalPassengers"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      name="Total Pasajeros"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Distribución Actual por Estación</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={currentStationData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={10} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="passengers" fill="#3b82f6" name="Total" />
                    <Bar dataKey="departing" fill="#10b981" name="Partida" />
                    <Bar dataKey="arriving" fill="#8b5cf6" name="Destino" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
