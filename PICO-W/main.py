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
        if 'y' in params:
            percentage = params['y']
            print(f'Vertical Position: {percentage}%')
        else:
            print('Y position not found')
    else:
        print('Unknown Command')

    
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Pico Joystick Controller</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body, html {
            margin: 0;
            padding: 0;
            overflow: hidden; /* Disable scrolling */
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #f0f0f0;
        }
        body, html {
        height: 100vh; /* Use viewport height */
        max-height: 100vh; /* Prevent extending beyond the viewport height */
        }
        body, html {
        width: 100vw; /* Viewport width to ensure full width is covered */
        overflow-x: hidden; /* Specifically disable horizontal scrolling */
        }


        #joystick {
            width: 100px;
            height: 100px;
            background-color: #ddd;
            border-radius: 50%;
            position: absolute; /* Use absolute positioning within the flex container */
        }
        #handle {
            width: 50px;
            height: 50px;
            background-color: #bbb;
            border-radius: 50%;
            position: absolute;
            top: 50px; left: 25px; /* Centered within joystick */
            touch-action: none; /* Prevent the browser from handling touch actions */
        }
    </style>
</head>
<body>
    <div id="joystick">
        <div id="handle"></div>
    </div>
   <script>
    const joystick = document.getElementById('joystick');
    const handle = document.getElementById('handle');
    let active = false;
    let currentYPercentage = 0; // Assume starting at the middle (50%)
    let intervalId = null;

    function moveHandle(e) {
        e.preventDefault(); // Prevent default behavior for all events
        let event = e.type.includes('touch') ? e.touches[0] : e;
        let rect = joystick.getBoundingClientRect();
        let clientY = event.clientY - rect.top;

        // Ensure the handle stays within the joystick's vertical bounds
        let handleTopMin = 0;
        let handleTopMax = rect.height - handle.offsetHeight;
        let handleY = Math.max(Math.min(clientY - (handle.offsetHeight / 2), handleTopMax), handleTopMin);

        // Calculate the percentage position of the handle
        currentYPercentage = 100 - ((handleY / handleTopMax) * 100);
        handle.style.top = `${handleY}px`;
    }

    function updatePosition() {
        // Send the vertical position as a percentage, rounded to nearest integer
        sendPosition(Math.round(currentYPercentage));
    }

    function sendPosition(y) {
        console.log(`Vertical Position: ${y}%`); // For debugging
        fetch(`/position?y=${y}`).catch(console.error);
    }

    // Initialize periodic updates
    function startPeriodicUpdates() {
        if (!intervalId) {
            intervalId = setInterval(updatePosition, 400); // Update position every 1 second
        }
    }

    function stopPeriodicUpdates() {
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
    }

    // Event listeners to handle drag/move
    joystick.addEventListener('mousedown', (e) => { active = true; moveHandle(e); startPeriodicUpdates(); });
    joystick.addEventListener('touchstart', (e) => { active = true; moveHandle(e); startPeriodicUpdates(); }, {passive: false});

    document.addEventListener('mousemove', (e) => { if (active) moveHandle(e); });
    document.addEventListener('touchmove', (e) => { if (active) moveHandle(e); }, {passive: false});

    // Event listeners to stop moving the handle and updates
    document.addEventListener('mouseup', () => { active = false; });
    document.addEventListener('touchend', () => { active = false; });

    // Start periodic updates by default in case the joystick is not moved after page load
    startPeriodicUpdates();
</script>


</body>
</html>

"""

    
    response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html
    conn.sendall(response.encode('utf-8'))  # Send the response
    conn.close()  # Close the connection
