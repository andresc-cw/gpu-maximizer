# Gunicorn configuration for GPU Tycoon
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
workers = 1
worker_class = 'sync'
timeout = 120

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Worker configuration
keepalive = 5

# For session support - use a single worker or enable sticky sessions
# This ensures users connect to the same worker
worker_tmp_dir = '/dev/shm'

