-- src/infrastructure/persistence/scripts/init.sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    datetime DATETIME NOT NULL,
    department_id INT NOT NULL,
    job_id INT NOT NULL,
    CONSTRAINT FK_Employee_Department FOREIGN KEY (department_id) REFERENCES departments(id),
    CONSTRAINT FK_Employee_Job FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE TABLE departments (
    id INT PRIMARY KEY,
    name NVARCHAR(255) NOT NULL
);

CREATE TABLE jobs (
    id INT PRIMARY KEY,
    name NVARCHAR(255) NOT NULL
);

-- Índices para mejorar el rendimiento
CREATE INDEX IX_Employee_Department ON employees(department_id);
CREATE INDEX IX_Employee_Job ON employees(job_id);
CREATE INDEX IX_Employee_HireDate ON employees(datetime);