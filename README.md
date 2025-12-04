# Personal Finance App

Aplicación de gestión de finanzas personales construida con Django (backend) y Vue.js (frontend).

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose instalados
- Git

### Instalación y Ejecución

1. **Clonar el repositorio** (si aún no lo has hecho):
   ```bash
   git clone <tu-repositorio>
   cd personal-finance
   ```

2. **Iniciar la aplicación con Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Acceder a la aplicación**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs (Swagger): http://localhost:8000/api/docs/
   - Admin Django: http://localhost:8000/admin/

### Comandos Útiles

**Iniciar en segundo plano:**
```bash
docker-compose up -d
```

**Ver logs:**
```bash
docker-compose logs -f
```

**Detener la aplicación:**
```bash
docker-compose down
```

**Detener y eliminar volúmenes (incluyendo la base de datos):**
```bash
docker-compose down -v
```

**Reconstruir contenedores:**
```bash
docker-compose up --build
```

**Ejecutar migraciones manualmente:**
```bash
docker-compose exec backend python manage.py migrate
```

**Crear superusuario:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

## 🔧 Configuración

### Variables de Entorno

El `docker-compose.yml` ya incluye las variables de entorno necesarias. Si necesitas modificarlas, edita el archivo `docker-compose.yml`.

**Backend:**
- `DEBUG=True` - Modo desarrollo
- `SECRET_KEY` - Clave secreta de Django
- `DB_*` - Configuración de base de datos

**Frontend:**
- `VITE_API_URL=http://localhost:8000/api` - URL del API

## 🗄️ Base de Datos

La base de datos PostgreSQL se crea automáticamente al iniciar los contenedores. Los datos se persisten en un volumen de Docker llamado `postgres_data`.

**Credenciales por defecto:**
- Database: `finance_db`
- User: `finance_user`
- Password: `finance_pass`
- Port: `5432`

## 🛠️ Desarrollo

**Comandos útiles Backend:**
```bash
# Migraciones
docker-compose exec backend python manage.py migrate

# Crear migraciones
docker-compose exec backend python manage.py makemigrations

# Shell de Django
docker-compose exec backend python manage.py shell

# Crear superusuario
docker-compose exec backend python manage.py createsuperuser
```
**Comandos útiles Frontend:**
```bash
# Instalar dependencias (si cambias package.json)
docker-compose exec frontend npm install

# Build de producción
docker-compose exec frontend npm run build
```

## 🐛 Solución de Problemas

**Error de conexión a la base de datos:**
- Asegúrate de que el contenedor `db` esté corriendo: `docker-compose ps`
- Verifica los logs: `docker-compose logs db`

**El frontend no se conecta al backend:**
- Verifica que `VITE_API_URL` en `docker-compose.yml` sea `http://localhost:8000/api`
- Verifica que el backend esté corriendo: `docker-compose ps`

**Problemas con permisos:**
- En Linux/Mac, puede ser necesario ajustar permisos de archivos
- En Windows, asegúrate de que Docker Desktop tenga acceso a los archivos
