import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd

url_base = "/dash/weather/temperature-mode/"


def create_layout(df):
    return html.Div(children=[
        html.H1(children='Тривалість температурних режимів'),

        html.Div(
            children='''
            Графік тривалість температурних режимів.
        ''',
            style={"margin-bottom": "15px"}
        ),

        dcc.Dropdown(id="city",
                     options=[{"label": city, "value": city} for city in df["town"].unique()],
                     multi=False,
                     value="Київ",
                     style={"margin-bottom": "15px"},
                     ),

        dcc.DatePickerRange(
            id='date-picker',
            start_date=df["dtime"][0],
            min_date_allowed=df["dtime"][0],
            end_date=df["dtime"][len(df) - 1],
            max_date_allowed=df["dtime"][len(df) - 1],
            display_format="DD:MM:YYYY",
        ),
        dcc.Graph(
            id='temperature-graph',
            figure={}
        ),
    ])


def create_dash(server, df):
    app = dash.Dash(
        server=server,
        url_base_pathname=url_base,
    )
    app.layout = create_layout(df)

    @app.callback(
        dash.dependencies.Output(component_id='temperature-graph', component_property='figure'),
        [dash.dependencies.Input('date-picker', 'start_date'),
         dash.dependencies.Input('date-picker', 'end_date'),
         dash.dependencies.Input('city', 'value')])
    def update_output(start_date, end_date, city):
        dff = df.copy()

        dff = dff.loc[dff['town'] == city]

        dff['date'] = pd.to_datetime(dff['dtime'], errors='coerce').dt.date

        dff = dff.set_index(['date'])
        dff = dff.loc[pd.to_datetime(start_date):pd.to_datetime(end_date)]

        hours_amount = [len(dff.loc[dff['T'] == i]) * 0.5 for i in dff['T'].unique()]

        fig = px.bar(
            dff,
            x=dff['T'].unique(),
            y=hours_amount,
            text=hours_amount,
            title=f" Графік тривалості температурних режимів з "
                  f"{pd.to_datetime(start_date).strftime('%m/%d/%Y')} по "
                  f"{pd.to_datetime(end_date).strftime('%m/%d/%Y')}"
        )
        fig.update_xaxes(title_text='Температура у градусах по Цельсію(°С)')
        fig.update_yaxes(title_text='Кількість годин')
        fig.update_traces(hovertemplate='Градус: %{x} °С <br>Кількість годин: %{y}')

        return fig

    return app.server
