import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from math import ceil
import numpy as np

# Function to create a bar chart for binary categories


def binary_categories_bar_creation(filtered_df, category_code, year_range, number_of_country, country):
    binary_series_df = filtered_df[(filtered_df['Series Code'] == category_code) & (
        filtered_df['Country Name'] == country)]
    x_years_all = binary_series_df.loc[:,
                                       f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns
    x_years_all = [int(x[0:4]) for x in x_years_all]
    x_values = [year if (year % 5 == 0 and str(year)[-1] ==
                         '5') else None for year in x_years_all]

    y_values_all = binary_series_df.loc[:,
                                        f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].values[0]
    y_values = [val if (year % 5 == 0 and str(year)[-1] == '5')
                else None for year, val in zip(x_years_all, y_values_all)]

    y_values_final = [2 if y == 1.0 else 1 if y ==
                      0.0 else 0 for y in y_values]

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

# Function to create a histogram chart for binary categories


def binary_categories_hist_creation(filtered_df, category_code, year_range, number_of_country, country):
    series_df = filtered_df[(filtered_df['Series Code'] == category_code) & (
        filtered_df['Country Name'] == country)]
    x_values = [x[0:4] for x in series_df.loc[:,
                                              f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns]
    y_values = series_df.loc[:, f'{year_range[0]} [YR{year_range[0]}]':
                             f'{year_range[1]} [YR{year_range[1]}]'].values[0]

    y_values = pd.Series(y_values, index=x_values)
    y_values = y_values.interpolate(method='linear')

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

# Function to create the return object for a category chart


def create_return_for_category(data, x_values, category_code, title):
    return {
        'data': data,
        'layout': go.Layout(
            title=title,
            xaxis=dict(
                title='Year',
                tickangle=45,
                showgrid=True,
                range=[1970, 2021],
                tickvals=[i for i in range(
                    int(x_values[0]), int(x_values[-1]), 5)]
            ),
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

# Function to create the return object for a histogram category chart


def create_return_for_hist_category(data, x_values, category_code, title):
    if category_code == 'SG.LAW.INDX.EN':
        ytitle = 'Indicator'
    elif category_code == 'SE.TER.ENRR.FE':
        ytitle = '% gross'

    return {
        'data': data,
        'layout': go.Layout(
            title=title,
            xaxis={'title': 'Year'},
            yaxis=dict(
                title=ytitle,
                showgrid=True
            ),
            hovermode='closest',
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
                borderwidth=2,
                title='',
                itemsizing='constant'
            )
        )
    }


# Dictionary of series data
series_data = {
    'NY.GDP.MKTP.CD': 'GDP (current US$)'
}

# Dictionary of binary series data
binary_series_data = {
    'SG.GET.JOBS.EQ': 'A woman can get a job in the same way as a man',
    'SG.IND.WORK.EQ': 'A woman can work in an industrial job in the same way as a man',
    'SE.TER.ENRR.FE': 'School enrollment, tertiary, female (% gross)',
    'SG.LAW.INDX.EN': 'Women, Business and the Law: Entrepreneurship Indicator Score (scale 1-100)',
    'SG.CNT.SIGN.EQ': 'A woman can sign a contract in the same way as a man'
}

# Dictionary of country colors
country_colors = {
    0: '#fed98e',
    1: '#fe9929',
    2: '#d95f0e',
    3: '#993404'
}

# Read the data from CSV
df = pd.read_csv('../data/cleaned_data.csv')

# Select relevant columns from the dataframe
df_series = df[['Series Name', 'Country Name'] +
               [col for col in df if col.startswith('19') or col.startswith('20')]]

# Melt the dataframe
df_series = df_series.melt(
    id_vars=['Series Name', 'Country Name'], var_name='Year', value_name='Value')

# Convert the 'Year' column to integer
df_series['Year'] = df_series['Year'].str.extract('(\d+)').astype(int)

# Pivot the dataframe
df_series = df_series.pivot_table(
    index=['Country Name', 'Year'], columns='Series Name', values='Value').reset_index()

# Rename the columns
df_series.columns.name = ''
df_series.rename(columns={'Country Name': 'Country'}, inplace=True)

# List of group features
group_features = [
    'Population, total',
    'Population, female',
    'Population, male'
]

# Regions dictionary
regions = {
    "Europe": ["United Kingdom", "France", "Germany", "Italy"],
    "Middle East": ["Saudi Arabia", "Iran, Islamic Rep.", "Israel", "Turkiye"],
    "Asia": ["China", "Japan", "India", "Vietnam"],
    "Africa": ["Egypt, Arab Rep.", "South Africa", "Nigeria", "Kenya"],
    "South America": ["Brazil", 'Argentina', 'Venezuela, RB', "Uruguay"],
    "North and middle America": ['United States', 'Canada', 'Mexico', 'Panama']
}

# List of all countries
all_countries = df_series['Country'].unique().tolist()

# Copy of the dataframe
df_series_original = df_series.copy()

# Create the Dash app
app = Dash(__name__)

app.layout = html.Div([
    # Dropdown for country selection
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country}
                 for country in all_countries],
        multi=True,
        value=[]
    ),
    # RadioItems for region selection
    dcc.RadioItems(
        id='region-radio',
        options=[{'label': region, 'value': region}
                 for region in regions.keys()],
        value=None
    ),
    # Animated bar chart
    dcc.Graph(id='animated-chart'),
    # Population charts
    html.Div([
        dcc.Graph(id='total-population-chart', style={'width': '33%'}),
        dcc.Graph(id='male-population-chart', style={'width': '33%'}),
        dcc.Graph(id='female-population-chart', style={'width': '33%'}),
    ], style={'display': 'flex'}),
    html.Div(style={'height': '50px'}),
    # Year slider
    dcc.RangeSlider(
        id='year-slider',
        min=1970,
        max=2021,
        step=1,
        value=[1970, 2021],
        marks={i: str(i) for i in range(1960, 2023, 2)}
    ),
    # Indicator graph
    dcc.Graph(id='indicator-graph'),
    html.Div(style={'height': '50px'}),
    html.Div([
        # Binary indicator graphs
        html.H2(children='A woman can:'),
        html.Div([
            dcc.Graph(id='sg_get_jobs_eq_binary-indicator-graph',
                      style={'width': '33%'}),
            dcc.Graph(id='sg_get_work_eq_binary-indicator-graph',
                      style={'width': '33%'}),
            dcc.Graph(id='sg_cnt_sign_eq_binary-indicator-graph',
                      style={'width': '33%'}),
        ], style={'display': 'flex'}),
    ]),
    html.Div(style={'height': '50px'}),
    dcc.Graph(id='se_ter_enrr_fe_binary-indicator-graph'),
    html.Div(style={'height': '50px'}),
    html.Div(style={'height': '50px'}),
    html.Div([
        html.Div([dcc.Graph(id='heatmap-lawscore')], style={'width': '25%'}),
        html.Div([dcc.Graph(id='heatmap-entrepreneurship')],
                 style={'width': '25%'}),
        html.Div([dcc.Graph(id='heatmap-mobility')], style={'width': '25%'}),
        html.Div([dcc.Graph(id='heatmap-pay')], style={'width': '25%'}),
    ], style={'display': 'flex'}),
    html.Div(style={'height': '50px'}),
    dcc.Graph(id='animated-scatter-chart'),
])

# Callback to update dropdown values based on region selection


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

# Callback to update the animated chart


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
        melted_df_series = pd.melt(filtered_df_series, id_vars=[
                                   'Country', 'Year'], value_vars=group_features, var_name='Feature', value_name='Value')
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

        max_pop = melted_df_series[melted_df_series['Feature'] ==
                                   'Population, total'].groupby('Country')['Value'].max()
        for country in selected_countries:
            fig1.add_trace(
                go.Scatter(x=[country], y=[max_pop[country]],
                           mode='markers',
                           marker=dict(size=10, color='Red'),
                           showlegend=False)
            )

        return fig1

# Callback to update the total population chart


@app.callback(
    Output('total-population-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def total_population_chart(selected_countries):
    return population_line_chart('Population, total', selected_countries, 'Total Population')

# Callback to update the male population chart


@app.callback(
    Output('male-population-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def male_population_chart(selected_countries):
    return population_line_chart('Population, male', selected_countries, 'Male Population')

# Callback to update the female population chart


@app.callback(
    Output('female-population-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def female_population_chart(selected_countries):
    return population_line_chart('Population, female', selected_countries, 'Female Population')

# Helper function to create population line charts


def population_line_chart(feature, selected_countries, chart_title):
    if len(selected_countries) > 4:
        return go.Figure()
    else:
        filtered_df_series = df_series_original[df_series_original['Country'].isin(
            selected_countries)]
        melted_df_series = pd.melt(filtered_df_series, id_vars=['Country', 'Year'], value_vars=[
                                   feature], var_name='Feature', value_name='Value')

        if melted_df_series.empty:
            return go.Figure()

        scaler = MinMaxScaler()
        melted_df_series['Value'] = scaler.fit_transform(
            melted_df_series[['Value']])

        line_chart = px.line(melted_df_series,
                             x="Year",
                             y="Value",
                             color="Country",
                             labels={'Value': feature})

        line_chart.update_layout(
            title_text=chart_title,
            xaxis=dict(
                title='Year',
                tickangle=45,
                showgrid=True,
                range=[1970, 2021],
                tickvals=[i for i in range(int(melted_df_series['Year'].min()), int(
                    melted_df_series['Year'].max()) + 1, 5)]
            ),
            yaxis=dict(
                overlaying='y',
                tickangle=-90,
                range=[0, 1],
                showgrid=True,
                tickvals=[0, 1],
                ticktext=['0', '1']
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
                borderwidth=2,
                title='',
                itemsizing='constant'
            )
        )

        return line_chart


# Callback to update the graphs


@app.callback(
    [Output('indicator-graph', 'figure'),
     Output('sg_get_jobs_eq_binary-indicator-graph', 'figure'),
     Output('sg_get_work_eq_binary-indicator-graph', 'figure'),
     Output('se_ter_enrr_fe_binary-indicator-graph', 'figure'),
     Output('sg_cnt_sign_eq_binary-indicator-graph', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graph(selected_countries, year_range):
    if not selected_countries:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure()

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
                    showgrid=False
                ),
                hovermode='closest'
            )
        },
        create_return_for_category(sg_get_jobs_eq_traces, x_values,
                                   'SG.GET.JOBS.EQ', 'Get a job in the<br>same way as a man'),
        create_return_for_category(sg_get_work_eq_traces, x_values, 'SG.IND.WORK.EQ',
                                   'Work in an industrial job<br>in the same way as a man'),
        create_return_for_hist_category(
            sg_sec_enrr_fe_traces, x_values, 'SE.TER.ENRR.FE', 'Gross enrollment ratio for tertiary school '),
        # create_return_for_hist_category(
        #     sg_law_indx_en_traces, x_values, 'SG.LAW.INDX.EN', 'Women, Business and the Law: Entrepreneurship Indicator Score'),
        create_return_for_category(sg_cnt_sign_eq_traces, x_values,
                                   'SG.CNT.SIGN.EQ', 'Sign a contract in the <br> same way as a man')
    )

# Calback to draw GDP chart


@app.callback(
    Output('animated-scatter-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def animated_gpd(selected_countries):
    if len(selected_countries) > 4:
        return go.Figure()
    else:
        filtered_df = df_series_original[df_series_original['Country'].isin(
            selected_countries)]
        chart = px.scatter(filtered_df, x='GDP per capita (Current US$)', y='Life expectancy at birth, total (years)',
                           animation_frame='Year', animation_group='Country', size="Population, total", color='Country', log_x=True, size_max=55, range_x=[100, 100000], range_y=[25, 100],
                           labels={
                               'x': 'GDP per capita (Current US$)', 'y': 'Life expectancy at birth, total (years)'},
                           title='GDP vs Life Expectancy Over Time')

        return chart


@app.callback(
    [Output('heatmap-lawscore', 'figure'),
     Output('heatmap-entrepreneurship', 'figure'),
     Output('heatmap-mobility', 'figure'),
     Output('heatmap-pay', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_law_index(selected_countries):
    if len(selected_countries) > 4:
        return go.Figure()
    else:
        filtered_df = df_series_original[df_series_original['Country'].isin(
            selected_countries)]
        filtered_df = filtered_df[filtered_df['Year'] >= 1990]

        employment_features = [
            "Women Business and the Law Index Score (scale 1-100)",
            "Women, Business and the Law: Entrepreneurship Indicator Score (scale 1-100)",
            "Women, Business and the Law: Mobility Indicator Score (scale 1-100)",
            "Women, Business and the Law: Pay Indicator Score (scale 1-100)"
        ]

        custom_titles = ["Index Score", 'Entrepreneurship Indicator Score', 'Mobility Indicator Score', 'Pay Indicator Score'

                         ]

        figures = []

        for feature, title in zip(employment_features, custom_titles):
            heatmap_df = filtered_df.pivot(
                index='Year', columns='Country', values=feature)
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_df.values,
                x=heatmap_df.columns.values,
                y=heatmap_df.index.values,
                zmin=0,
                zmax=100,
                hoverongaps=False
            ))

            fig.update_layout(
                title={
                    'text': title,
                    'y': 0.9,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                title_font=dict(
                    size=15,
                    color='rgb(37,37,37)'),
            )
            figures.append(fig)

        return figures


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
