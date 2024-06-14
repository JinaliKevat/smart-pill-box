from machine import Pin
from time import sleep
from hx711 import HX711
import socket
import network
import _thread

# Setup softAP (Access Point) network
AP_SSID = "PillBox_AP"
AP_PASSWORD = "password"

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=AP_SSID, password=AP_PASSWORD)

# Print softAP network details
ap_ip = ap.ifconfig()[0]
print("SoftAP started")
print("Connect to WiFi network:", AP_SSID)
print("SoftAP IP address:", ap_ip)



# Function to handle client requests
def handle_client(conn):
    global r2, N, o1 # Declare global variables
    
    request = conn.recv(1024)
    print("Request:", request)
    
    # Pill counting logic
    r1 = load_cell.get_units()  # Getting new response
    print("r1", r1)
    
    W = round((r1 - r2) / o1)  # Getting the number of pills changed value
    print("No. of pills changed =", W)
    
    N += W  # Updating total number of pills value
    print("Total pills:", N)
    print("-----------------------------")
    
    if r1 != r2: 
        r2 = r1  # Updating r2 after each cycle
        for i in range(30):
            skip = load_cell.get_units()  # Skipping again for stabilized values
        print("r2", r2)
    
    # Generate HTTP response
    response = HTML_TEMPLATE.format(N=N)
    conn.sendall(b'HTTP/1.1 200 OK\r\n')
    conn.sendall(b'Content-Type: text/html\r\n')
    conn.sendall(b'Connection: close\r\n\r\n')
    conn.sendall(response.encode())
    conn.close()

def start_web_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(1)
    print("Server started")
    
    while True:
        
        client_conn, client_addr = server_socket.accept()
        print("Client connected from:", client_addr)
        calibration(client_conn)
        _thread.start_new_thread(msg, (client_conn,))
        
        while True:
            
            client_conn, client_addr = server_socket.accept()
            print("Client connected from:", client_addr)
            msg(client_conn)
            _thread.start_new_thread(handle_client, (client_conn,))

        
            while True:
                
                client_conn, client_addr = server_socket.accept()
                print("Client connected from:", client_addr)
                handle_client(client_conn)

# Pins
PD_SCK_PIN = Pin(5, Pin.OUT)
DOUT_PIN = Pin(4, Pin.IN)

# HX711 constructor
load_cell = HX711(PD_SCK_PIN, DOUT_PIN)

# Calibration value
calibration_value = 70  # Set your calibration value here
load_cell.set_scale(calibration_value)

# Start HX711
load_cell.is_ready()
sleep(2)
load_cell.tare()

# Global variables for pill counting
r2 = 0
N = 0

# HTML template for the webpage
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>PILL BOX THAT IS NOT VERY SMART, YET!:))</title>
    <meta http-equiv="refresh" content="0.5"> <!-- Refresh the page every 0.5 seconds -->
</head>
<body style="background-color: #f0f0f0; font-family: Arial, sans-serif; text-align: center;">
    <h1>Total Pill Count</h1>
    <p style="font-size: 24px;">Total Pills: {N}</p>
</body>
</html>
"""

HTML_TEMPLATE2 = """<!DOCTYPE html>
<html>
<head>
    <title>PILL BOX THAT IS NOT VERY SMART, YET!:))</title>
    <meta http-equiv="refresh" content="0.5"> <!-- Refresh the page every 2 seconds -->
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f2f2f2;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        p {
            color: #666;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Calibration:</h1>
        <p>Place 1 pill for calibration</p> <!-- Removed {N} placeholder -->
    </div>
</body>
</html>

"""
HTML_TEMPLATE3= """<!DOCTYPE html>
<html>
<head>
    <title>PILL BOX THAT IS NOT VERY SMART, YET!:))</title>
    <meta http-equiv="refresh" content="0.5"> <!-- Refresh the page every 2 seconds -->
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f2f2f2;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        p {
            color: #666;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Calibration Done!! Now you can enter your pills</h1>
        <p></p>
    </div>
</body>
</html>

"""

def calibration(conn):
    request = conn.recv(1024)
    print("Request:", request)
    
    # Generate HTTP response
    response = HTML_TEMPLATE2
    conn.sendall(b'HTTP/1.1 200 OK\r\n')
    conn.sendall(b'Content-Type: text/html\r\n')
    conn.sendall(b'Connection: close\r\n\r\n')
    conn.sendall(response.encode())
    sleep(7)
    conn.close()
    
    # Calibration process
    print("Place 1 pill for calibration: ")
    sleep(5)
    for i in range(150):
        skip = load_cell.get_units()
        if i % 10 == 0:
            print(skip)
    global o1
    o1 = load_cell.get_units()
    print("o1", o1)
    print("----------------------------------")
    sleep(2)
    


def msg(conn):
    request = conn.recv(1024)
    print("Request:", request)
    
    # Generate HTTP response
    response = HTML_TEMPLATE3
    conn.sendall(b'HTTP/1.1 200 OK\r\n')
    conn.sendall(b'Content-Type: text/html\r\n')
    conn.sendall(b'Connection: close\r\n\r\n')
    conn.sendall(response.encode())
    conn.close()

# Start the web server after calibration
start_web_server()