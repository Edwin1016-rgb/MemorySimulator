import React, { useState, useEffect } from 'react';
import { iniciarSimulacion, siguienteTick, resetSimulacion, obtenerEstado } from "../api/schedulerApi";
import MemoryView from "../components/MemoryView";
import ProcessList from "../components/ProcessList";
import StatsPanel from "../components/StatsPanel";

export default function Home() {
  const [estado, setEstado] = useState(null);
  const [eventos, setEventos] = useState([]);
  const [cargando, setCargando] = useState(false);

  // Función para cargar el estado actualizado
  const cargarEstado = async () => {
    setCargando(true);
    try {
      const res = await obtenerEstado();
      if (res.data.success) {
        console.log("🔥 Estado completo:", res.data.data);
        setEstado(res.data.data);
        console.log("Contenido RAM:", res.data.data.memoria?.ram?.contenido);
        console.log("Contenido SWAP:", res.data.data.memoria?.swap?.contenido);
        // Mantener solo los últimos 20 eventos para no saturar la UI
        if (res.data.data.eventos) {
          setEventos(prev => [...res.data.data.eventos.slice(0, 5), ...prev.slice(0, 15)]);
        }
      }
    } catch (error) {
      console.error("Error al cargar estado:", error);
    } finally {
      setCargando(false);
    }
  };

  const handleIniciar = async () => {
    await iniciarSimulacion();
    await cargarEstado();
  };

  const handleTick = async () => {
    await siguienteTick();
    await cargarEstado();
  };

  const handleReset = async () => {
    await resetSimulacion();
    setEstado(null);
    setEventos([]);
  };

  // Cargar estado inicial al montar el componente
  useEffect(() => {
    cargarEstado();
  }, []);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4 min-h-screen ">
      <h1 className="text-2xl font-bold mb-4 col-span-3">Gestor de Memoria - Sistemas Operativos</h1>
      {/* Panel principal */}
      <div className="lg:col-span-2 space-y-4">
        <MemoryView 
            ram={estado?.memoria?.ram} 
            swap={estado?.memoria?.swap} 
            cargando={cargando}
        />
        <ProcessList estado={estado} cargando={cargando} />
      </div>

      {/* Sidebar */}
      <div className="lg:col-span-1 space-y-6">
        <StatsPanel 
          estado={estado} 
          eventos={eventos} 
          cargando={cargando} 
        />
        
        <div className="flex flex-col sm:flex-row lg:flex-col gap-2 bg-white p-4 rounded-lg shadow">
          <button 
            className="btn btn-primary flex-1" 
            onClick={handleIniciar}
            disabled={cargando}
          >
            {cargando ? 'Cargando...' : 'Iniciar'}
          </button>
          <button 
            className="btn btn-secondary flex-1" 
            onClick={handleTick}
            disabled={cargando || estado?.finished}
          >
            {estado?.finished ? 'Completado' : 'Siguiente Tick'}
          </button>
          <button 
            className="btn btn-accent flex-1" 
            onClick={handleReset}
            disabled={cargando}
          >
            Reiniciar
          </button>
        </div>
      </div>
    </div>
  );
}