import pandas as pd
import numpy as np
import os
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go


app = Dash(__name__)

### data processing
# get current directory this script is installed in
current_fp = os.getcwd()
main_dir = os.path.join(current_fp, 'ARem')
filenames = os.listdir(main_dir)

read_list = [] # list of options
for file in filenames:
    # file contains some pdfs and read-me files. skipping those.
    if not file.endswith(".pdf") and not file.startswith('.'): 
        read_list.append(file)
# read in files 
activity_mean = pd.read_csv(os.path.join(current_fp, 'activity_mean.csv'))
activity_var = pd.read_csv(os.path.join(current_fp, 'activity_variance.csv'))

df = pd.concat([activity_mean, activity_var])
df['subject_id'] = df['subject_id'].astype(int).astype(str)

### dashboard layout
app.layout = html.Div([
    ## headers
    html.H1(children='Time Series Visualizations - Sensor Signal Strength data'),
    html.Div(children='''
       The data used for analysis was retrieved from an experiment done by Palumbo, Filippo et al (2016), where sensors were placed on research partipants to collect data on signal strengths between sensors when a certain activity was performed. When the data was collected and the activity was measured, Sensor 1 was worn on the participant's chest, Sensor 2 was worn on the participant's right ankle, Sensor 3 was worn on the participant's left ankle.
    '''),
    html.Div(children='''
    Please see the GitHub repository readme file https://github.com/schristinelin/rss_human_activity/blob/main/README.md for detailed descriptions
     '''),
    html.Div(children = ''' 
        Sensor pair variables description:
    '''),

    html.Div(children = ''' 
       RSS12 - signal strength between sensor 1 and 2
       '''),
    html.Div(children = ''' 
       RSS13 - signal strength between sensor 1 and 3
       '''),
    html.Div(children = ''' 
       RSS23 - signal strength between sensor 2 and 3
       '''),

    ## dropdowns
    html.Div([
        # first dropdown - activity type
        html.Div([
            html.Label(['Activity type:'], style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Dropdown(
                read_list, 
                'bending1', 
                id='activity_type')
                ], style={'width': '48%', 'display': 'inline-block'}),
        # second dropdown - sensors to display
        html.Div([
            html.Label(['Sensor pairs:'], style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Dropdown(
                ['RSS 12', 'RSS 13', 'RSS 23'],
                'RSS 12',
                id='sensor_type',
                multi = True)
                ], style={'width': '48%'}),
       # third dropdown - subject IDs
        html.Div([
            html.Label(['Participant ID:'], style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Dropdown(
                list(range(1,16)),
                '1',
                id='subject_ids')
                ], style={'width': '48%'}),
        # selection - measure type mean/variance
        html.Div([
            html.Label(['Measure type:'], style={'font-weight': 'bold', "text-align": "center"}),
            dcc.RadioItems(
                ['Mean', 'Variance'],
                'Mean',
                id='measure_type')
                ], style={'width': '48%', 'display': 'inline-block'})
            
    ]),

    ## graphs
    dcc.Graph(id='main_plot')
])

# callback list
@app.callback(
    # output - visualizations
    Output('main_plot', 'figure'),
    # input - variables from dropdown/selected values
    Input('activity_type', 'value'),
    Input('measure_type', 'value'),
    [Input('sensor_type', 'value')],
    Input('subject_ids', 'value'))

### function to update and generate visualizations
def update_graph(activity_type, measure_type, sensor_type, subject_ids):
    # select measure 
    df_measure = df[df['num_type'] == measure_type.lower()]


    # select subject
    subject_ids = str(subject_ids)
    df_subject = df_measure[df_measure['subject_id'] == subject_ids]
    
    # select columns with selected activity types
    select_re = 'subject_id|time|' + activity_type
    df_activity = df_subject.iloc[:,df_subject.columns.str.contains(select_re)] # get all RSS columns

    # select columns with selected sensors
    sensors_var = 'subject_id|time|'+'|'.join(list(map(lambda x: x.replace(' ', '').lower(), sensor_type)))
    df_sensors = df_activity.iloc[:,df_activity.columns.str.contains(sensors_var)]

    ## plot
    plot_df = pd.melt(df_sensors, id_vars = ['time', 'subject_id'])
    fig = px.line(plot_df, x="time", y="value", color = 'variable', title='Time series signal strength, subject ' +subject_ids )

    fig.update_layout(transition_duration=500)

    return fig
    
 
## launch command
if __name__ == '__main__':
    app.run_server()

