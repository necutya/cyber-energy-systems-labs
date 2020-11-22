import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
import pandas as pd

url_base = "/dash/weather/rose/"


def create_layout(df):
    return html.Div(children=[
        html.H1(children='Троянда вітрів'),

        dcc.Dropdown(id="city",
                     options=[{"label": city, "value": city} for city in df["town"].unique()],
                     multi=False,
                     value="Київ",
                     style={"margin-bottom": "15px"},
                     ),
        dcc.Graph(
            id='temperature-graph',
            figure={},

        ),
        html.P(id="shtil",
               children=[],
               style={"text-align": "center"},)
    ])


def create_dash(server, df):
    app = dash.Dash(
        server=server,
        url_base_pathname=url_base,
    )
    app.layout = create_layout(df)

    # directions = ['Пн', 'Пн-Сх', 'Сх', 'Пд-Сх', 'Пд', 'Пд-Зх', 'Зх', 'Пн-Зх', 'С-В', ]

    @app.callback(
        [dash.dependencies.Output(component_id='temperature-graph', component_property='figure'),
         dash.dependencies.Output(component_id='shtil', component_property='children')],
        [dash.dependencies.Input('city', 'value')])
    def update_output(city):
        dff = df.copy()

        dff = dff.loc[dff['town'] == city]

        kol_shtili = dff.loc[df['FF'] == 0].shape[0]
        shtil = (kol_shtili / dff.shape[0]) * 100

        count = dff['FF'].shape[0]
        percents = []
        for viter in dff['dd'].unique():
            df2 = dff.loc[dff['dd'] == viter]
            percents.append((df2.shape[0] / (count - kol_shtili)) * 100)

        fig = px.bar_polar(
            dff,
            r=percents,
            color=percents,
            theta=dff['dd'].unique(),
            title=f"Роза вітрів у місці {city} за 2012 рік",
        )
        fig.update_traces(hovertemplate='Середня сила вітру на %{theta} у місті ' + city + ':%{r}%')
        fig.update_layout(
            polar_radialaxis_ticksuffix='%',
            font_size=16,
        )
        text = f"Відсоток штилю у місті {city}: {shtil}%"
        return fig, text

    return app.server
