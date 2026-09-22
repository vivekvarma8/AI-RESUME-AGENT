import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1
worker_class = 'sync'
timeout = 300  # 5 minutes for first load
max_requests = 1000
max_requests_jitter = 50

# Don't preload - let it load lazily
preload_app = False

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True

graceful_timeout = 30
keepalive = 5