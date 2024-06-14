# Import necessary libraries
import bluetooth
from machine import Pin
from hx711 import HX711
import time

# Define Bluetooth UUIDs
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    bluetooth.FLAG_WRITE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# Define the BLEUART class for Bluetooth communication
class BLEUART:
    def __init__(self, ble, name="PillBox_UART", rxbuf=50):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._ble.gatts_set_buffer(self._rx_handle, rxbuf, True)
        self._connections = set()
        self._rx_buffer = bytearray()
        self._handler = None
        self._payload = b"\x02\x01\x06\x11\xff\x06\x03\x03\xe0\xff\x01\x02\x00\x00\x00"
        self._advertise()

    def _irq(self, event, data):
        if event == 1:  # IRQ_CENTRAL_CONNECT
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == 2:  # IRQ_CENTRAL_DISCONNECT
            conn_handle, _, _ = data
            if conn_handle in self._connections:
                self._connections.remove(conn_handle)
            self._advertise()
        elif event == 3:  # IRQ_GATTS_WRITE
            conn_handle, value_handle = data
            if conn_handle in self._connections and value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(self._rx_handle)
                if self._handler:
                    self._handler()

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def send(self, data):
        for conn_handle in self._connections:
            try:
                self._ble.gatts_notify(conn_handle, self._tx_handle, data)
            except OSError as e:
                print("Failed to send notification:", e)

    def is_connected(self):
        return len(self._connections) > 0

    def any(self):
        return len(self._rx_buffer) > 0

    def read(self, sz=None):
        if not sz:
            sz = len(self._rx_buffer)
        result = self._rx_buffer[0:sz]
        self._rx_buffer = self._rx_buffer[sz:]
        return result

# Setup Bluetooth and UART
ble = bluetooth.BLE()
uart = BLEUART(ble)

# Main loop
while not uart.is_connected():
    time.sleep(1)  # Wait for connection

# Pins for load cell
PD_SCK_PIN = Pin(5, Pin.OUT)
DOUT_PIN = Pin(4, Pin.IN)

# HX711 constructor
load_cell = HX711(PD_SCK_PIN, DOUT_PIN)

# Calibration value
calibration_value = 70  # Set your calibration value here
load_cell.set_scale(calibration_value)

# Start HX711
load_cell.is_ready()
time.sleep(2)
load_cell.tare()

# Global variables for pill counting
r2 = 0
N = 0
prev_N = N
# Calibration process
uart.send("Please put 1 pill for calibration")
print("Please put 1 pill for calibration")
time.sleep(5)
for i in range(150):
    load_cell.get_units()
    if i % 10 == 0:
        print("skip")
o1 = load_cell.get_units()
uart.send("Calibration Done")
print("Calibration Done")

# Pill counting loop
while True:
            
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
            skip = load_cell.get_units()  #
        print("r2", r2)
        
    if N != prev_N:
        # Calculate the change in N
        change_in_N = N - prev_N
        if change_in_N > 0:
            uart.send("Total added pills: {}".format(change_in_N))
            print("Total added pills:", change_in_N)
        else:
            uart.send("Total taken pills: {}".format(-change_in_N))  # Convert negative change to positive
            print("Total taken pills:", -change_in_N)  # Convert negative change to positive
        
        uart.send("Total pills: {}".format(N))
        print("Total pills:", N)
        
        # Update previous value of N
        prev_N = N
            
    
