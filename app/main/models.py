from run import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    items = db.relationship('Item', backref='user')

    def __repr__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        return ' '.join((self.first_name, self.surname))


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False, uniqeu=True)
    electric_power = db.Column(db.Integer(), nullable=False)
    use_times = db.relationship('UseTime', backref='item')

    def __repr__(self) -> str:
        return f"{self.name} - {self.user}"


class UseTime:
    __tablename__ = 'use_times'
    id = db.Column(db.Integer(), primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)
    end_time = db.Column(db.DateTime(), nullable=False)

    def __repr__(self) -> str:
        return f"{self.start_time}"

