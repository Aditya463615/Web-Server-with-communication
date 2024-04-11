from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Dictionary to store connected clients
clients = {}

# Route for the admin page
@app.route('/admin')
def admin():
    return render_template('admin.html', clients=str(clients))

# Route for the client page
@app.route('/client')
def client():
    return render_template('client.html')

# Event handler for when a client connects
@socketio.on('connect')
def handle_connect():
    ip = request.remote_addr
    clients[request.sid] = {
        'id': request.sid,
        'ip': ip,
        'status': 'Active',
        'connected_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'disconnected_time': None,
        'device_name': 'Unknown'  # You can modify this to get the actual device name
        # Add other necessary information here
    }
    print('Client connected:', ip)
    emit('update_client_list', {'clients': list(clients.values())}, broadcast=True)

# Event handler for when a client disconnects
@socketio.on('disconnect')
def handle_disconnect():
    client = clients.pop(request.sid, None)
    if client:
        client['status'] = 'Inactive'
        client['disconnected_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('Client disconnected:', client['ip'])
        emit('update_client_list', {'clients': list(clients.values())}, broadcast=True)

# Event handler for sending messages from admin to clients
@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']
    for client in clients:
        emit('receive_message', {'message': message}, room=client)

# Event handler for sending messages from admin to specific clients
@socketio.on('send_message_to_specific')
def handle_send_message_to_specific(data):
    message = data['message']
    client_id = data['clientId']
    client = clients.get(client_id)
    if client:
        emit('receive_message', {'message': message}, room=client['id'])

if __name__ == '__main__':
    socketio.run(app, debug=True, host='192.168.31.151')
