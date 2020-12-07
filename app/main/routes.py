from flask import render_template, redirect, Blueprint, request, session, flash, url_for
from variables import *
from dash_weather import (
    dash_weather,
    dash_weather_mode,
    dash_rose,
    dash_wind_durations,
    dash_sunn,
    dash_sunn_activeness
)
from thermal_characteristics.calculations import calc_heat_loss_capacity
from thermal_characteristics.forms import ThermalFrom
from thermal_characteristics import utils

main = Blueprint('main', __name__)


@main.route('/', methods=["GET", "POST"])
@main.route('/home', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        if not start_date or not end_date:
            flash("Усі поля дати повинні бути обов'язково введені", "error")
        elif start_date > end_date:
            flash("Дата початку не можу бути быльше ніж дата завершення", "error")
        else:
            user_inputs = {
                'city': request.form.get("city"),
                'start_date': request.form.get("start_date"),
                'end_date': request.form.get("end_date"),
            }
            session["main_inputs"] = user_inputs
            flash("Вхідні дані збережені", "success")
    return render_template("home.html", cities=CITIES, start_date=START_DATE.strftime("%Y-%m-%dT%H:%M:%S%Z"),
                           end_date=END_DATE.strftime("%Y-%m-%dT%H:%M:%S%Z"))


@main.route('/weather')
def weather():
    return render_template(
        "weather.html",
        dash_weather_url=dash_weather.url_base,
        dash_weather_mode_url=dash_weather_mode.url_base,
        dash_rose_url=dash_rose.url_base,
        dash_wind_url=dash_wind_durations.url_base,
        dash_sunn_url=dash_sunn.url_base,
        dash_sunn_activeness_url=dash_sunn_activeness.url_base,
    )


@main.route('/thermal-characteristics-inputs', methods=["GET", "POST"])
def thermal_inputs():
    form = ThermalFrom()
    if request.method == "POST":
        if form.validate_on_submit():
            if not form.t_heating.data and not form.p_of_heater.data:
                flash("Необхідно заповнити одне з наступних полів", "error")
            elif form.t_heating.data and form.p_of_heater.data:
                flash("Дозволено лише заповнити одне з наступних полів", "error")
            else:
                data = {
                    'q_tepl': form.q_tepl.data,
                    's': form.s.data,
                    'n_people': form.n_people.data,
                    'T_inWater': form.T_inWater.data,
                    'T_endBak': form.T_endBak.data,
                    'T_shower': form.T_shower.data,
                    'Q_shower_Normal': form.Q_shower_Normal.data,
                    'N_Shower': form.N_Shower.data,
                    'T_Bath': form.T_Bath.data,
                    'Q_bath_Normal': form.Q_bath_Normal.data,
                    'N_Bath': form.N_Bath.data,
                    'T_Count_In': form.T_Count_In.data,
                    'prices': {
                        'tarif_heat_energy': form.tarif_heat_energy.data,
                        'price_of_gas': form.price_of_gas.data,
                        'price_of_coal': form.price_of_coal.data,
                        'tarif_electricity_energy': form.tarif_electricity_energy.data,
                        'price_of_wood': form.price_of_wood.data,
                        'price_of_pelet': form.price_of_pelet.data,
                    }
                }
                if form.t_heating.data:
                    data.update(dict(t_heating=form.t_heating.data))
                else:
                    data.update(dict(p_of_heater=form.p_of_heater.data))
                session["thermal_inputs"] = data
                return redirect(url_for("main.thermal_results"))
    return render_template("thermal-inputs.html", form=form)


@main.route('/thermal-characteristics')
def thermal_results():
    data = session.get('thermal_inputs')
    q_hot_water, heater_time, heater_power = utils.make_thermal_calculations(data=data)

    x1 = int(OUTSIDE_TEMPERATURES[session.get('main_inputs')['city']])
    y1 = float(data['q_tepl'] * data['s'])
    x2 = int(data['T_Count_In'])
    y2 = 0

    k = (y2 - y1) / (x2 - x1)
    b = y2 - (y2 - y1) / (x2 - x1) * x2
    x = []
    y = []
    for itr in range(x1, x2 + 1):
        x.append(itr)
        y.append(round(k * itr + b, 3))

    plot_line_data = {
        'labels': x,
        'data': y,
        'k': k,
        'b': b,
    }

    dff = DF.copy()
    dff = dff[dff['town'] == session.get('main_inputs')['city']]
    dff = dff[(session.get('main_inputs')['start_date'] < dff['dtime']) & (
                dff['dtime'] < session.get('main_inputs')['end_date'])]
    all_temp = dff["T"].value_counts()
    all_temp = all_temp.to_dict()
    w_tep_i = 0
    for value in all_temp:
        w_tep_i += (k * value + b) * all_temp[value]
    w_tep_i /= 1000

    # RETARD CALCULATIONS
    heating_types_prices = []
    heating_types_prices.append(data['prices']['price_of_gas'] * w_tep_i * 0.1075)
    heating_types_prices.append(data['prices']['price_of_coal'] * w_tep_i / 1000 * 0.1792)
    heating_types_prices.append(data['prices']['tarif_electricity_energy'] * w_tep_i * 1.01)
    heating_types_prices.append(data['prices']['price_of_wood'] * w_tep_i * 0.287)
    heating_types_prices.append(data['prices']['price_of_pelet'] * w_tep_i / 1000 * 0.1953)
    heating_types_prices.append(data['prices']['tarif_heat_energy'] * w_tep_i * 0.086)

    return render_template(
        "thermal-results.html",
        heater_time=heater_time,
        heater_power=heater_power,
        q_hot_water=q_hot_water,
        plot_line_data=plot_line_data,
        w_tep_i=w_tep_i,
        heating_types_prices=heating_types_prices
    )
