import copy
from collections import deque

class MemoryManager:
    def __init__(self, ram_size=1024, swap_size=2048):
        """
        ram_size, swap_size: tamaños totales en KB
        """
        self.ram_size = ram_size
        self.swap_size = swap_size
        self.next_fit_pointer = 0  
        self.lru_order = deque()   
        self.procesos_activos = {} 
        self.reset()

    def reset(self):
        self.ram = [{"pid": None, "size": self.ram_size, "tipo": "libre"}]
        self.swap = [{"pid": None, "size": self.swap_size, "tipo": "libre"}]
        self.next_fit_pointer = 0
        self.lru_order.clear()
        self.procesos_activos.clear()

    def asignar_proceso(self, proceso):
        """
        Asigna un proceso a memoria según modo y estrategia.
        Ahora incluye tracking para liberación posterior.
        """
        pid = proceso["pid"]
        mode = proceso.get("mode", "contigua")
        asignacion = proceso.get("asignacion", "variable")
        estrategia = proceso.get("estrategia", "first_fit")
        
        # Registrar proceso para tracking
        self.procesos_activos[pid] = {
            "tiempo_restante": proceso.get("tiempo_ejecucion", 5),
            "tiempo_cpu_restante": proceso.get("tiempo_cpu", 3),
            "ubicacion": "ram",  # ram o swap
            "priority": proceso.get("priority", 1),
            "size": proceso["size"],
            "last_access": 0  # Para LRU
        }

        # Intentar asignar inicialmente
        asignado = False
        if mode == "contigua":
            asignado = self.asignacion_contigua(proceso, asignacion, estrategia)
        elif mode == "segmentacion":
            asignado = self.asignacion_segmentacion(proceso)
        elif mode == "paginacion":
            asignado = self.asignacion_paginacion(proceso)

        if not asignado:
            # Intentar swap inteligente para liberar espacio
            asignado = self.swap_inteligente(proceso)

        if not asignado:
            # Remover del tracking si no se pudo asignar
            del self.procesos_activos[pid]
            raise MemoryError(f"No se pudo asignar proceso {pid}: memoria llena")

        # Actualizar LRU
        if pid in self.lru_order:
            self.lru_order.remove(pid)
        self.lru_order.append(pid)

        return True

    def liberar_proceso(self, pid):
        """
        Libera toda la memoria ocupada por un proceso.
        """
        if pid not in self.procesos_activos:
            return False

        # Liberar de RAM
        for bloque in self.ram:
            if bloque["pid"] == pid:
                bloque["pid"] = None
                bloque["tipo"] = "libre"

        # Liberar de SWAP
        for bloque in self.swap:
            if bloque["pid"] == pid:
                bloque["pid"] = None
                bloque["tipo"] = "libre"

        # Fusionar bloques libres
        self.fusionar_bloques_libres()
        self.fusionar_bloques_libres_swap()
        
        # Remover del tracking
        if pid in self.procesos_activos:
            del self.procesos_activos[pid]
        
        # Remover de LRU
        if pid in self.lru_order:
            self.lru_order.remove(pid)

        return True

    def tick_procesos(self):
        """
        Actualiza el tiempo de ejecución de todos los procesos.
        Retorna lista de PIDs que terminaron.
        """
        procesos_terminados = []
        
        for pid, info in list(self.procesos_activos.items()):
            info["tiempo_restante"] -= 1
            if info["tiempo_restante"] <= 0:
                procesos_terminados.append(pid)
                self.liberar_proceso(pid)

        return procesos_terminados

    ### Asignación Contigua Mejorada ###
    def asignacion_contigua(self, proceso, asignacion, estrategia):
        size = proceso["size"]
        if asignacion == "fija":
            return self.asignacion_fija(proceso, size)
        else:
            idx = self.buscar_bloque_libre(estrategia, size)
            if idx is None:
                return False
            return self.ocupar_bloque(idx, proceso, size, "contigua")

    def asignacion_fija(self, proceso, size):
        """Asignación de bloques fijos (simulación simple)"""
        for i, bloque in enumerate(self.ram):
            if bloque["pid"] is None and bloque["size"] >= size:
                # En bloques fijos, usamos todo el bloque
                bloque["pid"] = proceso["pid"]
                bloque["tipo"] = "contigua_fija"
                return True
        return False

    def buscar_bloque_libre(self, estrategia, size):
        bloques_libres = [(i, b) for i, b in enumerate(self.ram) 
                         if b["pid"] is None and b["size"] >= size]
        
        if not bloques_libres:
            return None
            
        if estrategia == "first_fit":
            return bloques_libres[0][0]
        elif estrategia == "best_fit":
            return min(bloques_libres, key=lambda x: x[1]["size"])[0]
        elif estrategia == "worst_fit":
            return max(bloques_libres, key=lambda x: x[1]["size"])[0]
        elif estrategia == "next_fit":
            return self.next_fit_buscar(bloques_libres, size)
        else:
            return bloques_libres[0][0]

    def next_fit_buscar(self, bloques_libres, size):
        """Implementación mejorada de Next Fit"""
        # Buscar desde el puntero actual hacia adelante
        for idx, bloque in bloques_libres:
            if idx >= self.next_fit_pointer:
                self.next_fit_pointer = idx
                return idx
        
        # Si no encuentra, reiniciar desde el principio
        if bloques_libres:
            self.next_fit_pointer = bloques_libres[0][0]
            return bloques_libres[0][0]
        
        return None

    def ocupar_bloque(self, idx, proceso, size, tipo):
        bloque = self.ram[idx]
        if bloque["size"] == size:
            bloque["pid"] = proceso["pid"]
            bloque["tipo"] = tipo
        else:
            bloque_asignado = {"pid": proceso["pid"], "size": size, "tipo": tipo}
            bloque_libre = {"pid": None, "size": bloque["size"] - size, "tipo": "libre"}
            self.ram[idx] = bloque_asignado
            self.ram.insert(idx + 1, bloque_libre)
        
        self.fusionar_bloques_libres()
        return True

    def fusionar_bloques_libres(self):
        """Fusiona bloques libres adyacentes en RAM"""
        i = 0
        while i < len(self.ram) - 1:
            if self.ram[i]["pid"] is None and self.ram[i + 1]["pid"] is None:
                self.ram[i]["size"] += self.ram[i + 1]["size"]
                del self.ram[i + 1]
            else:
                i += 1

    def fusionar_bloques_libres_swap(self):
        """Fusiona bloques libres adyacentes en SWAP"""
        i = 0
        while i < len(self.swap) - 1:
            if self.swap[i]["pid"] is None and self.swap[i + 1]["pid"] is None:
                self.swap[i]["size"] += self.swap[i + 1]["size"]
                del self.swap[i + 1]
            else:
                i += 1

    ### Asignación Segmentación ###
    def asignacion_segmentacion(self, proceso):
        segmentos = proceso.get("segmentos", [proceso["size"]])
        segmentos_asignados = []
        
        for seg_size in segmentos:
            idx = self.buscar_bloque_libre("best_fit", seg_size)
            if idx is None:
                # Deshacer asignaciones parciales
                for seg_idx in segmentos_asignados:
                    self.ram[seg_idx]["pid"] = None
                    self.ram[seg_idx]["tipo"] = "libre"
                self.fusionar_bloques_libres()
                return False
            
            self.ocupar_bloque(idx, {"pid": proceso["pid"]}, seg_size, "segmento")
            segmentos_asignados.append(idx)
        
        return True

    ### Asignación Paginación ###
    def asignacion_paginacion(self, proceso):
        PAGE_SIZE = 64
        paginas_necesarias = (proceso["size"] + PAGE_SIZE - 1) // PAGE_SIZE
        paginas_asignadas = []
        
        for _ in range(paginas_necesarias):
            idx = self.buscar_bloque_libre("first_fit", PAGE_SIZE)
            if idx is None:
                # Deshacer asignaciones parciales
                for pag_idx in paginas_asignadas:
                    self.ram[pag_idx]["pid"] = None
                    self.ram[pag_idx]["tipo"] = "libre"
                self.fusionar_bloques_libres()
                return False
            
            self.ocupar_bloque(idx, {"pid": proceso["pid"]}, PAGE_SIZE, "pagina")
            paginas_asignadas.append(idx)
        
        return True

    ### Swap Inteligente ###
    def swap_inteligente(self, proceso_nuevo):
        """
        Algoritmo inteligente de swap basado en:
        1. Prioridad (menor prioridad sale primero)
        2. LRU (Least Recently Used)
        3. Tamaño (procesos grandes si es necesario)
        """
        size_needed = proceso_nuevo["size"]
        priority_nuevo = proceso_nuevo.get("priority", 1)
        
        # Encontrar candidatos para swap (menor prioridad que el nuevo)
        candidatos = []
        for pid, info in self.procesos_activos.items():
            if (info["ubicacion"] == "ram" and 
                info["priority"] >= priority_nuevo and 
                pid != proceso_nuevo["pid"]):
                candidatos.append((pid, info))
        
        if not candidatos:
            return False
        
        # Ordenar por prioridad (mayor primero) y luego por LRU
        candidatos.sort(key=lambda x: (x[1]["priority"], 
                                     list(self.lru_order).index(x[0]) 
                                     if x[0] in self.lru_order else 0))
        
        # Intentar mover candidatos hasta liberar suficiente espacio
        espacio_liberado = 0
        for pid, info in candidatos:
            if self.mover_a_swap(pid):
                espacio_liberado += info["size"]
                if espacio_liberado >= size_needed:
                    # Intentar asignar el nuevo proceso
                    return self.asignar_proceso_directo(proceso_nuevo)
        
        return False

    def asignar_proceso_directo(self, proceso):
        """Asigna proceso sin recursión infinita"""
        mode = proceso.get("mode", "contigua")
        asignacion = proceso.get("asignacion", "variable")
        estrategia = proceso.get("estrategia", "first_fit")

        if mode == "contigua":
            return self.asignacion_contigua(proceso, asignacion, estrategia)
        elif mode == "segmentacion":
            return self.asignacion_segmentacion(proceso)
        elif mode == "paginacion":
            return self.asignacion_paginacion(proceso)
        return False

    def mover_a_swap(self, pid):
        """Mueve un proceso de RAM a SWAP"""
        if pid not in self.procesos_activos:
            return False
        
        bloques_proceso = [b for b in self.ram if b["pid"] == pid]
        total_size = sum(b["size"] for b in bloques_proceso)
        
        # Buscar espacio en swap
        idx_swap = self.buscar_bloque_libre_swap(total_size)
        if idx_swap is None:
            return False
        
        # Mover a swap
        self.ocupar_bloque_swap(idx_swap, pid, total_size)
        
        # Liberar de RAM
        for bloque in self.ram:
            if bloque["pid"] == pid:
                bloque["pid"] = None
                bloque["tipo"] = "libre"
        
        self.fusionar_bloques_libres()
        
        # Actualizar ubicación
        self.procesos_activos[pid]["ubicacion"] = "swap"
        
        return True

    def buscar_bloque_libre_swap(self, size):
        bloques_libres = [(i, b) for i, b in enumerate(self.swap) 
                         if b["pid"] is None and b["size"] >= size]
        if not bloques_libres:
            return None
        return min(bloques_libres, key=lambda x: x[1]["size"])[0]  # Best fit

    def ocupar_bloque_swap(self, idx, pid, size):
        bloque = self.swap[idx]
        if bloque["size"] == size:
            bloque["pid"] = pid
            bloque["tipo"] = "swap"
        else:
            bloque_asignado = {"pid": pid, "size": size, "tipo": "swap"}
            bloque_libre = {"pid": None, "size": bloque["size"] - size, "tipo": "libre"}
            self.swap[idx] = bloque_asignado
            self.swap.insert(idx + 1, bloque_libre)
        
        self.fusionar_bloques_libres_swap()

    def obtener_estadisticas(self):
        """Obtiene estadísticas del estado actual de memoria"""
        ram_ocupada = sum(b["size"] for b in self.ram if b["pid"] is not None)
        swap_ocupado = sum(b["size"] for b in self.swap if b["pid"] is not None)
        
        return {
            "ram_total": self.ram_size,
            "ram_ocupada": ram_ocupada,
            "ram_libre": self.ram_size - ram_ocupada,
            "swap_total": self.swap_size,
            "swap_ocupado": swap_ocupado,
            "swap_libre": self.swap_size - swap_ocupado,
            "procesos_activos": len(self.procesos_activos),
            "fragmentacion_ram": len([b for b in self.ram if b["pid"] is None])
        }
    def obtener_estado_memoria(self):
        """Devuelve solo el estado de la memoria (RAM y SWAP)"""
        stats = self.obtener_estadisticas()
        
        return {
            "ram": {
                "bloques": self.ram,
                "total": self.ram_size,
                "usada": stats["ram_ocupada"],
                "libre": stats["ram_libre"],
                "fragmentacion": stats["fragmentacion_ram"]
            },
            "swap": {
                "bloques": self.swap,
                "total": self.swap_size,
                "usada": stats["swap_ocupado"],
                "libre": stats["swap_libre"]
            },
            "procesos_activos": {
                pid: {
                    "size": info["size"],
                    "ubicacion": info["ubicacion"],
                    "tiempo_restante": info["tiempo_restante"]
                }
                for pid, info in self.procesos_activos.items()
            }
    }
    def __repr__(self):
        stats = self.obtener_estadisticas()
        return f"RAM: {self.ram}\nSWAP: {self.swap}\nStats: {stats}"