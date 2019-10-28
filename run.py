from datetime import datetime
import os
import time
import serial
import board
import digitalio
import busio
import adafruit_bme280
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


i2c = busio.I2C(board.SCL, board.SDA)
air = adafruit_bme280.Adafruit_BME280_I2C(i2c)
cereal = serial.Serial('/dev/ttyUSB0')

influx_cloud_url = os.getenv('INFLUXDB_URL')
influx_cloud_token = os.getenv('INFLUXDB_TOKEN')
bucket = os.getenv('INFLUXDB_BUCKET')
org = os.getenv('INFLUXDB_ORG')
client = InfluxDBClient(url=influx_cloud_url, token=influx_cloud_token)
timeseries = client.write_api(write_options=SYNCHRONOUS)

quality = []
for i in range(10):
    quality.append(cereal.read())

pm_2_5 = int.from_bytes(b''.join(quality[2:4]), byteorder='little') / 10
pm_10 = int.from_bytes(b''.join(quality[4:6]), byteorder='little') / 10
    
point = Point('air') \
        .tag('location', 'desk') \
        .field('temperature', air.temperature) \
        .field('humidity', air.humidity) \
        .field('pressure', air.pressure) \
        .field('pm2.5', pm_2_5) \
        .field('pm10', pm_10) \
        .time(time=datetime.utcnow())

timeseries.write(
    org = org,
    bucket = bucket,
    record = point,
)
