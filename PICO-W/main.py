import socket
import network


ap = network.WLAN(network.AP_IF)
ap.config(essid='Pico-W-AP', password='123456789')
ap.active(True)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5) 

print('Access Point Started')
print('Network Name (SSID):', ap.config('essid'))

while True:
    conn, addr = s.accept() 
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024) 
    print('Content = %s' % str(request))

    response = """HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Pico W Web Server</title>
</head>
<body>
    <h1>Welcome to the Pico W Web Server!</h1>
    <p>This is a simple web page served directly from a Raspberry Pi Pico W.</p>
</body>
</html>
"""
    conn.send(response) 
    conn.close()
