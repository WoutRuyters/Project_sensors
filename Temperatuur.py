from RPi import GPIO
import time
from DB1.database import Database
from flask import Flask

app = Flask(__name__)

conn = Database(app=app, user='wout', password='wout', db='Project', host='localhost', port=3306)

sensor_file_name = '/sys/bus/w1/devices/28-0000085b4617/w1_slave'
print("Het script runt")

rode_rgb = 23
groene_rgb = 22
blauwe_rgb = 18
teller = 0


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(rode_rgb, GPIO.OUT)
    GPIO.setup(groene_rgb, GPIO.OUT)
    GPIO.setup(blauwe_rgb, GPIO.OUT)


def check_omstandigheden():
    temperatuur = conn.get_data("SELECT `Ideale Temperatuur` FROM planten WHERE Plantnaam = 'Kerstomaat'")
    for dictionary in temperatuur:
        for key, value in dictionary.items():
            ideale_temperatuur = value
            return ideale_temperatuur


def main():
    global teller
    setup()
    if teller == 0:
        fo = open(sensor_file_name, 'r')
        lijn = fo.readline()
        lijn = fo.readline()
        delen = lijn.split("t=")
        temp = int(delen[1]) / 1000
        if check_omstandigheden() == temp:
            GPIO.output(groene_rgb, 1)
            GPIO.output(rode_rgb, 0)
            GPIO.output(blauwe_rgb, 0)
        elif check_omstandigheden() > temp:
            GPIO.output(rode_rgb, 1)
            GPIO.output(groene_rgb, 0)
            GPIO.output(blauwe_rgb, 0)
        elif check_omstandigheden() < temp:
            GPIO.output(blauwe_rgb, 1)
            GPIO.output(groene_rgb, 0)
            GPIO.output(rode_rgb, 0)
        print("Het is %0.2f °C" % float(temp))
        fo.close()
        conn.set_data("INSERT INTO temperatuursensor(Temperatuur) VALUES (%s)",
                      temp)
        time.sleep(1)
        teller += 1


def destroy():
    GPIO.cleanup()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()

