# smart-pill-box
In today's fast-paced world, maintaining adherence to medication schedules is a significant challenge. To address this issue, we have developed the Smart Pill Box, an innovative solution designed to ensure accurate and timely medication intake. Our device leverages a load cell and HX711 ADC converter to precisely measure the number of pills stored and track the quantity dispensed during each use. At the heart of the Smart Pill Box is the XIAO ESP32 C3 microcontroller, which manages device operations and facilitates seamless communication with users.
We use a webserver based application and a bluetooth based application to share data with the user in real time.

# Components
1. Load Cell
2. Hx711 ADC
3. XIAO ESP32 C3
4. 3.7 V rechargable battery

# Software
1. MicroPython for ESP32
2. Thonny IDE - for installing and running MicroPython
3. Bluetooth Terminal app - https://play.google.com/store/apps/details?id=de.kai_morich.serial_bluetooth_terminal
4. Hx711 MicroPython gpio library by robert-hh - https://github.com/robert-hh/hx711/tree/master
