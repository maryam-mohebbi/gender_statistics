import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the data and perform necessary transformations
df = pd.read_csv('../data/survival.csv')

# Read the data and perform necessary transformations
dff = pd.read_csv('../data/cleaned_data.csv')
new_df = dff.melt(
    id_vars=['Series Name', 'Series Code', 'Country Name', 'Country Code'],
    var_name='Year',
    value_name='Value'
)
new_df['Year'] = new_df['Year'].str.slice(0, 4).astype(int)

# Define the regions and countries
regions = {
    "Europe": ["United Kingdom", "France", "Germany", "Italy"],
    "Middle East": ["Saudi Arabia", "Iran, Islamic Rep.", "Israel", "Turkiye"],
    "Asia": ["China", "Japan", "India", "Vietnam"],
    "Africa": ["Egypt, Arab Rep.", "South Africa", "Nigeria", "Kenya"],
    "South America": ["Brazil", 'Argentina', 'Venezuela, RB', "Uruguay"],
    "North and middle America": ['United States', 'Canada', 'Mexico', 'Panama'],
}

formatted_data = pd.DataFrame()  # Empty DataFrame to store the formatted data

for region, countries in regions.items():
    region_data = new_df[new_df['Country Name'].isin(countries)]
    region_data['Region'] = region  
    formatted_data = pd.concat([formatted_data, region_data])

formatted_data.sort_values(by=['Year', 'Region', 'Country Name'], inplace=True)

# Reset the index of the formatted data
formatted_data.reset_index(drop=True, inplace=True)

# Fertility
fertility = ['Fertility rate, total (births per woman)']
fert = formatted_data[formatted_data['Series Name'].isin(fertility)]

# Define the mortality categories
mortality_categories = [
    'Mortality rate, adult, female (per 1,000 female adults)',
    'Mortality rate, adult, male (per 1,000 male adults)',
]

# Define the infant categories
infant_categories = [
    'Number of infant deaths, female',
    'Number of infant deaths, male',
]

# Define the solid colors for each category
category_colors = {
    'Mortality rate, adult, female (per 1,000 female adults)': 'rgb(31, 119, 180)',
    'Mortality rate, adult, male (per 1,000 male adults)': 'rgb(255, 127, 14)',
    'Number of infant deaths, female': 'rgb(31, 119, 180)',
    'Number of infant deaths, male': 'rgb(255, 127, 14)',
}

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    children=[
        # Birth vs Death Rate
        html.H1('Birth vs. Death Rate',
                style={'font-family': 'Arial, sans-serif','text-align': 'center','font-weight': 'bold', 'font-size':'35px', 'color': '#6082B6'}
        ),
        dcc.Graph(
            id='animated-bubble-plot',
            figure=px.scatter(df, x='Birth rate, crude (per 1,000 people)', y='Death rate, crude (per 1,000 people)',
                              animation_frame='Year', hover_name='Country Name', color='Region',
                              size='Population, total', size_max=100,
                              labels={'Birth rate, crude (per 1,000 people)': 'Birth rate, crude (per 1,000 people)',
                                      'Death rate, crude (per 1,000 people)': 'Death rate, crude (per 1,000 people)',
                                      'Population': 'Population, total'}
                             ).update_layout(
                xaxis_title='Birth rate, crude (per 1,000 people)',
                yaxis_title='Death rate, crude (per 1,000 people)',
                height=550,
                width = 1500
            )
        ),
        html.P('Figure 4: The scatter plot depicts the relationship between the Birth Rate and Death Rate per 1,000 population across various countries. '
               'It offers a visual representation of population dynamics by illustrating the number of births and deaths occurring within a given year. '
               'The position of each data point provides an indication of the relative balance between births and deaths, allowing for comparisons and '
               'insights into population trends.',
               style={'font-family': 'Arial, sans-serif', 'text-align':'left', 'color':'gray', 'font-size':'16px',
                      'padding-left': '150px', 'padding-right': '300px', 'padding-bottom':'50px'}
        ),
        html.Hr(style={'height':'10px','color':'Black','background-color':'Gray'}),

        # DropDown
        html.H4('Select a region:',style={'font-family': 'Arial, sans-serif', 'font-weight': 'bold', 'font-size':'18px', 'color': 'Black'}),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': region, 'value': region} for region in regions.keys()],
                value='Europe',
                clearable=False,
                style={'borderColor': 'Black'}
            ),

        # Fertility line plot.
        html.H1('Trends in Fertility Rate', style={'font-family': 'Arial, sans-serif','text-align': 'center','font-weight': 'bold',
                                                   'font-size':'35px', 'color': '#6082B6'}), # Fertility Rate
        dcc.Graph(id='line-plot'),
        html.P(
            'Figure 5: The line plot showcases the fertility rates across different countries. '
            'It provides insights into the number of live births occurring per 1,000 women of reproductive age (ages 15 to 49) annually.'
            'The plot allows for easy comparison and analysis of fertility patterns and trends across countries over time.',
            style={'font-family': 'Arial, sans-serif', 'text-align': 'left', 'color': 'gray', 'font-size': '16px',
                   'padding-left': '150px', 'padding-right': '300px', 'padding-bottom': '50px'}
            ),
        html.Hr(style={'height': '10px', 'color': 'Black', 'background-color': 'Gray'}),

        # Mortality stacked graph
        html.H1('Mortality Rates by Gender and Country',
                style={'font-family': 'Arial, sans-serif','text-align': 'center','font-weight': 'bold', 'font-size':'35px', 'color': '#6082B6'}
        ),
        html.Div([
            dcc.Graph(id='mortality-graph'),
        ]),
        html.P(
            'Figure 6: The stacked area graph depicts the mortality rates by gender for different countries. '
            'It enables a visual comparison of the trends and patterns in mortality rates for adult males and females over time.',
            style={'font-family': 'Arial, sans-serif', 'text-align': 'left', 'color': 'gray', 'font-size': '16px',
                   'padding-left': '150px', 'padding-right': '300px', 'padding-bottom': '50px'}
        ),
        html.Hr(style={'height': '10px', 'color': 'Black', 'background-color': 'Gray'}),

        # Infants stacked graph
        html.H1('Country-wise Infant Deaths Count: Male vs. Female',
                style={'font-family': 'Arial, sans-serif','text-align': 'center','font-weight': 'bold', 'font-size':'35px', 'color': '#6082B6'}
        ),
        html.Div([
            dcc.Graph(id='infants-graph'),
        ]),
        html.P(
            'Figure 7: The stacked area graph showcases the count of infant deaths categorized by gender for various countries. '
            'It allows for a comparative analysis of the trends and patterns in infant mortality between males and females over time.',
            style={'font-family': 'Arial, sans-serif', 'text-align': 'left', 'color': 'gray', 'font-size': '16px',
                   'padding-left': '150px', 'padding-right': '300px', 'padding-bottom': '50px'}
        ),
        html.Hr(style={'height': '10px', 'color': 'Black', 'background-color': 'Gray'}),

        # Immunization Heatmaps
        html.H1('Child Immunization: DPT and Measles',
                style={'font-family': 'Arial, sans-serif','text-align': 'center','font-weight': 'bold', 'font-size':'35px', 'color': '#6082B6'}
        ),
        dcc.Graph(id='immunization-heatmap-dpt'),
        html.P(
            'Figure 8.1: The heatmap represents the percentage of children aged 12-23 months who have received DPT (Diphtheria, Pertussis, and Tetanus) vaccination. '
            'It provides an overview of the immunization rates for these diseases across different countries and years.',
            style={'font-family': 'Arial, sans-serif', 'text-align': 'left', 'color': 'gray', 'font-size': '16px',
                   'padding-left': '150px', 'padding-right': '300px'}
        ),
        html.Br(),
        html.Br(),
        dcc.Graph(id='immunization-heatmap-measles'),
        html.P(
            'Figure 8.2: This heatmap displays the percentage of children aged 12-23 months who have received measles vaccination. '
            'It illustrates the immunization rates for measles across various countries and years, offering insights into the coverage and trends in measles vaccination.',
            style={'font-family': 'Arial, sans-serif', 'text-align': 'left', 'color': 'gray', 'font-size': '16px',
                   'padding-left': '150px', 'padding-right': '300px', 'padding-bottom': '50px'}
        ),
        html.Hr(style={'height': '10px', 'color': 'Black', 'background-color': 'Gray'}),

        # Survival Scatter Plot
        html.H1('Survival: Age 65+ (Male vs Female)',
                style={'font-family': 'Arial, sans-serif','text-align': 'center','font-weight': 'bold', 'font-size':'35px', 'color': '#6082B6'}
        ),
        dcc.Graph(
            id='animated-bubble-plot-survival',
            figure=px.scatter(df, x='Survival Rate (Male)', y='Survival Rate (Female)',
                              animation_frame='Year', hover_name='Country Name', color='Region',
                              size='Population, total', size_max=100, 
                              labels={'Survival Rate (Male)': 'Survival Rate (Male)',
                                      'Survival Rate (Female)': 'Survival Rate (Female)',
                                      'Population': 'Population, total'}
                             ).update_layout(
                xaxis_title='Survival Rate (Male)',
                yaxis_title='Survival Rate (Female)',
                height=550,
                width = 1500,
            )
        ),
        html.P(
            'Figure 9: The scatter plot compares the survival rates of males and females aged 65 and above, providing '
            'insights into the demographic dynamics of longevity. It enables a visual comparison of male and female survival '
            'rates across different countries and years.',
            style={'font-family': 'Arial, sans-serif', 'text-align': 'left', 'color': 'gray', 'font-size': '16px',
                   'padding-left': '150px', 'padding-right': '300px', 'padding-bottom': '50px'}
        ),
    ]
)

# mortality graphs____________________
@app.callback(
    Output('mortality-graph', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_mortality_graph(region):
    # Filter the data for the selected region
    region_data = formatted_data[formatted_data['Region'] == region]
    
    # Filter the data for the mortality categories
    category_data = region_data[region_data['Series Name'].isin(mortality_categories)]
    
    # Create the stacked area graph for mortality rates
    fig = px.area(category_data, x='Year', y='Value', color='Series Name', facet_col='Country Name',
                  title=f"Mortality Rates - {region}", labels={'Value': 'Mortality Rate'},
                  color_discrete_map=category_colors)  # Set the color map
    
    return fig

# infants graphs____________________
@app.callback(
    Output('infants-graph', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_infants_graph(region):
    # Filter the data for the selected region
    region_data = formatted_data[formatted_data['Region'] == region]
    
    # Filter the data for the infant categories
    category_data = region_data[region_data['Series Name'].isin(infant_categories)]
    
    # Create the stacked area graph for infants category
    fig = px.area(category_data, x='Year', y='Value', color='Series Name', facet_col='Country Name',
                  title=f"Infants Category - {region}", labels={'Value': 'Infant Indicator'},
                  color_discrete_sequence=['blue', 'red'])  # Set the color map
    
    return fig

# fertility line plot____________________
@app.callback(
    Output('line-plot', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_line_plot(region):
    # Filter the data for the selected region
    filtered_data = fert[fert['Region'] == region]

    # Create the line plot using Plotly Express
    fig = px.line(filtered_data, x='Year', y='Value', color='Country Name',
                  labels={'Year': 'Year', 'Value': 'Fertility Rate (Births per Woman)'})
    
    return fig

# Heatmaps for immunization of dpt and measles____________________
@app.callback(
    Output('immunization-heatmap-dpt', 'figure'),
    Output('immunization-heatmap-measles', 'figure'),
    Input('region-dropdown', 'value')
)
def update_heatmaps(region):
    countries = regions.get(region, [])

    # Filter the data for the selected region and countries
    newdf = dff[dff['Country Name'].isin(countries)]
    df1 = newdf[newdf['Series Name'] == 'Immunization, DPT (% of children ages 12-23 months)']
    df2 = newdf[newdf['Series Name'] == 'Immunization, measles (% of children ages 12-23 months)']

    # Create the heatmap figures
    heatmap_dpt = go.Figure(
        data=go.Heatmap(
            z=df1.iloc[:, 4:].values,
            x=df1.columns[4:],
            y=df1['Country Name'],
            colorscale='Viridis',
            colorbar=dict(title='1%-100%'),
        )
    ).update_layout(
        title='Immunization, DPT (% of children ages 12-23 months)',
        height=500,
        width=1400
    )

    heatmap_measles = go.Figure(
        data=go.Heatmap(
            z=df2.iloc[:, 4:].values,
            x=df2.columns[4:],
            y=df2['Country Name'],
            colorscale='Viridis',
            colorbar=dict(title='1%-100%'),
        )
    ).update_layout(
        title='Immunization, measles (% of children ages 12-23 months)',
        height=500,
        width=1400
    )

    return heatmap_dpt, heatmap_measles

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
