# Azure ETL POC
- Autor: Renato Maximiliano Rivera Abad
- Role: Data Engineer
## Overview
Proof of Concept for ETL (Extract, Transform, Load) operations using Azure Cloud Services. This project implements a data migration system with REST API endpoints for data ingestion and data load.

## Features
- CSV data ingestion with validation
- Batch transaction support (1-1000 rows)
- Table backup/restore using AVRO format
- Data Load in SQL Database

## Tech Stack
- Python
- Azure Functions
- Azure Blob Storage
- Azure SQL Database
- FastAPI