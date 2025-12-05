🛰️ SmartCargo-AIPA — Backend Oficial

Asesor preventivo virtual para la carga aérea y marítima (NO certifica, NO inspecciona, NO reemplaza reguladores).
Desarrollado para proteger la mercancía del cliente mediante análisis, predicciones y alertas 100% automáticas.

⚠️ Aviso Legal

SmartCargo-AIPA:

NO toca, inspecciona ni manipula carga.

NO certifica Dangerous Goods ni actúa como TSA, IATA, USDA ni ninguna agencia reguladora.

NO emite documentos oficiales.

👉 Es un asesor experto basado en datos, regulaciones públicas y buenas prácticas logísticas. Toda información generada es orientativa y no sustituye requisitos legales reales.

🎯 Objetivo del Software

Crear el sistema más completo del mundo para prevenir errores en toda la vida de la carga:

Desde preparación → embalaje → documentación → compatibilidad → riesgos → aceptación por aerolínea/handler/barco.

SmartCargo-AIPA detecta errores antes de que existan y emite alertas, sugerencias y predicciones totalmente automatizadas.

🧠 Funcionalidades Principales
✔️ Gestión total de carga

Crear, actualizar y seguir cargas

Estado automático (En revisión / OK / Riesgo / Rechazo probable)

✔️ Embalaje, pallets y fotos

Validación de pallets (madera, plástico, ISPM-15, fumigación)

Alturas permitidas

Compatibilidad entre productos (alimentos, químicos, DG, animales, perecederos)

✔️ Documentos

AWB / HBL

Packing List

Invoice

SLI

Declaraciones DG (solo revisión técnica, NO certificación)

✔️ Alertas automáticas

Altura excedida

Mala estiba

Productos incompatibles

Falta de ventilación

Riesgo TSA/K9

Riesgo de rechazo por aerolínea o puerto

Fotos incompletas o inconsistentes

✔️ Simulaciones

Predice en segundos:

Probabilidad de rechazo

Necesidad de reempaque

Costos extra por retrasos

Reglas específicas TSA / IATA / aerolíneas / puertos

✔️ Multilenguaje completo

Inglés (oficial)

Español

Francés

Portugués

Mandarín

✔️ Modos de pago

Servicios por uso (verificación, simulación, reportes)

Suscripción mensual

Suscripción anual

Básico / Premium

✔️ Actualización centralizada

Un solo archivo controla las reglas TSA, IATA, aerolíneas, puertos, DG, compatibilidades, etc.
Sin reiniciar el servidor.

⚙️ Tecnologías Utilizadas
Tecnología	Uso
Python 3.11+	Lenguaje principal
FastAPI	API REST del backend
PostgreSQL	Base de datos
Stripe	Pagos y suscripciones
Uvicorn	Servidor ASGI
Google Generative AI / Gemini	Motor de análisis y asesoría
Jinja2	Plantillas para reportes
CORS Middleware	Conexión segura con el frontend
Render	Hosting backend
GitHub	Repositorio principal
🗂 Estructura de Base de Datos (SQL)
Tablas principales:

pallets

documentos

alertas

fotos

cargas

usuarios

pagos

El archivo completo de creación de tablas está en:
📄 /database/schema.sql

🚀 Despliegue en Render (Backend)
1️⃣ Crear servicio web

Type: Web Service

Runtime: Python 3

Build command:

pip install -r requirements.txt


Start command:

uvicorn main:app --host 0.0.0.0 --port 10000

2️⃣ Variables de Entorno necesarias en Render

Render ya guarda las claves, NO las pones en .env.

Variable	Descripción
DATABASE_URL	PostgreSQL de Render (15GB recomendado)
STRIPE_SECRET_KEY	Clave privada Stripe
GOOGLE_API_KEY	Key de Gemini
CORS_ORIGINS	URL del frontend SmartCargo-Advisory
🔗 Conexión con el Frontend (SmartCargo-ADVISORY)

Frontend recomendado: sitio estático en Render
Repo: SmartCargo-ADVISORY

Configurar en index.html:

const BACKEND_URL = "https://smartcargo-aipa.onrender.com";

📡 Rutas principales del Backend
📦 Cargas
Método	Ruta	Función
POST	/cargas	Crear una carga
GET	/cargas	Listar cargas
GET	/cargas/{id}	Ver una carga
DELETE	/cargas/{id}	Eliminar
📄 Documentos y Fotos

| POST | /upload | Subir y analizar archivo |
| POST | /save-analysis | Guardar informe final |

🚨 Alertas y Simulaciones

| GET | /simulacion/{tipo}/{errores} | Predicción de rechazo |

🧠 Asistente Inteligente

| POST | /advisory | Preguntas y análisis de carga |

💳 Pagos

| POST | /create-payment | Crear pago único |
| POST | /checkout | Crear suscripción Stripe |

🧪 Cómo ejecutar localmente
git clone https://github.com/tuusuario/SmartCargo-AIPA.git
cd SmartCargo-AIPA
pip install -r requirements.txt
uvicorn main:app --reload

📞 Contacto & Créditos

Desarrollado por Maykel Rodríguez García
Creador de SmartCargo-AIPA, asesor logístico, y especialista en prevención de errores en carga aérea y marítima.

✔️ PROYECTO LISTO PARA PRODUCCIÓN

SmartCargo-AIPA está blindado, sin acceso físico a carga, sin funciones que impliquen certificación, y con seguridad avanzada en API, BD y pagos.
