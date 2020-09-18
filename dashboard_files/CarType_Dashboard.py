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

car_data = pd.read_csv('/Users/prtk/Documents/Isha/Capstone/file/car_data.csv')
# car_data = pd.read_csv('/home/isha/Grayatom/capstone/file-20200627T163657Z-001/file/car_data.csv')
available_years = car_data['invoice_year'].unique().tolist()
available_years.sort()
available_years.append('All')

# filtered_data = 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([


	html.Div([

		html.Div([

			html.Div([
				
				html.Div([
					html.Div(['Year'],
					className = 'label-text'),
					dcc.RadioItems(
					id='years',
					options = [
					{'label': 'All', 'value': 'All'},
					{'label': '2012', 'value': 2012},
					{'label': '2013', 'value': 2013},
					{'label': '2014', 'value': 2014},
					{'label': '2015', 'value': 2015},
					{'label': '2016', 'value': 2016}],
					value = 'All',
					labelStyle={'display': 'inline-block'},
					className='filter-radio'
					)
				],
				className='form-component')
			],
			className="form-layout"),

			html.Div([

				html.Div([
					html.Div(['Region'],
					className = 'label-text'),

					dcc.Dropdown(
					id='region',
					className='filter-dropdown'
					)
				],
				className='form-component'),

				html.Div([
					html.Div(['State'],
					className = 'label-text'),
					dcc.Dropdown(
					id='state',
					className='filter-dropdown'
					)
				],
				className='form-component'),

				],
			className="form-layout"),

			html.Div([

				html.Div([
					html.Div([
						'Service Type'],
						className = 'label-text'),
					dcc.Dropdown(
						id='service',
						className='filter-dropdown'
						)
				],
				className='form-component')
				],
			className="form-layout"),

		],
		className='filter-container'),


		html.Div([
			html.Div([

				html.P("Total Cars"),
				html.H4(
					id="cars-text",
					className="cars-text")
				],
				id='cars',
				className='info-sub-container')
		],className='info-container')


	],className='filter-info-container'),


	html.Div([
		dcc.Graph(id='class_distribution',className='graph-panel'),
		dcc.Graph(id='class_revenue',className='graph-panel')
		],className = 'graph-container'),

	html.Div([
		dcc.Graph(id='make_distribution',className='graph-panel'),
		dcc.Graph(id='model_distribution',className='graph-panel')
		],className='graph-container'),
	# html.Div([
	# 	dcc.Graph(id='class_revenue',className='graph-panel'),
	# 	],className = 'graph-container'),

	html.Div([
		dcc.Graph(id='make_revenue',className='graph-panel'),
		dcc.Graph(id='model_revenue',className='graph-panel')
		],className='graph-container'),


	html.Div([
		html.Div([

			html.Div([
				html.Div(['Car Class'],
				className = 'label-text'),
				dcc.Dropdown(
            	id='class',
            	className = 'filter-dropdown'
            	)
			],
			className='form-component'),

			html.Div([
				html.Div(['Car Make'],
				className = 'label-text'),
				dcc.Dropdown(
            	id='make',
            	className = 'filter-dropdown'
            	)
			],
			className='form-component'),

			html.Div([
				html.Div(['Car Model'],
				className = 'label-text'),
				dcc.Dropdown(
            	id='model',
            	className = 'filter-dropdown'
            	)
			],
			className='form-component')


			],

		className="form-layout"),

	],className = 'car-filter-container'),


	html.Div([
		dcc.Graph(id='service_structure',className='graph-panel'),
		dcc.Graph(id='service_revenue',className='graph-panel')
	],className='graph-container'),

	html.Div([
		dcc.Graph(id='state_count',className='graph-panel'),
		dcc.Graph(id='state_revenue',className='graph-panel')
	],className='graph-container'),




	# html.Div([
	# 	dcc.Graph(id='plant_location',className='graph-panel')
	# ],className='graph-container')

	]
	)

@app.callback(
	Output('region','options'),
	[Input('years','value')])

def update_region_options(year):
	if year == 'All':
		filtered_data = car_data
	else: 
		filtered_data = car_data[car_data['invoice_year'] == int(year)]
	regions = filtered_data['Region'].unique()
	regions = [x for x in regions if str(x) != 'nan']
	regions.insert(0,'All')
	return [{'label':i,'value':i} for i in regions]

@app.callback(
	Output('region','value'),
	[Input('region','options')])
def update_region_values(region):
	if len(region)>0:
		return region[0]['value']
		

@app.callback(
	Output('state','options'),
	[Input('region','value'),
	Input('years','value')])

def update_state_options(region,year):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == (int(year))]
	if region != 'All':
		filtered_data = filtered_data[filtered_data['Region'] == region]
	states = filtered_data['State'].unique()
	states = [x for x in states if str(x) != 'nan']
	states.insert(0,'All')
	return [{'label':i, 'value':i} for i in states]

@app.callback(
	Output('state','value'),
	[Input('state','options')])

def updated_state_values(state):
	if(len(state)>0):
		return state[0]['value']

@app.callback(
	Output('service','options'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value')]
	)
def update_service_options(year,region,state):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All':
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	services = filtered_data['Order Type'].unique()
	services = [x for x in services if str(x) != 'nan']
	services.insert(0,'All')
	return [{'label':i,  'value':i} for i in services]

@app.callback(
	Output('service','value'),
	[Input('service','options')])
def update_service_value(service):
	if len(service)>0:
		return service[0]['value']

@app.callback(
	Output('class','options'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value')]
	)

def update_class_options(year,region,state):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All':
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	car_class = filtered_data['Car_Class'].unique()
	car_class = [x for x in car_class if str(x) != 'nan']
	car_class.insert(0,'All')
	return [{'label':i,'value':i} for i in car_class]

@app.callback(
	Output('class','value'),
	[Input('class','options')])
def update_class_value(car_class):
	if len(car_class)>0:
		return car_class[0]['value']

@app.callback(
	Output('make','options'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value'),
	Input('class','value')])

def update_make_options(year,region, state, car_class):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if car_class != 'All':
		filtered_data = filtered_data[filtered_data['Car_Class'] == car_class]
	car_make = filtered_data['Make'].unique()
	car_make = [x for x in car_make if str(x) != 'nan']
	car_make.insert(0,'All')
	return [{'label':i,'value':i} for i in car_make]

@app.callback(
	Output('make','value'),
	[Input('make','options')])
def update_make_values(make):
	if len(make)>0:
		return make[0]['value']
		

@app.callback(
	Output('model','options'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value'),
	Input('class','value'),
	Input('make','value')])

def update_model_options(year,region,state,car_class,make):
	# print(year,car_class,make)
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if car_class != 'All':
		filtered_data = filtered_data[filtered_data['Car_Class'] == car_class]
	if make != 'All':
		filtered_data = filtered_data[filtered_data['Make'] == make]
	# print(filtered_data.head())
	car_model = filtered_data['Model'].unique()
	car_model = [x for x in car_model if str(x) != 'nan']
	car_model.insert(0,'All')
	return [{'label':i, 'value':i} for i in car_model]

@app.callback(
	Output('model','value'),
	[Input('model','options')])

def updated_model_values(model):
	if(len(model)>0):
		return model[0]['value']




@app.callback(
	Output('cars-text','children'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value'),
	Input('service','value')]
	)
def update_car_text(year,region,state,service):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if service != 'All':
		filtered_data = filtered_data[filtered_data['Order Type'] == service]

	total_cars = filtered_data['Regn No'].count()
	total_cars = f"{total_cars:,}"
	return total_cars



@app.callback(
	Output('state_count','figure'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value'),
	Input('class','value'),
	Input('make','value'),
	Input('model','value')]
	)

def update_state_count_bar(year,region,state,car_class,make,model):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if car_class != 'All':
		filtered_data = filtered_data[filtered_data['Car_Class'] == car_class]
	if make != 'All':
		filtered_data = filtered_data[filtered_data['Make'] == make]
	if model != 'All':
		filtered_data = filtered_data[filtered_data['Model'] == model]
	state_count_chart = pd.DataFrame(filtered_data.groupby(['City'])['Regn No'].count()).sort_values(by='Regn No',ascending=False).head(10)
	# fig = go.Figure(data=[go.Pie(labels=state_count_chart.index,	
 #                                 values=state_count_chart['Regn No'])])
	# fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20, hole = 0.3)
	# fig.update_layout(title_text = "Number of Orders Received From Each City of the State", annotations=[dict(text = state, x = 0.5, y = 0.5, font_size=15, showarrow=False)])
	fig = go.Figure(data=[go.Bar(x = state_count_chart.index,
                                 y = state_count_chart['Regn No'])])
	fig.update_layout(title_text='Top Car Owning Cities',xaxis = dict(categoryorder = 'total descending',
		title = 'Cities'),
	yaxis=dict(title = 'Car Counts'))

	return fig

@app.callback(
	Output('state_revenue','figure'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value'),
	Input('class','value'),
	Input('make','value'),
	Input('model','value')]
	)

def update_state_revenue_bar(year,region,state,car_class,make,model):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if car_class != 'All':
		filtered_data = filtered_data[filtered_data['Car_Class'] == car_class]
	if make != 'All':
		filtered_data = filtered_data[filtered_data['Make'] == make]
	if model != 'All':
		filtered_data = filtered_data[filtered_data['Model'] == model]
	state_rev_chart = pd.DataFrame(filtered_data.groupby(['City'])['Total Amt Wtd Tax.'].sum()).sort_values(by='Total Amt Wtd Tax.',ascending=False).head(10)
	# fig = go.Figure(data=[go.Pie(labels=state_count_chart.index,	
 #                                 values=state_count_chart['Regn No'])])
	# fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20, hole = 0.3)
	# fig.update_layout(title_text = "Number of Orders Received From Each City of the State", annotations=[dict(text = state, x = 0.5, y = 0.5, font_size=15, showarrow=False)])
	fig = go.Figure(data=[go.Bar(x = state_rev_chart.index,
                                 y = state_rev_chart['Total Amt Wtd Tax.'])])
	fig.update_layout(title_text='Top Revenue Generating Cities',xaxis = dict(categoryorder = 'total descending',
		title = 'Cities'),
	yaxis=dict(title = 'Revenue'))
	return fig






@app.callback(
	[Output('class_distribution','figure'),
	Output('make_distribution','figure'),
	Output('model_distribution','figure'),],
	[Input('years','value'),
	Input('region','value'),
	Input('state','value'),
	Input('service','value')]
	)

def update_distribution(year,region, state,service):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if service != 'All':
		filtered_data = filtered_data[filtered_data['Order Type'] == service]
	distribution_data = filtered_data
	fig_1 = go.Figure(data=[go.Pie(labels = distribution_data['Car_Class'].unique(),
		values=distribution_data['Car_Class'].value_counts())])
	fig_1.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20, hole = 0.4)
	fig_1.update_layout(title_text = "Distribution of Count by Car Class", annotations=[dict(text = state, x = 0.5, y = 0.5, font_size=15, showarrow=False)])
	
	make_count = pd.DataFrame(distribution_data.groupby(['Make'])['Regn No'].count()).sort_values(by='Regn No',ascending=False).head(15)
	fig_2 = go.Figure(data=[go.Bar(y = make_count.index,
	                             x = make_count['Regn No'],orientation='h')])

	fig_2.update_layout(title_text = "Top Car Companies Serviced", yaxis= dict(title='Car Make',categoryorder = 'total ascending'),
		xaxis = dict(title = 'Count'))
	
	# fig_2 = go.Figure(data=[go.Pie(labels = make_count.index,
	# 	values=make_count['Regn No'])])
	# fig_2.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20, hole = 0.4)
	# fig_2.update_layout(title_text = "Car Make: {}".format(state), annotations=[dict(text = state, x = 0.5, y = 0.5, font_size=15, showarrow=False)])
	model_count = pd.DataFrame(distribution_data.groupby(['Model'])['Regn No'].count()).sort_values(by='Regn No',ascending=False).head(15)
	fig_3 = go.Figure(data=[go.Bar(y = model_count.index,
	                             x = model_count['Regn No'],orientation = 'h')])

	fig_3.update_layout(title_text = "Top Car Models Serviced", yaxis= dict(title='Car Model',categoryorder = 'total ascending'),
		xaxis=dict(title = 'Count'))
	
	return fig_1,fig_2,fig_3

@app.callback(
	[Output('class_revenue','figure'),
	Output('make_revenue','figure'),
	Output('model_revenue','figure')],
	[Input('years','value'),
	Input('region','value'),
	Input('state','value'),
	Input('service','value')]
	)

def update_revenue(year,region, state,service):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if service != 'All':
		filtered_data = filtered_data[filtered_data['Order Type'] == service]
	revenue_data = filtered_data
	class_revenue = pd.DataFrame(revenue_data.groupby(['Car_Class'])['Total Amt Wtd Tax.'].sum()).sort_values(by='Total Amt Wtd Tax.',ascending = False)
	fig_1 = go.Figure(data=[go.Pie(labels = class_revenue.index,
		values=class_revenue['Total Amt Wtd Tax.'])])
	fig_1.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20, hole = 0.4)
	fig_1.update_layout(title_text = "Distribution of Revenue by Car Class", annotations=[dict(text = state, x = 0.5, y = 0.5, font_size=15, showarrow=False)])
	
	make_count = pd.DataFrame(revenue_data.groupby(['Make'])['Total Amt Wtd Tax.'].sum()).sort_values(by='Total Amt Wtd Tax.',ascending=False).head(15)
	fig_2 = go.Figure(data=[go.Bar(x = make_count.index,
	                             y = make_count['Total Amt Wtd Tax.'])])

	fig_2.update_layout(title_text = "Revenue by Car Companies", xaxis= dict(title='Car Make',categoryorder = 'total descending'),
		yaxis = dict(title = 'Revenue'))
	
	# fig_2 = go.Figure(data=[go.Pie(labels = make_count.index,
	# 	values=make_count['Regn No'])])
	# fig_2.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20, hole = 0.4)
	# fig_2.update_layout(title_text = "Car Make: {}".format(state), annotations=[dict(text = state, x = 0.5, y = 0.5, font_size=15, showarrow=False)])
	model_count = pd.DataFrame(revenue_data.groupby(['Model'])['Total Amt Wtd Tax.'].sum()).sort_values(by='Total Amt Wtd Tax.',ascending=False).head(15)
	fig_3 = go.Figure(data=[go.Bar(x = model_count.index,
	                             y = model_count['Total Amt Wtd Tax.'])])

	fig_3.update_layout(title_text = "Revenue by Car Models", xaxis= dict(title='Car Model',categoryorder = 'total descending'),
		yaxis=dict(title = 'Revenue'))
	
	return fig_1,fig_2,fig_3

@app.callback(
	[Output('service_structure','figure'),
	Output('service_revenue','figure')],
	[Input('years','value'),
	Input('region','value'),
	Input('state','value'),
	Input('class','value'),
	Input('make','value'),
	Input('model','value')]
	)

def update_service_structure(year,region,state,car_class,make,model):
	filtered_data = car_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]
	if car_class != 'All':
		filtered_data = filtered_data[filtered_data['Car_Class'] == car_class]
	if make != 'All':
		filtered_data = filtered_data[filtered_data['Make'] == make]
	if model != 'All':
		filtered_data = filtered_data[filtered_data['Model'] == model]
	fig = go.Figure(data=[go.Pie(labels=filtered_data['Order Type'].unique(),
	                       values=filtered_data['Order Type'].value_counts())])
	fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20, hole = 0.4)
	fig.update_layout(title_text = "Service Structure", annotations=[dict(text = make, x = 0.5, y = 0.5, font_size=12, showarrow=False)])
	service_revenue_df = pd.DataFrame(filtered_data.groupby(['Order Type'])['Total Amt Wtd Tax.'].sum())
	service_revenue_df = service_revenue_df.reset_index()
	rev = go.Figure(data=[go.Pie(labels=service_revenue_df['Order Type'],
		values=service_revenue_df['Total Amt Wtd Tax.'])])
	rev.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20, hole = 0.4)
	rev.update_layout(title_text = "Service Revenue", annotations=[dict(text = make, x = 0.5, y = 0.5, font_size=12, showarrow=False)])
	return fig,rev



if __name__ == '__main__':
    app.run_server(port=8000,debug=True)

