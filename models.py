# models.py
from typing import List, Dict

# =================
# CLASES
# =================
class Question:
    def __init__(self, id: int, text: str, options: List[str], alerts: List[str] = None):
        self.id = id
        self.text = text
        self.options = options
        self.alerts = alerts or ["" for _ in options]
        self.selected = ""
        self.alert = ""

class Level:
    def __init__(self, name: str, questions: List[Question]):
        self.name = name
        self.questions = questions

class CargoReport:
    def __init__(self, report_id: str, operator: str, levels: List[Level]):
        self.report_id = report_id
        self.operator = operator
        self.levels = levels

    # =================
    # CALCULO DE SEMAFORO
    # =================
    def calculate_semaforo(self):
        red, yellow, green = 0, 0, 0
        for lvl in self.levels:
            for q in lvl.questions:
                if q.alert.upper() == "ROJA":
                    red += 1
                elif q.alert.upper() == "AMARILLA":
                    yellow += 1
                else:
                    green += 1
        if red > 0:
            return "RED"
        elif yellow > 0:
            return "YELLOW"
        return "GREEN"

    # =================
    # GENERA RECOMENDACIONES
    # =================
    def generate_recommendations(self):
        recs = []
        for lvl in self.levels:
            for q in lvl.questions:
                if q.alert.upper() == "ROJA":
                    recs.append(f"Question {q.id}: {q.text} – Immediate action required")
                elif q.alert.upper() == "AMARILLA":
                    recs.append(f"Question {q.id}: {q.text} – Review / Hold")
        return recs

# =================
# PREGUNTAS POR NIVEL
# =================
questions_data = [
    # Nivel 1 – Identificación y Transporte
    {"level":"Level 1", "id":1, "text":"Tipo de carga", 
     "options":["Farmacéutica","DG (Dangerous Goods)","Perecederos","Human Remains","General Cargo / Consolidados / Unificados","Otro"], 
     "alerts":["","","","","",""]},
    {"level":"Level 1", "id":2, "text":"Quien entrega", 
     "options":["Chofer autorizado","Freight Forwarder","Empresa","Propietario / Dueño personalmente"], 
     "alerts":["","","",""]},
    {"level":"Level 1", "id":3, "text":"Medio de transporte terrestre", 
     "options":["Camión refrigerado","Camión común","Otro"], 
     "alerts":["","",""]},
    {"level":"Level 1", "id":4, "text":"Estado de la carga al recibir", 
     "options":["Mezclada con otras cargas","Separada por tipo de mercancía","Pallets / bultos organizados correctamente"], 
     "alerts":["","",""]},
    {"level":"Level 1", "id":5, "text":"Altura máxima del pallet / bulto", 
     "options":["Dentro de límites","Excede límites – ALERTA ROJA"], 
     "alerts":["","ROJA"]},
    {"level":"Level 1", "id":6, "text":"Largo máximo del pallet / bulto", 
     "options":["Dentro de límites","Excede límites – ALERTA ROJA"], 
     "alerts":["","ROJA"]},
    {"level":"Level 1", "id":7, "text":"Tipos de sello del camión", 
     "options":["SSCF","Seguridad estándar","Otro","Faltante – ALERTA ROJA"], 
     "alerts":["","","","ROJA"]},
    {"level":"Level 1", "id":8, "text":"Limpieza del camión", 
     "options":["Adecuada","No adecuada – ALERTA ROJA"], 
     "alerts":["","ROJA"]},

    # Nivel 2 – Documentación Base
    {"level":"Level 2", "id":9, "text":"AWB original presente", 
     "options":["Dentro del sobre","Sueltos","No disponible – ALERTA ROJA"], 
     "alerts":["","","ROJA"]},
    {"level":"Level 2", "id":10, "text":"Copias de AWB y documentos", 
     "options":["Fuera del sobre","Legibles","Ordenadas por tipo"], 
     "alerts":["","",""]},
    {"level":"Level 2", "id":11, "text":"Letra de documentos", 
     "options":["Legible","Tamaño adecuado","Sin borrones / tachaduras"], 
     "alerts":["","",""]},
    {"level":"Level 2", "id":12, "text":"Nombre del shipper coincide con factura/documentos", 
     "options":["Sí","Posible HOLD – ALERTA AMARILLA","No – ALERTA ROJA"], 
     "alerts":["","AMARILLA","ROJA"]},
    {"level":"Level 2", "id":13, "text":"AWB coincide con carga física (peso/dimensiones/volumen)", 
     "options":["Sí","No – ALERTA ROJA"], 
     "alerts":["","ROJA"]},
    {"level":"Level 2", "id":14, "text":"Facturas, packing list, permisos separados y organizados", 
     "options":["Sí","No – ALERTA AMARILLA"], 
     "alerts":["","AMARILLA"]},
    {"level":"Level 2", "id":15, "text":"Documentos consolidados / master vs house AWB en orden", 
     "options":["Sí","No – ALERTA ROJA"], 
     "alerts":["","ROJA"]},
    {"level":"Level 2", "id":16, "text":"Sello de origen / fitosanitario colocado correctamente", 
     "options":["Sí","No – ALERTA ROJA"], 
     "alerts":["","ROJA"]},

    # Nivel 3 – Pallets y Embalaje
    {"level":"Level 3", "id":17, "text":"Tipo de pallet", 
     "options":["Madera estándar","Madera tratada / fitosanitaria","Plástico","Otro"], 
     "alerts":["","","",""]},
    {"level":"Level 3", "id":18, "text":"Envoltura de pallet", 
     "options":["Film transparente","Film opaco / cubierto","No envuelto – ALERTA AMARILLA"], 
     "alerts":["","","AMARILLA"]},
    {"level":"Level 3", "id":19, "text":"Pallets cumplen altura máxima", 
     "options":["Sí","No – ALERTA ROJA"], 
     "alerts":["","ROJA"]},
    {"level":"Level 3", "id":20, "text":"Etiquetas visibles", 
     "options":["Hacia fuera","Hacia dentro","No visibles – ALERTA AMARILLA"], 
     "alerts":["","","AMARILLA"]},
    {"level":"Level 3", "id":21, "text":"Mezcla de mercancías", 
     "options":["Separada por tipo / restricciones","Mezclada – ALERTA ROJA"], 
     "alerts":["","ROJA"]},

    # Nivel 4 – Carga específica (ejemplos: Pharma, DG, Perecederos, Human Remains, General)
    {"level":"Level 4", "id":22, "text":"Clasificación farmacéutica", 
     "options":["Time & Temperature Sensitive","Ambient","CRT / RCL / Frozen"], 
     "alerts":["","",""]},
    {"level":"Level 4", "id":23, "text":"Rango de temperatura declarado", 
     "options":["+2 a +8 °C","+15 a +25 °C","Otro"], 
     "alerts":["","","ROJA"]},
    {"level":"Level 4", "id":24, "text":"Dry ice", 
     "options":["Etiquetado correctamente","Cantidad correcta","Otro – ALERTA ROJA"], 
     "alerts":["","","ROJA"]},
    {"level":"Level 4", "id":25, "text":"SLI firmado", 
     "options":["Sí","No – ALERTA ROJA"], 
     "alerts":["","ROJA"]},
    {"level":"Level 4", "id":26, "text":"Packaging validado", 
     "options":["Gel packs","Dry ice","Caja sellada"], 
     "alerts":["","",""]},
    {"level":"Level 4", "id":27, "text":"Documentos adicionales", 
     "options":["MSDS","Certificado de temperatura","Etiquetado correcto"], 
     "alerts":["","",""]},

    # Nivel 5 – Registro de semáforo y conclusión final (simplificado)
    {"level":"Level 5", "id":28, "text":"Resultado final del cargo", 
     "options":["Cumple – Compliant","Requiere revisión – Warn","No cumple – Fail"], 
     "alerts":["","AMARILLA","ROJA"]},
]

# =================
# CONSTRUCCIÓN DE NIVELES
# =================
def build_levels() -> List[Level]:
    """Agrupa preguntas por nivel"""
    levels_dict: Dict[str, List[Question]] = {}
    for q in questions_data:
        question = Question(id=q["id"], text=q["text"], options=q["options"], alerts=q.get("alerts"))
        if q["level"] not in levels_dict:
            levels_dict[q["level"]] = []
        levels_dict[q["level"]].append(question)
    return [Level(name=lvl, questions=questions) for lvl, questions in levels_dict.items()]
