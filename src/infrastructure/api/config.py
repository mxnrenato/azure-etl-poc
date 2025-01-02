from pydantic import BaseSettings

class Settings(BaseSettings):
    azure_storage_connection_string: str
    azure_sql_connection_string: str
    azure_monitor_connection_string: str
    
    class Config:
        env_file = ".env"

settings = Settings()