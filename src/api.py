import time
from flask import Flask


app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)