from flask import Flask, render_template, request
import requests
import json

with open("config.json", "r") as c:
    config = json.load(c)["configuration"]

BASE = config["base"]
BASE_HOUR = config['hour']
API_KEY = config["key"]
BASE_AIR = config["air"]


class CurrentWeather:
    MainWeather = None
    WeatherIcon = None
    MainTemp = None
    WindSpeed = None
    LocationName = None
    FeelsLike = None
    Humidity = None

    def __init__(self, raw_data):
        self.MainWeather = raw_data['weather'][0]['main']
        self.WeatherIcon = raw_data['weather'][0]['icon']
        self.MainTemp = raw_data['main']['temp']
        self.WindSpeed = raw_data['wind']['speed']
        self.LocationName = raw_data['name']
        self.FeelsLike = raw_data['main']['feels_like']
        self.Humidity = raw_data['main']['humidity']


class HourlyWeather:
    HourlyTime = None
    HourlyTemp = None
    HourlyWeather = None
    HourlyIcon = None

    def __init__(self, hour):
        self.HourlyTime = hour['dt']
        self.HourlyTemp = hour['temp']
        self.HourlyWeather = hour['weather'][0]['main']
        self.HourlyIcon = hour['weather'][0]['icon']


class AirPollution:
    AirQuality = None
    CO = None
    NO = None
    NO2 = None
    O3 = None
    SO2 = None
    NH3 = None

    def __init__(self, air_quality):
        self.AirQuality = int(air_quality["list"][0]["main"]["aqi"])
        self.CO = air_quality["list"][0]["components"]["co"]
        self.NO = air_quality["list"][0]["components"]["no"]
        self.NO2 = air_quality["list"][0]["components"]["no2"]
        self.O3 = air_quality["list"][0]["components"]["o3"]
        self.SO2 = air_quality["list"][0]["components"]["so2"]
        self.NH3 = air_quality["list"][0]["components"]["nh3"]


class Alerts:
    AlertEvent = None
    AlertDesc = None
    AlertTagList = None

    def __init__(self, alerts_data):
        self.AlertEvent = alerts_data["event"]
        self.AlertDesc = alerts_data["description"]
        self.AlertTagList = alerts_data["tags"]


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


def extract_data(location):
    city = location
    url = BASE + "q=" + city + "&appid=" + API_KEY + "&units=metric"
    response = requests.get(url)
    return response


def get_hourly(latitude, longitude):
    url = BASE_HOUR + f"lat={latitude}&lon={longitude}&exclude=minutely,daily,alerts&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response


def get_air_data(latitude, longitude):
    url = BASE_AIR + f"lat={latitude}&lon={longitude}&appid={API_KEY}"
    response = requests.get(url)
    return response


def get_alert_data(latitude, longitude):
    url = BASE_HOUR + f"lat={latitude}&lon={longitude}&exclude=current,minutely,daily,hourly&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response


@app.route("/", methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        location = request.form.get('location')
        response = extract_data(location)
        raw_data = response.json()
        current = CurrentWeather(raw_data)
        return render_template("location.html", data=current)
    return render_template("index.html")


@app.route("/location/", methods=['GET', 'POST'])
def location_page():
    if request.method == 'POST':
        location = request.form.get('location')
        response = extract_data(location)
        raw_data = response.json()
        curr = CurrentWeather(raw_data)
        return render_template("location.html", data=curr)


@app.route("/hourly", methods=['GET', 'POST'])
def hourly_page():
    if request.method == 'POST':
        location = request.form.get('location')
        response = extract_data(location)
        raw_data = response.json()
        current = CurrentWeather(raw_data)
        lat, lon = raw_data['coord']['lat'], raw_data['coord']['lon']
        hourly_response = get_hourly(lat, lon)
        hourly_data = hourly_response.json()
        hours = hourly_data['hourly']
        hour_list = []
        for hour in hours:
            x = HourlyWeather(hour)
            hour_list.append(x)
        return render_template("hourly_forecast.html", hourdata=hour_list, currentdata=current)
    return render_template("hourly.html")


@app.route("/air_quality", methods=['GET', 'POST'])
def air_quality_page():
    if request.method == 'POST':
        location = request.form.get('location')
        response = extract_data(location)
        raw_data = response.json()
        lat, lon = raw_data['coord']['lat'], raw_data['coord']['lon']
        air_data_response = get_air_data(lat, lon)
        air_data = air_data_response.json()
        air = AirPollution(air_data)
        return render_template("air_quality.html", air_data=air)
    return render_template("air_quality_homepage.html")


@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response


app.run(debug=True)
