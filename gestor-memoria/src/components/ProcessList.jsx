import React from 'react';

export default function ProcessList({ estado }) {
  // Extraemos procesos activos únicos de RAM
  const procesosActivos = estado?.ram
    ? Array.from(new Set(estado.ram.map(bloque => bloque.pid).filter(pid => pid !== null)))
    : [];

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Procesos</h3>
      <div>Activos: {procesosActivos.length}</div>
      <div>
        Lista: {procesosActivos.length > 0 ? procesosActivos.join(", ") : "Ninguno"}
      </div>
      {/* Si tienes datos para en espera o pendientes, agregar aquí */}
      <div>En espera: {/* ... */}</div>
      <div>Pendientes: {/* ... */}</div>
    </div>
  );
}
