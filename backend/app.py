from flask import Flask, jsonify
from flask_cors import CORS
from scheduler import Scheduler
import logging
import json
import os

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
scheduler = Scheduler()

REQUIRED_FIELDS = {"pid": str, "size": int, "priority": int, "mode": str}

VALID_MODES = {"contigua", "segmentacion", "paginacion"}
VALID_ASIGNACIONES = {"fija", "variable"}
VALID_ESTRATEGIAS = {"first_fit", "best_fit", "next_fit", "worst_fit"}

def validar_procesos_json():
    try:
        with open("data/procesos.json", "r") as f:
            procesos = json.load(f)

        for i, proceso in enumerate(procesos):
            for campo, tipo in REQUIRED_FIELDS.items():
                if campo not in proceso:
                    raise ValueError(f"Falta el campo obligatorio '{campo}' en el proceso #{i+1}")
                if not isinstance(proceso[campo], tipo):
                    raise ValueError(f"El campo '{campo}' en el proceso #{i+1} debe ser de tipo {tipo.__name__}")

            if proceso["mode"] not in VALID_MODES:
                raise ValueError(f"Modo inválido en el proceso #{i+1}: {proceso['mode']}")

            if proceso["mode"] == "contigua":
                asignacion = proceso.get("asignacion", "variable")
                estrategia = proceso.get("estrategia", "first_fit")
                if asignacion not in VALID_ASIGNACIONES:
                    raise ValueError(f"Asignación inválida en el proceso #{i+1}: {asignacion}")
                if estrategia not in VALID_ESTRATEGIAS:
                    raise ValueError(f"Estrategia inválida en el proceso #{i+1}: {estrategia}")

            if proceso["mode"] == "segmentacion":
                if "segmentos" in proceso:
                    if not isinstance(proceso["segmentos"], list) or not all(isinstance(s, int) for s in proceso["segmentos"]):
                        raise ValueError(f"Segmentos inválidos en el proceso #{i+1}")
        logging.info("Validación de procesos.json completada con éxito.")
    except Exception as e:
        logging.error(f"Error en la validación de procesos.json: {e}")
        raise

@app.before_first_request
def validar_datos():
    validar_procesos_json()


@app.route('/iniciar', methods=['GET'])
def iniciar_simulador():
    scheduler.reset()
    return jsonify({"status": "iniciado"})


@app.route("/tick")
def tick():
    try:
        resultado = scheduler.tick()

        if resultado.get("error") == "memory_full":
            logging.warning(f"Memoria llena al asignar proceso {resultado['proceso']['pid']}.")
            return jsonify({
                "error": "memory_full",
                "ram": resultado["ram"],
                "swap": resultado["swap"],
                "proceso": resultado["proceso"],
                "finished": True
            })

        elif resultado.get("error") == "simulation_finished":
            logging.info("Simulación finalizada.")
            return jsonify({"finished": True})

        return jsonify({
            "ram": resultado.get("ram"),
            "swap": resultado.get("swap"),
            "proceso": resultado.get("proceso"),
            "finished": False
        })

    except Exception as e:
        logging.error(f"Error inesperado durante el tick: {e}")
        return jsonify({"error": "internal_error", "message": str(e)}), 500


@app.route("/reset")
def reset():
    scheduler.reset()
    logging.info("Simulación reiniciada.")
    return "OK"

@app.route("/estado", methods=['GET'])
def obtener_estado():
    try:
        estado = scheduler.obtener_estado_completo()
        return jsonify({
            "success": True,
            "data": estado
        })
    except Exception as e:
        logging.error(f"Error al obtener estado: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)