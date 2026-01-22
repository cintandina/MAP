👤 Autor / Mantenimiento

Proyecto desarrollado para Cintandina
Desarrollador: César Velásquez -cesarandresvelasquez01@gmail.com

MAP – Plataforma de Gestión y Trazabilidad QR
📌 Descripción general

MAP es una aplicación web desarrollada en Django para la gestión, trazabilidad y validación de entregas mediante códigos QR, orientada a procesos logísticos y de control de productos.

La plataforma permite:

Generar y administrar seriales QR

Gestionar clientes, productos y plantillas

Controlar solicitudes

Confirmar entregas con evidencia (imagen, firma, datos)

Publicar landings dinámicas por cliente

Almacenar archivos en Amazon S3

Desplegarse en Heroku de forma segura

🧱 Arquitectura técnica

Backend: Django (Python)

Base de datos: PostgreSQL

Frontend: Django Templates

Autenticación: Django Auth + modelo de usuario personalizado

Control de acceso: Roles y decoradores personalizados

Almacenamiento de archivos: Amazon S3

Archivos estáticos: Whitenoise

Correo: SendGrid

Despliegue: Heroku

Configuración: Variables de entorno (.env)

🌱 Entornos

La aplicación soporta múltiples entornos controlados por la variable:

DJANGO_ENV=development | production

🔹 Desarrollo (local)

DEBUG = True

PostgreSQL local

Carga de variables desde .env

URLs base:

http://127.0.0.1:8000

🔹 Producción (Heroku)

DEBUG = False

Base de datos vía DATABASE_URL

Archivos en S3

Dominios permitidos:

qr-sb.cintandina.com

*.herokuapp.com

🔐 Variables de entorno requeridas
Django
DJANGO_ENV=production
SECRET_KEY=your-secret-key
BASE_URL=https://qr-sb.cintandina.com
DEFAULT_FROM_EMAIL=cintainteligente@gmail.com

Base de datos (Heroku)
DATABASE_URL=postgres://...

Amazon S3
USE_S3=1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-2

☁️ Almacenamiento de archivos (S3)

Cuando USE_S3=1:

Archivos multimedia se almacenan en Amazon S3

URLs públicas firmadas deshabilitadas

No se sobrescriben archivos existentes

Cuando USE_S3=0 (local):

Archivos se guardan en /media

📁 Estructura del proyecto
MAP/
├── modulo_gestion_qr/
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── forms.py
│   ├── models.py
│   ├── signals.py
│   ├── urls.py
│   └── views.py
├── templates/
├── static/
├── manage.py
├── requirements.txt
└── README.md

🧩 Modelos principales

User (modelo personalizado)

Rol

Cliente

Producto

TemplateCliente

Serial

Solicitud

Entrega

Ubicacion

🧠 Landings dinámicas por cliente

El sistema permite seleccionar plantillas HTML de landing mediante patrones definidos en settings.py.

Plantillas permitidas
LANDING_TEMPLATE_PATTERNS = [
    'landing_cinta.html',
    'cliente_*.html',
    'template_*.html',
    'delmonte_landing1.html',
    'templateCintandina.html',
    'templateProducto1.html',
]

Plantillas excluidas

Archivos base, dashboards, formularios internos y vistas administrativas se excluyen explícitamente para evitar errores de selección.

🔐 Seguridad

CSRF configurado por entorno

ALLOWED_HOSTS dinámico

Sanitización de inputs (Bleach)

Sesiones cerradas al cerrar navegador

Separación de vistas públicas (QR) y privadas (admin)

⚙️ Instalación local
1️⃣ Clonar el repositorio
git clone https://github.com/cintandina/MAP.git
cd MAP

2️⃣ Crear entorno virtual
python -m venv venv
venv\Scripts\activate

3️⃣ Instalar dependencias
pip install -r requirements.txt

4️⃣ Crear archivo .env
DJANGO_ENV=development
SECRET_KEY=dev-key
USE_S3=0

5️⃣ Migraciones
python manage.py migrate

6️⃣ Crear superusuario
python manage.py createsuperuser

7️⃣ Ejecutar servidor
python manage.py runserver

📊 Logging

Logging configurado para:

Django

Almacenamiento S3

boto3 / botocore

Módulo principal (modulo_gestion_qr)

Salida por consola con formato detallado.

🏷️ Versionamiento

Este proyecto sigue Semantic Versioning:

vMAJOR.MINOR.PATCH


Versión actual:

v1.0.0

🚀 Estado del proyecto

✅ Código estable

✅ Desplegado en Heroku

✅ Integración S3

✅ Versionado

🔄 En evolución



📄 Licencia

Proyecto de uso privado.
No está autorizada su redistribución sin consentimiento del propietario.# MAP
