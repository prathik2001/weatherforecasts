import requests
import json
import csv
import sys
import os
from dotenv import load_dotenv
from geocodio import GeocodioClient
from flask import Flask, render_template, request
from twilio.rest import Client

load_dotenv()
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
	return render_template('weather.html')

@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
	if request.method == 'POST':
		project_path = request.form['address']
		user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'}

		geo_client = GeocodioClient(os.getenv('GEOCODIO_KEY'))
		try:
			location1 = geo_client.geocode(project_path)
			coords = location1.coords
			try:
				url = 'https://api.weather.gov/points/' + str(coords[0]) + ',' + str(coords[1])
			except:
				return "National Weather Service lookup failed."
				sys.exit(1)
		except:
			return "Location not found. Please ensure the address was entered correctly."
			sys.exit(1)

		data = requests.get(url, headers = user_agent)
		location_data = data.json()
		cwa = location_data['properties']['cwa']
		location_url = location_data['properties']['forecast']
		forecast = requests.get(location_url)
		forecast_json = forecast.json()

		wfo = csv.reader(open('wfo.csv', "r"), delimiter=",")

		for row in wfo:
			if cwa == row[0]:
				wfo_info = row[0] + ' - ' + row[1]

		forecast_day_list = []
		forecast_list = []

		# Retrieves 7 days and 7 nights of forecasts.
		for x in range(0,14):
			forecast_day = str(forecast_json['properties']['periods'][x]['name']) 
			forecast_day_list.append(forecast_day)
			forecast = str(forecast_json['properties']['periods'][x]['detailedForecast'])
			forecast_list.append(forecast)

		return render_template('forecast.html', forecast = forecast_list, forecast_day = forecast_day_list, wfo = wfo_info)

@app.route('/sms', methods=['GET', 'POST'])
def sms():
	account_sid = os.getenv('ACCOUNT_SID')
	auth_token = os.getenv('AUTH_TOKEN')
	client = Client(account_sid, auth_token)

	if request.method == 'POST':
		number = "+1" + request.form['number']
		project_path = request.form['address']
		user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'}
		geo_client = GeocodioClient(os.getenv('GEOCODIO_KEY'))
		try:
			location1 = geo_client.geocode(project_path)
			coords = location1.coords
			try:
				url = 'https://api.weather.gov/points/' + str(coords[0]) + ',' + str(coords[1])
			except:
				return "National Weather Service lookup failed."
				sys.exit(1)
		except:
			return "Location not found. Please ensure the address was entered correctly."
			sys.exit(1)

		data = requests.get(url, headers = user_agent)
		location_data = data.json()
		cwa = location_data['properties']['cwa']
		location_url = location_data['properties']['forecast']
		forecast = requests.get(location_url)
		forecast_json = forecast.json()

		forecast_day_list = []
		forecast_list = []

		for x in range(0,4):
			forecast_day = str(forecast_json['properties']['periods'][x]['name']) 
			forecast_day_list.append(forecast_day)
			forecast = str(forecast_json['properties']['periods'][x]['detailedForecast'])
			forecast_list.append(forecast)

		custom = []

		custom.append(forecast_day_list[0])
		custom.append(forecast_list[0])
		custom.append(forecast_day_list[1])
		custom.append(forecast_list[1])
		custom.append(forecast_day_list[2])
		custom.append(forecast_list[2])
		custom.append(forecast_day_list[3])
		custom.append(forecast_list[3])

		body = ("Here's your weather report for " + projectpath + ": " + "\n\n" + 
				custom[0] + ': ' + custom[1] + '\n\n' + custom[2] + ': ' 
				+ custom[3] + "\n\n" + custom[4] + ': ' + custom[5] + '\n\n' 
				+ custom[6] + ': ' + custom[7] + "\n\n" + "Enjoy your day!")

		message = client.messages \
	                .create(
	                     body=body,
	                     from_='+12058945876',
	                     to=number
	                 )
	    
	return render_template('weather.html')

if __name__ == '__main__':
    app.run()
