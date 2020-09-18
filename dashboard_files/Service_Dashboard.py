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

invoice_data = pd.read_csv('/Users/prtk/Documents/Isha/Capstone/file/car_data.csv')
# invoice_data = pd.read_csv('/home/isha/Grayatom/capstone/file-20200627T163657Z-001/file/new_invoice_data.csv')
available_years = invoice_data['invoice_year'].unique().tolist()
available_years.sort()
available_years.append('All')

# filtered_data = 

plant_data = pd.read_excel('/Users/prtk/Documents/Isha/Capstone/file/Plant Master.xlsx')

cut_labels = ['Upto_25K', '25K_50K', '50K_100K', '100K_200K','200K_400K','400K_800K','800K_1.6M','1.6M_3.2M','3.2M_6.4M','>6.4B']
cut_bins = [0,25000,50000, 100000,200000,400000,800000,1600000,3200000,6400000,9999999]
invoice_data['Age_by_kms'] = pd.cut(invoice_data['KMs Reading'],bins=cut_bins,labels = cut_labels)

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
			className='form-component')
			],

		className="form-layout"),

	],className='filter-container'),


	html.Div([

		html.Div([

			html.P("Total Revenue"),
			html.H4(
				id="revenue-text",
				className="info-text")
			],
			id='revenue',
			className='info-sub-container'
			),

		html.Div([

			html.P("Total Jobs"),
			html.H4(
				id="jobs-text",
				className="jobs-text")
			],
			id='jobs',
			className='info-sub-container'
			)
		],className='info-container')


		],className='filter-info-container'),


	html.Div([
		dcc.Graph(id='sales_by_service',className='graph-panel'),
		dcc.Graph(id='service_type',className='graph-panel')
	],className='graph-container'),

	html.Div([
		dcc.Graph(id='season-trend',className='graph-panel'),
		dcc.Graph(id='invoice_charges',className='graph-panel')
	],className='graph-container'),

	html.Div([
		dcc.Graph(id='km-trend-count',className='graph-panel'),
		dcc.Graph(id='km-trend-sales',className='graph-panel')
	],className='graph-container')

	]
	)

@app.callback(
	Output('region','options'),
	[Input('years','value')])

def update_region_options(year):
	if year == 'All':
		filtered_data = invoice_data
	else: 
		filtered_data = invoice_data[invoice_data['invoice_year'] == int(year)]
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

	filtered_data = invoice_data
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
    [Output('revenue-text','children'),
    Output('jobs-text','children'),
    Output('sales_by_service', 'figure'),
    Output('service_type','figure'),
    Output('season-trend','figure')],
    [Input('years','value'),
    Input('region', 'value'),
    Input('state', 'value')])

def update_graph(year,region,state):
	
	filtered_data  = invoice_data
	if year != 'All':
		filtered_data = filtered_data[filtered_data['invoice_year'] == int(year)]
	if region != 'All': 
		filtered_data = filtered_data[filtered_data['Region'] == region]
	if state != 'All':
		filtered_data = filtered_data[filtered_data['State'] == state]



	invoice_region = pd.DataFrame(filtered_data.groupby(['Order Type'])['Total Amt Wtd Tax.'].sum())

	sales_pie = go.Figure(data=[go.Pie(labels=invoice_region.index,
	                             values=invoice_region['Total Amt Wtd Tax.'])])


	sales_pie.update_traces(hoverinfo='label+value',textinfo='percent', textfont_size=20)
	sales_pie.update_layout(
	title="Sales by Services",
	font=dict(
	    family="Courier New, monospace",
	    size=14,
	    color="#7f7f7f")
	)


	region_order_count = pd.DataFrame(filtered_data.groupby(['Order Type'])['Order Type'].count()).rename(columns={'Order Type':'Order_Count'}).sort_values(by=['Order_Count'],ascending=False)

	count_bar = go.Figure(go.Bar(
            y=region_order_count.index,
            x=region_order_count['Order_Count'],
            orientation='h'))


	count_bar.update_layout(
	title="Service Type",
	font=dict(
	    family="Courier New, monospace",
	    size=14,
	    color="#7f7f7f"),
	xaxis=dict(title='Order Counts'))

	season_order_count = pd.DataFrame(filtered_data.groupby(['Order Type','order_month'])['Order Type'].count()).rename(columns={'Order Type':'Order_Count'})
	season_order_count.reset_index(inplace=True)

	season_line = px.line(x=season_order_count['order_month'], y=season_order_count['Order_Count'], color=season_order_count['Order Type'])
	season_line.update_layout(title="Seasonal Trend",
    font=dict(
        family="Courier New, monospace",size=14,color="#7f7f7f"),
    xaxis = dict(
        tickmode = 'linear',
        tick0 = 0,
        dtick = 1,
        title='Months'
	    ),
    yaxis = dict(title='Order Counts')
	)


	total_revenue = round(filtered_data['Total Amt Wtd Tax.'].sum(),2)
	total_revenue = f"{total_revenue:,}"
	total_orders = filtered_data['Order Type'].count()



	return total_revenue,total_orders,sales_pie,count_bar,season_line


@app.callback(
	Output('invoice_charges','figure'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value')]
	)

def update_invoice_charges(year,region,state):

	charges_data  = invoice_data
	if year != 'All':
		charges_data = charges_data[charges_data['invoice_year'] == int(year)]
	if region != 'All': 
		charges_data = charges_data[charges_data['Region'] == region]
	if state != 'All':
		charges_data = charges_data[charges_data['State'] == state]


	charges_data = charges_data.groupby(['Order Type'])[['Labour Total','Misc Total','OSL Total','Parts Total']].sum()
	charges_data.reset_index(inplace=True)
	invoice_charges_fig = go.Figure(go.Bar(x=charges_data['Order Type'], y=charges_data['Labour Total'], name='Labour Charges'))
	invoice_charges_fig.add_trace(go.Bar(x=charges_data['Order Type'], y=charges_data['Misc Total'], name='Miscellaneous Charges'))
	invoice_charges_fig.add_trace(go.Bar(x=charges_data['Order Type'], y=charges_data['OSL Total'], name='Out Sourced Labour'))
	invoice_charges_fig.add_trace(go.Bar(x=charges_data['Order Type'],y=charges_data['Parts Total'],name='Parts Charges'))
	invoice_charges_fig.update_layout(barmode='relative', xaxis=dict(categoryorder ='total ascending',title='Service Type'),title = "Invoice Breakdown",
		font=dict(family="Courier New, monospace",size=14,color="#7f7f7f"),yaxis = dict(title='Revenue Generated'))

	return invoice_charges_fig

@app.callback(
	Output('km-trend-count','figure'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value')]
	)

def update_km_trend_graph(year,region,state):

	state_count_by_age  = invoice_data
	if year != 'All':
		state_count_by_age = state_count_by_age[state_count_by_age['invoice_year'] == int(year)]
	if region != 'All': 
		state_count_by_age = state_count_by_age[state_count_by_age['Region'] == region]
	if state != 'All':
		state_count_by_age = state_count_by_age[state_count_by_age['State'] == state]

	state_count_by_age = state_count_by_age.groupby(['Order Type','Age_by_kms'])['Regn No'].count().reset_index()

	count_by_age_fig = px.line(state_count_by_age, x='Age_by_kms', y='Regn No',color='Order Type')
	count_by_age_fig.update_layout(title_text = 'Count of Orders by Kms',
		font=dict(family="Courier New, monospace",size=14,color="#7f7f7f"))
	count_by_age_fig.update_xaxes(title_text='Age Of Car')
	count_by_age_fig.update_yaxes(title_text='Count')
	return count_by_age_fig

@app.callback(
	Output('km-trend-sales','figure'),
	[Input('years','value'),
	Input('region','value'),
	Input('state','value')]
	)

def update_km_sales_graph(year,region,state):

	state_sales_by_age  = invoice_data
	if year != 'All':
		state_sales_by_age = state_sales_by_age[state_sales_by_age['invoice_year'] == int(year)]
	if region != 'All': 
		state_sales_by_age = state_sales_by_age[state_sales_by_age['Region'] == region]
	if state != 'All':
		state_sales_by_age = state_sales_by_age[state_sales_by_age['State'] == state]

	state_sales_by_age = state_sales_by_age.groupby(['Order Type','Age_by_kms'])['Total Amt Wtd Tax.'].mean().reset_index()
	sales_by_age_fig = px.line(state_sales_by_age, x='Age_by_kms', y='Total Amt Wtd Tax.',color='Order Type')
	sales_by_age_fig.update_layout(title_text = 'Average Sales by Kms',
		font=dict(family="Courier New, monospace",size=14,color="#7f7f7f"))
	sales_by_age_fig.update_xaxes(title_text='Age Of Car')
	sales_by_age_fig.update_yaxes(title_text='Average Sales')
	return sales_by_age_fig


if __name__ == '__main__':
    app.run_server(debug=True)




