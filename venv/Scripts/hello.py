
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
terror = pd.read_csv('globalterrorismdb_0718dist.csv', low_memory=False, error_bad_lines=False, encoding='ISO-8859-1')
terror.rename(columns={'iyear':'Year','imonth':'Month',
	'iday':'Day','country_txt':'Country','region_txt':'Region',
	'attacktype1_txt':'AttackType','target1':'Target',
	'nkill':'Killed','nwound':'Wounded','summary':'Summary',
	'gname':'Group','targtype1_txt':'Target_type',
	'weaptype1_txt':'Weapon_type','motive':'Motive'},inplace=True)
terror['Year'] = terror['Year'].astype(float)
terror['Killed'] = terror['Killed'].astype(float)
terror = terror.drop(['Month', 'Day', 'approxdate'], axis=1)
terror = terror.groupby('Year').count().reset_index()
#terror = terror.pivot_table(terror, index=['Year', ])
terror = terror.head(48)
#terror.drop(['Month','Day', 'Country','Region','AttackType','Target','Killed',
#	'Wounded','Summary','Group','Target_type','Weapon_type','Motive'],axis=1)
#terror.drop(['Summary', 'Region', 'Motive', 'Weapon_type', 'Group', 'Target_type', 'Country','AttackType', 'Target', 'Killed', 'Wounded'], axis=1)


app = Flask(__name__)

@app.route('/')
def result():
	chart_data = terror.to_dict(orient='records')
	chart_data = json.dumps(chart_data, indent=2)
	data = {'chart_data': chart_data}
	return render_template('result.html', data=data)


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