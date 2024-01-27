import threading

from flask import Flask



app = Flask(__name__)

class SharedState:
    def __init__(self):
        self._lock = threading.Lock()
        self._cable_status = "Off"

    @property
    def cable_status(self):
        with self._lock:
            return self._cable_status

    @cable_status.setter
    def cable_status(self, value):
        with self._lock:
            self._cable_status = value

shared_state = SharedState()

@app.route('/')
def home():
    return f'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

