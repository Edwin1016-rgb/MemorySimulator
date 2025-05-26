import React from 'react';

export default function ProcessList({ estado }) {
  // Procesos activos ahora vienen directamente de procesos_activos
  const procesosActivos = estado?.procesos?.activos 
    ? Object.keys(estado.procesos.activos) 
    : [];

  const procesosEnEspera = estado?.procesos?.en_espera || [];
  const procesosTerminados = estado?.procesos?.terminados || [];
  const procesosPendientes = estado?.procesos?.pendientes || [];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold mb-2">Procesos</h3>
      
      <div className="bg-blue-500 p-3 rounded">
        <h4 className="font-medium">Activos: {procesosActivos.length}</h4>
        <div className="text-sm">
          {procesosActivos.length > 0 
            ? procesosActivos.join(", ") 
            : "Ninguno"}
        </div>
      </div>

      <div className="bg-yellow-500 p-3 rounded">
        <h4 className="font-medium">En espera: {procesosEnEspera.length}</h4>
        {procesosEnEspera.length > 0 && (
          <div className="text-sm">
            {procesosEnEspera.map(p => p.pid).join(", ")}
          </div>
        )}
      </div>

      <div className="bg-green-500 p-3 rounded">
        <h4 className="font-medium">Terminados: {procesosTerminados.length}</h4>
        {procesosTerminados.length > 0 && (
          <div className="text-sm">
            {procesosTerminados.join(", ")}
          </div>
        )}
      </div>

      <div className="bg-gray-500 p-3 rounded">
        <h4 className="font-medium">Pendientes: {procesosPendientes.length}</h4>
        {procesosPendientes.length > 0 && (
          <div className="text-sm">
            {procesosPendientes.map(p => p.pid).join(", ")}
          </div>
        )}
      </div>
    </div>
  );
}