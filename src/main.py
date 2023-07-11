import pandas as pd
import plotly.express as px
from dash import Dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from math import ceil
import numpy as np


def binary_categories_bar_creation(filtered_df, category_code, year_range, number_of_country, country):
    binary_series_df = filtered_df[(filtered_df['Series Code'] == category_code) & (
        filtered_df['Country Name'] == country)]

    x_years_all = binary_series_df.loc[:,
                                       f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns
    x_years_all = [int(x[0:4]) for x in x_years_all]
    x_values = []
    for year in x_years_all:
        if year % 5 == 0 and str(year)[-1] == '5':
            x_values.append(year)
        else:
            x_values.append(None)

    y_values_all = binary_series_df.loc[:, f'{year_range[0]} [YR{year_range[0]}]':
                                           f'{year_range[1]} [YR{year_range[1]}]'].values[0]
    y_values = []
    for year, val in zip(x_years_all, y_values_all):
        if year % 5 == 0 and str(year)[-1] == '5':
            y_values.append(val)
        else:
            y_values.append(None)
    y_values_final = []
    for y in y_values:
        if y == 1.0:
            y_values_final.append(2)
        elif y == 0.0:
            y_values_final.append(1)
        else:
            y_values_final.append(0)

    bar_offset_shift = None
    if number_of_country == 0:
        bar_offset_shift = -1
    elif number_of_country == 1:
        bar_offset_shift = -2
    elif number_of_country == 2:
        bar_offset_shift = 0
    elif number_of_country == 3:
        bar_offset_shift = 1

    binary_trace = go.Bar(
        x=x_years_all,
        y=y_values_final,
        name=country,
        yaxis='y2',
        marker_color=country_colors[number_of_country],
        width=1,
        offset=bar_offset_shift
    )

    return binary_trace


def binary_categories_hist_creation(filtered_df, category_code, year_range, number_of_country, country):
    series_df = filtered_df[(filtered_df['Series Code'] == category_code) & (
        filtered_df['Country Name'] == country)]

    x_values = series_df.loc[:,
                             f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns
    x_values = [x[0:4] for x in x_values]
    y_values = series_df.loc[:, f'{year_range[0]} [YR{year_range[0]}]':
                             f'{year_range[1]} [YR{year_range[1]}]'].values[0]

    # convert y_values into pandas Series for the sake of convenience
    y_values = pd.Series(y_values, index=x_values)

    # use interpolate method to fill the missing values
    # the method could be 'linear', 'pad', 'nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'polynomial', 'spline', 'barycentric', 'krogh', 'piecewise_polynomial', 'from_derivatives', 'pchip', 'akima', 'cubicspline'
    y_values = y_values.interpolate(method='linear')

    # or if you prefer, you can fill it using the forward-fill method like this:
    # y_values = y_values.fillna(method='ffill')
    name_of_graph = country
    trace = go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines',
        name=name_of_graph,
        yaxis='y1',
        marker_color=country_colors[number_of_country],
        showlegend=True
    )
    return trace


def create_return_for_category(data, x_values, category_code, title):

    return {
        'data': data,
        'layout': go.Layout(
            title=title,
            xaxis=dict(title='Year',
                       tickangle=45,
                       showgrid=True,
                       range=[1970, 2021],
                       tickvals=[i for i in range(int(x_values[0]), int(x_values[-1]), 5)]),
            yaxis2=dict(
                overlaying='y',
                tickangle=-90,
                range=[0, 2],
                showgrid=True,
                tickvals=[1, 2],
                ticktext=['no', 'yes']
            ),
            hovermode='x',
            autosize=True,
            margin=dict(l=50, r=50, t=150, b=50),
            legend=dict(
                x=0.5,
                y=-0.5,
                xanchor='center',
                yanchor='top',
                orientation='h',
                traceorder="normal",
                font=dict(
                    family="sans-serif",
                    size=12,
                    color="black"
                ),
                bordercolor="Black",
                borderwidth=2

            )
        )

    }


def create_return_for_hist_category(data, x_values, category_code):

    if category_code == 'SG.LAW.INDX.EN':
        ytitle = 'Indicator'
    elif category_code == 'SE.TER.ENRR.FE':
        ytitle = '% gross'

    return {
        'data': data,
        'layout': go.Layout(
            title=binary_series_data[category_code],
            xaxis={'title': 'Year'},
            yaxis=dict(title=ytitle,
                       showgrid=True,
                       ),
            hovermode='closest',
        )
    }


series_data = {
    'NY.GDP.MKTP.CD': 'GDP (current US$)'
}

binary_series_data = {'SG.GET.JOBS.EQ': 'A woman can get a job in the same way as a man',
                      'SG.IND.WORK.EQ': 'A woman can work in an industrial job in the same way as a man',
                      'SE.TER.ENRR.FE': 'School enrollment, tertiary, female (% gross)',
                      'SG.LAW.INDX.EN': 'Women, Business and the Law: Entrepreneurship Indicator Score (scale 1-100)',
                      'SG.CNT.SIGN.EQ': 'A woman can sign a contract in the same way as a man',
                      }

country_colors = {0: '#fed98e',
                  1: '#fe9929',
                  2: '#d95f0e',
                  3: '#993404'}

df = pd.read_csv('../data/cleaned_data.csv')

df_series = df[['Series Name', 'Country Name'] +
               [col for col in df if col.startswith('19') or col.startswith('20')]]

df_series = df_series.melt(id_vars=['Series Name', 'Country Name'],
                           var_name='Year', value_name='Value')

df_series['Year'] = df_series['Year'].str.extract('(\d+)').astype(int)

df_series = df_series.pivot_table(index=['Country Name', 'Year'],
                                  columns='Series Name', values='Value').reset_index()

df_series.columns.name = ''
df_series.rename(columns={'Country Name': 'Country'}, inplace=True)


group_features = ['Population, total',
                  'Population, female',
                  'Population, male',]

regions = {
    "Europe": ["United Kingdom", "France", "Germany", "Italy"],
    "Middle East": ["Saudi Arabia", "Iran, Islamic Rep.", "Israel", "Turkiye"],
    "Asia": ["China", "Japan", "India", "Vietnam"],
    "Africa": ["Egypt, Arab Rep.", "South Africa", "Nigeria", "Kenya"],
    "South America": ["Brazil", 'Argentina', 'Venezuela, RB', "Uruguay"],
    "North and middle America": ['United States', 'Canada', 'Mexico', 'Panama'],

}
all_countries = df_series['Country'].unique().tolist()


df_series_original = df_series.copy()


app = Dash(__name__)


app.layout = html.Div([
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country}
                 for country in all_countries],
        multi=True,
        value=[]
    ),
    dcc.RadioItems(
        id='region-radio',
        options=[{'label': region, 'value': region}
                 for region in regions.keys()],
        value=None
    ),
    dcc.Graph(id='animated-chart'),

    dcc.RangeSlider(
        id='year-slider',
        min=1970,
        max=2021,
        step=1,
        value=[1970, 2021],
        marks={i: str(i) for i in range(1960, 2023, 2)}
    ),
    html.Div([
        dcc.Graph(id='indicator-graph'),
    ]),
    html.H2(children='A woman can:'),

    html.Div([

        dcc.Graph(id='sg_get_jobs_eq_binary-indicator-graph',
                  style={'width': '33%'}),
        dcc.Graph(id='sg_get_work_eq_binary-indicator-graph',
                  style={'width': '33%'}),
        dcc.Graph(id='sg_cnt_sign_eq_binary-indicator-graph',
                  style={'width': '33%'}),
    ], style={'display': 'flex'}),
    dcc.Graph(id='se_ter_enrr_fe_binary-indicator-graph'),
    dcc.Graph(id='sg_law_indx_en_binary-indicator-graph'),

])


@app.callback(
    Output('country-dropdown', 'value'),
    [Input('region-radio', 'value')],
    [State('country-dropdown', 'options')]
)
def update_dropdown_values(selected_region, available_options):
    if selected_region is None:
        return []
    else:
        region_countries = regions[selected_region]
        return [country['value'] for country in available_options if country['value'] in region_countries]


@app.callback(
    Output('animated-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def population_chart(selected_countries):
    if len(selected_countries) > 4:
        return go.Figure()
    else:
        filtered_df_series = df_series_original[df_series_original['Country'].isin(
            selected_countries)]

        melted_df_series = pd.melt(filtered_df_series, id_vars=['Country', 'Year'],
                                   value_vars=group_features,
                                   var_name='Feature', value_name='Value')
        fig1 = px.bar(melted_df_series,
                      x="Country",
                      y='Value',
                      color="Feature",
                      animation_frame="Year",
                      animation_group="Country",
                      labels={'Value': 'Population'},
                      title='Population Change Over Time',
                      barmode='group')
        fig1.update_layout(yaxis_range=[0, melted_df_series['Value'].max()])

        max_pop = melted_df_series[melted_df_series['Feature'] == 'Population, total'].groupby('Country')[
            'Value'].max()
        for country in selected_countries:
            fig1.add_trace(
                go.Scatter(x=[country], y=[max_pop[country]],
                           mode='markers',
                           marker=dict(size=10, color='Red'),
                           showlegend=False)
            )

        return fig1


@app.callback(
    [Output('indicator-graph', 'figure'),
     Output('sg_get_jobs_eq_binary-indicator-graph', 'figure'),
     Output('sg_get_work_eq_binary-indicator-graph', 'figure'),
     Output('se_ter_enrr_fe_binary-indicator-graph', 'figure'),
     Output('sg_law_indx_en_binary-indicator-graph', 'figure'),
     Output('sg_cnt_sign_eq_binary-indicator-graph', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graph(selected_countries, year_range):
    if not selected_countries:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

    filtered_df = df[df['Country Name'].isin(selected_countries)]
    traces = []
    sg_get_jobs_eq_traces = []
    sg_get_work_eq_traces = []
    sg_sec_enrr_fe_traces = []
    sg_law_indx_en_traces = []
    sg_cnt_sign_eq_traces = []
    y_scatter_max = []

    for number_of_country, country in enumerate(selected_countries):
        first_series_df = filtered_df[filtered_df['Series Code']
                                      == 'NY.GDP.MKTP.CD']

        x_values = first_series_df.loc[:,
                                       f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns
        x_values = [x[0:4] for x in x_values]
        y_values = first_series_df[first_series_df['Country Name'] == country].loc[:,
                                                                                   f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].values[0]

        y_values_fixed = []
        for idx, y_value in enumerate(y_values):
            if idx == 0 or np.isnan(y_value) == False:
                existed_value = y_value
                y_values_fixed.append(existed_value)
            elif np.isnan(y_value):
                y_values_fixed.append(existed_value)

        y_scatter_max.append(max(y_values))
        name_of_graph = country
        trace = go.Scatter(
            x=x_values,
            y=y_values_fixed,
            mode='lines',
            name=name_of_graph,
            yaxis='y1',
            marker_color=country_colors[number_of_country],
            showlegend=True
        )
        traces.append(trace)

        sg_get_jobs_eq_traces.append(binary_categories_bar_creation(
            filtered_df, 'SG.GET.JOBS.EQ', year_range, number_of_country, country))
        sg_get_work_eq_traces.append(binary_categories_bar_creation(
            filtered_df, 'SG.IND.WORK.EQ', year_range, number_of_country, country))
        sg_cnt_sign_eq_traces.append(binary_categories_bar_creation(
            filtered_df, 'SG.CNT.SIGN.EQ', year_range, number_of_country, country))
        sg_sec_enrr_fe_traces.append(binary_categories_hist_creation(
            filtered_df, 'SE.TER.ENRR.FE', year_range, number_of_country, country))
        sg_law_indx_en_traces.append(binary_categories_hist_creation(
            filtered_df, 'SG.LAW.INDX.EN', year_range, number_of_country, country))

    return (
        {
            'data': traces,
            'layout': go.Layout(
                title='Prosperity of the economy depends on the participation of women',
                xaxis={'title': 'Year'},
                yaxis=dict(
                    title='GDP (current US$)',
                    showgrid=False,

                ),
                hovermode='closest',

            )
        },
        create_return_for_category(
            sg_get_jobs_eq_traces, x_values, 'SG.GET.JOBS.EQ', 'Get a job in the<br>same way as a man'),
        create_return_for_category(
            sg_get_work_eq_traces, x_values, 'SG.IND.WORK.EQ', 'Work in an industrial job<br>in the same way as a man'),
        create_return_for_hist_category(
            sg_sec_enrr_fe_traces, x_values, 'SE.TER.ENRR.FE'),
        create_return_for_hist_category(
            sg_law_indx_en_traces, x_values, 'SG.LAW.INDX.EN'),
        create_return_for_category(
            sg_cnt_sign_eq_traces, x_values, 'SG.CNT.SIGN.EQ', 'Sign a contract in the <br> same way as a man')
    )


if __name__ == '__main__':
    app.run_server(debug=True)
