from dash import Dash, html, dcc, dash_table, Output, Input, State
import pandas as pd
import plotly.express as px
from sklearn.datasets import load_wine
import base64
import io
import requests
# Incorporate data
df = pd.read_csv('https://github.com/seaborn/seaborn-data/raw/master/penguins.csv')

def load_data():
    wine = load_wine()
    wine_df = pd.DataFrame(wine.data, columns=wine.feature_names)
    wine_df['WineType'] = [wine.target_names[t] for t in wine.target]
    return wine_df

wine_df = load_data()

# Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
ingredients = wine_df.drop(columns=['WineType']).columns
avg_wine_df = wine_df.groupby("WineType").mean().reset_index()

x_axis = dcc.Dropdown(id='x_axis', options=[{'label': col, 'value': col} for col in ingredients], value='alcohol', clearable=False)
y_axis = dcc.Dropdown(id='y_axis', options=[{'label': col, 'value': col} for col in ingredients], value='malic_acid', clearable=False)
color_encode = dcc.Checklist(id='color_encode', options=[{'label': 'Color-Encode', 'value': 'Color-Encode'}])

multi_select = dcc.Dropdown(id='multi-select', options=[{'label': col, 'value': col} for col in ingredients], value=['alcohol', 'ash', 'malic_acid'], clearable=False, multi=True)

def create_scatter(x_axis='alcohol', y_axis='ash', color_encode=False):
    scatter = px.scatter(wine_df, x=x_axis, y=y_axis, color='WineType' if color_encode else None, title="{} vs {} ".format(x_axis.capitalize(), y_axis.capitalize()))
    scatter.update_layout(height=600)
    return scatter

def create_bar(ingredients=['alcohol', 'malic_acid', 'ash']):
    bar = px.bar(avg_wine_df, x='WineType', y=ingredients, title='avg ingrdient per wine winetype')
    bar.update_layout(height=600)
    return bar

app = Dash(__name__, external_stylesheets=external_stylesheets, title='final-project', suppress_callback_exceptions=True)
server=app.server
# App layout
data_page1 = {'content': 'Page 1 Content'}
data_page2 = {'content': 'Page 2 Content'}
data_page3 = {'content': 'Page 3 Content'}

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Page 1', value='tab-1'),
        dcc.Tab(label='Page 2', value='tab-2'),
        dcc.Tab(label='Page 3', value='tab-3'),
    ]),
    html.Div(id='tabs-content'),
    # Hidden div to store comments across page changes
   
])
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))   
def update_content(selected_tab):
    if selected_tab == 'tab-1':
        return html.Div([
            html.Div(className='row', children='content of penguins_csv ',
                     style={'textAlign': 'center', 'color': 'green', 'fontSize': 50}),
            dcc.RadioItems(options=['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g'],
                           value='bill_length_mm',
                           inline=True,
                           id='my-radio-buttons-final'
            ),
            html.Div(className='all_columns', children=[
                dash_table.DataTable(data=df.to_dict('records'), page_size=11, style_table={'overflowX': 'auto'})
            ]),
            html.Div(className='row', children='figure',
                     style={'textAlign': 'center', 'color': 'blue', 'fontSize': 50}),
            html.Div(className='all columns', children=[
                dcc.Graph(figure={}, id='histo-chart-final')
            ])
        ])
    elif selected_tab == 'tab-2':
        return html.Div([
            html.Div(className='row', children='content of wine',
                     style={'textAlign': 'center', 'color': 'blue', 'fontSize':50}),
            html.Div(
                children=[x_axis, y_axis, color_encode,
                          dcc.Graph(id='scatter_fig', figure=create_scatter())
                ],
                style={"display": 'inline-block', "width": '48%'}
            ),
            html.Div(
                children=[multi_select, html.Br(),
                          dcc.Graph(id='bar_fig', figure=create_bar())
                ],
                style={"display": 'inline-block', "width": '48%'}
            ),
        ])
    
    elif selected_tab == 'tab-3':
        return html.Div([
            html.Div(className='row', children='other application ',
                     style={'textAlign': 'center', 'color': 'red', 'fontSize': 50}),
            html.Label('Comments:'),
            dcc.Textarea(id='comments-textarea', style={'width': '100%', 'height': 100}),
            html.Div(id='hidden-comments', style={'display': 'none'}),
            # Button to clear comments
            html.Button('Clear Comments', id='clear-comments-button', n_clicks=0),
            html.Br(),
            dcc.Upload(
                id='upload-data',
                children=html.Button('Upload File'),
                multiple=False
            ),
            html.Div(id='comments-container'),  # Separate container for comments
            html.Div([
                dash_table.DataTable(id='uploaded-files-table'),
                dcc.Dropdown(id='download-dropdown'),
                html.Br(),  # Add a line break
                html.A(html.Button('google'), href='https://www.google.com.tw/?hl=zh_TW', target='_blank'),
                html.A(html.Button('youtube'), href='https://www.youtube.com/?hl=zh-TW&gl=TW', target='_blank'),
                html.A(html.Button('facebook'), href='https://www.facebook.com/?locale=zh_TW', target='_blank'),
                html.A(html.Button('instagram'), href='https://www.instagram.com/', target='_blank'),
                html.A(html.Button('proxima'), href='https://ai-nutc.tw/person_page/proxima.html', target='_blank'),
                
                # 新增 API 调用部分
                html.Br(),
                html.Label('API URL:'),
                dcc.Input(id='api-url-input', type='text', value=''),  # 输入 API 地址的输入框
                html.Button('Call API', id='call-api-button', n_clicks=0),  # 用于触发 API 调用的按钮
                html.Div(id='api-result'),  # 用于显示 API 调用结果的元素
            ])
        ])

@app.callback(Output('hidden-comments', 'children'),
              Input('comments-textarea', 'value'),
              prevent_initial_call=True)
#def store_comments(comments):
    #return comments

# Add callback to clear the comments textarea
@app.callback(Output('comments-textarea', 'value'),
              Input('clear-comments-button', 'n_clicks'),
              prevent_initial_call=True)
def clear_comments(n_clicks):
    if n_clicks:
        return ''

# Add callback to update the comments container
@app.callback(Output('comments-container', 'children'),
              Input('hidden-comments', 'children'))
def update_comments_container(comments):
    return comments

@app.callback(
    Output('histo-chart-final', 'figure'),
    Input('my-radio-buttons-final', 'value')
)
def update_graph(col_chosen):
    fig = px.histogram(df, x='island', y=col_chosen, histfunc='avg')
    return fig

@app.callback(Output('scatter_fig', 'figure'),
              [Input('x_axis', 'value'), Input('y_axis', 'value'), Input('color_encode', 'value')])
def update_scatter(x_axis, y_axis, color_encode):
    return create_scatter(x_axis, y_axis, color_encode)

@app.callback(Output('bar_fig', 'figure'), [Input('multi-select', 'value')])
def update_bar(ingredients):
    return create_bar(ingredients)


@app.callback(
    Output('uploaded-files-table', 'data'),
    Output('download-dropdown', 'options'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def update_output(contents, filename):
    if contents is None:
        return [], []
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    # Assume that the user uploaded a CSV file
    df_upload = pd.read_csv(io.StringIO(decoded.decode('utf-8')))#file name must be english or use ISO-8859-1
    
    # You can now use df_upload in your application
    # For example, display the first 5 rows in a DataTable
    return df_upload.head().to_dict('records'), [{'label': filename, 'value': filename}]
@app.callback(
    Output('api-result', 'children'),
    [Input('call-api-button', 'n_clicks')],
    [State('api-url-input', 'value')],
    prevent_initial_call=True
)
def call_api(n_clicks, api_url):
    if n_clicks:
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                api_result = response.text
            else:
                api_result = f'Error: {response.status_code}'
        except Exception as e:
            api_result = f'Error: {str(e)}'
        return f'API Result: {api_result}'


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True,port=5000)
