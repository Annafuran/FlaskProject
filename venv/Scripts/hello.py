from flask import Flask, render_template
import numpy as np
import json
import pandas as pd
import folium
import seaborn as sns
import csv
import matplotlib.pyplot as plt
from folium.map import *
from folium import plugins
from folium.plugins import MeasureControl
from folium.plugins import FloatImage
import sys
import io
import random
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

#Hämtar och byter namn på datan, för enklare hantering.
terror = pd.read_csv('globalterrorismdb_0718dist.csv', low_memory=False, error_bad_lines=False, encoding='ISO-8859-1', nrows=100000)

terror.rename(columns={'iyear':'Year','imonth':'Month',
	'iday':'Day','country_txt':'Country','region_txt':'Region',
	'latitude' : 'Lat', 'longitude' : 'Long',
	'attacktype1_txt':'AttackType','target1':'Target',
	'nkill':'Killed','nwound':'Wounded','summary':'Summary',
	'gname':'Group','targtype1_txt':'Target_type',
	'weaptype1_txt':'Weapon_type','motive':'Motive'},inplace=True)

#Våra olika dataset
terror_Group = terror[['Killed', 'Group']]
terror_Location = terror[['Killed', 'Group', 'Lat', 'Long', 'Year', 'Weapon_type']]
terror_Weapon = terror[['Killed', 'Weapon_type']]
terror_Killed = terror[['Killed']]
terror_Country = terror[['Killed', 'Country']]
terror_Header_Wounded = terror[['Wounded']]
terror_Header_Killed = terror[['Killed']] #kan ta bort denna?
terror_Header_Target_type = terror[['Target_type', 'Killed']]
terror_Year = terror[['Killed', 'Year']]


#Sortera ut okänd data
terror_Weapon =terror_Weapon[terror_Weapon.Weapon_type != 'Unknown']
terror_Group =terror_Group[terror_Group.Group != 'Unknown']
terror_Location=terror_Location[terror_Location.Killed != 0]
terror_Location=terror_Location[terror_Location.Group != 'Unknown']
#Tar bort tomma NaNvärden.
terror_Location = terror_Location.dropna()

#Grupperar, sen sorterar så "flest kills" hamnar högst upp.
#GROUP
terror_Group = terror_Group.groupby('Group').agg({'Group':'first', 'Killed': 'sum'})
terror_Group = terror_Group.sort_values(by='Killed', ascending=False)
#WEAPON
terror_Weapon = terror_Weapon.groupby('Weapon_type').agg({'Weapon_type':'first', 'Killed': 'sum'})
terror_Weapon = terror_Weapon.sort_values(by='Killed', ascending = False)
#LOCATION
terror_Location = terror_Location.sort_values(by='Killed', ascending=False)
#COUNTRY
terror_Country = terror_Country.groupby('Country').agg({'Country' : 'first','Killed' : 'sum'})
terror_Country = terror_Country.sort_values(by = 'Killed', ascending = False)
#YEAR
terror_Year = terror_Year.groupby('Year').agg({'Year' : 'first', 'Killed' : 'sum'})
terror_Year = terror_Year.sort_values(by = 'Killed', ascending = False)

#För header
terror_Header_Target_type = terror_Header_Target_type.groupby('Target_type').agg({'Target_type' : 'first','Killed' : 'sum'})
terror_Header_Target_type = terror_Header_Target_type.sort_values(by='Killed', ascending=False)

#Gör om datatyper till floats.
terror['Year'] = terror['Year'].astype(float)
terror['Killed'] = terror['Killed'].astype(float)

#Droppar onödig data
terror = terror.drop(['Month', 'Day', 'approxdate'], axis=1)
terror = terror.groupby('Year').count().reset_index()

#Tar endast med de första i antal. Viktigt att ta med så mkt som möjligt i location. 9000 funkar utan att lagga.
terror_Group = terror_Group.head(10)
terror_Location = terror_Location.head(9000)
terror_Weapon = terror_Weapon.head(9)

app = Flask(__name__)

@app.route('/')
def result():
	chart_data = terror.to_dict(orient='records')
	chart_data = json.dumps(chart_data, indent=2)
	data = {'chart_data': chart_data}

	chart_data_group = terror_Group.to_dict(orient='records')
	chart_data_group = json.dumps(chart_data_group, indent=2)
	data_group = {'chart_data_group' : chart_data_group}

	chart_data_weapon = terror_Weapon.to_dict(orient = 'records')
	chart_data_weapon = json.dumps(chart_data_weapon, indent = 2)
	data_weapon = {'chart_data_weapon' : chart_data_weapon}

	chart_data_location = terror_Location.to_dict(orient = 'records')
	chart_data_location = json.dumps(chart_data_location, indent=2)
	data_location = {'chart_data_location' : chart_data_location}

	chart_data_country = terror_Country.to_dict(orient = 'records')
	chart_data_country = json.dumps(chart_data_country, indent=2)
	data_country= {'chart_data_country' : chart_data_country}

	chart_data_target_type = terror_Header_Target_type.to_dict(orient = 'records')
	chart_data_target_type = json.dumps(chart_data_target_type, indent=2)
	data_target_type = {'chart_data_target_type' : chart_data_target_type}

	chart_data_year = terror_Year.to_dict(orient = 'records')
	chart_data_year = json.dumps(chart_data_year, indent=2)
	data_year= {'chart_data_year' : chart_data_year}

	#Skicka alla varabler
	return render_template('result.html', data=data, data_group=data_group, data_location=data_location, data_weapon=data_weapon,
		data_country=data_country, data_target_type=data_target_type, data_year=data_year)

@app.route('/bar')
def bar():
		bar_labels = labels
		bar_values = values
		return render_template('bar_chart.html', title='Casualties', max=17000, labels=bar_labels, values=bar_values)

@app.route('/plot.png')
def plot_png():
		fig = create_figure()
		output = io.BytesIO()
		FigureCanvas(fig).print_png(output)
		return Response(output.getvalue(), mimetype='image/png')


def create_figure():
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	xs = range(100)
	ys = [random.randint(1, 50) for x in xs]
	axis.plot(xs, ys)
	return fig

#m._repr_html_()
