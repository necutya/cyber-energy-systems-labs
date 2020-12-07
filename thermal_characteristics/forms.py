from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, SubmitField
from wtforms.validators import NumberRange, DataRequired, Optional


class ThermalFrom(FlaskForm):
    q_tepl = FloatField(
        'Питомі теловтрати будівлі (Вт/м²)',
        validators=[DataRequired(), NumberRange(0, 500)],
        default=30
    )
    s = FloatField(
        "Опалювальна площа будинку (м²)",
        validators=[DataRequired(), NumberRange(0, 2000)],
        default=50
    )
    n_people = IntegerField(
        "Кількість людей",
        validators=[DataRequired(), NumberRange(0, 2000)],
        default=5
    )
    T_inWater = FloatField(
        "Температура вхідної води (°C)",
        validators=[DataRequired(), NumberRange(1, 99)],
        default=15
    )
    T_endBak = FloatField(
        "Кінцева температура бака (°C)",
        validators=[DataRequired(), NumberRange(1, 99)],
        default=85
    )
    T_shower = FloatField(
        "Температура води при прийомі душу (°C)",
        validators=[DataRequired(), NumberRange(1, 99)],
        default=30
    )
    Q_shower_Normal = FloatField(
        "Кількість води, яка витрачається при прийомі душу (л)",
        validators=[DataRequired(), NumberRange(1, 99)],
        default=60
    )
    N_Shower = IntegerField(
        "Кількість прийомів душу на добу",
        validators=[DataRequired(), NumberRange(1, 3)],
        default=1
    )
    T_Bath = FloatField(
        "Температура води при прийомі ванни (°C)",
        validators=[DataRequired(), NumberRange(1, 99)],
        default=35
    )
    Q_bath_Normal = FloatField(
        "Кількість води, яка витрачається при прийомі ванни (л)",
        validators=[DataRequired(), NumberRange(1, 2000)],
        default=150
    )
    N_Bath = IntegerField(
        "Кількість прийомів ванни на добу",
        validators=[DataRequired(), NumberRange(1, 3)],
        default=1
    )
    T_Count_In = FloatField(
        "Розрахункова температура повітря всередині будівлі (°C)",
        validators=[DataRequired(), NumberRange(1, 99)],
        default=20
    )

    # One of
    t_heating = FloatField(
        "Тривалість нагріву ємності (год)",
        validators=[Optional(), NumberRange(1, 100), ],
    )
    p_of_heater = FloatField(
        "Необхідна теплова потужність нагрівача (Вт)",
        validators=[Optional(), NumberRange(1, 200), ],
    )

    #Third block
    tarif_heat_energy  = FloatField(
        "Тариф на теплову енергію (грн/Гкал)",
        validators=[DataRequired(), NumberRange(1, 100000), ],
        default=12
    )
    price_of_gas = FloatField(
        "Вартість 1м^3 газу (грн)",
        validators=[DataRequired(), NumberRange(1, 100000), ],
        default=8
    )
    price_of_coal = FloatField(
        "Вартість 1т вугілля (грн)",
        validators=[DataRequired(), NumberRange(100, 100000), ],
        default=6800
    )
    tarif_electricity_energy = FloatField(
        "Тариф на ел. енергію (грн/кВт*год)",
        validators=[DataRequired(), NumberRange(0, 10000), ],
        default=1
    )
    price_of_wood = FloatField(
        "Ціна 1т дров (грн)",
        validators=[DataRequired(), NumberRange(0, 100000), ],
        default=200
    )
    price_of_pelet = FloatField(
        "Ціна 1т пелет (грн)",
        validators=[DataRequired(), NumberRange(0, 100000), ],
        default=3000
    )

