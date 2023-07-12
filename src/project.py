import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px


# Read the data and perform necessary transformations
df = pd.read_csv('../data/survival.csv')

# Read the data and perform necessary transformations
df2 = pd.read_csv('../data/cleaned_data.csv')
new_df = df2.melt(
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

# sereis name

mortality_series = [
    'Mortality rate, adult, female (per 1,000 female adults)',
    'Mortality rate, adult, male (per 1,000 male adults)',
]
infants = [ 'Number of infant deaths, female',
    'Number of infant deaths, male',
    'Number of infant deaths']

fertility =['Fertility rate, total (births per woman)']

immuni =[ 'Immunization, measles (% of children ages 12-23 months)',
    'Immunization, DPT (% of children ages 12-23 months)',]

# mortality____________________________________________________________________
mortality = formatted_data[formatted_data['Series Name'].isin(mortality_series)]

# Create a dictionary to map full names to abbreviated names
abbreviations = {
    'Mortality rate, adult, female (per 1,000 female adults)': 'Adult Female (per 1000)',
    'Mortality rate, adult, male (per 1,000 male adults)': 'Adult Male (per 1000)',
}

mor_plots = []

for region, countries in regions.items():
    region_data = mortality[mortality['Country Name'].isin(countries)]

    fig = px.area(region_data, x='Year', y='Value', color='Series Name', facet_col='Country Name',
                  title=f"Mortality Rates - {region}", labels={'Value': 'Mortality Rate'})

    # Abbreviate the legend labels
    for trace in fig.data:
        trace.name = abbreviations[trace.name]

    mor_plots.append(dcc.Graph(figure=fig))

# Infants____________________________________________________________________
infant = formatted_data[formatted_data['Series Name'].isin(infants)]

fert = formatted_data[formatted_data['Series Name'].isin(fertility)]

# Imunnity____________________________________________________________________
immunity = pd.read_csv('../data/cleaned_data.csv')
series = ['Immunization, DPT (% of children ages 12-23 months)', 'Immunization, measles (% of children ages 12-23 months)']
countries = ["United Kingdom", "France", "Germany", "Italy", "Spain", 
            "Saudi Arabia", "Iran, Islamic Rep.", "Israel", "Turkiye", 
            "China", "Japan", "India", "Vietnam", 
            "Egypt, Arab Rep.", "South Africa", "Nigeria","Kenya",
            "Brazil", 'Argentina', 'Venezuela, RB', "Uruguay",
            'United States', 'Canada', 'Mexico', 'Panama', 
]
newdf = immunity[immunity['Series Name'].isin(series)]
newdf = newdf[newdf['Country Name'].isin(countries)]
df1 = newdf[newdf['Series Name']=='Immunization, DPT (% of children ages 12-23 months)']
df2 = newdf[newdf['Series Name']=='Immunization, measles (% of children ages 12-23 months)']

# Fertiliy___________________________________________________________________
fert = formatted_data[formatted_data['Series Name'].isin(fertility)]

# Create separate plots for each region and country


in_plots = []

for region, countries in regions.items():
    region_data = infant[infant['Country Name'].isin(countries)]

    fig = px.area(region_data, x='Year', y='Value', color='Series Name', facet_col='Country Name',
                  title=f"Infants Deaths - {region}", labels={'Value': 'Infants Death count'})

    in_plots.append(dcc.Graph(figure=fig))

# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    children=[
        html.H1('Scatter plot: Birth Vs Death Rate per 1000 people'), # birth vs death
        html.H4('Birth Rate: indicates the number of birth occurring during the year, per 1,000 population estimated at midyear'),
        html.H4('Death Rate: indicates the number of deaths occurring during the year, per 1,000 population estimated at midyear'),
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
                height = 700,
            )
        ),

        html.Br(),
        html.H1('Fertility Rate Line Plot'), # fertility plots
        html.H4('Fertility rate: number of live births per 1,000 women of reproductive age (ages 15 to 49 years) per year'),
        dcc.RadioItems(
            id='region-radio',
            options=[{'label': region, 'value': region} for region in formatted_data['Region'].unique()],
            value='Europe',
            labelStyle={'display': 'inline-block'}
        ),
        dcc.Graph(id='line-plot'),

        html.Br(),
        html.H1('Mortality Rates Stacked area charts'),
        html.H4('Mortality Rate: units of deaths per 1,000 individuals per year'),
        html.H4('Adult male Mortality Rate: units of deaths per 1,000 adult male per year'),
        html.H4('Adult female Mortality Rate: units of deaths per 1,000 adult female per year'),
        html.Div(mor_plots), # mortality plots
        html.Br(),
        html.H1('Infants Death Stacked Area charts'), # infants death plots
        html.H4('Infants Death: total no of infants death'),
        html.H4('Infants Death in male: total no of infants death in male'),
        html.H4('Infants Death in female: total no of infants death in female'),
        html.Div(in_plots),
        html.H1('Immunization Heatmaps'), # immunization heat maps
        html.H4('DPT vaccine: protects children and adults against diphtheria (D), pertussis (P, also known as whooping cough) and tetanus (T)'),
        html.H4('measures in percentage'),
        dcc.Graph(
            id='immunization-heatmap',
            figure=px.imshow(
                df1.iloc[:, 4:].values,
                labels=dict(x='Year', y='Country Name', color='%'),
                x=df1.columns[4:],
                y=df1['Country Name'],
                title='Immunization, DPT (% of children ages 12-23 months)',
                color_continuous_scale='Viridis',
            ).update_layout(
                height=1000,
                width=1500
            )
        ),
        html.H4('Measles: a highly contagious, serious airborne disease caused by a virus that can lead to severe complications and death.'),
        html.H4('measures in percentage'),
        dcc.Graph(
                id='immunization-heatmap',
                figure=px.imshow(
                    df2.iloc[:, 4:].values,
                    labels=dict(x='Year', y='Country Name', color='%'),
                    x=df2.columns[4:],
                    y=df2['Country Name'],
                    title='Immunization, measles (% of children ages 12-23 months)',
                    color_continuous_scale='Viridis',
                ).update_layout(
                    height=1000,
                    width=1500
                )
        ),
        html.Br(),
        html.H1('Scatter plot: Survival to age 65, (% of cohort)'), # survival sactter plot
        html.H4('Survival to age 65, in male and female, measures in percentage'),
        dcc.Graph(
            id='animated-bubble-plot',
            figure=px.scatter(df, x='Survival Rate (Male)', y='Survival Rate (Female)',
                              animation_frame='Year', hover_name='Country Name', color='Region',
                              size='Population, total', size_max=100, 
                              labels={'Survival Rate (Male)': 'Survival Rate (Male)',
                                      'Survival Rate (Female)': 'Survival Rate (Female)',
                                      'Population': 'Population, total'}
                             ).update_layout(
                title='Survival Rates: Male vs Female',
                xaxis_title='Survival Rate (Male)',
                yaxis_title='Survival Rate (Female)',
                height = 700
            )
        )
    ]
)

@app.callback(
    Output('line-plot', 'figure'),
    [Input('region-radio', 'value')]
)

def update_line_plot(region):
    # Filter the data for the selected region
    filtered_data = fert[fert['Region'] == region]

    # Create the line plot using Plotly Express
    fig = px.line(filtered_data, x='Year', y='Value', color='Country Name', labels={'Year': 'Year', 'Value': 'Fertility rate, total (births per woman)'})

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
