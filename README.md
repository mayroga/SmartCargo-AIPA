Sistema Operativo de Validación Documental y Pre-Aceptación de Carga Aérea

1️⃣ Objetivo

SMARTCARGO-AIPA no es una web bonita ni una IA de adorno.
Es un sistema operacional real diseñado para Avianca Cargo, sus agentes de counter, warehouses, forwarders, camioneros y dueños de mercancía.

Pregunta clave que responde:

¿Esta carga puede subir al avión HOY, SÍ o NO, y por qué?

Resultados operativos claros:

🟢 LISTA PARA ACEPTACIÓN

🟡 ACEPTABLE CON RIESGO

🔴 NO ACEPTABLE

2️⃣ Principios de Diseño

Avianca-first: Checklist específico por aerolínea, tipo de carga y país de destino.

Roles diferenciados: Cada usuario ve solo lo que necesita para actuar.

Motor de validación documental robusto: Reglas duras antes de IA.

Trazabilidad y evidencia: Quién subió qué documento, cuándo, versión y responsable.

Decisión operativa única: Semáforo y razones claras.

Zero IA de adorno: IA solo para detección de inconsistencias y validación de documentos.

3️⃣ Usuarios y Roles
Rol	Qué ve / Acción	Ejemplo de uso
Dueño	Estado de carga, riesgos, trazabilidad	Sabe si su mercancía puede viajar hoy
Forwarder	Documentos faltantes, errores de formato	Prepara paquetes listos para airline
Camionero	“Green light” para ir o no	Evita viajes inútiles y pérdida de tiempo
Warehouse	Aceptar / Rechazar / Hold	Decide en counter con semáforo operativo
Admin	Reglas, auditoría, trazabilidad	Configura reglas y revisa evidencia
4️⃣ Flujo Operativo (MVP)
Pantalla 1 – Identificación de la Carga

Campos obligatorios:

Aerolínea (default: Avianca Cargo)

MAWB

HAWB (si aplica)

Origen / Destino

Fecha de vuelo

Tipo de carga (GEN, DG, PER, HUM, AVI, VAL)

Si algún dato falta → ❌ NO SIGUE

Pantalla 2 – Subida de Documentos

Documentos estructurados según tipo de carga:

Commercial Invoice

Packing List

Shipper’s Letter of Instruction (SLI)

AWB / HAWB

Certificados según tipo de carga

MSDS (si aplica)

Permisos país destino

Cada documento muestra:

Estado: ✔ Válido / ❌ Inválido / ⚠ Dudoso

Versión

Fecha de carga

Responsable

Pantalla 3 – Resultado Operativo

Semáforo operativo:

🟢 LISTA PARA ACEPTACIÓN

🟡 ACEPTABLE CON RIESGO

🔴 NO ACEPTABLE

Ejemplo de razones:

❌ Invoice sin Incoterm
❌ Packing List no coincide con piezas
❌ MSDS vencido
❌ Falta copia externa del Packing List


Acción sugerida:

Corregir documentos

No enviar camión

5️⃣ Motor de Validación Documental

Reglas Avianca-first por tipo de carga, país destino y versión de documento.

Valida:

Documentos obligatorios

Copias dentro / fuera del folder

Formato y consistencia de información (Invoice vs Packing List)

Restricciones especiales (DG, PER, HUM, VAL, MSDS)

IA solo como soporte:

Detecta inconsistencias en PDFs/Excel

Valida formatos

No genera texto explicativo ni chat

6️⃣ Stack Técnico

Backend: FastAPI + PostgreSQL + Redis

Almacenamiento: Local o S3

Motor de reglas: Python puro + pydantic

IA auxiliar: OpenAI / Google GenAI

Frontend operativo: Formularios claros, sin animaciones, semáforo visible

Seguridad: Roles, trazabilidad y audit logging

7️⃣ Beneficios Clave

Reduce errores y holds en counter

Evita viajes de camioneros inútiles

Disminuye reprocesos y tiempo de build-up / breakdown

Ofrece trazabilidad legal y evidencia de documentos

Optimiza la cadena logística, enfocada en decisión operativa

8️⃣ Próximos Pasos para MVP

Conectar con base de datos real y almacenamiento de documentos

Implementar reglas completas Avianca-first y por tipo de carga

Ajustar vistas por rol con semáforo operativo

Pruebas con cargas reales y forwarders para validar eficacia

SMARTCARGO-AIPA by MAY ROGA LLC:

No es un ChatGPT bonito.
Es la barrera de calidad documental que Avianca necesita.


smartcargo_aipa/
├─ frontend/
│   ├─ index.html                # Pantalla principal (Identificación de carga + upload docs + resultado)
│   ├─ styles.css                # Estilos operativos, sin marketing
│   └─ scripts.js                # JS para manejar uploads, validaciones preliminares
│
├─ backend/
│   ├─ main.py                   # FastAPI: endpoints, validación, roles
│   ├─ rules.py                  # Motor de reglas de aceptación
│   ├─ database.py               # Conexión PostgreSQL + modelos
│   └─ utils.py                  # Funciones auxiliares: checklists, auditoría, semáforo
│
├─ storage/                      # Documentos subidos (S3 local o bucket)
│
├─ requirements.txt              # FastAPI, psycopg2, python-multipart, etc.
└─ README.md
