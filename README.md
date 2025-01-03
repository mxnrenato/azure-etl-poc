# Azure ETL POC

## Descripción
Proyecto de prueba de concepto (POC) para un proceso ETL utilizando servicios de Azure, implementado con Python y FastAPI siguiendo los principios de Clean Architecture.

## Arquitectura del Proyecto

Este proyecto implementa los principios de Arquitectura Limpia (Clean Architecture) con una estructura clara de capas:

- **Domain Layer**: Contiene las entidades del negocio y reglas empresariales
- **Application Layer**: Implementa los casos de uso de la aplicación
- **Infrastructure Layer**: Maneja detalles técnicos y implementaciones externas
  - API
  - Base de datos
  - Servicios externos
  - Logging
  - Persistencia

La arquitectura está diseñada siguiendo los principios SOLID y mantiene una clara separación de responsabilidades.

## Prerrequisitos

- Python 3.8+
- pip
- virtualenv
- Azure CLI (para autenticación con Key Vault)
- Docker (opcional, para ejecución containerizada)

## Configuración del Entorno

1. Clonar el repositorio:
```bash
git clone [URL-del-repositorio]
cd azure-etl-poc
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
```

5. Configurar Azure Key Vault:
   - Asegúrate de tener acceso al Key Vault
   - Actualiza AZURE_KEY_VAULT_URL en tu .env
   - Autentica con Azure:
   ```bash
   az login
   ```

## Ejecución del Proyecto

### Ejecución Local

1. Activar el entorno virtual (si no está activado):
```bash
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Iniciar el servidor FastAPI:
```bash
uvicorn src.infrastructure.api.main:app --host 0.0.0.0 --port 8000
```

El servidor estará disponible en `http://0.0.0.0:8000/api/docs#/`

### Ejecución con Docker

1. Construir la imagen:
```bash
docker build -t azure-etl-poc .
```

2. Ejecutar el contenedor:
```bash
docker run -d \
  --name azure-etl-poc \
  -p 8000:8000 \
  --env-file .env \
  azure-etl-poc
```

3. Verificar los logs:
```bash
docker logs azure-etl-poc
```

## Gestión de Secretos

El proyecto utiliza Azure Key Vault para la gestión segura de secretos:

1. Variables almacenadas en Key Vault:
   - Connection strings
   - Claves de API
   - Configuraciones sensibles

2. Variables locales (solo desarrollo):
   - Definidas en .env
   - Ejemplo de estructura en .env.example
   - No se comprometen en el repositorio

## Documentación API

- Swagger UI: `http://0.0.0.0:8000/api/docs#/`
- ReDoc: `http://0.0.0.0:8000/api/redoc`

## Estructura del Proyecto

```
azure-etl-poc/
├── src/
│   ├── application/      # Casos de uso
│   ├── domain/          # Entidades y reglas de negocio
│   ├── infrastructure/  # Implementaciones técnicas
│   │   ├── api/        # Endpoints FastAPI
│   │   ├── db/         # Configuración de base de datos
│   │   ├── logging/    # Configuración de logs
│   │   └── services/   # Servicios externos
│   └── functions/      # Funciones Azure
├── tests/              # Tests unitarios y de integración
├── .env               # Variables de entorno (no versionado)
├── .env.example       # Template de variables de entorno
├── Dockerfile         # Configuración de Docker
├── requirements.txt   # Dependencias del proyecto
└── README.md         # Este archivo
```

## Configuración de Desarrollo

### Linting y Formato
```bash
flake8 .
```

### Tests
```bash
pytest
```

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Soporte

Para reportar problemas o solicitar ayuda:
1. Abrir un issue en el repositorio
2. Contactar al equipo de desarrollo

## Licencia

[Tipo de Licencia] - ver archivo LICENSE para más detalles