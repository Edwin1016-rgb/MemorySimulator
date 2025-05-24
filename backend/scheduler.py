from memory_manager import MemoryManager
import json
from collections import deque

class Scheduler:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.load_processes()
        self.current_tick = 0
        self.procesos_terminados = []
        self.procesos_en_espera = deque()
        self.finished = False
        self.estadisticas = {
            "procesos_ejecutados": 0,
            "procesos_fallidos": 0,
            "tiempo_total": 0,
            "swaps_realizados": 0
        }

    def load_processes(self):
        with open("data/procesos.json", "r") as f:
            self.process_list = json.load(f)
        
        # Ordenar por tiempo de llegada
        self.process_list.sort(key=lambda p: p.get("tiempo_llegada", 0))
        self.procesos_pendientes = self.process_list.copy()

    def tick(self):
        """
        Simula un tick del sistema:
        1. Actualiza tiempo de procesos activos
        2. Libera procesos terminados
        3. Procesa llegadas de nuevos procesos
        4. Intenta asignar procesos en espera
        """
        if self.finished:
            return {"error": "simulation_finished"}

        self.current_tick += 1
        eventos = []

        # 1. Actualizar procesos activos y liberar terminados
        procesos_terminados = self.memory_manager.tick_procesos()
        for pid in procesos_terminados:
            self.procesos_terminados.append(pid)
            eventos.append(f"Proceso {pid} terminado y liberado")
            self.estadisticas["procesos_ejecutados"] += 1

        # 2. Procesar llegadas de nuevos procesos
        nuevas_llegadas = []
        while (self.procesos_pendientes and 
               self.procesos_pendientes[0].get("tiempo_llegada", 0) <= self.current_tick):
            proceso = self.procesos_pendientes.pop(0)
            nuevas_llegadas.append(proceso)
            eventos.append(f"Proceso {proceso['pid']} llega al sistema")

        # 3. Intentar asignar nuevas llegadas
        for proceso in nuevas_llegadas:
            try:
                self.memory_manager.asignar_proceso(proceso)
                eventos.append(f"Proceso {proceso['pid']} asignado exitosamente")
            except MemoryError:
                # Si no se puede asignar, ponerlo en cola de espera
                self.procesos_en_espera.append(proceso)
                eventos.append(f"Proceso {proceso['pid']} en cola de espera")

        # 4. Intentar asignar procesos en espera
        procesos_asignados_desde_espera = []
        for _ in range(len(self.procesos_en_espera)):
            if not self.procesos_en_espera:
                break
            
            proceso = self.procesos_en_espera.popleft()
            try:
                self.memory_manager.asignar_proceso(proceso)
                eventos.append(f"Proceso {proceso['pid']} asignado desde cola de espera")
                procesos_asignados_desde_espera.append(proceso['pid'])
            except MemoryError:
                # Volver a ponerlo en espera
                self.procesos_en_espera.append(proceso)

        # 5. Verificar si la simulación debe terminar
        if (not self.procesos_pendientes and 
            not self.procesos_en_espera and 
            not self.memory_manager.procesos_activos):
            self.finished = True
            eventos.append("Simulación completada - todos los procesos terminaron")

        # 6. Preparar respuesta
        estadisticas = self.memory_manager.obtener_estadisticas()
        
        return {
            "tick": self.current_tick,
            "ram": self.memory_manager.ram,
            "swap": self.memory_manager.swap,
            "eventos": eventos,
            "procesos_terminados": procesos_terminados,
            "procesos_en_espera": len(self.procesos_en_espera),
            "procesos_pendientes": len(self.procesos_pendientes),
            "estadisticas": estadisticas,
            "finished": self.finished
        }

    def ejecutar_hasta_el_final(self):
        """
        Ejecuta la simulación completa hasta que todos los procesos terminen
        """
        resultado_completo = {
            "ticks": [],
            "resumen": {},
            "exitoso": True
        }
        
        tick_count = 0
        max_ticks = 1000  # Prevenir bucles infinitos
        
        while not self.finished and tick_count < max_ticks:
            tick_result = self.tick()
            resultado_completo["ticks"].append(tick_result)
            tick_count += 1
            
            # Si hay un error crítico
            if tick_result.get("error"):
                resultado_completo["exitoso"] = False
                break

        # Generar resumen final
        resultado_completo["resumen"] = {
            "ticks_totales": tick_count,
            "procesos_ejecutados": len(self.procesos_terminados),
            "procesos_fallidos": len(self.procesos_en_espera),
            "eficiencia_memoria": self.calcular_eficiencia(),
            "procesos_terminados": self.procesos_terminados
        }
        
        return resultado_completo

    def calcular_eficiencia(self):
        """Calcula métricas de eficiencia del gestor"""
        stats = self.memory_manager.obtener_estadisticas()
        
        total_procesos = len(self.process_list)
        procesos_exitosos = len(self.procesos_terminados)
        
        return {
            "tasa_exito": (procesos_exitosos / total_procesos) * 100 if total_procesos > 0 else 0,
            "utilizacion_ram": (stats["ram_ocupada"] / stats["ram_total"]) * 100,
            "utilizacion_swap": (stats["swap_ocupado"] / stats["swap_total"]) * 100,
            "fragmentacion": stats["fragmentacion_ram"]
        }

    def obtener_proceso_info(self, pid):
        """Obtiene información detallada de un proceso"""
        if pid in self.memory_manager.procesos_activos:
            return self.memory_manager.procesos_activos[pid]
        return None

    def reset(self):
        """Reinicia completamente la simulación"""
        self.memory_manager.reset()
        self.load_processes()
        self.current_tick = 0
        self.procesos_terminados = []
        self.procesos_en_espera = deque()
        self.finished = False
        self.estadisticas = {
            "procesos_ejecutados": 0,
            "procesos_fallidos": 0,
            "tiempo_total": 0,
            "swaps_realizados": 0
        }

    def obtener_estado_completo(self):
        """Obtiene el estado completo del sistema"""
        return {
            "tick_actual": self.current_tick,
            "memoria": {
                "ram": self.memory_manager.ram,
                "swap": self.memory_manager.swap,
                "estadisticas": self.memory_manager.obtener_estadisticas()
            },
            "procesos": {
                "activos": dict(self.memory_manager.procesos_activos),
                "terminados": self.procesos_terminados,
                "en_espera": list(self.procesos_en_espera),
                "pendientes": self.procesos_pendientes
            },
            "metricas": self.calcular_eficiencia(),
            "finished": self.finished
        }