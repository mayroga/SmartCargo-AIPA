from flask import Flask, render_template, request, jsonify
from models import CargoReport, Level, Question
import datetime
import uuid

app = Flask(__name__)

# ====================== PREGUNTAS ======================
questions_data = [
    # Nivel 1 – Identificación y transporte
    {"level": "Nivel 1", "id":1, "text":"Tipo de carga", "options":["Farmacéutica","DG","Perecederos","Human Remains","General Cargo","Otro"], "alerts":["", "", "", "", "", ""]},
    {"level": "Nivel 1", "id":2, "text":"Quién entrega", "options":["Chofer autorizado","Freight Forwarder","Empresa","Propietario / Dueño personalmente"], "alerts":["", "", "", ""]},
    {"level": "Nivel 1", "id":3, "text":"Medio de transporte terrestre", "options":["Camión refrigerado","Camión común","Otro"], "alerts":["", "", ""]},
    {"level": "Nivel 1", "id":4, "text":"Estado de la carga al recibir", "options":["Mezclada con otras cargas","Separada por tipo de mercancía","Pallets / bultos organizados correctamente"], "alerts":["", "", ""]},
    {"level": "Nivel 1", "id":5, "text":"Altura máxima del pallet / bulto", "options":["Dentro de límites","Excede límites – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level": "Nivel 1", "id":6, "text":"Largo máximo del pallet / bulto", "options":["Dentro de límites","Excede límites – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level": "Nivel 1", "id":7, "text":"Tipos de sello del camión", "options":["SSCF","Seguridad estándar","Otro","Faltante – ALERTA ROJA"], "alerts":["","","","ROJA"]},
    {"level": "Nivel 1", "id":8, "text":"Limpieza del camión", "options":["Adecuada","No adecuada – ALERTA ROJA"], "alerts":["","ROJA"]},
    # Nivel 2 – Documentación base
    {"level": "Nivel 2", "id":9, "text":"AWB original presente", "options":["Dentro del sobre","Sueltos","No disponible – ALERTA ROJA"], "alerts":["","","ROJA"]},
    {"level": "Nivel 2", "id":10, "text":"Copias de AWB y documentos", "options":["Fuera del sobre","Legibles","Ordenadas por tipo"], "alerts":["","",""]},
    {"level": "Nivel 2", "id":11, "text":"Letra de documentos", "options":["Legible","Tamaño adecuado","Sin borrones / tachaduras"], "alerts":["","",""]},
    {"level": "Nivel 2", "id":12, "text":"Nombre del shipper coincide con factura/documentos", "options":["Sí","Posible HOLD – ALERTA AMARILLA","No – ALERTA ROJA"], "alerts":["","AMARILLA","ROJA"]},
    {"level": "Nivel 2", "id":13, "text":"AWB coincide con carga física", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level": "Nivel 2", "id":14, "text":"Facturas, packing list, permisos separados y organizados", "options":["Sí","No – ALERTA AMARILLA"], "alerts":["","AMARILLA"]},
    {"level": "Nivel 2", "id":15, "text":"Documentos consolidados / master vs house AWB en orden", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level": "Nivel 2", "id":16, "text":"Sello de origen / fitosanitario colocado correctamente", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    # Nivel 3 – Pallets y embalaje
    {"level": "Nivel 3", "id":17, "text":"Tipo de pallet", "options":["Madera estándar","Madera tratada / fitosanitaria","Plástico","Otro"], "alerts":["","","",""]},
    {"level": "Nivel 3", "id":18, "text":"Envoltura de pallet", "options":["Film transparente","Film opaco / cubierto","No envuelto – ALERTA AMARILLA"], "alerts":["","","AMARILLA"]},
    {"level": "Nivel 3", "id":19, "text":"Pallets cumplen altura máxima", "options":["Sí","No – ALERTA ROJA"], "alerts":["","ROJA"]},
    {"level": "Nivel 3", "id":20, "text":"Etiquetas visibles", "options":["Hacia fuera","Hacia dentro","No visibles – ALERTA AMARILLA"], "alerts":["","","AMARILLA"]},
    {"level": "Nivel 3", "id":21, "text":"Mezcla de mercancías", "options":["Separada por tipo / restricciones","Mezclada – ALERTA ROJA"], "alerts":["","ROJA"]},
    # Nivel 4 – Carga específica (solo ejemplos, se pueden completar todos los niveles hasta 49)
]

def build_levels() -> list:
    levels_dict = {}
    for q in questions_data:
        question = Question(id=q["id"], text=q["text"], options=q["options"])
        if q["level"] not in levels_dict:
            levels_dict[q["level"]] = []
        levels_dict[q["level"]].append(question)
    return [Level(name=lvl, questions=questions) for lvl, questions in levels_dict.items()]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    report_id = f"RPT-{uuid.uuid4().hex[:8]}"
    role = data.get("role","Unknown")
    levels = build_levels()
    
    # Asignar respuestas y alertas automáticamente
    answers = data.get("answers", {})
    for lvl in levels:
        for q in lvl.questions:
            sel = answers.get(str(q.id), "")
            q.selected = sel
            # Asignar alerta según opción
            if sel in q.options:
                idx = q.options.index(sel)
                # Si hay alertas definidas, se asigna
                q.alert = q.get("alerts")[idx] if hasattr(q,"alerts") else ""
    
    report = CargoReport(report_id=report_id, role=role, levels=levels)
    semaforo = report.calculate_semáforo()
    recs = report.generate_recommendations()
    return jsonify({"report_id": report_id, "semaforo": semaforo, "recs": recs})

if __name__ == '__main__':
    app.run(debug=True)
