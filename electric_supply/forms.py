from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import NumberRange, Length, ValidationError, DataRequired
from wtforms.fields.html5 import DateTimeLocalField
from datetime import datetime, timedelta, date, time


class ItemForm(FlaskForm):
    name = StringField(
        'Назва приладу',
        validators=[
            DataRequired(message="Обов'язкове для заповнення"),
            Length(min=3, max=255, message="Некоректна довжина назви")
        ],
    )
    electric_power = IntegerField(
        "Потужність приладу (Вт)",
        validators=[DataRequired(), NumberRange(0, 2000)],
    )


class UseTimeForm(FlaskForm):
    start = DateTimeLocalField("Початок роботи", format="%Y-%m-%dT%H:%M", default=datetime.now())
    end = DateTimeLocalField("Кінець роботи", format="%Y-%m-%dT%H:%M", default=datetime.now() + timedelta(hours=2))

    def validate_start(self, start):
        if start.data >= self.end.data:
            raise ValidationError("Дата початку не може бути більша ніж дата кінця.")
        # Time management
        spent_days = date.today().weekday()
        left_days = 7 - spent_days
        min_date = datetime.combine(date.today(), time()) - timedelta(days=spent_days)
        max_date = datetime.combine(date.today(), time()) + timedelta(days=left_days)
        if start.data < min_date or start.data > max_date:
            raise ValidationError("Дата початку виходити за межі поточної неділі.")

    def validate_end(self, end):
        # Time management
        spent_days = date.today().weekday()
        left_days = 7 - spent_days
        min_date = datetime.combine(date.today(), time()) - timedelta(days=spent_days)
        max_date = datetime.combine(date.today(), time()) + timedelta(days=left_days)
        if end.data < min_date or end.data > max_date:
            raise ValidationError("Дата кінця виходити за межі поточної неділі.")
