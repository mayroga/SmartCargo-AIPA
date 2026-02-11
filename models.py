from dataclasses import dataclass, field
from typing import List, Dict

# Cada pregunta tendrá texto, opciones, valor seleccionado y alerta asociada
@dataclass
class Question:
    id: int
    text: str
    options: List[str]
    selected: str = ""
    alert: str = ""  # "ROJA", "AMARILLA", "VERDE"

@dataclass
class Level:
    name: str
    questions: List[Question]

@dataclass
class CargoReport:
    report_id: str
    role: str
    levels: List[Level] = field(default_factory=list)

    def calculate_semáforo(self) -> str:
        """Calcula el semáforo global del reporte"""
        rojo = any(q.alert == "ROJA" for lvl in self.levels for q in lvl.questions)
        amarillo = any(q.alert == "AMARILLA" for lvl in self.levels for q in lvl.questions)
        if rojo:
            return "🔴 Riesgos críticos → acción inmediata"
        elif amarillo:
            return "🟡 Riesgos controlables → revisar / corregir"
        else:
            return "🟢 Cumplimientos → OK"

    def generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en alertas"""
        recs = []
        for lvl in self.levels:
            for q in lvl.questions:
                if q.alert == "ROJA":
                    recs.append(f"{q.text}: CORREGIR INMEDIATAMENTE")
                elif q.alert == "AMARILLA":
                    recs.append(f"{q.text}: REVISAR / POSIBLE HOLD")
        return recs
