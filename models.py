# models.py
from typing import List

# ================= CLASES =================
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
    def __init__(self, report_id: str, role: str, levels: List[Level]):
        self.report_id = report_id
        self.role = role
        self.levels = levels

    def calculate_semaforo(self):
        red, yellow, green = 0, 0, 0
        for lvl in self.levels:
            for q in lvl.questions:
                if q.alert == "ROJA":
                    red += 1
                elif q.alert == "AMARILLA":
                    yellow += 1
                else:
                    green += 1
        if red > 0:
            return "RED"
        elif yellow > 0:
            return "YELLOW"
        return "GREEN"

    def generate_recommendations(self):
        recs = []
        for lvl in self.levels:
            for q in lvl.questions:
                if q.alert == "ROJA":
                    recs.append(f"Pregunta {q.id}: {q.text} - Acción inmediata requerida")
                elif q.alert == "AMARILLA":
                    recs.append(f"Pregunta {q.id}: {q.text} - Revisar / Hold")
        return recs

# ================= PREGUNTAS =================
questions_data = [
    # Nivel 1 – Identificación y transporte
    {"level":"Nivel 1", "id":1, "text":"Tipo de carga", "options":["Farmacéutica","DG","Perecederos","Human Remains","General Cargo / Consolidados / Unificados","Otro"], "alerts":["","","","","",""]},
    {"level":"Nivel 1", "id":2, "text":"Quién entrega", "options":["Chofer autorizado","Freight Forwarder","Empresa","Propietario / Dueño personalmente"], "alerts":["","","",""]},
    {"level":"Nivel 1", "id":3, "text":"Medio de transporte terrestre", "options":["Camión refrigerado","Camión común","Otro"], "alerts":["","",""]},
    {"level":"Nivel 1", "id":4, "text":"Estado de la carga al recibir", "options":["Mezclada con otras cargas","Separada por tipo de mercancía","Pallets / bultos organizados correctamente"], "alerts":["ROJA","",""]},
    {"level":"Nivel 1", "id":5, "text":"Altura máxima del pallet / bulto", "options":["Dentro de límites","Excede límites – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level":"Nivel 1", "id":6, "text":"Largo máximo del pallet / bulto", "options":["Dentro de límites","Excede límites – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level":"Nivel 1", "id":7, "text":"Tipos de sello del camión", "options":["SSCF","Seguridad estándar","Otro","Faltante – ALERTA ROJA"], "alerts":["","","","ROJA"]},
    {"level":"Nivel 1", "id":8, "text":"Limpieza del camión (aplica Pharma, Alimentos, Perecederos)", "options":["Adecuada","No adecuada – ALERTA ROJA"], "alerts":["","ROJA"]},

    # Nivel 2 – Documentación base
    {"level":"Nivel 2", "id":9, "text":"¿AWB original presente?", "options":["Dentro del sobre","Sueltos","No disponible – ALERTA ROJA"], "alerts":["","","ROJA"]},
    {"level":"Nivel 2", "id":10, "text":"¿Copias de AWB y documentos?", "options":["Fuera del sobre","Legibles","Ordenadas por tipo"], "alerts":["","",""]},
    {"level":"Nivel 2", "id":11, "text":"Letra de documentos", "options":["Legible","Tamaño adecuado","Sin borrones / tachaduras"], "alerts":["","",""]},
    {"level":"Nivel 2", "id":12, "text":"Nombre del shipper coincide con factura/documentos", "options":["Sí","Posible HOLD – ALERTA AMARILLA","No – ALERTA ROJA"], "alerts":["","AMARILLA","ROJA"]},
    {"level":"Nivel 2", "id":13, "text":"AWB coincide con carga física (peso/dimensiones/volumen)", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level":"Nivel 2", "id":14, "text":"Facturas, packing list, permisos separados y organizados", "options":["Sí","No – ALERTA AMARILLA"], "alerts":["","AMARILLA"]},
    {"level":"Nivel 2", "id":15, "text":"Documentos consolidados / master vs house AWB en orden", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level":"Nivel 2", "id":16, "text":"Sello de origen / fitosanitario colocado correctamente", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},

    # Nivel 3 – Pallets y embalaje
    {"level":"Nivel 3", "id":17, "text":"Tipo de pallet", "options":["Madera estándar","Madera tratada / fitosanitaria","Plástico","Otro"], "alerts":["","","",""]},
    {"level":"Nivel 3", "id":18, "text":"Envoltura de pallet", "options":["Film transparente","Film opaco / cubierto","No envuelto – ALERTA AMARILLA"], "alerts":["","","AMARILLA"]},
    {"level":"Nivel 3", "id":19, "text":"Pallets cumplen altura máxima", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level":"Nivel 3", "id":20, "text":"Etiquetas visibles", "options":["Hacia fuera","Hacia dentro","No visibles – ALERTA AMARILLA"], "alerts":["","","AMARILLA"]},
    {"level":"Nivel 3", "id":21, "text":"Mezcla de mercancías", "options":["Separada por tipo / restricciones","Mezclada – ALERTA ROJA"], "alerts":["","ROJA"]},

    # Nivel 4 – Carga específica (Farmacéutica, DG, Perecederos, Human Remains, General Cargo)
    # Se agregan solo ejemplos, resto sigue misma lógica hasta la pregunta 49
    {"level":"Nivel 4", "id":22, "text":"Clasificación Farmacéutica", "options":["Time & Temperature Sensitive","Ambient","CRT / RCL / Frozen"], "alerts":["","",""]},
    {"level":"Nivel 4", "id":23, "text":"Rango de temperatura declarado", "options":["+2 a +8 °C","+15 a +25 °C","Otro"], "alerts":["","","ROJA"]},
    {"level":"Nivel 4", "id":24, "text":"Dry ice", "options":["Etiquetado correctamente","Cantidad correcta","Otro – ALERTA ROJA"], "alerts":["","","ROJA"]},
    {"level":"Nivel 4", "id":25, "text":"Trae SLI firmado", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level":"Nivel 4", "id":26, "text":"Packaging validado", "options":["Gel packs","Dry ice","Caja sellada"], "alerts":["","",""]},
    {"level":"Nivel 4", "id":27, "text":"Documentos adicionales", "options":["MSDS","Certificado de temperatura","Etiquetado correcto"], "alerts":["","",""]},
    {"level":"Nivel 4", "id":28, "text":"Temperatura registrada durante transporte terrestre", "options":["Sí","No – ALERTA AMARILLA"], "alerts":["","AMARILLA"]},
    {"level":"Nivel 4", "id":29, "text":"Fechas de caducidad legibles", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    # DG, Perecederos, Human Remains y General Cargo preguntas se añaden siguiendo la misma estructura
]

def build_levels() -> list:
    """Agrupa preguntas por nivel y devuelve lista de Level"""
    levels_dict = {}
    for q in questions_data:
        question = Question(id=q["id"], text=q["text"], options=q["options"], alerts=q.get("alerts"))
        if q["level"] not in levels_dict:
            levels_dict[q["level"]] = []
        levels_dict[q["level"]].append(question)
    return [Level(name=lvl, questions=questions) for lvl, questions in levels_dict.items()]
