# Finanzas Personales

Aplicación web completa para administrar finanzas personales con sistema de cuentas de usuario independientes.

## Stack Tecnológico

- **Frontend**: Vue.js 3 (Composition API) + Tailwind CSS
- **Backend**: Django + Django REST Framework
- **Base de datos**: PostgreSQL
- **Autenticación**: JWT (JSON Web Tokens)

## Características

- ✅ Gestión de múltiples cuentas financieras
- ✅ Registro de ingresos, gastos y transferencias
- ✅ Categorías personalizables
- ✅ Presupuestos con alertas
- ✅ Seguimiento de inversiones
- ✅ Gestión de deudas y préstamos
- ✅ Transacciones recurrentes
- ✅ Reportes y gráficos
- ✅ Exportación de datos (CSV, Excel)
- ✅ Modo claro/oscuro
- ✅ Diseño responsive

## Requisitos

- Docker y Docker Compose
- O alternativamente:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 15+

## Instalación con Docker (Recomendado)

```bash
# Clonar el repositorio
git clone <repo-url>
cd personal-finance

# Iniciar los servicios
docker-compose up -d

# La aplicación estará disponible en:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs/
```

## Instalación Manual

### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
python manage.py migrate

# Crear datos de prueba
python manage.py seed_data

# Iniciar servidor
python manage.py runserver
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
# Crear archivo .env con:
# VITE_API_URL=http://localhost:8000/api

# Iniciar servidor de desarrollo
npm run dev
```

## Usuario Demo

Después de ejecutar `seed_data`:

- **Email**: demo@finanzas.com
- **Contraseña**: demo1234

## Estructura del Proyecto

```
personal-finance/
├── backend/
│   ├── apps/
│   │   ├── users/          # Autenticación y usuarios
│   │   ├── accounts/       # Cuentas financieras
│   │   ├── categories/     # Categorías
│   │   ├── transactions/   # Transacciones
│   │   ├── budgets/        # Presupuestos
│   │   ├── investments/    # Inversiones
│   │   ├── debts/          # Deudas
│   │   └── reports/        # Dashboard y reportes
│   ├── config/             # Configuración Django
│   ├── requirements.txt
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── components/     # Componentes Vue
│   │   ├── views/          # Páginas
│   │   ├── stores/         # Pinia stores
│   │   ├── services/       # API calls
│   │   └── router/         # Vue Router
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Registro de usuario |
| POST | `/api/auth/login/` | Iniciar sesión |
| GET | `/api/accounts/` | Listar cuentas |
| GET | `/api/transactions/` | Listar transacciones |
| GET | `/api/categories/` | Listar categorías |
| GET | `/api/budgets/` | Listar presupuestos |
| GET | `/api/investments/` | Listar inversiones |
| GET | `/api/debts/` | Listar deudas |
| GET | `/api/reports/dashboard/` | Dashboard |
| GET | `/api/reports/` | Reportes |
| GET | `/api/reports/export/` | Exportar datos |

Ver documentación completa en `/api/docs/`

## Transacciones Recurrentes

Para procesar transacciones recurrentes automáticamente, ejecutar:

```bash
python manage.py process_recurring
```

Se recomienda configurar un cron job para ejecutar diariamente:

```bash
0 1 * * * cd /path/to/backend && python manage.py process_recurring
```

## Desarrollo

### Backend

```bash
# Ejecutar tests
python manage.py test

# Crear nuevas migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

### Frontend

```bash
# Desarrollo
npm run dev

# Build producción
npm run build

# Preview build
npm run preview
```

## Variables de Entorno

### Backend (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=finance_db
DB_USER=finance_user
DB_PASSWORD=finance_pass
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api
```

## Licencia

MIT





