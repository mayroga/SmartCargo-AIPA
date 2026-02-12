# models.py
from typing import List

# ================= CLASES =================
class Question:
    def __init__(self, id: int, text: str, options: List[str], alerts: List[str] = None):
        self.id = id
        self.text = text
        self.options = options
        self.alerts = alerts or ["OK" for _ in options]
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
    {"level":"Level 1", "id":1, "text":"Type of cargo", "options":["Pharmaceutical","DG","Perishable","Human Remains","General Cargo","Other"], "alerts":["OK","AMARILLA","AMARILLA","OK","OK","OK"]},
    {"level":"Level 1", "id":2, "text":"Who delivers", "options":["Authorized Driver","Freight Forwarder","Company","Owner personally"], "alerts":["OK","OK","OK","AMARILLA"]},
    {"level":"Level 1", "id":3, "text":"Land transport method", "options":["Refrigerated Truck","Regular Truck","Other"], "alerts":["OK","OK","AMARILLA"]},
    {"level":"Level 1", "id":4, "text":"Cargo condition upon receipt", "options":["Mixed with other cargo","Separated by type","Pallets/bundles organized correctly"], "alerts":["AMARILLA","OK","OK"]},
    {"level":"Level 1", "id":5, "text":"Max pallet/bundle height", "options":["Within limits","Exceeds limits"], "alerts":["OK","ROJA"]},
    {"level":"Level 1", "id":6, "text":"Max pallet/bundle length", "options":["Within limits","Exceeds limits"], "alerts":["OK","ROJA"]},
    {"level":"Level 1", "id":7, "text":"Truck seal type", "options":["SSCF","Standard Security","Other","Missing"], "alerts":["OK","OK","OK","ROJA"]},
    {"level":"Level 1", "id":8, "text":"Truck cleanliness", "options":["Adequate","Not adequate"], "alerts":["OK","ROJA"]},

    # Nivel 2 - Documentation
    {"level":"Level 2", "id":9, "text":"Original AWB present", "options":["Inside envelope","Loose","Not available"], "alerts":["OK","AMARILLA","ROJA"]},
    {"level":"Level 2", "id":10, "text":"AWB and documents copies", "options":["Outside envelope","Legible","Organized by type"], "alerts":["OK","OK","OK"]},
    {"level":"Level 2", "id":11, "text":"Document writing", "options":["Legible","Correct size","No smudges/erasures"], "alerts":["OK","OK","OK"]},
    {"level":"Level 2", "id":12, "text":"Shipper name matches invoice/documents", "options":["Yes","Possible HOLD","No"], "alerts":["OK","AMARILLA","ROJA"]},
    {"level":"Level 2", "id":13, "text":"AWB matches physical cargo", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 2", "id":14, "text":"Invoices, packing list, permits organized", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 2", "id":15, "text":"Consolidated/master vs house AWB in order", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 2", "id":16, "text":"Origin/Phytosanitary seal correct", "options":["Yes","No"], "alerts":["OK","ROJA"]},

    # Nivel 3 - Pallets & Packaging
    {"level":"Level 3", "id":17, "text":"Pallet type", "options":["Standard wood","Treated/Phytosanitary wood","Plastic","Other"], "alerts":["OK","OK","OK","AMARILLA"]},
    {"level":"Level 3", "id":18, "text":"Pallet wrapping", "options":["Transparent film","Opaque film","Not wrapped"], "alerts":["OK","OK","AMARILLA"]},
    {"level":"Level 3", "id":19, "text":"Pallets meet max height", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 3", "id":20, "text":"Labels visible", "options":["Outwards","Inwards","Not visible"], "alerts":["OK","OK","AMARILLA"]},
    {"level":"Level 3", "id":21, "text":"Cargo mix", "options":["Separated by type/restrictions","Mixed"], "alerts":["OK","ROJA"]},

    # Nivel 4 - Temperature & Handling
    {"level":"Level 4", "id":22, "text":"Temperature log available", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 4", "id":23, "text":"Cargo handled with care", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 4", "id":24, "text":"Sensitive items marked", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 4", "id":25, "text":"Fragile items separated", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},

    # Nivel 5 - Security & Compliance
    {"level":"Level 5", "id":26, "text":"Security seal intact", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 5", "id":27, "text":"Compliance certificates", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 5", "id":28, "text":"Driver authorization valid", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 5", "id":29, "text":"Dangerous goods label", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 5", "id":30, "text":"DG packaging intact", "options":["Yes","No"], "alerts":["OK","ROJA"]},

    # Nivel 6 - Documentation verification
    {"level":"Level 6", "id":31, "text":"Invoice number matches AWB", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 6", "id":32, "text":"Packing list included", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 6", "id":33, "text":"Permits valid", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 6", "id":34, "text":"Shipper info correct", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 6", "id":35, "text":"Consignee info correct", "options":["Yes","No"], "alerts":["OK","ROJA"]},

    # Nivel 7 - Labels & Markings
    {"level":"Level 7", "id":36, "text":"Cargo labels visible", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 7", "id":37, "text":"Fragile labels visible", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 7", "id":38, "text":"Temperature labels visible", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 7", "id":39, "text":"DG labels visible", "options":["Yes","No"], "alerts":["OK","ROJA"]},

    # Nivel 8 - Final Checks
    {"level":"Level 8", "id":40, "text":"Cargo documentation complete", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 8", "id":41, "text":"Cargo condition verified", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 8", "id":42, "text":"Segregation checked", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 8", "id":43, "text":"Temperature recorded", "options":["Yes","No"], "alerts":["OK","ROJA"]},

    # Nivel 9 - Supervisor checks
    {"level":"Level 9", "id":44, "text":"Supervisor review done", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 9", "id":45, "text":"Special cargo approval", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},

    # Nivel 10 - Miscellaneous
    {"level":"Level 10", "id":46, "text":"Cargo insurance valid", "options":["Yes","No"], "alerts":["OK","ROJA"]},
    {"level":"Level 10", "id":47, "text":"Shipment tracking active", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 10", "id":48, "text":"Customer informed", "options":["Yes","No"], "alerts":["OK","AMARILLA"]},
    {"level":"Level 10", "id":49, "text":"Final release authorized", "options":["Yes","No"], "alerts":["OK","ROJA"]},
]

def build_levels() -> List[Level]:
    """Agrupa preguntas por nivel"""
    levels_dict = {}
    for q in questions_data:
        question = Question(id=q["id"], text=q["text"], options=q["options"], alerts=q.get("alerts"))
        if q["level"] not in levels_dict:
            levels_dict[q["level"]] = []
        levels_dict[q["level"]].append(question)
    return [Level(name=lvl, questions=questions) for lvl, questions in levels_dict.items()]
