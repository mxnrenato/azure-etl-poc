cd /home/site/wwwroot
pip install -r requirements.txt
gunicorn src.infrastructure.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000