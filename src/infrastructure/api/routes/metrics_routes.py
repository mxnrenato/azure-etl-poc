from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from src.infrastructure.db.connection import get_db_cursor
from settings import AZURE_SQL_CONNECTION_STRING

class QuarterlyHiresResponse(BaseModel):
    department: str
    job: str
    Q1: int
    Q2: int
    Q3: int
    Q4: int

class DepartmentHiresResponse(BaseModel):
    id: int  # Cambiado de str a int
    department: str
    hired: int

router = APIRouter()

@router.get("/metrics/quarterly-hires-2021", response_model=List[QuarterlyHiresResponse])
async def get_quarterly_hires_2021():
    """
    Get the number of employees hired for each job and department in 2021, divided by quarter.
    Results are ordered alphabetically by department and job.
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            WITH QuarterlyHires AS (
                SELECT 
                    d.department,
                    j.job,
                    DATEPART(QUARTER, e.datetime) as quarter,
                    COUNT(*) as hires
                FROM employees e
                JOIN departments d ON e.department_id = d.id
                JOIN jobs j ON e.job_id = j.id
                WHERE YEAR(e.datetime) = 2021
                GROUP BY d.department, j.job, DATEPART(QUARTER, e.datetime)
            )
            SELECT 
                department,
                job,
                SUM(CASE WHEN quarter = 1 THEN hires ELSE 0 END) as Q1,
                SUM(CASE WHEN quarter = 2 THEN hires ELSE 0 END) as Q2,
                SUM(CASE WHEN quarter = 3 THEN hires ELSE 0 END) as Q3,
                SUM(CASE WHEN quarter = 4 THEN hires ELSE 0 END) as Q4
            FROM QuarterlyHires
            GROUP BY department, job
            ORDER BY department, job;
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                QuarterlyHiresResponse(
                    department=row.department,
                    job=row.job,
                    Q1=row.Q1,
                    Q2=row.Q2,
                    Q3=row.Q3,
                    Q4=row.Q4
                ) for row in rows
            ]
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving quarterly hires data: {str(e)}"
        )

@router.get("/metrics/departments-above-mean-2021", response_model=List[DepartmentHiresResponse])
async def get_departments_above_mean_2021():
    """
    Get departments that hired more employees than the mean in 2021,
    ordered by number of employees hired (descending).
    """
    try:
        with get_db_cursor() as cursor:
            query = """
            WITH DepartmentHires AS (
                SELECT 
                    d.id,
                    d.department,
                    COUNT(*) as hired_count
                FROM employees e
                JOIN departments d ON e.department_id = d.id
                WHERE YEAR(e.datetime) = 2021
                GROUP BY d.id, d.department
            ),
            HiresMean AS (
                SELECT AVG(CAST(hired_count AS FLOAT)) as mean_hires
                FROM DepartmentHires
            )
            SELECT 
                id,
                department,
                hired_count as hired
            FROM DepartmentHires, HiresMean
            WHERE hired_count > mean_hires
            ORDER BY hired_count DESC;
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [
                DepartmentHiresResponse(
                    id=row.id,
                    department=row.department,
                    hired=row.hired
                ) for row in rows
            ]
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving departments above mean: {str(e)}"
        )