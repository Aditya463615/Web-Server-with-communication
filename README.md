# Web-Server-with-communication
this is an example of how you can setup your Flask server with a communication service from `admin` page to `clients` page.
# Modules required 
install the following modules to use this script file 
```bash
pip install Flask
pip install Flask-SocketIO
```
# Setup your server
```python
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
    socketio.run(app, debug=True, host='0.0.0.0')
```
# admin page 
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Page</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1>Admin Page</h1>
        <div class="form-group">
            <label for="message">Message:</label>
            <input type="text" class="form-control" id="message">
        </div>
        <button class="btn btn-primary mb-3" onclick="sendMessageToAll()">Send Message to All</button>
        
        <!-- Container to display connected clients -->
        <div class="card">
            <div class="card-header">Connected Clients</div>
            <table class="table">
                <thead>
                    <tr>
                        <th>IP Address</th>
                        <th>Status</th>
                        <th>Connected Time</th>
                        <th>Disconnected Time</th>
                        <th>Device Name</th>
                        <!-- Add other necessary columns here -->
                    </tr>
                </thead>
                <tbody id="clientList">
                    <!-- Client information will be added here dynamically -->
                </tbody>
            </table>
        </div>
    
        <!-- Form to send message to a specific client -->
        <div class="mt-3">
            <label for="specificMessage">Send Message to Specific Client:</label>
            <input type="text" class="form-control" id="specificMessage">
            <select class="form-control mt-2" id="clientSelect">
                <!-- Client options will be added here dynamically -->
            </select>
            <button class="btn btn-success mt-2" onclick="sendMessageToSpecific()">Send Message</button>
        </div>
    </div>    

    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.2/socket.io.js"></script>
    <script>
        var socket = io.connect('http://' + document.domain + ':' + location.port);
    
        function sendMessageToAll() {
            var message = $('#message').val();
            socket.emit('send_message', {message: message});
        }
    
        function sendMessageToSpecific() {
            var message = $('#specificMessage').val();
            var clientId = $('#clientSelect').val();
            socket.emit('send_message_to_specific', {message: message, clientId: clientId});
        }
    
        // Update client list when a client connects or disconnects
        socket.on('update_client_list', function(data) {
            $('#clientList').empty();
            data.clients.forEach(function(client) {
                $('#clientList').append('<tr>' +
                    '<td>' + client.ip + '</td>' +
                    '<td>' + client.status + '</td>' +
                    '<td>' + client.connected_time + '</td>' +
                    '<td>' + (client.disconnected_time ? client.disconnected_time : '') + '</td>' +
                    '<td>' + client.device_name + '</td>' +
                    // Add other necessary columns here
                    '</tr>');
            });
    
            // Update client options for sending specific message
            $('#clientSelect').empty();
            data.clients.forEach(function(client) {
                $('#clientSelect').append('<option value="' + client.id + '">' + client.ip + '</option>');
            });
        });
    </script>    
</body>
</html>
```
# client page
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Client Page</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1>Client Page</h1>
        <div id="message-container"></div>
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.2/socket.io.js"></script>
    <script>
        var socket = io.connect('http://' + document.domain + ':' + location.port);

        socket.on('receive_message', function(data) {
            $('#message-container').append('<p>' + data.message + '</p>');
        });
    </script>
</body>
</html>
```
### You can modify the `admin.html` page and `client.html` page 
# Know more about the modules 
- Flask(https://flask.palletsprojects.com/en/3.0.x/)
- Socket.io(https://flask-socketio.readthedocs.io/en/latest/getting_started.html)
