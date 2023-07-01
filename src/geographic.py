from dash.dependencies import Input, Output
from dash import html
from dash import dcc
import dash
import pandas as pd
import plotly.express as px
from io import StringIO


df = pd.read_csv('../data/cleaned_data.csv', quotechar='"')

df_melt = df.melt(id_vars=['Series Name', 'Series Code', 'Country Name', 'Country Code'],
                  var_name='Year',
                  value_name='Value')

df_melt['Year'] = df_melt['Year'].apply(lambda x: int(x[0:4]))


app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='series_dropdown',
        options=[{'label': i, 'value': i}
                 for i in df_melt['Series Name'].unique()],
        value=df_melt['Series Name'].unique()[0]
    ),
    dcc.Graph(id='choropleth')
])


@app.callback(
    Output('choropleth', 'figure'),
    Input('series_dropdown', 'value')
)
def update_graph(selected_series):
    filtered_df = df_melt[df_melt['Series Name'] == selected_series]

    fig = px.choropleth(filtered_df,
                        locations="Country Name",
                        locationmode='country names',
                        color="Value",
                        hover_name="Country Name",
                        animation_frame="Year",
                        projection="natural earth",
                        title=selected_series,
                        color_continuous_scale=px.colors.sequential.Plasma,
                        height=600
                        )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
