import React, { useState } from 'react';
import { iniciarSimulacion, siguienteTick, resetSimulacion } from "../api/schedulerApi";
import MemoryView from "../components/MemoryView";
import ProcessList from "../components/ProcessList";
import StatsPanel from "../components/StatsPanel";

export default function Home() {
  const [estado, setEstado] = useState(null);
  const [eventos, setEventos] = useState([]);

  const handleIniciar = async () => {
    await iniciarSimulacion();
    const res = await siguienteTick();
    setEstado(res.data);
  };

  const handleTick = async () => {
    const res = await siguienteTick();
    setEstado(res.data);
    if (res.data.eventos) setEventos(prev => [...prev, ...res.data.eventos]);
  };

  const handleReset = async () => {
    await resetSimulacion();
    setEstado(null);
    setEventos([]);
  };

  return (
    <div className="grid grid-cols-3 gap-4 p-4">
      <div className="col-span-2">
        <MemoryView ram={estado?.ram} swap={estado?.swap} />
        <ProcessList estado={estado} />
      </div>
      <div className="col-span-1 space-y-6">
        <StatsPanel estado={estado} eventos={eventos} />
        <div className="flex justify-between space-x-2">
          <button className="btn btn-primary" onClick={handleIniciar}>Iniciar</button>
          <button className="btn btn-secondary" onClick={handleTick}>Tick</button>
          <button className="btn btn-accent" onClick={handleReset}>Reset</button>
        </div>
      </div>
    </div>
  );
}
