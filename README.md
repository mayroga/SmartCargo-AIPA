# SmartCargo-AIPA Backend

**SmartCargo-AIPA** es un software único que funciona como un **TSA preventivo virtual** solo como asesor.  
Su objetivo es cubrir todos los episodios de la vida de la carga, priorizando la **seguridad y correcta manipulación**, evitando errores, retrasos y costos extras.  

> ⚠️ **Nota Legal:** SmartCargo-AIPA no manipula carga, no certifica ni reemplaza reguladores. Solo proporciona **alertas, sugerencias y predicciones**.

---

## 🛠 Funcionalidades

- Gestión de **cargas y pallets**.
- Subida y verificación de **documentos y fotos**.
- Alertas automáticas de **incompatibilidad, DG, temperatura, altura, retrasos**.
- Simulaciones de aceptación o rechazo en **aeropuertos, puertos y handlers**.
- Reportes exportables en **PDF/Excel**.
- Panel por actor: Cliente, Forwarder, Transportista, Aerolínea/Handler.
- Multilenguaje: inglés (oficial), español, francés, portugués, mandarín.
- Suscripciones y pagos: básico o premium, mensual o anual.
- Actualización centralizada de reglas y regulaciones.

---

## ⚙️ Tecnologías

- **Python 3.11+**
- **FastAPI** para API REST
- **PostgreSQL** para base de datos
- **Stripe** para pagos
- **Uvicorn** como servidor ASGI
- **Jinja2** para plantillas si se necesitan reportes HTML
- **Python-dotenv** para variables de entorno

---

## 🗂 Estructura de Base de Datos

- pallets
- documentos
- alertas
- fotos
- cargas
- usuarios
- pagos

---

## 🚀 Despliegue en Render

1. Crear un nuevo servicio web en Render.
2. Conectar el repositorio `SmartCargo-AIPA` de GitHub.
3. Configurar las **variables de entorno**:

