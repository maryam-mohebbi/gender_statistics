import pandas as pd
import plotly.express as px
from dash import Dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from math import ceil


df = pd.read_csv('../data/cleaned_data.csv')

df = df[['Series Name', 'Country Name'] +
        [col for col in df if col.startswith('19') or col.startswith('20')]]

df = df.melt(id_vars=['Series Name', 'Country Name'],
             var_name='Year', value_name='Value')

df['Year'] = df['Year'].str.extract('(\d+)').astype(int)

df = df.pivot_table(index=['Country Name', 'Year'],
                    columns='Series Name', values='Value').reset_index()

df.columns.name = ''
df.rename(columns={'Country Name': 'Country'}, inplace=True)


group_features = ['Population, total',
                  'Population, female',
                  'Population, male',]

regions = {
    "Europe": ["United Kingdom", "France", "Germany", "Italy", "Spain", "Belgium", "Netherlands", "Switzerland", "Sweden", "Poland"],
    "Middle East": ["Saudi Arabia", "Iran, Islamic Rep.", "Israel", "Turkiye", "United Arab Emirates", "Iraq", "Lebanon", "Qatar", "Jordan", "Kuwait"],
    "Asia": ["China", "Japan", "India", "Vietnam", "Russian Federation", "Thailand", "Indonesia", "Pakistan", "Philippines", "Malaysia"],
    "Africa": ["Egypt, Arab Rep.", "South Africa", "Nigeria", "Kenya", "Morocco", "Ethiopia", "Tanzania", "Algeria", "Ghana", "Uganda"],
    "South America": ["Brazil", 'Argentina', 'Venezuela, RB', "Uruguay", "Colombia", "Chile", "Peru", "Guyana", "Suriname", "Ecuador"],
    "North and middle America": ['United States', 'Canada', 'Mexico', 'Panama', 'Costa Rica', 'Jamaica', 'Dominican Republic'],

}
all_countries = df['Country'].unique().tolist()


df_original = df.copy()


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
    dcc.Graph(id='boxplot-chart'),
    dcc.Graph(id='animated-scatter-chart'),
    html.Div([
        html.Div([dcc.Graph(id='heatmap1')], style={'width': '33%'}),
        html.Div([dcc.Graph(id='heatmap2')], style={'width': '33%'}),
        html.Div([dcc.Graph(id='heatmap3')], style={'width': '33%'}),
    ],
        style={'display': 'flex'}),
    dcc.Graph(id='employment-ratio-chart'),
    html.Div([
        html.Div([
            html.Div([dcc.Graph(id='heatmap11')], style={'width': '25%'}),
            html.Div([dcc.Graph(id='heatmap12')], style={'width': '25%'}),
            html.Div([dcc.Graph(id='heatmap13')], style={'width': '25%'}),
            html.Div([dcc.Graph(id='heatmap14')], style={'width': '25%'}),
        ], style={'display': 'flex'}),

        html.Div([
            html.Div([dcc.Graph(id='heatmap15')], style={'width': '25%'}),
            html.Div([dcc.Graph(id='heatmap16')], style={'width': '25%'}),
            html.Div([dcc.Graph(id='heatmap17')], style={'width': '25%'}),
            html.Div([dcc.Graph(id='heatmap18')], style={'width': '25%'}),
        ], style={'display': 'flex'}),

        html.Div([
            html.Div([dcc.Graph(id='heatmap19')], style={'width': '25%'}),
            html.Div([dcc.Graph(id='heatmap20')], style={'width': '25%'}),

        ], style={'display': 'flex'}),
        dcc.Graph(id='animated-scatter-chart2'),
        dcc.Graph(id='line-chart'),
    ])


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
    [Output('animated-chart', 'figure'),
     Output('boxplot-chart', 'figure'),
     Output('animated-scatter-chart', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_chart(selected_countries):
    if len(selected_countries) > 10:
        return go.Figure(), go.Figure()
    else:
        filtered_df = df_original[df_original['Country'].isin(
            selected_countries)]

        melted_df = pd.melt(filtered_df, id_vars=['Country', 'Year'],
                            value_vars=group_features,
                            var_name='Feature', value_name='Value')
        fig1 = px.bar(melted_df,
                      x="Country",
                      y='Value',
                      color="Feature",
                      animation_frame="Year",
                      animation_group="Country",
                      labels={'Value': 'Population'},
                      title='Population Change Over Time',
                      barmode='group')
        fig1.update_layout(yaxis_range=[0, melted_df['Value'].max()])

        max_pop = melted_df[melted_df['Feature'] == 'Population, total'].groupby('Country')[
            'Value'].max()
        for country in selected_countries:
            fig1.add_trace(
                go.Scatter(x=[country], y=[max_pop[country]],
                           mode='markers',
                           marker=dict(size=10, color='Red'),
                           showlegend=False)
            )

        fig2 = px.box(filtered_df, x="Country", y=group_features)

        fig3 = px.scatter(filtered_df, x='GDP per capita (Current US$)', y='Life expectancy at birth, total (years)',
                          animation_frame='Year', animation_group='Country', size="Population, total", color='Country', log_x=True, size_max=55, range_x=[100, 100000], range_y=[25, 100],
                          labels={
                              'x': 'GDP per capita (Current US$)', 'y': 'Life expectancy at birth, total (years)'},
                          title='GDP vs Life Expectancy Over Time')

        return fig1, fig2, fig3


@app.callback(
    [Output('heatmap1', 'figure'),
     Output('heatmap2', 'figure'),
     Output('heatmap3', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_heatmap(selected_countries):
    if len(selected_countries) > 10:
        return go.Figure()
    else:
        filtered_df = df_original[df_original['Country'].isin(
            selected_countries)]
        filtered_df = filtered_df[filtered_df['Year'] >= 1990]

        employment_features = [
            "Employment to population ratio, 15+, female (%) (modeled ILO estimate)",
            "Employment to population ratio, 15+, male (%) (modeled ILO estimate)",
            "Employment to population ratio, 15+, total (%) (modeled ILO estimate)"
        ]

        global_min = filtered_df[employment_features].min().min()
        global_max = filtered_df[employment_features].max().max()

        custom_titles = ["Female Employment Ratio",
                         "Male Employment Ratio", "Total Employment Ratio"]

        figures = []

        for feature, title in zip(employment_features, custom_titles):
            heatmap_df = filtered_df.pivot(
                index='Year', columns='Country', values=feature)
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_df.values,
                x=heatmap_df.columns.values,
                y=heatmap_df.index.values,
                zmin=global_min,
                zmax=global_max,
                hoverongaps=False))

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


@app.callback(
    Output('employment-ratio-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_employment_ratio_chart(selected_countries):
    if not selected_countries:
        return go.Figure()

    filtered_df = df[df['Country'].isin(selected_countries)]
    filtered_df = filtered_df[filtered_df['Year'] >= 1990]

    filtered_df['Labor force proportion'] = (
        filtered_df['Labor force, total'] / filtered_df['Population, total']) * 100

    n = len(selected_countries)
    n_cols = 4
    n_rows = ceil(n / n_cols)

    fig = make_subplots(rows=n_rows, cols=n_cols,
                        subplot_titles=selected_countries, vertical_spacing=0.1)
    min_val = filtered_df[[
        'Employment to population ratio, 15+, total (%) (modeled ILO estimate)', 'Labor force proportion']].min().min()
    max_val = filtered_df[[
        'Employment to population ratio, 15+, total (%) (modeled ILO estimate)', 'Labor force proportion']].max().max()

    for i, country in enumerate(selected_countries, start=1):
        country_df = filtered_df[filtered_df['Country'] == country]
        row = ceil(i / n_cols)
        col = i if i <= n_cols else i % n_cols if i % n_cols != 0 else n_cols
        labor_force_employment_proportion = (
            country_df['Employment to population ratio, 15+, total (%) (modeled ILO estimate)'] *
            (country_df['Population, total'] - country_df['Population ages 0-14, total']) /
            country_df['Population, total']
        )

        fig.add_trace(
            go.Scatter(x=country_df['Year'], y=labor_force_employment_proportion,
                       name=f'Employment Ratio', legendgroup=country, hovertemplate='Year=%{x}<br>Employment Ratio=%{y}',
                       line=dict(color='red')),  # setting line color to red
            row=row, col=col
        )
        fig.add_trace(
            go.Scatter(x=country_df['Year'], y=country_df['Labor force proportion'],
                       name=f'Labor Force Proportion', legendgroup=country, hovertemplate='Year=%{x}<br>Labor Force Proportion=%{y}',
                       line=dict(color='blue')),  # setting line color to blue
            row=row, col=col
        )

    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Employment Ratio (%)", secondary_y=False)
    fig.update_yaxes(title_text="Labor Force Proportion (%)", secondary_y=True)
    fig.update_yaxes(title_text="Employment Ratio (%)", range=[
                     min_val-1, max_val+1], secondary_y=False)
    fig.update_yaxes(title_text="Labor Force Proportion (%)", range=[
                     min_val-1, max_val+1], secondary_y=True)

    fig.update_layout(
        height=400*n_rows, title_text="Comparison between Employment Ratio and Labor Force Proportion", showlegend=False)

    return fig


@app.callback(
    [Output('heatmap11', 'figure'),
     Output('heatmap12', 'figure'),
     Output('heatmap13', 'figure'),
     Output('heatmap14', 'figure'),
     Output('heatmap15', 'figure'),
     Output('heatmap16', 'figure'),
     Output('heatmap17', 'figure'),
     Output('heatmap18', 'figure'),
     Output('heatmap19', 'figure'),
     Output('heatmap20', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_heatmap(selected_countries):
    if len(selected_countries) > 10:
        return go.Figure()
    else:
        filtered_df = df_original[df_original['Country'].isin(
            selected_countries)]
        filtered_df = filtered_df[filtered_df['Year'] >= 1990]

        employment_features = [
            "A woman can get a job in the same way as a man (1=yes; 0=no)",
            "A woman can work in a job deemed dangerous in the same way as a man (1=yes; 0=no)",
            "A woman can work in an industrial job in the same way as a man (1=yes; 0=no)",
            "A woman can work in an industrial job in the same way as a man (1=yes; 0=no)",
            "Dismissal of pregnant workers is prohibited (1=yes; 0=no)",
            "A woman can travel outside her home in the same way as a man (1=yes; 0=no)",
            "A woman can travel outside the country in the same way as a man (1=yes; 0=no)",
            "A woman has the same rights to remarry as a man (1=yes; 0=no)",
            "A woman can register a business in the same way as a man (1=yes; 0=no)",
            "A woman can sign a contract in the same way as a man (1=yes; 0=no)"
        ]

        custom_titles = ["get a job in the same way as a man",
                         "work in a job deemed dangerous in the same way as a man",
                         "work in an industrial job in the same way as a man",
                         "work in an industrial job in the same way as a man",
                         "Dismissal of pregnant workers is prohibited",
                         "A woman can travel outside her home in the same way as a man",
                         "A woman can travel outside the country in the same way as a man",
                         "A woman has the same rights to remarry as a man",
                         "A woman can register a business in the same way as a man",
                         "A woman can sign a contract in the same way as a man"]

        global_min = filtered_df[employment_features].min().min()
        global_max = filtered_df[employment_features].max().max()

        figures = []

        for feature, title in zip(employment_features, custom_titles):
            heatmap_df = filtered_df.pivot(
                index='Year', columns='Country', values=feature)
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_df.values,
                x=heatmap_df.columns.values,
                y=heatmap_df.index.values,
                zmin=0,
                zmax=1,
                colorscale=[[0, 'orange'], [1, 'blue']],
                colorbar=dict(
                    tickvals=[0, 1],
                    ticktext=['No', 'Yes'],
                    ticks='outside'
                ),
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


@app.callback(
    [Output('animated-scatter-chart2', 'figure')],
    [Input('country-dropdown', 'value')]
)
def update_chart(selected_countries):
    if len(selected_countries) > 10:
        return [go.Figure()]
    else:
        filtered_df = df_original[df_original['Country'].isin(
            selected_countries)]

        print(filtered_df[['Country', 'Year', 'GDP per capita (Current US$)',
              'Women Business and the Law Index Score (scale 1-100)', 'Population ages 15-64, female']].head())

        fig3 = px.scatter(filtered_df,
                          x='GDP per capita (Current US$)',
                          y='Women Business and the Law Index Score (scale 1-100)',
                          size='Population ages 15-64, female',
                          animation_frame='Year',
                          animation_group='Country',
                          color='Country',
                          log_x=True,
                          size_max=55,
                          range_x=[100, 100000],
                          range_y=[0, 100])
        return [fig3]


@app.callback(
    Output('line-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_line_chart(selected_countries):
    if len(selected_countries) > 10:
        return go.Figure()
    else:
        filtered_df = df_original[df_original['Country'].isin(
            selected_countries)]
        fig = px.line(filtered_df, x="Year", y="Women Business and the Law Index Score (scale 1-100)", color='Country',
                      title='Women Business and the Law Index Score Over Time', range_y=[0, 100])
        return fig


if __name__ == '__main__':
    app.run_server(debug=True)
