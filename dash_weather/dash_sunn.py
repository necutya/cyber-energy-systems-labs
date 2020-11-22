import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd

url_base = "/dash/weather/sun/"


def create_layout(df):

    return html.Div(children=[
        html.H1(children='Інтенсивність сонячної інсоляції'),

        html.Div(
            children='''
            Графік інтенсивності сонячної інсоляції
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

        intens = [dff['ETRN'][i] for i in range(0, dff.shape[0])]

        fig = px.bar(
            dff,
            x="date",
            y=intens,
            hover_data={"date": "%d.%m.%Y %H:%m"},
            title=f"Інтенсивність сонячної інсоляції у місті New York з "
                  f"{pd.to_datetime(start_date).strftime('%m/%d/%Y')} по "
                  f"{pd.to_datetime(end_date).strftime('%m/%d/%Y')}"
        )
        fig.update_xaxes(title_text='Дата', tickformat="%d.%m.%Y %H:%m", tick0=dff["date"][0], dtick=30*86400000)
        fig.update_yaxes(title_text='Інтенсивніть (Вт/м2)')
        fig.update_traces(hovertemplate='На %{x} інтенсивність сягала %{y} (Вт/м2)')

        return fig

    return app.server
