import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
from plotly import graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff
import time
from datetime import datetime as dt
import numpy as np
import pgeocode
nomi = pgeocode.Nominatim('IN')


plant_data = pd.read_csv('/Users/prtk/Documents/Isha/Capstone/file/new_invoice_customer.csv')
# plant_data = pd.read_csv('/home/isha/Grayatom/capstone/file-20200627T163657Z-001/file/new_invoice_customer.csv')
available_states = plant_data['State'].unique().tolist()
available_states.sort()
available_states.append('All')

# Dividing Dataset into different quarters

quarter_dict = {'Quarter_1':[1,2,3],'Quarter_2':[4,5,6],'Quarter_3':[7,8,9],'Quarter_4':[10,11,12]}

def set_quarters(row):
    if row in quarter_dict['Quarter_1']:
        return 'Quarter_1'
    elif row in quarter_dict['Quarter_2']:
        return 'Quarter_2'
    elif row in quarter_dict['Quarter_3']:
        return 'Quarter_3'
    elif row in quarter_dict['Quarter_4']:
        return 'Quarter_4'

plant_data['Quarters'] = plant_data['invoice_month'].apply(lambda row:set_quarters(row))

plant_data['Service_Time'] = pd.to_timedelta(plant_data['Service_Time'])
plant_data['Service_Hours'] = plant_data['Service_Time'].apply(lambda time:time.total_seconds() / 3600)
bins=[plant_data['Service_Hours'].min(),plant_data['Service_Hours'].quantile(0.50),plant_data['Service_Hours'].quantile(0.75),plant_data['Service_Hours'].max()]
labels=["Fast","Medium","Slow"]
plant_data["Eff_labels"]=pd.cut(plant_data["Service_Hours"], bins=bins, labels=labels)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([


	html.Div([
		
		html.Div([

			html.Div([

				html.Div([
					html.Div(['State'],
					className = 'label-text'),

					dcc.Dropdown(
					id='state',
					className='filter-dropdown',
					options = [{'label':i, 'value':i} for i in available_states],
					value = 'All'
					)
				],
				className='form-component'),

				html.Div([
					html.Div(['City'],
					className = 'label-text'),
					dcc.Dropdown(
					id='city',
					className='filter-dropdown'
					)
				],
				className='form-component'),

				],
			className="form-layout"),

			html.Div([

				html.Div([
					html.Div([
						'Plant Name'],
						className = 'label-text'),
					dcc.Dropdown(
						id='plant',
						className='filter-dropdown'
						)
				],
				className='form-component')
				],
			className="form-layout"),

		],
		className='filter-container'),

		]),

		html.Div([
		dcc.Graph(id='order_count',className='graph-panel'),
		dcc.Graph(id='order_revenue',className='graph-panel')
		
		],className='graph-container'),


		html.Div([
			
			html.Div([
				html.Div(['Year'],
				className = 'label-text'),
				dcc.RadioItems(
				id='year',
				options = [
				{'label': '2012', 'value': 2012},
				{'label': '2013', 'value': 2013},
				{'label': '2014', 'value': 2014},
				{'label': '2015', 'value': 2015},
				{'label': '2016', 'value': 2016}],
				value = 2012,
				labelStyle={'display': 'inline-block'},
				className='filter-radio'
				)
			],
			className='form-component')
		],
		className="form-layout"),



		html.Div([
		dcc.Graph(id='plant_locations',className='graph-panel'),
		dcc.Graph(id='plant_map',className='graph-panel')
		
		],className='graph-container'),






		# html.Div([
		# dcc.Graph(id='efficiency_chart',className='graph-panel'),
		
		# ],className='graph-container')

		])


@app.callback(
	Output('city','options'),
	[Input('state','value'),
	]
)

def update_city_options(state):
	filtered_data = plant_data
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	cities = filtered_data['City'].unique()
	cities = [x for x in cities if str(x) != 'nan']
	cities.insert(0,'All')
	return [{'label':i, 'value':i} for i in cities]

@app.callback(
	Output('city','value'),
	[Input('city','options')]
)

def updated_city_values(city):
	if(len(city)>0):
		return city[0]['value']

@app.callback(
	Output('plant','options'),
	[Input('state','value'),
	Input('city','value')
	]
)


def update_plant_options(state,city):
	filtered_data = plant_data
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if city != 'All':
		filtered_data = filtered_data[filtered_data['City'] == city]
	plants = filtered_data['Plant Name1'].unique()
	plants = [x for x in plants if str(x) != 'nan']
	plants.insert(0,'All')
	return [{'label':i, 'value':i} for i in plants]

@app.callback(
	Output('plant','value'),
	[Input('plant','options')]
)

def updated_plant_values(plant):
	if(len(plant)>0):
		return plant[0]['value']

@app.callback(
	[Output('order_count','figure'),
	Output('order_revenue','figure')],
	[Input('state','value'),
	Input('city','value'),
	Input('plant','value')]
)
def update_plant_stats(state,city,plant):
	filtered_data = plant_data
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if city != 'All':
		filtered_data = filtered_data[filtered_data['City'] == city]
	if plant != 'All':
		filtered_data = filtered_data[filtered_data['Plant Name1'] == plant]
	# print(filtered_data.columns)
	filtered_data["Quarters"] = filtered_data["Quarters"].astype("str")
	# print(filtered_data.dtypes)
	# filtered_data['Quarters'] = pd.Categorical(filtered_data['Quarters'], ["Quarter_1", "Quarter_2","Quarter_4","Quarter_4"])
	plant_count = pd.DataFrame(filtered_data.groupby(["invoice_year","Quarters"])["Customer No."].count())
	print(plant_count.head())
	plant_count.columns = ["orders_completed"]
	plant_count = plant_count.reset_index()
	plant_count = plant_count.sort_values(by = ["invoice_year", "Quarters"], ascending = True)
	plant_count.loc[-1] = [2012, 'Quarter_1', 0]  # adding a row
	plant_count.index = plant_count.index + 1  # shifting index
	plant_count = plant_count.sort_index()  # sorting by index

	fig_1 = px.bar(plant_count, x="invoice_year", y="orders_completed", color='Quarters', barmode='group',
             height=400)
	fig_1.update_layout(title = 'Quarterly Order Count Analysis',xaxis=dict(title = 'Years',dtick=1,categoryorder = 'category ascending'), yaxis=dict(title = 'Total Orders'))
	plant_revenue = pd.DataFrame(filtered_data.groupby(["invoice_year", "Quarters"])["Total Amt Wtd Tax."].sum())
	plant_revenue.columns = ["revenue_generated"]
	plant_revenue = plant_revenue.reset_index()
	plant_revenue = plant_revenue.sort_values(by = ["invoice_year", "Quarters"], ascending = True)
	plant_revenue.loc[-1] = [2012, 'Quarter_1', 0]  # adding a row
	plant_revenue.index = plant_revenue.index + 1  # shifting index
	plant_revenue = plant_revenue.sort_index()  # sorting by index
	fig_2 = px.bar(plant_revenue, x="invoice_year", y="revenue_generated", color='Quarters', barmode='group',
	             height=400)
	fig_2.update_layout(title = 'Quarterly Revenue Analysis',xaxis=dict(title = 'Years',dtick=1,categoryorder = 'category ascending'), yaxis=dict(title = 'Revenue'))
	return fig_1,fig_2



@app.callback(
	Output('plant_locations','figure'),
	[Input('year','value')]
	)

def update_plant_locations(year):
	filtered_data = plant_data
	if year != 'All':
		filtered_data = plant_data[plant_data['invoice_year'] == (int(year))]


	location_data = pd.DataFrame(filtered_data.groupby(['State'])['Plant Name1'].count())
	location_data = location_data.reset_index()
	fig = px.bar(location_data,y='State',x='Plant Name1',orientation='h',height=400)
	fig.update_layout(xaxis=dict(title='States'),yaxis=dict(title='Workshop Counts'),title='Workshop Presence')
	return fig

@app.callback(
		Output('plant_map','figure'),
		[Input('year','value')]
		)

def update_map(year):
	filtered_data = plant_data[plant_data['invoice_year'] == (int(year))]
	loc_map = pd.DataFrame(filtered_data.groupby(['Plant Name1','Latitude','Longitude'])['Total Amt Wtd Tax.'].sum())
	loc_map = loc_map.reset_index()
	plant_loc_map =px.scatter_mapbox(loc_map, lat="Latitude", lon="Longitude",color="Total Amt Wtd Tax.",
							hover_name = 'Plant Name1',size = 'Total Amt Wtd Tax.', 
							color_continuous_scale=px.colors.cyclical.IceFire, size_max=15)
	# fig.update_geos(fitbounds="locations")
	plant_loc_map.update_layout(autosize=False,mapbox= dict(accesstoken="pk.eyJ1IjoiaXNoYWd1bGF0aSIsImEiOiJja2JjOThqamcwOHl0MnNtcHc0bmx0NHVsIn0.vMWHkKrh1l0wDeu9xcxFMA",
						bearing=10,
						pitch=60,zoom=5
						),geo = dict(showland = True),

						width=900,
						height=600, 
						title = "Workshop Areas",mapbox_style="light",
						)
	return plant_loc_map


if __name__ == '__main__':
	app.run_server(port=8910,debug=True)
