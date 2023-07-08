import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import dash
import pandas as pd


categories = {'SG.LAW.INDX': 'Women Business and the Law Index Score (1-100)',
              'SG.LAW.INDX.EN': "Women, Business and the Law: Entrepreneurship Indicator Score (1-100)",
              'SG.LAW.INDX.PY': "Women, Business and the Law: Pay Indicator Score (1-100)",
              'SG.LAW.INDX.WP':  "Women, Business and the Law: Workplace Indicator Score (1-100)",
              'SG.LAW.INDX.PE':  "Women, Business and the Law: Pension Indicator Score (1-100)",
              'SG.LAW.INDX.PR':  "Women, Business and the Law: Parenthood Indicator Score (1-100)",
              'SG.LAW.INDX.MR':  "Women, Business and the Law: Marriage Indicator Score (1-100)",
              'SG.LAW.INDX.AS':  "Women, Business and the Law: Assets Indicator Score (1-100)"
}

countries = ['Germany', 'Spain', 'United States', 'Argentina', 'China', 'India', 'Iran', 'Afghanistan']

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(
        id='category-dropdown',
        options=[{'label': i[1], 'value': i[0]} for i in categories.items()],
        value='SG.LAW.INDX'
    ),
    dcc.Dropdown(
        id='first-year-dropdown',
        options=[{'label': year, 'value': year} for year in [year for year in range(1970, 2021, 1)]],
        value='1970'
    ),
    dcc.Dropdown(
        id='second-year-dropdown',
        options=[{'label': year, 'value': year} for year in [year for year in range(1970, 2021, 1)]],
        value='2020'
    ),
    html.H1(id='chart-title', children='Two Pie Charts', style={'text-align': 'center', 'fontFamily': 'Calibri'}),
    html.Div(children=[
        dcc.Graph(id='pie-chart-1',
                  className='six columns',
                  style={'float': 'left'}),
        dcc.Graph(id='pie-chart-2',
                  className='six columns',
                  style={'float': 'right', 'margin-left': '5%', 'margin-right': '5%'})])
])


@app.callback(
    [Output('chart-title', 'children'),
     Output('pie-chart-1', 'figure'),
     Output('pie-chart-2', 'figure')],
    [Input('category-dropdown', 'value'),
     Input('first-year-dropdown', 'value'),
     Input('second-year-dropdown', 'value')]
)


def update_graph(category_code, first_year, second_year):
        category_name = categories[category_code]
        filtered_category_df = df[df['Series Code'] == category_code]

        first_year_country_values = []
        for country in countries:
            filtered_category_country_df = filtered_category_df[filtered_category_df['Country Name'] == country]
            first_year_country_value = filtered_category_country_df.loc[:, f'{first_year} [YR{first_year}]'].values[0]
            first_year_country_values.append(first_year_country_value)

        second_year_country_values = []
        for country in countries:
            filtered_category_country_df = filtered_category_df[filtered_category_df['Country Name'] == country]
            second_year_country_value = filtered_category_country_df.loc[:, f'{second_year} [YR{second_year}]'].values[0]
            second_year_country_values.append(second_year_country_value)

        first_pie_trace = go.Pie(labels=countries,
                                 values=first_year_country_values,
                                 hole=.3,
                                 textinfo='value',
                                 marker_colors=colors_pastel)
        second_pie_trace = go.Pie(labels=countries,
                                  values=second_year_country_values,
                                  hole=.3,
                                  textinfo='value',
                                  marker_colors=colors_pastel)
        height = 500
        width = 600
        updated_figure1 = {
            'data': [first_pie_trace],
            'layout': go.Layout(title={'text': '<b>' + str(first_year) + '<b>'},
                                height=height,
                                width=width
                                )
        }
        updated_figure2 = {
            'data': [second_pie_trace],
            'layout': go.Layout(title={'text': '<b>' + str(second_year) + '<b>'},
                                height=height,
                                width=width
                                )
        }
        return category_name, updated_figure1, updated_figure2

colors_antique = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
colors_pastel = ['#B6E880', '#AB63FA', '#FFA15A', '#FF6692', '#19D3F3', '#EF553B', '#FF97FF', '#636EFA', '#00CC96', '#FECB52']

df = pd.read_csv('../data/cleaned_data.csv')

if __name__ == '__main__':
    app.run_server(debug=True)

