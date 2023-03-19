from dash import Dash, html, dcc, Output, Input, dash_table
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import sys, pathlib
import pandas as pd
import os
import numpy as np 
import plotly.express as px

current_folder = pathlib.Path(__file__).parent.resolve()
src_folder = str(current_folder.parent.absolute())
if src_folder not in sys.path:
	sys.path.insert(0, src_folder)

load_figure_template('SIMPLEX')

app = Dash(__name__,external_stylesheets=[dbc.themes.SIMPLEX])

df = pd.read_excel(os.path.join(src_folder, "net_zero_tracker_canada.xlsx"))
canada = df[df["country"]=="CAN"]
corporations = canada[canada["actor_type"]=="Company"]
sector = corporations["industry"].fillna("Other").unique().tolist()
sector.append("All")

bert = pd.read_csv(os.path.join(src_folder,"Bert-positivity-score.csv"), names=['name', 'list'])
positives = []
for i in range(len(bert)):
    posVal = float("0."+bert["list"].iloc[i].split(".")[-1][:-1])
    positives.append(posVal)
bert["positives"] = positives

word2vec = pd.read_csv(os.path.join(src_folder,"companyName_pledgeScore.csv"))
df1 = pd.merge(corporations, word2vec, left_on="name", right_on="companyName")
master_df = pd.merge(df1, bert, left_on="name", right_on="name")

d_target = pd.DataFrame({
	"Points": [0, 1, 2],
	"Target": ["No target", "Net zero", "Emission reduction"]
})

d_status = pd.DataFrame({
	"Points": [0, 1, 2, 3],
	"Status": ["No target", "Proposed", "Pledge", "In corporate strategy"]
})

d_plan = pd.DataFrame({
	"Points": [0, 1],
	"Detailed plan": ["No", "Yes"]
})

d_reporting = pd.DataFrame({
	"Points": [0, 1, 2],
	"Reporting Mechanism": ["No", "Less than annual", "Annual"]
})

d_scope = pd.DataFrame({
	"Points": [0, 1, 2],
	"Scope 3 Coverage": ["No", "Partial", "Yes"]
})

d_carbon = pd.DataFrame({
	"Points": [0, 1],
	"Uses Carbon Credits": ["Yes", "No"]
})

app.layout = html.Div([
	html.H1("Holding Canadian companies accountable on climate promises",style={"margin-left": "10px","margin-top":"20px", "margin-bottom":"20px"}),
	html.Div(dcc.Markdown("Climate change is an ever-looming threat to mankind, and while individuals can certainly take steps to mitigate its effects, the impact of human actions is often dwarfed by the constant overexploitation of the environment by corporations. It is only recently that many companies have begun to prioritize environmental sustainability, but unfortunately, some of these companies engage in 'greenwashing,' where they promote their environmental efforts but do not actually take concrete steps to fight climate change. This project aims to compare the environmental marketing of companies with their actual actions to assess the sincerity of their commitment to the environment."),style={"margin-left": "10px","margin-top":"20px","margin-right":"20px", "margin-bottom":"20px"}),
	html.Div([dcc.Graph(id='climate-graph', figure={}, style={"margin-left":"10px",'width': '80%', 'display': 'inline-block','verticalAlign': 'top'}), html.Img(src='assets/legend.png', height='280', style={'width': '10%', 'display': 'inline-block', 'verticalAlign': 'top'})]),
	html.Div([html.H6("Sector: "), dcc.Dropdown(options=sector, value='All', id='sector')], style={"margin-left":"10px","margin-bottom":"20px",'width': '40%', 'display': 'inline-block'}),
	
	html.Div([html.H6("NLP Model: "), dcc.Dropdown(options=["BERT sentiment analysis", "word2vec"], value='word2vec', id='model')], style={"margin-left":"10px","margin-bottom":"20px",'width': '40%', 'display': 'inline-block'}),
	html.Br(),
	html.Div(dcc.Markdown("Calculation of strength of climate pledge (data using [Net Zero Tracker](https://zerotracker.net/)): "),style={"margin-left": "10px","margin-top":"20px"}),
	html.Div([html.Div([dash_table.DataTable(d_target.to_dict('records'), [{"name":i, "id":i} for i in d_target.columns])], style={"margin-left":"10px","margin-right":"10px","margin-bottom":"70px",'width': '20%', 'display': 'inline-block','verticalAlign': 'top'}),
			html.Div([dash_table.DataTable(d_status.to_dict('records'), [{"name":i, "id":i} for i in d_status.columns])], style={"margin-left":"20px","margin-bottom":"70px",'width': '20%', 'display': 'inline-block','verticalAlign': 'top'}),
			html.Div([dash_table.DataTable(d_plan.to_dict('records'), [{"name":i, "id":i} for i in d_plan.columns])], style={"margin-left":"20px","margin-bottom":"70px",'width': '20%', 'display': 'inline-block','verticalAlign': 'top'})
			]),
	html.Div([html.Div([dash_table.DataTable(d_reporting.to_dict('records'), [{"name":i, "id":i} for i in d_reporting.columns])], style={"margin-left":"20px","margin-bottom":"100px",'width': '20%', 'display': 'inline-block','verticalAlign': 'top'}),
			html.Div([dash_table.DataTable(d_scope.to_dict('records'), [{"name":i, "id":i} for i in d_scope.columns])], style={"margin-left":"20px","margin-bottom":"100px",'width': '20%', 'display': 'inline-block','verticalAlign': 'top'}),
			html.Div([dash_table.DataTable(d_carbon.to_dict('records'), [{"name":i, "id":i} for i in d_carbon.columns])], style={"margin-left":"20px","margin-bottom":"100px",'width': '20%', 'display': 'inline-block','verticalAlign': 'top'})
			])	
	])

def tracker_to_value(dataframe):
	target_dict = {"No target": 0, "Net zero":2, "Climate neutral":2, "Emissions reduction target":1, "Other":0, "Emissions intensity target":1, "Carbon neutral(ity)":2}
	status_dict = {"None":0, "Declaration / pledge":2, "In corporate strategy":3, "Proposed / in discussion":1}
	plan_dict = {"No":0, "None":0, "Yes":1}
	report_dict = {"No reporting mechanism": 0, "Annual reporting": 2, "Less than annual reporting": 1, "None":0}
	scope_dict = {"Partial":1,"Yes":2,"Not Specified":0, "No":0, "None":0}
	carbon_dict = {"Not Specified":0, "No":1, "Yes":0, "None":0}
	dataframe["target_score"] = dataframe["end_target"].replace(target_dict)
	dataframe["status_score"] = dataframe["end_target_status"].fillna("None").replace(status_dict)
	dataframe["plan_score"] = dataframe["has_plan"].fillna("None").replace(plan_dict)
	dataframe["report_score"] = dataframe["reporting_mechanism"].fillna("None").replace(report_dict)
	dataframe["scope_score"] = dataframe["scope_3"].fillna("None").replace(scope_dict)
	dataframe["carbon_score"] = dataframe["carbon_credit_offsets"].fillna("None").replace(carbon_dict)
	dataframe["total_score"] = dataframe["target_score"] + dataframe["status_score"] +dataframe["plan_score"]+dataframe["report_score"]+dataframe["scope_score"]+dataframe["carbon_score"]
	np.random.seed(42)
	dataframe["PR_score"] = np.random.uniform(size=len(dataframe))
	return dataframe

def year_to_color(years):
	d = {9999:"No target", 2020:"2020", 2025:"2025", 2030:"2030", 2040:"2040", 2050:"2050"}
	return years.fillna(9999).replace(d)

@app.callback(
	Output('climate-graph', 'figure'),
	Input('sector', 'value'),
	Input('model', 'value')
)
def update_graph(sector, model):
	df = tracker_to_value(master_df)
	if sector != "All":
		display = df[df["industry"]==sector]
	else:
		display = df
	if model == 'word2vec':
		xdata = display["pledgeScore"]
	else:
		xdata = display["positives"]
	fig = px.scatter(x=xdata, 
		  			y=display["total_score"], 
					hover_name=display["name"], 
					size=display["annual_revenue"].fillna(1), 
					color = year_to_color(display["end_target_year"]),
					color_discrete_map = {"No target":"black", "2020":"limegreen", "2025":"lightskyblue", "2030":"navajowhite", "2040":"orange", "2050":"red"},
					labels={'x':"Extent of climate claims", 'y':"Calculated strength of climate pledge"})
	
	fig.update_layout(showlegend=False)
	return fig

if __name__ == '__main__':
    app.run_server(debug=True)