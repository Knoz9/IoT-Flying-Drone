import socket
import network

ap = network.WLAN(network.AP_IF)
ap.config(essid='Pico-Drone', password='123456789')
ap.active(True)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

print('Access Point Started')
print('Network Name (SSID):', ap.config('essid'))

def parse_query_params(query):
    """Parse query parameters from the URL."""
    params = {}
    for param in query.split('&'):
        key_value = param.split('=')
        if len(key_value) == 2:
            params[key_value[0]] = key_value[1]
    return params

while True:
    conn, addr = s.accept()  # Accept incoming connection
    request = conn.recv(1024).decode('utf-8')  # Receive the request and decode it
    request_line = request.split('\r\n')[0]  # Get the first line of the request
    path, _, query = request_line.split(' ')[1].partition('?')
    
    if path == '/position':
        params = parse_query_params(query)
        # Now expecting x1, y1 for joystick1 and x2, y2 for joystick2
        x1 = params.get('x1', '0')  # Default to 0 if not provided
        y1 = params.get('y1', '0')  # Default to 0 if not provided
        x2 = params.get('x2', '0')  # Default to 0 if not provided
        y2 = params.get('y2', '0')  # Default to 0 if not provided
        print(f'Joystick 1 Position: X={x1}%, Y={y1}% | Joystick 2 Position: X={x2}%, Y={y2}%')
    else:
        print('Unknown Command')

    # HTML with two independent joysticks
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Pico Joystick Controller</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="path/to/icon.png">
    <meta name="apple-mobile-web-app-title" content="Pico Joystick">
    <style>
        body, html {
            margin: 0;
            padding: 0;
            overflow: hidden;
            height: 100%;
            display: flex;
            justify-content: space-around;
            align-items: center;
            background-color: #f0f0f0;
        }
        .joystick {
            width: 100px;
            height: 100px;
            background-color: #ddd;
            border-radius: 50%;
            position: relative;
            margin-bottom: -150px;
        }
        .handle {
            width: 50px;
            height: 50px;
            background-color: #bbb;
            border-radius: 50%;
            position: absolute;
            top: 25px; left: 25px;
            touch-action: none;
        }
        .spacer {
            width: 60vw; /* Width of the spacer to control the space between joysticks */
            height: 100%; /* Match the parent's height */
            /* No background color needed as it's an invisible spacer */
        }
    </style>
</head>
<body>
    <div class="joystick" id="joystick1">
        <div class="handle"></div>
    </div>
    <div class="spacer"></div> <!-- Invisible spacer element -->
    <div class="joystick" id="joystick2">
        <div class="handle"></div>
    </div>
<script>
let joystickPositions = {
    joystick1: { x: 50, y: 50 },
    joystick2: { x: 50, y: 50 }
};
let updateInterval;

function initJoystick(joystickId) {
    const joystick = document.getElementById(joystickId);
    const handle = joystick.querySelector('.handle');

    function moveHandle(event, touchId) {
        const touch = Array.from(event.changedTouches).find(t => t.identifier === touchId);
        if (!touch) return;

        const rect = joystick.getBoundingClientRect();
        const clientX = touch.clientX - rect.left;
        const clientY = touch.clientY - rect.top;
        const maxX = rect.width - handle.offsetWidth;
        const maxY = rect.height - handle.offsetHeight;
        const handleX = Math.max(Math.min(clientX - (handle.offsetWidth / 2), maxX), 0);
        const handleY = Math.max(Math.min(clientY - (handle.offsetHeight / 2), maxY), 0);
        joystickPositions[joystickId].x = (handleX / maxX) * 100;
        joystickPositions[joystickId].y = (handleY / maxY) * 100;

        handle.style.left = `${handleX}px`;
        handle.style.top = `${handleY}px`;
    }

    joystick.addEventListener('touchstart', (e) => {
        Array.from(e.changedTouches).forEach(touch => {
            moveHandle(e, touch.identifier);
        });
    }, {passive: false});

    joystick.addEventListener('touchmove', (e) => {
        Array.from(e.changedTouches).forEach(touch => {
            moveHandle(e, touch.identifier);
        });
    }, {passive: false});

    joystick.addEventListener('touchend', (e) => {
        // Touch end logic if needed
    });
}

function startSendingPositions() {
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(sendPositions, 500);
}

function sendPositions() {
    const { joystick1, joystick2 } = joystickPositions;
    console.log(`Joystick 1 Position: X=${joystick1.x}%, Y=${joystick1.y}% | Joystick 2 Position: X=${joystick2.x}%, Y=${joystick2.y}%`);
    fetch(`/position?x1=${joystick1.x}&y1=${joystick1.y}&x2=${joystick2.x}&y2=${joystick2.y}`)
        .catch(console.error);
}

// Initialize both joysticks and start sending positions
initJoystick('joystick1');
initJoystick('joystick2');
startSendingPositions();
</script>
</body>
</html>

"""

    response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html
    conn.sendall(response.encode('utf-8'))  # Send the response
    conn.close()  # Close the connection


