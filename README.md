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
