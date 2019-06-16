from RPi import GPIO
import spidev
import time
import random
from DB1.database import Database
from flask import Flask

app = Flask(__name__)

conn = Database(app=app, user='wout', password='wout', db='Project', host='localhost', port=3306)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10 ** 5  # 100 kHz
blauwe_led = 27
teller = 0

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(blauwe_led, GPIO.OUT)

def read_spi(channel):
    spidata = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((spidata[1] & 3) << 8) + spidata[2]
    return data


def convert_volt(data):
    volt = (data * 3.3) / float(1023)
    volt = round(volt)
    return volt


def convert_procent(data):
    procent =(data * 100) / float(1023.0)
    procent = 100 - procent
    return round(procent, 2)


def check_omstandigheden():
    vochtigheid = conn.get_data("SELECT `Ideale Vochtigheid` FROM planten WHERE Plantnaam = 'Kerstomaat'")
    for dictionary in vochtigheid:
        for key, value in dictionary.items():
            ideale_vochtigheid = value
            return ideale_vochtigheid

def main():
    setup()
    global teller
    if teller == 0:
        channeldata = read_spi(0)
        percentage = convert_procent(channeldata)
        percentage2 = random.randint(75, 77)
        if check_omstandigheden() > percentage2:
            GPIO.output(blauwe_led, 1)
        else:
            GPIO.output(blauwe_led, 0)
        print("Vochtigheid = %s %%" % percentage2)
        conn.set_data("INSERT INTO vochtigheidssensor(Vochtigheid) VALUES (%s)",
                      percentage2)
        time.sleep(1)
        teller += 1


def destroy():
    GPIO.cleanup()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()


