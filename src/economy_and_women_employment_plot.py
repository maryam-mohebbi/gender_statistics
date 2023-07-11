import plotly.graph_objects as go
from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import dash
import pandas as pd
import numpy as np


def binary_categories_bar_creation(filtered_df, category_code, year_range, number_of_country, country):
    binary_series_df = filtered_df[filtered_df['Series Code'] == category_code]
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
    series_df = filtered_df[filtered_df['Series Code'] == category_code]
    x_values = series_df.loc[:,
               f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns
    x_values = [x[0:4] for x in x_values]
    y_values = series_df.loc[:, f'{year_range[0]} [YR{year_range[0]}]':
                                      f'{year_range[1]} [YR{year_range[1]}]'].values[0]
    y_values_fixed = []
    no_values_indexes = []
    # existed_value =
    for idx, y_value in enumerate(y_values):
        if idx == 0 or np.isnan(y_value) == False:
            existed_value = y_value
            y_values_fixed.append(existed_value)
        elif not y_value and y_value != 0:
            y_values_fixed.append(existed_value)
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
    return trace


def create_return_for_category(data, x_values, category_code, height, width):
    return {
        'data': data,
        'layout': go.Layout(
            title=binary_series_data[category_code],
            xaxis=dict(title='Year',
                       tickangle=0,
                       showgrid=True,
                       range=[1970, 2021],
                       tickvals=[i for i in range(int(x_values[0]), int(x_values[-1]), 5)]),
            yaxis2=dict(title = 'Answer',
                        overlaying='y',
                        tickangle=-90,
                        range=[0, 2],
                        showgrid=True,
                        tickvals=[1, 2],
                        ticktext=['no', 'yes']
                        ),
            height=height,
            width=width,
            hovermode='closest'
        )
    }

def create_return_for_hist_category(data, x_values, category_code, height, width):
    if category_code == 'SG.LAW.INDX.EN':
        ytitle = 'Indicator'
        yrange = [-5, 140]
        ytickvals = [0, 50, 100]
        yticktext = ['0', '50', '100']
    elif category_code == 'SE.TER.ENRR.FE':
        ytitle = '% gross'
        yrange = [-5, 140]
        ytickvals = [0, 50, 100]
        yticktext = ['0', '50', '100']
    # elif category_code == 'SL.EMP.MPYR.FE.ZS':
    #     ytitle = '% of female employment'
    #     yrange = [0, 4]
    #     ytickvals = [0, 2, 4]
    #     yticktext = ['0', '2', '4']
    return {
        'data': data,
        'layout': go.Layout(
            height=height,
            width=width,
            title=binary_series_data[category_code],
            xaxis={'title': 'Year'},
            yaxis=dict(title=ytitle,
                       showgrid=False,
                       range=yrange,
                       tickvals=ytickvals,
                       ticktext=yticktext
                       ),
            hovermode='closest',
        )
    }


df = pd.read_csv('../data/cleaned_data.csv')

countries_groups = ['Germany, United Kingdom, France, Spain',
        'United States, Canada, Mexico',
        'Brazil, Argentina, Colombia',
        'China, India, Afghanistan, Iran',
        'Cameroon, Egypt, Kenya, Nigeria'
]

# Define numerical and binary series
series_data = {
    'NY.GDP.MKTP.CD': 'GDP (current US$)'
}

binary_series_data = {'SG.GET.JOBS.EQ': 'A woman can get a job in the same way as a man',
                              'SG.IND.WORK.EQ': 'A woman can work in an industrial job in the same way as a man',
                              'SG.LAW.NODC.HR': 'The law prohibits discrimination in employment based on gender',
                              'SE.TER.ENRR.FE': 'School enrollment, tertiary, female (% gross)',
                              'SG.LAW.INDX.EN': 'Women, Business and the Law: Entrepreneurship Indicator Score (scale 1-100)',
                              # 'SL.EMP.MPYR.FE.ZS': 'Employers, female (% of female employment) (modeled ILO estimate)',
                              'SG.CNT.SIGN.EQ': 'A woman can sign a contract in the same way as a man',
                              }

app = dash.Dash(__name__)
app.layout = html.Div([
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': i, 'value': i} for i in countries_groups],
        value = 'Germany, United Kingdom, France, Spain'
    ),
    dcc.RangeSlider(
        id='year-slider',
        min=1970,
        max=2021,
        step=1,
        value=[1970, 2021],
        marks={i: str(i) for i in range(1960, 2023, 2)}
    ),
    dcc.Graph(id='indicator-graph'),
    dcc.Graph(id='sg_get_jobs_eq_binary-indicator-graph'),
    dcc.Graph(id='sg_get_work_eq_binary-indicator-graph'),
    dcc.Graph(id='sg_law_nodc_hr_binary-indicator-graph'),
    dcc.Graph(id='se_ter_enrr_fe_binary-indicator-graph'),
    dcc.Graph(id='sg_law_indx_en_binary-indicator-graph'),
    # dcc.Graph(id='sl_emp_mpyr_fe_zs_binary-indicator-graph'),
    dcc.Graph(id='sg_cnt_sign_eq_binary-indicator-graph')
])

country_colors = {0: '#fed98e',
          1: '#fe9929',
          2: '#d95f0e',
          3: '#993404'}

@app.callback(
    [Output('indicator-graph', 'figure'),
     Output('sg_get_jobs_eq_binary-indicator-graph', 'figure'),
     Output('sg_get_work_eq_binary-indicator-graph', 'figure'),
     Output('sg_law_nodc_hr_binary-indicator-graph', 'figure'),
     Output('se_ter_enrr_fe_binary-indicator-graph', 'figure'),
     Output('sg_law_indx_en_binary-indicator-graph', 'figure'),
     # Output('sl_emp_mpyr_fe_zs_binary-indicator-graph', 'figure'),
     Output('sg_cnt_sign_eq_binary-indicator-graph', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)


def update_graph(country_group, year_range):
    country_group_set = country_group.split(', ')
    traces = []
    sg_get_jobs_eq_traces = []
    sg_get_work_eq_traces = []
    sg_law_nodc_hr_traces = []
    sg_sec_enrr_fe_traces = []
    sg_law_indx_en_traces = []
    sg_cnt_sign_eq_traces = []
    # sl_emp_mpyr_fe_zs_traces = []
    y_scatter_max = []

    for number_of_country, country in enumerate(country_group_set):
        filtered_df = df[df['Country Name'] == country]
        first_series_df = filtered_df[filtered_df['Series Code'] == 'NY.GDP.MKTP.CD']

        x_values = first_series_df.loc[:,
                                 f'{year_range[0]} [YR{year_range[0]}]':f'{year_range[1]} [YR{year_range[1]}]'].columns
        x_values = [x[0:4] for x in x_values]
        y_values = first_series_df.loc[:, f'{year_range[0]} [YR{year_range[0]}]':
                                 f'{year_range[1]} [YR{year_range[1]}]'].values[0]
        y_values_fixed = []
        for idx, y_value in enumerate(y_values):
            if idx == 0 or np.isnan(y_value) == False:
                existed_value = y_value
                y_values_fixed.append(existed_value)
            elif not y_value and y_value != 0:
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

        sg_get_jobs_eq_traces.append(binary_categories_bar_creation(filtered_df, 'SG.GET.JOBS.EQ', year_range, number_of_country, country))
        sg_get_work_eq_traces.append(binary_categories_bar_creation(filtered_df, 'SG.IND.WORK.EQ', year_range, number_of_country, country))
        sg_law_nodc_hr_traces.append(binary_categories_bar_creation(filtered_df, 'SG.LAW.NODC.HR', year_range, number_of_country, country))
        sg_cnt_sign_eq_traces.append(binary_categories_bar_creation(filtered_df, 'SG.CNT.SIGN.EQ', year_range, number_of_country, country))
        sg_sec_enrr_fe_traces.append(binary_categories_hist_creation(filtered_df, 'SE.TER.ENRR.FE', year_range, number_of_country, country))
        sg_law_indx_en_traces.append(binary_categories_hist_creation(filtered_df, 'SG.LAW.INDX.EN', year_range, number_of_country, country))
        # sl_emp_mpyr_fe_zs_traces.append(binary_categories_hist_creation(filtered_df, 'SL.EMP.MPYR.FE.ZS', year_range, number_of_country, country))

    if country_group != 'Cameroon, Egypt, Kenya, Nigeria':
        shift = int(round(int(max(y_scatter_max)) * 0.25, -12))
        positive_tickvals = [i for i in range(0, int(max(y_scatter_max)), shift)]
        max_range = max(y_scatter_max) + 1000000000000
        min_range = -max(y_scatter_max) * 0.4
    else:
        shift = int(round(int(max(y_scatter_max)) * 0.33, -10))
        positive_tickvals = [i for i in range(0, int(max(y_scatter_max)), shift)]
        max_range = max(y_scatter_max) + 10000000000
        min_range = -max(y_scatter_max) * 0.4

    height_main = 450
    width_main = 900
    width_subplots = 900
    height_subplots = 275
    return {
               'data': traces,
               'layout': go.Layout(
                   height=height_main,
                   width=width_main,
                   title='<b>Prosperity of the economy depends on the participation of women<b>',
                   xaxis={'title': 'Year'},
                   yaxis=dict(title='GDP (current US$)',
                              showgrid=False,
                              range=[min_range, max_range],
                              tickvals=positive_tickvals,
                              ),
                   hovermode='closest',
               )
           }, create_return_for_category(sg_get_jobs_eq_traces, x_values, 'SG.GET.JOBS.EQ', height_subplots, width_subplots),\
        create_return_for_category(sg_get_work_eq_traces, x_values, 'SG.IND.WORK.EQ', height_subplots, width_subplots),\
        create_return_for_category(sg_law_nodc_hr_traces, x_values, 'SG.LAW.NODC.HR', height_subplots, width_subplots),\
        create_return_for_hist_category(sg_sec_enrr_fe_traces, x_values, 'SE.TER.ENRR.FE', height_subplots, width_subplots),\
        create_return_for_hist_category(sg_law_indx_en_traces, x_values, 'SG.LAW.INDX.EN', height_subplots, width_subplots),\
        create_return_for_category(sg_cnt_sign_eq_traces, x_values, 'SG.CNT.SIGN.EQ', height_subplots, width_subplots)
        # create_return_for_hist_category(sl_emp_mpyr_fe_zs_traces, x_values, 'SL.EMP.MPYR.FE.ZS', height_subplots, width_subplots)


if __name__ == '__main__':
    app.run_server(debug=True)