from flask import render_template, redirect, Blueprint, request, session, flash, url_for
from datetime import datetime, timedelta, date, time

from sqlalchemy import extract

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

from app import db
from app.main.models import User, UseTime, Item
from electric_supply.forms import ItemForm, UseTimeForm

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


@main.route('/electric-supply-items', methods=["GET", "POST"])
def electric_supply_items():
    form = ItemForm()
    user: int = User.query.first()
    if request.method == "POST":
        if form.validate_on_submit():
            item = Item(name=form.name.data, electric_power=form.electric_power.data, user_id=user.id)
            db.session.add(item)
            db.session.commit()
            flash("Новий пристрій було додано!", 'success')
    items = Item.query.filter_by(user_id=user.id)
    return render_template(
        "electric-supply-items.html", form=form, items=items
    )


@main.route('/electric-supply-items/<int:item_id>/edit', methods=["GET", "POST"])
def electric_supply_items_edit(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm()
    user: int = User.query.first()
    if request.method == "POST":
        if form.validate_on_submit():
            item.name = form.name.data
            item.electric_power = form.electric_power.data
            db.session.commit()
            flash(f"Новий пристрій {item.name} було змінено!", 'success')
            return redirect(url_for('main.electric_supply_items'))
    elif request.method == 'GET':
        form.name.data = item.name
        form.electric_power.data = item.electric_power
    items = Item.query.filter_by(user_id=user.id)
    return render_template(
        "electric-supply-item-edit.html", form=form, items=items
    )


@main.route('/electric-supply-items/<int:item_id>/delete', methods=["GET", "POST"])
def electric_supply_items_delete(item_id):
    item = Item.query.get_or_404(item_id)
    item_name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f"Пристрій {item.name} було видалено!", 'success')
    return redirect(url_for('main.electric_supply_items'))


@main.route('/electric-supply-items/<int:item_id>/log', methods=["GET", "POST"])
def electric_supply_items_log(item_id):
    item = Item.query.get_or_404(item_id)
    form = UseTimeForm()
    last_monday = datetime.combine(date.today(), time()) - timedelta(days=date.today().weekday())
    logged_time = UseTime.query.filter_by(item_id=item.id).order_by("start_time")
    current_week = sorted([t for t in logged_time if t.start_time >= last_monday], key=lambda x: x.start_time)
    if request.method == "POST":
        if not form.start.data or not form.end.data:
            flash("Усі поля дати повинні бути обов'язково введені", "error")

        elif form.validate_on_submit():
            obj = UseTime(start_time=form.start.data, end_time=form.end.data, item_id=item.id)
            db.session.add(obj)
            db.session.commit()
            flash(f"Запис про час використання пристрою {item.name} було додано", 'success')

    return render_template(
        "electric-supply-item-log.html", form=form, logged_time=logged_time, current_week=current_week,
        item_name=item.name
    )


@main.route('/electric-supply-items/<int:item_id>/log/<int:log_id>/edit', methods=["GET", "POST"])
def electric_supply_items_log_edit(item_id, log_id):
    log = UseTime.query.get_or_404(log_id)
    item = Item.query.get_or_404(item_id)
    form = UseTimeForm()
    last_monday = datetime.combine(date.today(), time()) - timedelta(days=date.today().weekday())
    logged_time = UseTime.query.filter_by(item_id=item.id).order_by("start_time")
    current_week = sorted([t for t in logged_time if t.start_time >= last_monday], key=lambda x: x.start_time)
    if request.method == "POST":
        if not form.start.data or not form.end.data:
            flash("Усі поля дати повинні бути обов'язково введені", "error")

        elif form.validate_on_submit():
            log.start_time = form.start.data
            log.end_time = form.end.data
            db.session.add(log)
            db.session.commit()
            flash(f"Запис про час використання пристрою {item.name} було змінено", 'success')
            return redirect(url_for('main.electric_supply_items_log', item_id=item.id))

    elif request.method == 'GET':
        form.start.data = log.start_time
        form.end.data = log.end_time

    return render_template(
        "electric-supply-item-log-edit.html", form=form, logged_time=logged_time, current_week=current_week,
        item_name=item.name
    )


@main.route('/electric-supply-items/<int:item_id>/log/<int:log_id>/delete', methods=["GET", "POST"])
def electric_supply_items_log_delete(item_id, log_id):
    log = UseTime.query.get_or_404(log_id)
    item = Item.query.get_or_404(item_id)
    db.session.delete(log)
    db.session.commit()
    flash(f"Час використання пристрою  {item.name} було видалено!", 'success')
    return redirect(url_for('main.electric_supply_items_log', item_id=item.id))


@main.route('/electric-supply', methods=["GET", "POST"])
def electric_supply():
    date_price = None
    if request.method == 'POST':
        try:
            price = float(request.form.get("price"))
        except ValueError:
            flash("Невірний тип даних", "error")
        else:
            if price < 0:
                flash("Ціна не може бути менша 0", "error")
            global PRICE
            PRICE = price
            flash("Ціна за кВт успішно змінена", "success")
        date_price = request.form.get("price_date")
        date_price = datetime.strptime(date_price, '%Y-%m')

    day_names = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', "Пятниця", 'Субота', 'Неділя']
    days = {day: dict() for day in day_names}
    last_monday = datetime.combine(date.today(), time()) - timedelta(days=date.today().weekday())
    logged_time = UseTime.query.order_by("start_time")
    current_week = sorted([t for t in logged_time if t.start_time >= last_monday], key=lambda x: x.start_time)

    user: int = User.query.first()
    items = Item.query.filter_by(user_id=user.id)

    for index, day in enumerate(day_names):
        for item in items:
            item_name = '_'.join(item.name.split(' '))
            days[day][item_name] = [0] * 24
        for log in current_week:
            if log.start_time.weekday() == index:
                for i in range(log.start_time.hour, log.end_time.hour + 1):
                    days[day]['_'.join(log.item.name.split(' '))][i] = log.item.electric_power

    total = [0] * 24 * 7
    last_monday = datetime.combine(date.today(), time()) - timedelta(days=date.today().weekday())
    for log in current_week:
        for i in pd.date_range(start=log.start_time, end=log.end_time,
                               periods=round((log.end_time - log.start_time).
                                                     total_seconds() / 3600)).to_pydatetime().tolist():
            total[round((i - last_monday).total_seconds() / 3600) - 1] += log.item.electric_power

    total_max = []
    energo = []
    temp_max = 0
    temp_max_index = 0
    energo_temp = 0
    for index, value in enumerate(total):
        energo_temp += value
        if (index + 1) % 24 == 0:
            if temp_max_index != 0:
                total_max.append(temp_max_index)
            temp_max = 0
            temp_max_index = 0
            energo.append(energo_temp)
            energo_temp = 0
        if value > temp_max:
            temp_max_index = index
            temp_max = value

    avg_total_max = round(sum(total_max) / len(total_max), 3)
    max_energo = max(energo)
    energo_max_index = energo.index(max_energo)

    if date_price:
        month_data = UseTime.query.filter((extract('month', UseTime.start_time) == date_price.month) &
                                          (extract('year', UseTime.start_time) == date_price.year)).all()
        flash(f"Місяць та рік виборки успішно зроблені ({date_price.month} - {date_price.year})", "success")
    else:
        month_data = UseTime.query.filter(extract('month', UseTime.start_time) == datetime.now().month).all()
    total_electric_power = 0
    for log in month_data:
        for i in range(log.start_time.hour, log.end_time.hour + 1):
            total_electric_power += log.item.electric_power
    total_electric_power /= 1000
    prices = [total_electric_power * PRICE, total_electric_power * PRICE * .825, total_electric_power * PRICE * .8]


    return render_template(
        "electric-supply-results.html",
        price=PRICE, default_date=date_price if date_price else date.today(),
        days=days,
        total=total, total_max=total_max, avg_total_max=avg_total_max,
        energo=energo, energo_max_index=energo_max_index, max_energo=max_energo,
        prices=prices, min_prices=min(prices)
    )
