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
                    recs.append(f"Question {q.id}: {q.text} - Immediate action required")
                elif q.alert == "AMARILLA":
                    recs.append(f"Question {q.id}: {q.text} - Review / Hold")
        return recs


# ================= PREGUNTAS =================
questions_data = [
    # Nivel 1 - Identification & Transport
    {"level":"Level 1", "id":1, "text":"Type of cargo", "options":["Pharmaceutical","DG","Perishable","Human Remains","General Cargo","Other"], "alerts":["","","","","",""]},
    {"level":"Level 1", "id":2, "text":"Who delivers", "options":["Authorized Driver","Freight Forwarder","Company","Owner personally"], "alerts":["","","",""]},
    {"level":"Level 1", "id":3, "text":"Land transport method", "options":["Refrigerated Truck","Regular Truck","Other"], "alerts":["","",""]},
    {"level":"Level 1", "id":4, "text":"Cargo condition upon receipt", "options":["Mixed with other cargo","Separated by type","Pallets/bundles organized correctly"], "alerts":["","",""]},
    {"level":"Level 1", "id":5, "text":"Max pallet/bundle height", "options":["Within limits","Exceeds limits – RED ALERT"], "alerts":["","ROJA"]},
    {"level":"Level 1", "id":6, "text":"Max pallet/bundle length", "options":["Within limits","Exceeds limits – RED ALERT"], "alerts":["","ROJA"]},
    {"level":"Level 1", "id":7, "text":"Truck seal type", "options":["SSCF","Standard Security","Other","Missing – RED ALERT"], "alerts":["","","","ROJA"]},
    {"level":"Level 1", "id":8, "text":"Truck cleanliness", "options":["Adequate","Not adequate – RED ALERT"], "alerts":["","ROJA"]},
    # Nivel 2 - Documentation
    {"level":"Level 2", "id":9, "text":"Original AWB present", "options":["Inside envelope","Loose","Not available – RED ALERT"], "alerts":["","","ROJA"]},
    {"level":"Level 2", "id":10, "text":"AWB and documents copies", "options":["Outside envelope","Legible","Organized by type"], "alerts":["","",""]},
    {"level":"Level 2", "id":11, "text":"Document writing", "options":["Legible","Correct size","No smudges/erasures"], "alerts":["","",""]},
    {"level":"Level 2", "id":12, "text":"Shipper name matches invoice/documents", "options":["Yes","Possible HOLD – YELLOW","No – RED ALERT"], "alerts":["","AMARILLA","ROJA"]},
    {"level":"Level 2", "id":13, "text":"AWB matches physical cargo", "options":["Yes","No – RED ALERT"], "alerts":["","ROJA"]},
    {"level":"Level 2", "id":14, "text":"Invoices, packing list, permits organized", "options":["Yes","No – YELLOW ALERT"], "alerts":["","AMARILLA"]},
    {"level":"Level 2", "id":15, "text":"Consolidated/master vs house AWB in order", "options":["Yes","No – RED ALERT"], "alerts":["","ROJA"]},
    {"level":"Level 2", "id":16, "text":"Origin/Phytosanitary seal correct", "options":["Yes","No – RED ALERT"], "alerts":["","ROJA"]},
    # Nivel 3 - Pallets & Packaging (ejemplo)
    {"level":"Level 3", "id":17, "text":"Pallet type", "options":["Standard wood","Treated/Phytosanitary wood","Plastic","Other"], "alerts":["","","",""]},
    {"level":"Level 3", "id":18, "text":"Pallet wrapping", "options":["Transparent film","Opaque film","Not wrapped – YELLOW ALERT"], "alerts":["","","AMARILLA"]},
    {"level":"Level 3", "id":19, "text":"Pallets meet max height", "options":["Yes","No – RED ALERT"], "alerts":["","ROJA"]},
    {"level":"Level 3", "id":20, "text":"Labels visible", "options":["Outwards","Inwards","Not visible – YELLOW ALERT"], "alerts":["","","AMARILLA"]},
    {"level":"Level 3", "id":21, "text":"Cargo mix", "options":["Separated by type/restrictions","Mixed – RED ALERT"], "alerts":["","ROJA"]},
    # Aquí debes continuar agregando hasta la pregunta 49 con la misma estructura
]

def build_levels() -> list:
    """Agrupa preguntas por nivel"""
    levels_dict = {}
    for q in questions_data:
        question = Question(id=q["id"], text=q["text"], options=q["options"], alerts=q.get("alerts"))
        if q["level"] not in levels_dict:
            levels_dict[q["level"]] = []
        levels_dict[q["level"]].append(question)
    return [Level(name=lvl, questions=questions) for lvl, questions in levels_dict.items()]
