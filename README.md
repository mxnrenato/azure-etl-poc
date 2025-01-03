# Azure Data Processing System

## Description
Proof of Concept (POC) for a data processing system using Azure services, implemented with Python and FastAPI following Clean Architecture principles. The system handles employee data management with Azure Blob Storage for file storage and AVRO backups, and Azure SQL Database for structured data persistence.

## System Architecture

This project implements Clean Architecture principles with a clear layer structure:

- **Domain Layer**: Contains business entities and rules
  - Employee, Department, and Job entities
  - Repository interfaces
  - Business rules and validations

- **Application Layer**: Implements use cases
  - Data ingestion processing
  - Backup management
  - Analytics and metrics

- **Infrastructure Layer**: Handles technical implementations
  - FastAPI endpoints
  - Azure SQL Database integration
  - Azure Blob Storage operations
  - Azure Key Vault security

## Features

### 1. Data Ingestion
- Batch processing of CSV files
- Data validation and transformation
- Storage of raw files in Blob Storage
- Structured data persistence in SQL Database

### 2. Backup System
- AVRO format backups of database tables
- Secure storage in Azure Blob Storage
- Point-in-time recovery capabilities

### 3. Analytics & Metrics
- Quarterly hiring analytics
- Departmental performance metrics
- Custom data exploration

## API Endpoints

### Ingest
```http
POST /api/ingest/{table_name}
Description: Process and ingest data from file in batches
```

### Backup Operations
```http
POST /api/backup/{table_name}
Description: Create Backup

POST /api/restore/{table_name}
Description: Restore Backup
```

### Metrics
```http
GET /api/metrics/quarterly-hires-2021
Description: Get employee hiring data by quarter for 2021

GET /api/metrics/departments-above-mean-2021
Description: Get departments exceeding average hiring rate
```

## Project Structure
```
src/
├── application/
│   ├── interfaces/
│   │   └── storage_service.py
│   └── services/
│       └── ingest_service.py
├── domain/
│   ├── entities/
│   │   ├── employee.py
│   │   ├── department.py
│   │   └── job.py
│   └── repositories/
│       ├── employee_repository.py
│       ├── department_repository.py
│       └── job_repository.py
└── infrastructure/
    ├── api/
    │   └── routes/
    │       ├── ingest_routes.py
    │       ├── backup_routes.py
    │       └── metrics_routes.py
    ├── database/
    │   └── connection.py
    └── storage/
        └── azure_blob.py
```

## Prerequisites

- Python 3.8+
- Azure subscription
- Azure CLI
- pip
- virtualenv

## Environment Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd [project-directory]
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

## Environment Variables
```env
AZURE_KEY_VAULT_URL=your-key-vault-url
AZURE_STORAGE_CONNECTION_STRING=your-storage-connection
AZURE_SQL_CONNECTION_STRING=your-sql-connection
AZURE_BLOB_CONTAINER_ROW_DATA=raw-data
AZURE_BLOB_CONTAINER_BACKUPS=backups
```

## Running the Project

### Local Development
```bash
uvicorn src.infrastructure.api.main:app --reload
```

### Docker
```bash
docker build -t azure-data-processor .
docker run -p 8000:8000 --env-file .env azure-data-processor
```

## Documentation
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## Security

- Credentials managed through Azure Key Vault
- Environment variables for local development
- Azure Managed Identity integration
- Secure API configuration

## Testing
```bash
pytest
```

## Development Guidelines

### Code Style
```bash
flake8 .
black .
```

### Git Workflow
1. Create feature branch
2. Implement changes
3. Run tests
4. Submit pull request

## Support

For issues and feature requests:
1. Check existing issues
2. Create detailed bug report
3. Contact development team

## License

This project is licensed under [MIT] - see LICENSE file for details