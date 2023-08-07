from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from . import db
from .models import User, Appointment

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/appointments', methods=['POST', 'GET'])
@login_required
def manage_appointments():
    if request.method == 'POST':
        date_str = request.form.get('date')
        time_str = request.form.get('time')


        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()  # Updated format for date
        time_obj = datetime.strptime(time_str, '%H:%M').time()

        new_appointment = Appointment(date=date_obj, time=time_obj, user_id=current_user.id)

        db.session.add(new_appointment)
        db.session.commit()

        success_message = "Appointment created successfully!"
        return render_template("success.html", user=current_user, success_message=success_message)


    elif request.method == 'GET':
        # Handle GET request logic here if needed
        return render_template("appointment.html", user=current_user)
    
    else:
        error_message = "Error in Appointment creation!"
        return render_template("appointment.html", user=current_user, error_message=error_message)



@views.route('/match-appointments', methods=['GET'])
@login_required
def match_appointments_endpoint():
    current_user_id = current_user.id
    current_user_appointments = Appointment.query.filter_by(user_id=current_user_id).all()
    current_user_name = User.query.filter_by(id=current_user_id).first()

    matched_appointments_data = []

    for appointment in current_user_appointments:
        matching_appointments = Appointment.query.filter(
            Appointment.date == appointment.date,
            Appointment.time == appointment.time,
            Appointment.user_id != current_user_id
        ).all()

        for matching_appointment in matching_appointments:
            partner_user = User.query.get(matching_appointment.user_id)
            appointment_data = {
                # 'id': matching_appointment.user_id,
                'Current_user_id': matching_appointment.user_id,
                'Current_username': current_user_name.first_name,
                # 'partner_id': partner_user.id,
                'partner_username': partner_user.first_name,
                'date': matching_appointment.date.strftime('%d-%m-%Y'),
                'time': matching_appointment.time.strftime('%H:%M'),
            }
            matched_appointments_data.append(appointment_data)

    return render_template("matched.html", matched_appointments=matched_appointments_data , user=current_user)

