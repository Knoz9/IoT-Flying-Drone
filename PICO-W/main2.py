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
        joystick_id = params.get('id', '1')  # Default to joystick 1 if not specified
        x = params.get('x', '0')  # Default to 0 if not provided
        y = params.get('y', '0')  # Default to 0 if not provided
        print(f'Joystick {joystick_id} Position: X={x}%, Y={y}%')
    else:
        print('Unknown Command')

    # HTML with two independent joysticks
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Pico Joystick Controller</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    </style>
</head>
<body>
    <div class="joystick" id="joystick1">
        <div class="handle"></div>
    </div>
    <div class="joystick" id="joystick2">
        <div class="handle"></div>
    </div>
<script>
// Function to initialize a joystick
function initJoystick(joystickId) {
    const joystick = document.getElementById(joystickId);
    const handle = joystick.querySelector('.handle');
    let active = false;
    let currentXPercentage = 50; // Start in the middle for joystick2
    let currentYPercentage = 50; // Start in the middle
    let intervalId = null;

    function moveHandle(e) {
        e.preventDefault();
        let event = e.type.includes('touch') ? e.touches[0] : e;
        let rect = joystick.getBoundingClientRect();
        let clientY = event.clientY - rect.top;
        
        // Ensure the handle stays within the joystick's bounds
        let maxY = rect.height - handle.offsetHeight;
        let handleY = Math.max(Math.min(clientY - (handle.offsetHeight / 2), maxY), 0);
        
        if (joystickId === 'joystick1') {
            // Reverse Y percentage calculation for joystick1
            currentYPercentage = 100 - ((handleY / maxY) * 100);
            handle.style.top = `${handleY}px`;
            handle.style.left = `${(rect.width - handle.offsetWidth) / 2}px`; // Keep centered horizontally
        } else {
            // Allow free movement for joystick2
            let clientX = event.clientX - rect.left;
            let maxX = rect.width - handle.offsetWidth;
            let handleX = Math.max(Math.min(clientX - (handle.offsetWidth / 2), maxX), 0);
            currentXPercentage = (handleX / maxX) * 100;
            currentYPercentage = ((maxY - handleY) / maxY) * 100; // Maintain original Y calculation for joystick2
            handle.style.left = `${handleX}px`;
            handle.style.top = `${handleY}px`;
        }
    }

    function updatePosition() {
        // Send position updates; no changes needed here as adjustments are made above
        sendPosition(joystickId === 'joystick2' ? Math.round(currentXPercentage) : 0, Math.round(currentYPercentage));
    }

    function sendPosition(x, y) {
        console.log(`Joystick ${joystickId} Position: X=${x}%, Y=${y}%`);
        fetch(`/position?id=${joystickId}&x=${x}&y=${y}`).catch(console.error);
    }

    // Event listeners setup remains unchanged
    joystick.addEventListener('mousedown', (e) => { active = true; moveHandle(e); startPeriodicUpdates(); });
    joystick.addEventListener('touchstart', (e) => { active = true; moveHandle(e); startPeriodicUpdates(); }, {passive: false});
    document.addEventListener('mousemove', (e) => { if (active) moveHandle(e); });
    document.addEventListener('touchmove', (e) => { if (active) moveHandle(e); }, {passive: false});
    document.addEventListener('mouseup', () => { active = false; stopPeriodicUpdates(); });
    document.addEventListener('touchend', () => { active = false; stopPeriodicUpdates(); });

    function startPeriodicUpdates() {
        if (!intervalId) {
            intervalId = setInterval(updatePosition, 400);
        }
    }

    function stopPeriodicUpdates() {
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
    }
}

// Initialize both joysticks
initJoystick('joystick1');
initJoystick('joystick2');
</script>


</body>
</html>
"""

    response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html
    conn.sendall(response.encode('utf-8'))  # Send the response
    conn.close()  # Close the connection

