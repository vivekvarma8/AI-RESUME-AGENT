import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1
worker_class = 'sync'
timeout = 600  # Increased to 10 minutes
max_requests = 1000
max_requests_jitter = 50
preload_app = False

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'debug'  # Changed to debug
capture_output = True

graceful_timeout = 60
keepalive = 10

# Worker lifecycle
worker_tmp_dir = '/dev/shm'  # Use RAM disk for worker heartbeat