from flask import Blueprint, render_template, request, Flask
from models.model import *
from extensions import db
from flask import session
from zoneinfo import ZoneInfo
from io import BytesIO
import base64
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # non-GUI backend for headless rendering
from datetime import datetime, timedelta

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def default():
    return render_template("index.html")

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    username = request.form.get('username')
    password = request.form.get('password')

    user = User_Info.query.filter_by(user_name=username).first()

    if user and user.pwd == password:
        if user.role == 0:
            return "Admins must login from admin login page."
        session['user_id'] = user.id  # Store user in session
        return redirect(url_for('main_routes.user_dashboard'))
    else:
        return "Invalid credentials"

@main_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")

    full_name = request.form.get('full_name')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not full_name or not username or not email or not password or not confirm_password:
        return "All fields are required."

    if password != confirm_password:
        return "Passwords do not match."

    existing_user = User_Info.query.filter_by(user_name=username).first()
    if existing_user:
        return "Username already exists."

    new_user = User_Info(
        full_name=full_name,
        email=email,
        user_name=username,
        pwd=password,
        role=1
    )
    db.session.add(new_user)
    db.session.commit()

    return render_template("signup_success.html")


@main_routes.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template("admin_login.html")

    username = request.form.get('username')
    password = request.form.get('password')

    user = User_Info.query.filter_by(user_name=username).first()

    if user and user.pwd == password:
        if user.role == 0:
            # redirect to route that loads parking lot data
            return redirect(url_for('main_routes.admin_home'))
        return "You are not an admin!"
    else:
        return "Invalid credentials"


############### User Functionalities ##############
############### User Functionalities ##############

from flask import redirect, url_for

# user main dashboard
@main_routes.route('/user_dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    user = User_Info.query.get(user_id) if user_id else None
    lots = Parking_Lot.query.all()
    reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parking_timestamp.desc()).all()
    return render_template('user_dashboard.html', lots=lots, user=user, reservations=reservations)

#summary
@main_routes.route('/summary')
def user_summary():
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend

    user_id = session.get('user_id')
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    # Graph 1: Bookings per day (last 7 days)
    past_week = datetime.now(ZoneInfo("Asia/Kolkata")) - timedelta(days=7)
    filtered = [r for r in reservations if r.parking_timestamp >= past_week]

    date_counts = Counter(
        r.parking_timestamp.astimezone(ZoneInfo("Asia/Kolkata")).date()
        for r in filtered
    )

    dates = sorted(date_counts)
    counts = [date_counts[d] for d in dates]

    plt.figure(figsize=(6, 4))
    plt.bar([d.strftime("%d %b") for d in dates], counts, color="skyblue")
    plt.title("Bookings in Last 7 Days")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.tight_layout()
    graph1_path = os.path.join("static", "graph1.png")
    plt.savefig(graph1_path)
    plt.close()

    # Graph 2: Pie chart of status
    status_counts = Counter(r.status for r in reservations)
    plt.figure(figsize=(5, 5))
    plt.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1ff%%', colors=["green", "orange"])
    plt.title("Reservation Status Breakdown")
    graph2_path = os.path.join("static", "graph2.png")
    plt.savefig(graph2_path)
    plt.close()

    return render_template(
        "user_summary.html",
        graph1="graph1.png",
        graph2="graph2.png"
    )


# user logout
@main_routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_routes.login'))


# show book form
@main_routes.route('/show_book_form/<int:lot_id>', methods=['GET'])
def show_book_form(lot_id):
    user_id = session.get('user_id')
    lot = Parking_Lot.query.get_or_404(lot_id)

    # Find an available spot
    available_spot = Parking_Spot.query.filter_by(lot_id=lot_id, status='A').first()
    if not available_spot:
        return redirect(url_for('main_routes.user_dashboard'))

    return render_template(
        "book_parking.html",
        lot=lot,
        spot=available_spot,
        user_id=user_id
    )

# book parking spot
from sqlalchemy import and_

@main_routes.route('/book_lot', methods=['POST'])
def book_lot():
    user_id = request.form.get('user_id')
    lot_id = request.form.get('lot_id')
    spot_id = request.form.get('spot_id')
    vehicle_num = request.form.get('vehicle_num')

    #if vehicle is already parked in an active reservation
    active_reservation = Reservation.query.filter(
        and_(
            Reservation.vehicle_number == vehicle_num,
            Reservation.status == 'Active'
        )
    ).first()

    if active_reservation:
        flash("This vehicle is already parked. Please release it before booking a new spot.", "danger")
        return redirect(url_for('main_routes.user_dashboard'))

    lot = Parking_Lot.query.get(lot_id)
    spot = Parking_Spot.query.get(spot_id)

    if spot.status != 'A':
        return redirect(url_for('main_routes.user_dashboard'))
    spot.status = 'O'

    reservation = Reservation(
        spot_id=spot.id,
        user_id=user_id,
        vehicle_number=vehicle_num,
        parking_timestamp=datetime.now(ZoneInfo("Asia/Kolkata")),
        parking_cost=lot.price,
        status='Active'
    )

    db.session.add(reservation)
    db.session.commit()

    flash("Parking spot successfully booked.", "success")
    return redirect(url_for('main_routes.user_dashboard'))


# release parking spot
@main_routes.route('/release/<int:reservation_id>')
def release_spot(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    current_time = datetime.now(ZoneInfo("Asia/Kolkata"))

    # - Check if timestamp is naive
    if reservation.parking_timestamp.tzinfo is None:
        # Make it timezone-aware without shifting the clock
        reservation.parking_timestamp = reservation.parking_timestamp.replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    reservation.leaving_timestamp = current_time
    time_diff = current_time - reservation.parking_timestamp
    hours = max(time_diff.total_seconds() / 3600, 1)

    rate = reservation.spot.parking_lot.price
    cost = round(hours * rate, 2)

    return render_template(
        "release_parking_spot.html",
        reservation=reservation,
        cost=cost,
        releasing_time=current_time
    )

#confirm release
@main_routes.route('/confirm_release', methods=['POST'])
def confirm_release():
    # Get the reservation ID from the submitted form
    reservation_id = request.form.get('reservation_id')
    reservation = Reservation.query.get_or_404(reservation_id)

    # Mark reservation as released
    reservation.status = "Released"

    # Use current IST time for leaving timestamp
    reservation.leaving_timestamp = datetime.now(ZoneInfo("Asia/Kolkata"))

    # Free up the parking spot
    reservation.spot.status = 'A'

    # Commit all changes to the database
    db.session.commit()

    # Redirect user to their dashboard
    return redirect(url_for('main_routes.user_dashboard'))
    
# edit profile
@main_routes.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user = User_Info.query.get(session.get('user_id'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        user.full_name = full_name
        user.email = email
        if password:
            user.pwd = password  # (Consider hashing in real apps!)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('main_routes.edit_profile'))

    return render_template('user_edit_profile.html', user=user)


@main_routes.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')

    if not user_id:
        flash("User ID not found.", "danger")
        return redirect(url_for('main_routes.user_dashboard'))

    user = User_Info.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        session.clear()  # log the user out
        flash("Your account has been deleted.", "success")
        return redirect(url_for('main_routes.signup'))  # or login/register page
    else:
        flash("User not found.", "danger")
        return redirect(url_for('main_routes.user_dashboard'))

################### Admin Functionalities ##############
################### Admin Functionalities ##############

# admin home
@main_routes.route('/admin_home')
def admin_home():
    lots = Parking_Lot.query.all()
    return render_template('admin_dashboard.html', lots=lots)

# admin users
@main_routes.route('/admin_users', methods=['GET'])
def admin_users():
    users = User_Info.query.join(Reservation).filter(Reservation.user_id == User_Info.id).distinct().all()
    return render_template("admin_users.html", users=users)

# admin search
@main_routes.route('/admin_search', methods=['GET', 'POST'])
def admin_search():
    if request.method == 'POST':
        location = request.form.get('location')
        spot_id = request.form.get('spot_id')

        if location:
            lots = Parking_Lot.query.filter(Parking_Lot.prime_location_name.ilike(f"%{location}%")).all()
            if not lots:
                flash("No parking lots found for that location.", "warning")
            return render_template('admin_search_results.html', lots=lots)

        elif spot_id:
            # Assuming you already handle this correctly
            spot = Parking_Spot.query.filter_by(id=spot_id).first()
            if not spot:
                flash("No spot found with that ID.", "warning")
            return render_template('admin_parking_spot_details.html', spot=spot)

    return render_template('admin_search.html')

# admin summary 
@main_routes.route('/admin_summary', methods=['GET', 'POST'])
def admin_summary():
        return render_template("admin_summary.html")

# admin logout 
@main_routes.route('/admin_logout', methods=['GET', 'POST'])
def admin_logout():
        return render_template("admin_login.html")

# adding lot and spots by admin
@main_routes.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if request.method == 'GET':
        return render_template("add_lot.html")

    elif request.method == 'POST':
        location_name = request.form.get('location_name')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        price = request.form.get('price')
        max_spot = int(request.form.get('max_spot'))

        new_lot = Parking_Lot(
            prime_location_name=location_name,
            address=address,
            pin_code=pin_code,
            price=price,
            maximum_number_of_spots=max_spot
        )
        db.session.add(new_lot)
        db.session.commit()

        for _ in range(max_spot):
            spot = Parking_Spot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()

        return redirect(url_for('main_routes.admin_home'))


# edit parking lot
from flask import flash
@main_routes.route('/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    lot = Parking_Lot.query.get_or_404(lot_id)

    #  if any spot in the lot has an active reservation
    has_active_reservation = Reservation.query.join(Parking_Spot).filter(
        Parking_Spot.lot_id == lot.id,
        Reservation.status == 'Active'
    ).first()

    if has_active_reservation:
        flash("You cannot edit this parking lot because some spots are currently reserved.", "warning")
        return redirect(url_for('main_routes.admin_home'))

    if request.method == 'POST':
        lot.prime_location_name = request.form.get('location_name')
        lot.address = request.form.get('address')
        lot.pin_code = request.form.get('pin_code')
        lot.price = float(request.form.get('price'))
        lot.maximum_number_of_spots = int(request.form.get('max_spot'))

        db.session.commit()
        flash("Parking lot updated successfully!", "success")
        return redirect(url_for('main_routes.admin_home'))  

    return render_template("edit_parking_lot.html", lot=lot)


# delete lot
@main_routes.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_parking_lot(lot_id):
    lot = Parking_Lot.query.get_or_404(lot_id)

    # if spot is occupied
    occupied_spot = next((spot for spot in lot.spots if spot.status == 'O'), None)

    if occupied_spot:
        flash("Cannot delete lot: one or more spots are currently occupied.", "error")
        return redirect(url_for('main_routes.admin_home'))

    # delete if all O
    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted successfully.", "success")
    return redirect(url_for('main_routes.admin_home'))


# view/delete parking spot
@main_routes.route('/view_parking_spot/<int:spot_id>', methods=['GET', 'POST'])
def view_parking_spot(spot_id):
    spot = Parking_Spot.query.get_or_404(spot_id)

    if request.method == 'POST':
        if spot.status != 'A':
            flash("Cannot delete. Spot is currently occupied.", "danger")
            return redirect(url_for('main_routes.view_parking_spot', spot_id=spot.id))

        # max spots -1
        lot = spot.parking_lot
        if lot.maximum_number_of_spots > 0:
            lot.maximum_number_of_spots -= 1

        db.session.delete(spot)
        db.session.commit()

        flash("Spot deleted and lot updated successfully.", "success")
        return redirect(url_for('main_routes.admin_home'))

    return render_template("admin_parking_spot.html", spot=spot)

@main_routes.route('/admin_spot_details/<int:spot_id>')
def admin_parking_spot_details(spot_id):
    spot = Parking_Spot.query.get_or_404(spot_id)

    reservations = Reservation.query.filter_by(spot_id=spot_id).order_by(Reservation.parking_timestamp.desc()).all()

    return render_template('admin_parking_spot_details.html', spot=spot, reservations=reservations)
