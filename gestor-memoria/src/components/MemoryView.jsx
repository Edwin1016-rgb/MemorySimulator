import React from 'react';

export default function MemoryView({ ram, swap }) {
  const renderBloques = (memoria, label) => (
    <div>
      <h3 className="text-lg font-semibold mb-1">{label}</h3>
      <div className="flex gap-1 flex-wrap">
        {memoria?.map((b, i) => (
          <div
            key={i}
            className={`w-6 h-6 rounded ${b.pid ? "bg-red-500" : "bg-green-500"}`}
            title={b.pid ? `PID: ${b.pid}, Tamaño: ${b.size}, Tipo: ${b.tipo}` : "Libre"}
          ></div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-4 mb-4">
      {renderBloques(ram, "RAM")}
      {renderBloques(swap, "SWAP")}
    </div>
  );
}
