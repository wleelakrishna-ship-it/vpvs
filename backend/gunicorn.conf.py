# Gunicorn configuration for FastAPI
bind = "0.0.0.0:10000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
worker_connections = 1000
