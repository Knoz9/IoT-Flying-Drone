import network
import time
import socket
import machine

# Setup for onboard LED for visual feedback
led = machine.Pin(25, machine.Pin.OUT)  # Adjust pin number if needed

def blink_led(duration=0.1, count=1):
    """Toggle the LED to blink a specified number of times."""
    for _ in range(count):
        led.value(1)  # LED on
        time.sleep(duration)
        led.value(0)  # LED off
        time.sleep(duration)

# Initialize WiFi in station mode
sta_if = network.WLAN(network.STA_IF)

def connect_to_wifi(ssid, password, timeout=10):
    """Attempts to connect to the WiFi network with a timeout."""
    if sta_if.isconnected():
        return  # Already connected
    print('Connecting to network...')
    sta_if.active(True)
    sta_if.connect(ssid, password)
    for _ in range(timeout):
        if sta_if.isconnected():
            print('WiFi connected successfully')
            print('Network config:', sta_if.ifconfig())
            blink_led(0.1, 3)  # Blink 3 times to indicate successful connection
            return
        blink_led(0.2)  # Slow blink to indicate retry
        time.sleep(1)
    print("Failed to connect to WiFi")

# Attempt to connect to the WiFi network
connect_to_wifi('iPhone3', '123456789')

# Setup socket for server
def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    return s

s = create_socket()
print("Listening for connections...")

def parse_query_params(query):
    """Parse query parameters from the URL."""
    params = {}
    for param in query.split('&'):
        key_value = param.split('=')
        if len(key_value) == 2:
            params[key_value[0]] = key_value[1]
    return params

while True:
    # Check and reconnect to WiFi if necessary
    if not sta_if.isconnected():
        print("WiFi connection lost, attempting to reconnect...")
        connect_to_wifi('iPhone3', '123456789')  # Attempt to reconnect to WiFi
        s.close()  # Close the existing socket
        s = create_socket()  # Recreate the socket server
        print("Resuming listening for connections...")
    try:
        conn, addr = s.accept()  # Accept incoming connection
        print('Connection from:', addr)
        request = conn.recv(1024).decode('utf-8')  # Receive the request and decode it
        if not request:
            raise ValueError("Empty request received, closing connection.")
        request_line = request.split('\r\n')[0]
        path, _, query = request_line.split(' ')[1].partition('?')
        
        if path == '/position':
            params = parse_query_params(query)
            x1 = params.get('x1', '0')
            y1 = params.get('y1', '0')
            x2 = params.get('x2', '0')
            y2 = params.get('y2', '0')
            blink_led()
            print(f'Joystick 1 Position: X={x1}, Y={y1} | Joystick 2 Position: X={x2}, Y={y2}')
        else:
            print('Unknown Command')

        # [Include your HTML content here]
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
            width: 200px;
            height: 200px;
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
            top: 75px; left: 75px;
            touch-action: none;
        }
        .spacer {
            width: 40vw; /* Width of the spacer to control the space between joysticks */
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
    joystick1: { x: 1500, y: 1500 }, // Initialize with default middle values
    joystick2: { x: 1500, y: 1500 },
};
let previousPositions = JSON.parse(JSON.stringify(joystickPositions)); // To compare changes
let updateInterval;

function initJoystick(joystickId) {
    const joystick = document.getElementById(joystickId);
    const handle = joystick.querySelector('.handle');

    function mapValue(percentage, min, max) {
        return min + (max - min) * (percentage / 100);
    }

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
        const xPercentage = (handleX / maxX) * 100;
        const yPercentage = (handleY / maxY) * 100;

        // Map the percentage to the desired range
        joystickPositions[joystickId].x = mapValue(xPercentage, 1000, 2000);
        joystickPositions[joystickId].y = mapValue(yPercentage, 1000, 2000);

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

function positionsChanged() {
    return previousPositions.joystick1.x !== joystickPositions.joystick1.x ||
           previousPositions.joystick1.y !== joystickPositions.joystick1.y ||
           previousPositions.joystick2.x !== joystickPositions.joystick2.x ||
           previousPositions.joystick2.y !== joystickPositions.joystick2.y;
}

function updatePreviousPositions() {
    previousPositions = JSON.parse(JSON.stringify(joystickPositions));
}

function sendPositions() {
    if (positionsChanged()) {
        const { joystick1, joystick2 } = joystickPositions;
        console.log(`Joystick 1 Position: X=${Math.round(joystick1.x)}, Y=${Math.round(joystick1.y)} | Joystick 2 Position: X=${Math.round(joystick2.x)}, Y=${Math.round(joystick2.y)}`);
        fetch(`/position?x1=${Math.round(joystick1.x)}&y1=${Math.round(joystick1.y)}&x2=${Math.round(joystick2.x)}&y2=${Math.round(joystick2.y)}`)
            .then(() => updatePreviousPositions())
            .catch(console.error);
    }
}

function startSendingPositions() {
    if (updateInterval) clearInterval(updateInterval);
    updateInterval = setInterval(sendPositions, 300); // Adjusted for faster updates but with change checks
}

// Initialize both joysticks and start the position sending mechanism
initJoystick('joystick1');
initJoystick('joystick2');
startSendingPositions();
</script>
   
</body>
</html>
"""
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + html
        conn.sendall(response.encode('utf-8'))  # Send the response
    except Exception as e:
        print("Error handling connection:", e)
    finally:
        conn.close()  # Ensure connection is closed

