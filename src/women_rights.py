import pandas as pd
import plotly.express as px
from dash import Dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from sklearn.preprocessing import StandardScaler
from plotly.subplots import make_subplots
from math import ceil


def prepare_data(file_path):
    df = pd.read_csv(file_path)

    df = df[['Series Name', 'Country Name'] +
            [col for col in df if col.startswith('19') or col.startswith('20')]]

    df = df.melt(id_vars=['Series Name', 'Country Name'],
                 var_name='Year', value_name='Value')

    df['Year'] = df['Year'].str.extract('(\d+)').astype(int)

    df = df.pivot_table(index=['Country Name', 'Year'],
                        columns='Series Name', values='Value').reset_index()

    df.columns.name = ''
    df.rename(columns={'Country Name': 'Country'}, inplace=True)

    all_countries = df['Country'].unique().tolist()

    return df, all_countries


group_features = ['Population, total',
                  'Population, female',
                  'Population, male',]

regions = {
    'Europe': ['United Kingdom', 'France', 'Germany', 'Italy', 'Spain', 'Belgium', 'Netherlands', 'Switzerland', 'Sweden', 'Poland'],
    'Middle East': ['Saudi Arabia', 'Iran, Islamic Rep.', 'Israel', 'Turkiye', 'United Arab Emirates', 'Iraq', 'Lebanon', 'Qatar', 'Jordan', 'Kuwait'],
    'Asia': ['China', 'Japan', 'India', 'Vietnam', 'Russian Federation', 'Thailand', 'Indonesia', 'Pakistan', 'Philippines', 'Malaysia'],
    'Africa': ['Egypt, Arab Rep.', 'South Africa', 'Nigeria', 'Kenya', 'Morocco', 'Ethiopia', 'Tanzania', 'Algeria', 'Ghana', 'Uganda'],
    'South America': ['Brazil', 'Argentina', 'Venezuela, RB', 'Uruguay', 'Colombia', 'Chile', 'Peru', 'Guyana', 'Suriname', 'Ecuador'],
    'North and middle America': ['United States', 'Canada', 'Mexico', 'Panama', 'Costa Rica', 'Jamaica', 'Dominican Republic'],

}

df, all_countries = prepare_data('../data/cleaned_data.csv')
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
    dcc.Graph(id='line-chart-total'),
    dcc.Graph(id='line-chart-female'),
    dcc.Graph(id='line-chart-male'),
    dcc.Graph(id='employment-ratio-chart'),
    dcc.Graph(id='employment-ratio-chart-heatmap'),
    dcc.Graph(id='employment-equality-chart'),
    dcc.Graph(id='life-equality-chart'),
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


def get_standardized_population_chart(selected_countries, population_type):
    if len(selected_countries) > 10:
        return go.Figure()
    else:
        column_name = f'Population, {population_type}'
        filtered_df = df_original[df_original['Country'].isin(
            selected_countries)][['Year', 'Country', column_name]]

        scaler = StandardScaler()
        for country in selected_countries:
            filtered_df.loc[filtered_df['Country'] == country, column_name] = scaler.fit_transform(
                filtered_df.loc[filtered_df['Country'] == country, column_name].values.reshape(-1, 1))

        melted_df = pd.melt(filtered_df, id_vars=['Year', 'Country'], value_vars=[column_name],
                            var_name='Population Type', value_name='Value')

        fig = px.line(melted_df, x='Year', y='Value', color='Population Type', facet_col='Country', facet_col_wrap=5,
                      title=f'Standardized {population_type.capitalize()} Population Over Time')

        fig.update_xaxes(tickangle=45)

        num_rows = -(-len(selected_countries) // 5)

        for i in range(len(selected_countries)):
            fig.layout.annotations[i]['text'] = selected_countries[i]

            if (i // 5) + 1 < num_rows:
                fig.layout[f'xaxis{i+1}'].title.text = ''

        colors = {'Population, total': 'green',
                  'Population, male': 'blue', 'Population, female': 'red'}
        for trace in fig.data:
            population_type_name = trace.name
            trace.line.color = colors[population_type_name]

        for axis in fig.layout:
            if 'yaxis' in axis:
                fig.layout[axis]['title'] = ''

        fig.add_annotation(
            dict(
                x=-0.04,
                y=0.5,
                showarrow=False,
                text='Standardized Population Value',
                textangle=-90,
                xref='paper',
                yref='paper'
            )
        )

        fig.add_annotation(
            dict(
                x=0.5,
                y=-0.3,
                showarrow=False,
                text='Year',
                xref='paper',
                yref='paper'
            )
        )

        fig.update_layout(showlegend=False)

        return fig


@app.callback(
    Output('line-chart-total', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_total_population_chart(selected_countries):
    return get_standardized_population_chart(selected_countries, 'total')


@app.callback(
    Output('line-chart-female', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_female_population_chart(selected_countries):
    return get_standardized_population_chart(selected_countries, 'female')


@app.callback(
    Output('line-chart-male', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_male_population_chart(selected_countries):
    return get_standardized_population_chart(selected_countries, 'male')


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
    n_cols = min(5, n)
    n_rows = ceil(n / n_cols)

    fig = make_subplots(rows=n_rows, cols=n_cols,
                        subplot_titles=selected_countries, vertical_spacing=0.1)

    min_val_list = []
    max_val_list = []

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
                       name=f'Employment Ratio', legendgroup=country, hovertemplate='Year=%{x}<br>Employment Ratio=%{y}',
                       line=dict(color='red')),
            row=row, col=col
        )
        fig.add_trace(
            go.Scatter(x=country_df['Year'], y=country_df['Labor force proportion'],
                       name=f'Labor Force Proportion', legendgroup=country, hovertemplate='Year=%{x}<br>Labor Force Proportion=%{y}',
                       line=dict(color='blue')),
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
        height=420*n_rows, title_text='Comparison between Employment Ratio and Labor Force Proportion', showlegend=False)

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
    Output('employment-ratio-chart-heatmap', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_employment_ratio_heatmap(selected_countries):
    if len(selected_countries) > 10:
        return go.Figure()
    else:
        filtered_df = df_original[df_original['Country'].isin(
            selected_countries)]
        filtered_df = filtered_df[filtered_df['Year'] > 1990]

        employment_features = [
            'Employment to population ratio, 15+, female (%) (modeled ILO estimate)',
            'Employment to population ratio, 15+, male (%) (modeled ILO estimate)',
            'Employment to population ratio, 15+, total (%) (modeled ILO estimate)'
        ]

        global_min = filtered_df[employment_features].min().min()
        global_max = filtered_df[employment_features].max().max()

        custom_titles = ['Female Employment Ratio',
                         'Male Employment Ratio', 'Total Employment Ratio']

        n = len(employment_features)
        n_cols = min(5, n)
        n_rows = ceil(n / n_cols)

        fig = make_subplots(rows=n_rows, cols=n_cols,
                            subplot_titles=custom_titles, vertical_spacing=0.1)

        for idx, (feature, title) in enumerate(zip(employment_features, custom_titles)):
            heatmap_df = filtered_df.pivot(
                index='Year', columns='Country', values=feature)

            row = ceil((idx+1) / n_cols)
            col = (idx+1) if (idx+1) <= n_cols else (idx +
                                                     1) % n_cols if (idx+1) % n_cols != 0 else n_cols

            fig.add_trace(
                go.Heatmap(
                    z=heatmap_df.values,
                    x=heatmap_df.columns.values,
                    y=heatmap_df.index.values,
                    zmin=global_min,
                    zmax=global_max,
                    hoverongaps=False,
                    name=title,
                ),
                row=row, col=col
            )

        fig.update_layout(title_text='Employment Ratio Comparison by Genders')
        return fig


employment_features = [
    'A woman can get a job in the same way as a man (1=yes; 0=no)',
    'A woman can work at night in the same way as a man (1=yes; 0=no)',
    'A woman can work in a job deemed dangerous in the same way as a man (1=yes; 0=no)',
    'A woman can work in an industrial job in the same way as a man (1=yes; 0=no)',
    'Dismissal of pregnant workers is prohibited (1=yes; 0=no)',
    'Law mandates equal remuneration for females and males for work of equal value (1=yes; 0=no)',
    'There is paid parental leave (1=yes; 0=no)',
    'Paid leave is available to fathers (1=yes; 0=no)',
    'Paid leave of at least 14 weeks available to mothers (1=yes; 0=no)',
    'The age at which men and women can retire with full pension benefits is the same (1=yes; 0=no)',
    'The age at which men and women can retire with partial pension benefits is the same (1=yes; 0=no)',
    'The government administers 100% of maternity leave benefits (1=yes; 0=no)',
    'The law prohibits discrimination in employment based on gender (1=yes; 0=no)',
    'The law provides for the valuation of nonmonetary contributions (1=yes; 0=no)',
    'The mandatory retirement age for men and women is the same (1=yes; 0=no)',
    'There are periods of absence due to childcare accounted for in pension benefits (1=yes; 0=no)',
    'Criminal penalties or civil remedies exist for sexual harassment in employment (1=yes; 0=no)',
    'There is legislation on sexual harassment in employment (1=yes; 0=no)'
]

life_features = [
    'A woman can open a bank account in the same way as a man (1=yes; 0=no)',
    'Male and female surviving spouses have equal rights to inherit assets (1=yes; 0=no)',
    'Men and women have equal ownership rights to immovable property (1=yes; 0=no)',
    'The law grants spouses equal administrative authority over assets during marriage (1=yes; 0=no)',
    'The law prohibits discrimination in access to credit based on gender (1=yes; 0=no)',
    'A woman can apply for a passport in the same way as a man (1=yes; 0=no)',
    'A woman can be head of household in the same way as a man (1=yes; 0=no)',
    'A woman can choose where to live in the same way as a man (1=yes; 0=no)',
    'A woman can obtain a judgment of divorce in the same way as a man (1=yes; 0=no)',
    'A woman can travel outside her home in the same way as a man (1=yes; 0=no)',
    'A woman can travel outside the country in the same way as a man (1=yes; 0=no)',
    'A woman has the same rights to remarry as a man (1=yes; 0=no)',
    'The law is free of legal provisions that require a married woman to obey her husband (1=yes; 0=no)',
    'There is legislation specifically addressing domestic violence (1=yes; 0=no)',
    'A woman can register a business in the same way as a man (1=yes; 0=no)',
    'A woman can sign a contract in the same way as a man (1=yes; 0=no)'
]


# Function to calculate average score
def calculate_average_score(df, selected_countries, features):
    df_selected = df[df['Country'].isin(selected_countries)]

    for feature in features:
        df_selected[feature] = df_selected[feature].interpolate()

    df_selected['Average Score'] = df_selected[features].mean(axis=1)
    df_selected = df_selected[['Country', 'Year', 'Average Score']]

    return df_selected


@app.callback(
    Output('employment-equality-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_employment_equality_chart(selected_countries):
    df_score = calculate_average_score(
        df, selected_countries, employment_features)

    heatmap_data = df_score.pivot(
        index='Country', columns='Year', values='Average Score')

    fig = px.imshow(heatmap_data,
                    labels=dict(x='Year', y='Country', color='Average Score'),
                    title='Employment Equality Score Over Time',
                    color_continuous_scale='Viridis')

    fig.update_xaxes(nticks=len(heatmap_data.columns.unique()))

    return fig


@app.callback(
    Output('life-equality-chart', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_life_equality_chart(selected_countries):
    df_score = calculate_average_score(df, selected_countries, life_features)

    heatmap_data = df_score.pivot(
        index='Country', columns='Year', values='Average Score')

    fig = px.imshow(heatmap_data,
                    labels=dict(x='Year', y='Country', color='Average Score'),
                    title='Life Equality Score Over Time',
                    color_continuous_scale='Viridis')

    fig.update_xaxes(nticks=len(heatmap_data.columns.unique()))

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
