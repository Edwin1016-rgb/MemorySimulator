import React from 'react';

export default function StatsPanel({ estado, eventos }) {
  const calcularOcupada = (memoria) => {
    if (!memoria) return 0;
    return memoria.reduce((acc, bloque) => bloque.pid ? acc + bloque.size : acc, 0);
  };

  const ramOcupada = calcularOcupada(estado?.ram);
  const swapOcupada = calcularOcupada(estado?.swap);
  const ramTotal = estado?.ram ? estado.ram.reduce((acc, b) => acc + b.size, 0) : 0;
  const swapTotal = estado?.swap ? estado.swap.reduce((acc, b) => acc + b.size, 0) : 0;
  const fragmentacion = ramTotal - ramOcupada;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Estadísticas</h3>
      <div>RAM ocupada: {ramOcupada} / {ramTotal}</div>
      <div>SWAP ocupada: {swapOcupada} / {swapTotal}</div>
      <div>Fragmentación: {fragmentacion}</div>
      <h4 className="mt-4 font-semibold">Eventos recientes</h4>
      <ul className="list-disc ml-5 max-h-40 overflow-auto">
        {eventos.length === 0 && <li>No hay eventos</li>}
        {eventos.map((ev, i) => (
          <li key={i}>{ev}</li>
        ))}
      </ul>
    </div>
  );
}
