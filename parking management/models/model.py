from extensions import db
from datetime import datetime

class User_Info(db.Model):
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String, unique=True, nullable=False)
    pwd = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, nullable=False, default=1)

    reservations = db.relationship( 'Reservation',backref='user',lazy=True, cascade="all, delete-orphan")

class Parking_Lot(db.Model):
    __tablename__ = "parking_lot"
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.String, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    
    spots = db.relationship('Parking_Spot', backref='parking_lot', lazy=True, cascade="all, delete")


class Parking_Spot(db.Model):
    __tablename__ = "parking_spot"
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(1), nullable=False, default='A') # 'A' = Available, 'O' = Occupied

class Reservation(db.Model):
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'), nullable=False)
    vehicle_number = db.Column(db.String, nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Active') # 'Active' or 'Released'

    spot = db.relationship('Parking_Spot', backref=db.backref('reservations', passive_deletes=True))