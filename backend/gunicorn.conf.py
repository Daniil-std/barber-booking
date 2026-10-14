import os

bind = "0.0.0.0:" + os.environ.get("PORT", "8000")
# One process keeps the demo's in-memory throttle cache coherent.
workers = 1
worker_class = "gthread"
threads = 4
timeout = 60
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
capture_output = True
# Trust headers only when Django's deployment setting explicitly enables it.
forwarded_allow_ips = ""
