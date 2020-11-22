import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd

url_base = "/dash/weather/sun-activeness/"


def create_layout(df):

    return html.Div(children=[
        html.H1(children='Тривалість режимів сонячної активності'),

        html.Div(
            children='''
            Графік тривалості режимів сонячної активності
        ''',
            style={"margin-bottom": "15px"}
        ),

        dcc.DatePickerRange(
            id='date-picker',
            start_date=df['date'][0],
            min_date_allowed=df['date'][0],
            end_date=df['date'][len(df) - 1],
            max_date_allowed=df['date'][len(df) - 1],
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
         dash.dependencies.Input('date-picker', 'end_date')])
    def update_output(start_date, end_date):
        dff = df.copy()
        pd.options.mode.chained_assignment = None

        dff['date_new'] = pd.to_datetime(dff['date'], errors='coerce').dt.date

        dff = dff.set_index(['date_new'])

        dff = dff.loc[pd.to_datetime(start_date):pd.to_datetime(end_date)]

        iksi = sorted(dff['ETRN'].unique())[0:len(dff['ETRN'])]
        igriki =[]
        for x in iksi:
            igriki.append(dff.loc[dff['ETRN'] == x].shape[0])

        fig = px.bar(
            zip(iksi, igriki),
            x=iksi,
            y=igriki,
            title=f"Тривалість режимів сонячної активності у місті New York з "
                  f"{pd.to_datetime(start_date).strftime('%m/%d/%Y')} по "
                  f"{pd.to_datetime(end_date).strftime('%m/%d/%Y')}"
        )
        fig.update_xaxes(title_text='Сонячна активність')
        fig.update_yaxes(title_text='Годин')
        fig.update_traces(hovertemplate='Сонячна активність %{x} тривала %{y} годин')

        return fig

    return app.server
