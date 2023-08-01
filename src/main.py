import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
from sklearn.preprocessing import StandardScaler
from plotly.subplots import make_subplots
from math import ceil


df = pd.read_csv('../data/cleaned_data.csv')

df_series = df[['Series Name', 'Country Name'] +
               [col for col in df if col.startswith('19') or col.startswith('20')]]

df_series = df_series.melt(
    id_vars=['Series Name', 'Country Name'], var_name='Year', value_name='Value')

df_series['Year'] = df_series['Year'].str.extract('(\d+)').astype(int)

df_series = df_series.pivot_table(
    index=['Country Name', 'Year'], columns='Series Name', values='Value').reset_index()

df_series.columns.name = ''
df_series.rename(columns={'Country Name': 'Country'}, inplace=True)

group_features = [
    'Population, total',
    'Population, female',
    'Population, male'
]

regions = {
    'Europe': ['United Kingdom', 'France', 'Germany', 'Italy'],
    'Middle East': ['Saudi Arabia', 'Iran, Islamic Rep.', 'Israel', 'Turkiye'],
    'Asia': ['China', 'Japan', 'India', 'Vietnam'],
    'Africa': ['Egypt, Arab Rep.', 'South Africa', 'Nigeria', 'Kenya'],
    'South America': ['Brazil', 'Argentina', 'Venezuela, RB', 'Peru'],
    'North and middle America': ['United States', 'Canada', 'Mexico']
}

country_colors = {
    0: '#fed98e',
    1: '#fe9929',
    2: '#d95f0e',
    3: '#993404'
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
    dcc.Graph(id='population-animated-chart'),
    html.Div([
        dcc.Graph(id='line-chart-total', style={'width': '33%'}),
        dcc.Graph(id='line-chart-female', style={'width': '33%'}),
        dcc.Graph(id='line-chart-male', style={'width': '33%'}),], style={'display': 'flex'}),

    dcc.Graph(id='employment-ratio-chart'),

    dcc.RangeSlider(
        id='year-slider',
        min=1970,
        max=2021,
        step=1,
        value=[1970, 2021],
        marks={i: str(i) for i in range(1960, 2023, 2)}
    ),
    dcc.Graph(id='gdp-line-chart'),
    html.Div([
        dcc.Graph(id='chart-women-job', style={'width': '33%'}),
        dcc.Graph(id='chart-women-industrial-job', style={'width': '33%'}),
        dcc.Graph(id='chart-women-contract', style={'width': '33%'}),
    ], style={'display': 'flex'}),

    dcc.Graph(id='enrolment-line-chart'),
    html.Div([
        html.Div([dcc.Graph(id='heatmap-lawscore')], style={'width': '25%'}),
        html.Div([dcc.Graph(id='heatmap-entrepreneurship')],
                 style={'width': '25%'}),
        html.Div([dcc.Graph(id='heatmap-mobility')], style={'width': '25%'}),
        html.Div([dcc.Graph(id='heatmap-pay')], style={'width': '25%'}),
    ], style={'display': 'flex'}),
    dcc.Graph(id='animated-scatter-chart'),
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
    Output('population-animated-chart', 'figure'),
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
        fig = px.bar(melted_df_series,
                     x='Country',
                     y='Value',
                     color='Feature',
                     animation_frame='Year',
                     animation_group='Country',
                     labels={'Value': 'Population'},
                     title='Population Change Over Time',
                     barmode='group')
        fig.update_layout(yaxis_range=[0, melted_df_series['Value'].max()])

        max_pop = melted_df_series[melted_df_series['Feature'] ==
                                   'Population, total'].groupby('Country')['Value'].max()
        for country in selected_countries:
            fig.add_trace(
                go.Scatter(x=[country], y=[max_pop[country]],
                           mode='markers',
                           marker=dict(size=10, color='Red'),
                           showlegend=False)
            )

        return fig


def get_standardized_population_chart(selected_countries, population_type):
    if len(selected_countries) > 4:
        return go.Figure()
    else:
        column_name = f'Population, {population_type}'
        filtered_df = df_series_original[df_series_original['Country'].isin(
            selected_countries)][['Year', 'Country', column_name]]

        scaler = StandardScaler()
        for country in selected_countries:
            filtered_df.loc[filtered_df['Country'] == country, column_name] = scaler.fit_transform(
                filtered_df.loc[filtered_df['Country'] == country, column_name].values.reshape(-1, 1))

        melted_df = pd.melt(filtered_df, id_vars=['Year', 'Country'], value_vars=[column_name],
                            var_name='Population Type', value_name='Value')

        fig = px.line(melted_df, x='Year', y='Value', color='Country',
                      title=f'Standardized {population_type.capitalize()} Population Over Time')

        fig.update_xaxes(tickangle=45)

        fig.update_layout(showlegend=True, legend=dict(
            x=0.5,
            y=-0.5,
            xanchor='center',
            yanchor='top',
            orientation='h',
            traceorder='normal',
            title='',
            bordercolor='Black',
            borderwidth=2), legend_title_text='', title={
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},)

        return fig


@app.callback(
    [Output('line-chart-total', 'figure'),
     Output('line-chart-female', 'figure'),
     Output('line-chart-male', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_population_line_chart(selected_countries):
    total_chart = get_standardized_population_chart(
        selected_countries, 'total')
    female_chart = get_standardized_population_chart(
        selected_countries, 'female')
    male_chart = get_standardized_population_chart(selected_countries, 'male')

    return total_chart, female_chart, male_chart


@app.callback(
    Output('employment-ratio-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_employment_ratio_chart(selected_countries):
    if not selected_countries:
        return go.Figure()

    filtered_df = df_series[df_series['Country'].isin(selected_countries)]
    filtered_df = filtered_df[filtered_df['Year'] >= 1990]

    filtered_df['Labor force proportion'] = (
        filtered_df['Labor force, total'] / filtered_df['Population, total']) * 100

    n = len(selected_countries)
    n_cols = min(5, n)
    n_rows = ceil(n / n_cols)

    fig = make_subplots(rows=n_rows, cols=n_cols,
                        subplot_titles=selected_countries, vertical_spacing=0.1)

    min_val_list = []
    max_val_list = []

    fig.add_trace(
        go.Scatter(x=[None], y=[None],
                   mode='lines',
                   name='Employment Ratio',
                   line=dict(color='red'),
                   showlegend=True)
    )

    fig.add_trace(
        go.Scatter(x=[None], y=[None],
                   mode='lines',
                   name='Labor Force Proportion',
                   line=dict(color='blue'),
                   showlegend=True)
    )

    for i, country in enumerate(selected_countries, start=1):
        country_df = filtered_df[filtered_df['Country'] == country]

        labor_force_employment_proportion = (
            country_df['Employment to population ratio, 15+, total (%) (modeled ILO estimate)'] *
            (country_df['Population, total'] - country_df['Population ages 0-14, total']) /
            country_df['Population, total']
        )

        min_country = min(labor_force_employment_proportion.min(),
                          country_df['Labor force proportion'].min())
        max_country = max(labor_force_employment_proportion.max(),
                          country_df['Labor force proportion'].max())

        min_val_list.append(min_country)
        max_val_list.append(max_country)

        row = ceil(i / n_cols)
        col = i if i <= n_cols else i % n_cols if i % n_cols != 0 else n_cols

        fig.add_trace(
            go.Scatter(x=country_df['Year'], y=labor_force_employment_proportion,
                       name=f'Employment Ratio', hovertemplate='Year=%{x}<br>Employment Ratio=%{y}',
                       line=dict(color='red'), showlegend=False),
            row=row, col=col
        )
        fig.add_trace(
            go.Scatter(x=country_df['Year'], y=country_df['Labor force proportion'],
                       name=f'Labor Force Proportion', hovertemplate='Year=%{x}<br>Labor Force Proportion=%{y}',
                       line=dict(color='blue'), showlegend=False),
            row=row, col=col
        )

    min_val = min(min_val_list)
    max_val = max(max_val_list)

    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='', secondary_y=False)
    fig.update_yaxes(title_text='', secondary_y=True)
    fig.update_yaxes(range=[min_val-1, max_val+1], secondary_y=False)
    fig.update_yaxes(range=[min_val-1, max_val+1], secondary_y=True)

    fig.update_layout(
        height=420*n_rows,
        title_text='Comparison between Employment Ratio and Labor Force Proportion',
        showlegend=True,
        legend=dict(
            x=0.5,
            y=-0.5,
            xanchor='center',
            yanchor='top',
            orientation='h',
            traceorder='normal',
            font=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
            ),
            bordercolor='Black',
            borderwidth=2
        ),
    )

    fig.add_annotation(
        dict(
            x=-0.04,
            y=0.5,
            showarrow=False,
            text='Proportions (%)',
            textangle=-90,
            xref='paper',
            yref='paper'
        )
    )
    fig.add_annotation(
        dict(
            x=0.5,
            y=-0.1,
            showarrow=False,
            text='Year',
            xref='paper',
            yref='paper'
        )
    )

    return fig


@app.callback(
    Output('gdp-line-chart', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def gdp_chart(selected_countries, years_range):
    if len(selected_countries) > 4:
        return go.Figure()
    else:
        filtered_df_series = df_series_original[(df_series_original['Country'].isin(selected_countries)) &
                                                (df_series_original['Year'].between(years_range[0], years_range[1]))]

        fig = go.Figure()
        for i, country in enumerate(selected_countries):
            country_data = filtered_df_series[filtered_df_series['Country'] == country]
            fig.add_trace(go.Scatter(x=country_data['Year'],
                                     y=country_data['GDP (current US$)'],
                                     mode='lines',
                                     name=country,
                                     line=dict(color=country_colors[i % len(country_colors)])))

        fig.update_layout(
            title='GDP Change Over Time (current US$)',
            xaxis=dict(
                title='Year',
                showgrid=True,
                gridcolor='LightGray',
                showline=True,
                linecolor='black',
            ),
            yaxis=dict(
                title='GDP (current US$)',
                showgrid=True,
                gridcolor='LightGray',
                showline=True,
                linecolor='black',

            ),
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',

            legend=dict(
                x=0.5,
                y=-0.5,
                xanchor='center',
                yanchor='top',
                orientation='h',
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
                ),
                bordercolor='Black',
                borderwidth=2
            ),
        )

        return fig


@app.callback(
    [Output('chart-women-job', 'figure'),
     Output('chart-women-industrial-job', 'figure'),
     Output('chart-women-contract', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_bar_charts(selected_countries, years_range):
    figures = []

    features = [
        'A woman can get a job in the same way as a man (1=yes; 0=no)',
        'A woman can work in an industrial job in the same way as a man (1=yes; 0=no)',
        'A woman can sign a contract in the same way as a man (1=yes; 0=no)'
    ]

    for feature in features:
        fig = go.Figure()

        for i, country in enumerate(selected_countries):
            country_data = df_series_original[(df_series_original['Country'] == country) &
                                              (df_series_original['Year'].between(years_range[0], years_range[1])) &
                                              (df_series_original['Year'].astype(str).str[-1] == '5')]

            country_data = country_data[['Year', feature]]
            country_data.set_index('Year', inplace=True)

            country_data[feature] = country_data[feature].map({0: 1, 1: 2})

            y_values_final = country_data[feature].tolist()

            binary_trace = go.Bar(
                x=country_data.index,
                y=y_values_final,
                name=country,
                yaxis='y2',
                marker_color=country_colors[i % len(country_colors)],
                width=1,
                offset=i-1
            )

            fig.add_trace(binary_trace)
        clean_feature_title = feature.replace(' (1=yes; 0=no)', '')

        fig.update_layout(

            title={
                'text': f'{clean_feature_title}',
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'},
            title_font=dict(
                family='sans-serif',
                size=12,
                color='black',
            ),
            xaxis=dict(
                title='Year',
                dtick=5,
                tickangle=45,
                showgrid=True,
                range=[years_range[0], years_range[1]],
                gridcolor='LightGray',
                showline=True,
                linecolor='black',
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
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
                ),
                bordercolor='Black',
                borderwidth=2
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )

        figures.append(fig)

    return figures


@app.callback(
    Output('enrolment-line-chart', 'figure'),
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def enrolment_line_chart(selected_countries, years_range):
    if len(selected_countries) > 4:
        return go.Figure()
    else:
        filtered_df_series = df_series_original[(df_series_original['Country'].isin(selected_countries)) &
                                                (df_series_original['Year'].between(years_range[0], years_range[1]))]

        fig = go.Figure()
        for i, country in enumerate(selected_countries):
            country_data = filtered_df_series[filtered_df_series['Country'] == country]

            country_data['School enrollment, tertiary, female (% gross)'] = country_data[
                'School enrollment, tertiary, female (% gross)'].interpolate()

            fig.add_trace(go.Scatter(x=country_data['Year'],
                                     y=country_data['School enrollment, tertiary, female (% gross)'],
                                     mode='lines',
                                     name=country,
                                     line=dict(color=country_colors[i % len(country_colors)])))

        fig.update_layout(
            title='Gross enrollment ratio for tertiary school',
            xaxis=dict(
                title='Year',
                showgrid=True,
                gridcolor='LightGray',
                showline=True,
                linecolor='black',
            ),
            yaxis=dict(
                title='% gross',
                showgrid=True,
                gridcolor='LightGray',
                showline=True,
                linecolor='black',
            ),
            autosize=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',

            legend=dict(
                x=0.5,
                y=-0.5,
                xanchor='center',
                yanchor='top',
                orientation='h',
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
                ),
                bordercolor='Black',
                borderwidth=2
            ),
        )

        return fig


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
            'Women Business and the Law Index Score (scale 1-100)',
            'Women, Business and the Law: Entrepreneurship Indicator Score (scale 1-100)',
            'Women, Business and the Law: Mobility Indicator Score (scale 1-100)',
            'Women, Business and the Law: Pay Indicator Score (scale 1-100)'
        ]

        custom_titles = ['Women Business and the Law Index Score',
                         'Entrepreneurship Indicator Score',
                         'Mobility Indicator Score',
                         'Pay Indicator Score'
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
                    family='sans-serif',
                    size=12,
                    color='black'
                ),),

            figures.append(fig)

        return figures


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
                           animation_frame='Year', animation_group='Country', size='Population, total', color='Country', log_x=True, size_max=55, range_x=[100, 100000], range_y=[25, 100],
                           labels={
                               'x': 'GDP per capita (Current US$)', 'y': 'Life expectancy at birth, total (years)'},
                           title='GDP vs Life Expectancy Over Time')

        return chart


if __name__ == '__main__':
    app.run_server(debug=True)
