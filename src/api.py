import os
import sys
import time
import threading
from dotenv import load_dotenv
from prometheus_client import Gauge, make_wsgi_app
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import requests


app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

url_up = Gauge('url_up', 'Whether the URL is reachable', ['url'])
url_response_time = Gauge('url_response_time_seconds', 'Response time in seconds', ['url'])

start_time = time.time()
alive = True
ready = False

@app.route("/ready")
def check_ready():
    if ready == True:
        return {"status": "ready"}, 200
    return {"status": "not ready"}, 503

@app.route("/start")
def start():
    global ready
    ready = True
    return {"status": "ready enabled"}, 200

@app.route("/stop")
def stop():
    global ready
    ready = False
    return {"status": "ready disabled"}, 200

@app.route("/health")
def health():
    if not alive:
        return {"status": "down"}, 500
    return {"status": "ok"}, 200

@app.route("/kill")
def kill():
    global alive
    alive = False
    return {"status": "killed app"}, 200

@app.route("/")
def home():
    return{"message": "app running"}, 200

def monitor_urls():
    urls = os.getenv("URLS")
    if urls:
        url_list = urls.split(",")
    else:
        sys.exit(1)

    while True:
        for url in url_list:
            try:
                start_time = time.time()
                requests.get(url, timeout=5)

                url_up.labels(url=url).set(1)
                response_time = time.time() - start_time
                url_response_time.labels(url=url).set(response_time)
             
            except requests.exceptions.RequestException as request_exception: url_up.labels(url=url).set(0) 
        global ready
        ready = True
        time.sleep(30)                    

if __name__ == "__main__":
    if os.path.exists('.env'):
        load_dotenv('.env')

    t = threading.Thread(target=monitor_urls, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=5000)
    
    
