import React from 'react';

export default function MemoryView({ ram, swap, cargando }) { 
  // Función para renderizar los bloques de memoria
  console.log("RAM data:", ram);
  console.log("SWAP data:", swap);

  const renderBloques = (memoria, label) => (
    <div>
      <h3 className="text-lg font-semibold mb-1">{label}</h3>
      <div className="flex gap-1 flex-wrap">
        {/* Verificamos si hay bloques en memoria y los renderizamos */}
        {memoria?.bloques && memoria.bloques.length > 0 ? memoria.bloques.map((bloque, i) => {
          let estiloBloque = "w-8 h-8 rounded m-1"; // Tamaño de cada bloque
          let title = "Libre";
          let color = "bg-gray-700"; // Libre por defecto

          // Si el bloque tiene un PID, se ajustan los estilos según el tipo de memoria
          if (bloque.pid) {
            title = `PID: ${bloque.pid}, Tamaño: ${bloque.size}, Tipo: ${bloque.tipo}`;
            if (bloque.tipo === "contigua") {
              color = "bg-blue-500"; // Contigua
            } else if (bloque.tipo === "pagina") {
              color = "bg-purple-500"; // Paginación
              estiloBloque = "w-8 h-8 rounded m-1 bg-opacity-75"; // Sombra para paginación
            } else if (bloque.tipo === "segmento") {
              color = "bg-green-500"; // Segmentación
              estiloBloque = "w-8 h-8 rounded m-1 border-2 border-green-700"; // Borde para segmentación
            } else {
              color = "bg-amber-900"; // Default color for other types (like swap)
            }
          } else {
            // Si no tiene un PID, se podría considerar un bloque libre
            color = "bg-gray-500"; // No asignado o libre
          }

          return (
            <div
              key={i}
              className={`${estiloBloque} ${color}`}
              title={title}
            ></div>
          );
        }) : <p>No hay bloques en la memoria.</p>}
      </div>
    </div>
  );

  return (
    <div className="space-y-4 mb-4">
      {cargando ? (
        <p>Cargando...</p>
      ) : (
        <>
          {renderBloques(ram, "RAM")}
          {renderBloques(swap, "SWAP")}
        </>
      )}
    </div>
  );
}
