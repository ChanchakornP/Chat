from flask_socketio import SocketIO

from . import create_app

app = create_app()
socketio = SocketIO(app)

if __name__ == "__main__":
    socketio.run(port=8000, debug=True)
