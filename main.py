import network
import urequests
from machine import Pin, I2C
from time import sleep_ms
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import network_credentials
import routes

# Set up the WiFi connection
ssid = network_credentials.SSID
password = network_credentials.PASSWORD
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)
while not wifi.isconnected():
    pass
print("Wi-Fi Connected")

# Get routes from the config file
stop_id, agency_tag, route_number = routes.get_routes()


api_url = "http://retro.umoiq.com/service/publicJSONFeed?command=predictions&a={}&stopId={}&r={}&s=0".format(agency_tag, stop_id, route_number)


# Set up the LCD display
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Define a function to scroll a string on the LCD display
def scroll_string(string, line):
    for i in range(len(string) - 15):
        lcd.clear()
        lcd.move_to(0, line)
        lcd.putstr(string[i:i+16])
        sleep_ms(500)

# Set up the transit safety information
safety_info = [
    "Keep your belongings",
    "close to you at all times",
    "Report any suspicious",
    "activity to the driver",
    "Be aware of your",
    "surroundings",
    "Don't engage with",
    "aggressive passengers",
]

# Start by displaying the route information
display_route_info = True

while True:
    if display_route_info:
        # Retrieve real-time departure information from Nextbus
        response = urequests.get(api_url).json()

        # Extract the relevant departure information and route information
        if "predictions" in response and "direction" in response["predictions"][0]:
            next_bus_time = response["predictions"][0]["direction"][0]["prediction"][0]["minutes"]
            departure_info = "Next bus in {} min".format(next_bus_time)
            route_info = "Route: {}".format(response["predictions"][0]["routeTitle"])
        else:
            departure_info = "Error retrieving data"
            route_info = ""

        # Output the departure and route information to the LCD display
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(departure_info)
        lcd.move_to(0, 1)
        lcd.putstr(route_info)

    else:
        # Scroll the transit safety information on the LCD display
        for line, info in enumerate(safety_info):
            scroll_string(info, line)
            lcd.clear()
            sleep_ms(500)

    # Switch between displaying the route information and scrolling the transit safety information
    display_route_info = not display_route_info

    sleep_ms(30000)
