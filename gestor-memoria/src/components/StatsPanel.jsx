import React from 'react';

export default function StatsPanel({ estado, eventos }) {
  // Datos de memoria ahora vienen estructurados
  const ram = estado?.memoria?.ram || { total: 0, usada: 0 };
  const swap = estado?.memoria?.swap || { total: 0, usada: 0 };
  
  // Calcular porcentajes
  const ramPorcentaje = ram.total > 0 ? ((ram.usada / ram.total) * 100).toFixed(1) : 0;
  const swapPorcentaje = swap.total > 0 ? ((swap.usada / swap.total) * 100).toFixed(1) : 0;

  return (
    <div className="space-y-4 ">
      <h3 className="text-lg font-semibold mb-2">Estadísticas</h3>
      
      <div className="bg-blue-500 p-3 rounded">
        <h4 className="font-medium">RAM</h4>
        <div>{ram.usada} / {ram.total} KB ({ramPorcentaje}%)</div>
        <div className="w-full bg-gray-200 rounded-full h-2.5 mt-1">
          <div 
            className="bg-blue-600 h-2.5 rounded-full" 
            style={{ width: `${ramPorcentaje}%` }}
          ></div>
        </div>
      </div>

      <div className="bg-purple-500 p-3 rounded">
        <h4 className="font-medium">SWAP</h4>
        <div>{swap.usada} / {swap.total} KB ({swapPorcentaje}%)</div>
        <div className="w-full bg-gray-200 rounded-full h-2.5 mt-1">
          <div 
            className="bg-purple-600 h-2.5 rounded-full" 
            style={{ width: `${swapPorcentaje}%` }}
          ></div>
        </div>
      </div>

      <div className="bg-red-500 p-3 rounded">
        <h4 className="font-medium">Fragmentación</h4>
        <div>{ram.total - ram.usada} KB libres en {estado?.memoria?.ram?.fragmentacion || 0} bloques</div>
      </div>

      <div className="bg-green-500 p-3 rounded">
        <h4 className="font-medium">Métricas</h4>
        <div>Tick actual: {estado?.tick_actual || 0}</div>
        <div>Estado: {estado?.finished ? "Completado" : "En ejecución"}</div>
      </div>

      <div className="mt-4">
        <h4 className="font-semibold">Eventos recientes</h4>
        <ul className="list-disc ml-5 max-h-40 overflow-y-auto bg-gray-50 p-2 rounded">
          {eventos?.length === 0 && <li className="text-gray-500">No hay eventos</li>}
          {eventos?.map((ev, i) => (
            <li key={i} className="text-sm py-1">{ev}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}