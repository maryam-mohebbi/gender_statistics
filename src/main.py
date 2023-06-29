import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import dash
import plotly.express as px
import pandas as pd

df = pd.read_csv('../data/data.csv')
df_melted = pd.melt(df,
                    id_vars=['Series Name', 'Series Code',
                             'Country Name', 'Country Code'],
                    var_name='Year',
                    value_name='Value')

df_melted['Year'] = df_melted['Year'].str.slice(0, 4).astype(int)

app = dash.Dash(__name__)

country_codes = df_melted['Country Code'].unique()

app.layout = html.Div([
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': i, 'value': i} for i in country_codes],
        value='USA'
    ),
    dcc.RangeSlider(
        id='year-slider',
        min=1960,
        max=2022,
        step=1,
        value=[1960, 2022],
        marks={i: str(i) for i in range(1960, 2023, 2)}
    ),
    dcc.Graph(id='indicator-graph'),
    dcc.Graph(id='binary-indicator-graph')
])

# Define numerical and binary series
series_codes = ['SP.ADO.TFRT',
                'SP.POP.DPND',
                'NY.GDP.MKTP.CD',
                'NY.GDP.MKTP.KD.ZG',
                'NY.GDP.PCAP.CD',
                'SP.DYN.LE00.IN',
                'SP.DYN.LE00.FE.IN',
                'SP.DYN.LE00.MA.IN'
                ]


series_names = ['Adolescent fertility rate (births per 1,000 women ages 15-19)',
                'Age dependency ratio (% of working-age population)',
                'GDP (current US$)',
                'GDP growth (annual %)',
                'GDP per capita (Current US$)',
                'Life expectancy at birth, total (years)',
                'Life expectancy at birth, female (years)',
                'Life expectancy at birth, male (years)'
                ]


binary_series_codes = ['SG.APL.PSPT.EQ',
                       'SG.HLD.HEAD.EQ',
                       'SG.LOC.LIVE.EQ',
                       'SG.OBT.DVRC.EQ']
binary_series_names = ['Can a woman apply for a passport in the same way as a man?',
                       'Can a woman be head of household in the same way as a man?',
                       'Can a woman choose where to live in the same way as a man?',
                       'Can a woman obtain a judgment of divorce in the same way as a man?']


@app.callback(
    [Output('indicator-graph', 'figure'),
     Output('binary-indicator-graph', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graph(country_code, year_range):
    filtered_df = df[df['Country Code'] == country_code]
    traces = []
    binary_traces = []

    for series_code, series_name in zip(series_codes, series_names):
        series_df = filtered_df[filtered_df['Series Code'] == series_code]
        x_values = series_df.loc[:,
                                 f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns
        x_values = [x[0:4] for x in x_values]
        y_values = series_df.loc[:, f'{year_range[0]} [YR{year_range[0]}]':
                                 f'{year_range[1]} [YR{year_range[1]}]'].values[0]
        traces.append(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            name=series_name
        ))

    for series_code, series_name in zip(binary_series_codes, binary_series_names):
        binary_series_df = filtered_df[filtered_df['Series Code']
                                       == series_code]
        x_values = binary_series_df.loc[:,
                                        f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns
        x_values = [x[0:4] for x in x_values]
        y_values = binary_series_df.loc[:,
                                        f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].values[0]

        # Mapping values to 1 (Yes), 0 (No), and -1 (No data)
        y_values = [1 if y == '1' else (
            0 if y == '0' else -1) for y in y_values]

        binary_traces.append(go.Bar(
            x=x_values,
            y=y_values,
            name=series_name,
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Year'},
            yaxis={'title': 'Indicator Value'},
            title='Country Indicators Over Time',
            hovermode='closest'
        )
    }, {
        'data': binary_traces,
        'layout': go.Layout(
            xaxis={'title': 'Year'},
            yaxis={'title': 'Indicator Value',
                   # Adjust the range to include all categories
                   'range': [-1.5, 1.5],
                   'tickvals': [-1, 0, 1],
                   'ticktext': ['No data', 'No', 'Yes']},
            title='Binary Indicators Over Time',
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
