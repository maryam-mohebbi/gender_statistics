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
        filtered_df = df_original[df_original['Country'].isin(selected_countries)][['Year', 'Country', column_name]]
        
        scaler = StandardScaler()
        for country in selected_countries:
            filtered_df.loc[filtered_df['Country'] == country, column_name] = scaler.fit_transform(filtered_df.loc[filtered_df['Country'] == country, column_name].values.reshape(-1, 1))
        
        melted_df = pd.melt(filtered_df, id_vars=['Year', 'Country'], value_vars=[column_name],
                            var_name='Population Type', value_name='Value')
                
        fig = px.line(melted_df, x='Year', y='Value', color='Population Type', facet_col='Country', facet_col_wrap=5, 
                      title=f'Standardized {population_type.capitalize()} Population Over Time')
        
        fig.update_xaxes(tickangle=45)
        
        for i in range(len(selected_countries)):
            fig.layout.annotations[i]['text'] = selected_countries[i]
        
        fig.update_layout(showlegend=False)

                # Set custom colors
        colors = {'Population, total': 'green', 'Population, male': 'blue', 'Population, female': 'red'}
        for trace in fig.data:
            population_type_name = trace.name
            trace.line.color = colors[population_type_name]

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




if __name__ == '__main__':
    app.run_server(debug=True)
