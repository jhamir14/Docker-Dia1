# Loans Service

Servicio de préstamos con arquitectura hexagonal usando FastAPI.

## Arquitectura

- **Domain**: Entidades, reglas de negocio y validadores
- **Application**: Casos de uso y servicios de dominio
- **Infrastructure**: Adaptadores HTTP, repositorios, logging
- **Interfaces**: API REST con FastAPI
- **Tests**: Unit tests (domain) e integration tests (HTTP)

## Endpoints

- `POST /api/loans` → Crear préstamo
- `POST /api/loans/{loan_id}/return` → Devolver préstamo
- `GET /health` → Estado del servicio
- `GET /api/debug/loans` → Debug (desarrollo)
- `GET /openapi.json` → Documentación OpenAPI

## Desarrollo Local

### Comandos PowerShell

```powershell
# Desde la raíz del proyecto
cd microservices-lab

# Construir y levantar servicios
docker compose build
docker compose up -d

# Ver logs del servicio de préstamos
docker compose logs -f loans

# Ejecutar tests unitarios
docker compose run --rm loans pytest src/tests/unit/ -v

# Ejecutar tests de integración (requiere servicios corriendo)
docker compose run --rm loans pytest src/tests/integration/ -v

# Ejecutar todos los tests
docker compose run --rm loans pytest -v

# Parar servicios
docker compose down

# Limpiar volúmenes (reset DB)
docker compose down -v
```

## Ejemplos cURL

### Crear préstamo

```bash
curl -X POST http://localhost:8001/api/loans \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "book_id": "book456", 
    "days": 7
  }'
```

### Devolver préstamo

```bash
curl -X POST http://localhost:8001/api/loans/{loan_id}/return
```

### Obtener estado del servicio

```bash
curl http://localhost:8001/health
```

### Ver préstamos (debug)

```bash
curl http://localhost:8001/api/debug/loans
```

### Ver documentación OpenAPI

```bash
curl http://localhost:8001/openapi.json
```

## Ejemplos PowerShell

### Crear préstamo

```powershell
$body = @{
    user_id = "user123"
    book_id = "book456"
    days = 7
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/loans" `
                  -Method POST `
                  -ContentType "application/json" `
                  -Body $body
```

### Devolver préstamo

```powershell
$loanId = "your-loan-id-here"
Invoke-RestMethod -Uri "http://localhost:8001/api/loans/$loanId/return" `
                  -Method POST
```

### Ver estado del servicio

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/health"
```

## Configuración

- **Puerto**: 8001
- **Base de datos**: PostgreSQL (loans_db)
- **Logging**: JSON estructurado
- **Timeouts HTTP**: 3 segundos
- **Reintentos HTTP**: 2 intentos adicionales

## Validaciones de Negocio

- Máximo 15 días de préstamo
- Usuario debe estar activo
- Máximo 3 préstamos activos por usuario
- Libro debe estar disponible

## Tests

### Tests Unitarios (Domain)
```bash
pytest src/tests/unit/ -v
```

Cubren:
- Validadores de negocio (≥6 tests)
- Servicios de dominio
- Reglas de préstamo

### Tests de Integración (HTTP)
```bash
# En host (servicio corriendo con docker compose):
pytest src/tests/integration/ -v

# En contenedor (recomendado):
# Apunta al servicio por nombre en la red de docker compose
docker compose run --rm -e SERVICE_BASE_URL=http://loans_service:8001 loans pytest src/tests/integration/ -v
```

Cubren:
- Endpoints HTTP completos
- Ciclo de vida de préstamos
- Manejo de errores
- Concurrencia básica