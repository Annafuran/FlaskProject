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
terror_Location = terror[['Killed', 'Group', 'Lat', 'Long', 'Year']]
terror_Weapon = terror[['Killed', 'Weapon_type']]

#Sortera ut okänd data
terror_Weapon =terror_Weapon[terror_Weapon.Weapon_type != 'Unknown']
terror_Group =terror_Group[terror_Group.Group != 'Unknown']

#Grupperar i killed, sen sorterar så "flest kills" hamnar högst upp. 
terror_Group = terror_Group.groupby('Killed').agg({'Group':'first', 'Killed': 'first'})
terror_Group = terror_Group.drop_duplicates('Group', keep='last')
terror_Group = terror_Group.sort_index(ascending=False)

#Grupperar i killed
terror_Location = terror_Location.groupby('Killed').agg({'Lat':'mean', 'Long':'mean', 'Group':'first', 'Killed': 'first', 'Year': 'first'})

#Grupperar i killed, sen sorterar så "flest kills" hamnar högst upp.
terror_Weapon = terror_Weapon.groupby('Killed').agg({'Weapon_type':'first', 'Killed': 'first'})
terror_Weapon = terror_Weapon.sort_index(ascending = False)

#Gör om datatyper till floats. 
terror['Year'] = terror['Year'].astype(float)
terror['Killed'] = terror['Killed'].astype(float)

#Droppar onödig data
terror = terror.drop(['Month', 'Day', 'approxdate'], axis=1)
terror = terror.groupby('Year').count().reset_index()

#Tar endast med de första i antal. Obs viktigt att ej göra det på terror_location. 
terror = terror.head(48)
terror_Group = terror_Group.head(10)

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

	return render_template('result.html', data=data, data_group=data_group, data_location=data_location, data_weapon=data_weapon)


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
