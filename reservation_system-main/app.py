# 1. Imports
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import secrets
import datetime
import time


# 2. Flask app initialization
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # This is used for session management

# 3. Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# 4. Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(120), nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('date', 'service_id', name='unique_date_service'),)
    feedback = db.Column(db.String(500), nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # You can use a scale of 1-5 or 1-10, for example

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

app.config['MAIL_SERVER'] = 'your-mail-server.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
# 5. Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # You can add more fields as needed, like 'name', 'role', etc.

        # Check if a user with this email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('A user with this email already exists.', 'danger')
            return redirect(url_for('register'))

        user = User(email=email)
        user.set_password(password)

        # Generate a unique token for email verification
        user.verification_token = secrets.token_urlsafe(16)
        db.session.add(user)
        db.session.commit()

        # Send verification email
        verification_url = url_for('verify_email', token=user.verification_token, _external=True)
        msg = Message('Verify Your Email', sender='your-email@example.com', recipients=[user.email])
        msg.body = f"Click the link to verify your email: {verification_url}"
        mail.send(msg)

        flash('Registration successful! Please verify your email.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


        
   

@app.route('/verify_email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        flash('Invalid or expired token.')
        return redirect(url_for('login'))
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    flash('Email verified successfully!')
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate a unique token for password reset
            user.verification_token = secrets.token_urlsafe(16)
            db.session.commit()

            # Send password reset email
            reset_url = url_for('reset_password', token=user.verification_token, _external=True)
            msg = Message('Reset Your Password', sender='your-email@example.com', recipients=[user.email])
            msg.body = f"Click the link to reset your password: {reset_url}"
            mail.send(msg)

        flash('If an account with that email exists, a password reset link has been sent.')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        flash('Invalid or expired token.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user.set_password(new_password)
        user.verification_token = None
        db.session.commit()
        flash('Password reset successfully!')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user.role == 'provider':
        reservations = Reservation.query.filter_by(service_id=user.id).all()
        return render_template('provider_dashboard.html', reservations=reservations)
    
    elif user.role == 'customer':
        return render_template('customer_dashboard.html')
    

@app.route('/search', methods=['POST'])
def search():
    service_type = request.form.get('service_type')
    providers = Service.query.filter_by(name=service_type).all()
    return render_template('search_results.html', providers=providers)


@app.route('/add_service', methods=['POST'])
def add_service():
    service_name = request.form.get('service_name')
    provider_id = session['user_id']
    service = Service(name=service_name, provider_id=provider_id)
    db.session.add(service)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/reserve/<int:service_id>', methods=['POST'])
def reserve(service_id):
    user_id = session['user_id']
    date = request.form.get('date')
    time = request.form.get('time')
    
    # Combine date and time into a single datetime object
    datetime_str = f"{date} {time}"
    datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
    
    reservation = Reservation(user_id=user_id, date=datetime_obj, service_id=service_id)
    
    try:
        db.session.add(reservation)
        db.session.commit()
        flash('Reservation successful!')
        
        # Send email confirmation
        user = User.query.get(user_id)
        msg = Message('Reservation Confirmation', sender='your-email@example.com', recipients=[user.email])
        msg.body = f"Hello {user.email},\n\nYour reservation for {date} at {time} has been confirmed.\n\nThank you!"
        mail.send(msg)
    except IntegrityError:
        db.session.rollback()
        flash('This slot is already reserved. Please choose another time.')
    
    return redirect(url_for('dashboard'))


@app.route('/set_availability', methods=['POST'])
def set_availability():
    provider_id = session['user_id']
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    
    # Convert the date and times to appropriate data types
    date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    start_time_obj = datetime.datetime.strptime(start_time, '%H:%M').time()
    end_time_obj = datetime.datetime.strptime(end_time, '%H:%M').time()

    # Check if the provider already has an availability set for the given date
    existing_availability = Availability.query.filter_by(provider_id=provider_id, date=date_obj).first()
    if existing_availability:
        flash('You already have set availability for this date. Update or delete the existing one.')
        return redirect(url_for('dashboard'))

    # Create a new availability entry
    availability = Availability(provider_id=provider_id, date=date_obj, start_time=start_time_obj, end_time=end_time_obj)
    db.session.add(availability)
    db.session.commit()

    flash('Availability set successfully!')
    return redirect(url_for('dashboard'))

@app.route('/feedback/<int:reservation_id>', methods=['GET', 'POST'])
def give_feedback(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if request.method == 'POST':
        feedback = request.form.get('feedback')
        rating = request.form.get('rating')

        reservation.feedback = feedback
        reservation.rating = rating
        db.session.commit()

        flash('Thank you for your feedback!')
        return redirect(url_for('dashboard'))

    return render_template('feedback.html', reservation=reservation)


@app.route('/book/<int:provider_id>', methods=['GET', 'POST'])
def book(provider_id):
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        date = request.form.get('date')
        time = request.form.get('time')

        # Convert to datetime object
        datetime_str = f"{date} {time}"
        datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')

        # Create a new reservation
        reservation = Reservation(user_id=session['user_id'], service_id=service_id, date=datetime_obj)
        db.session.add(reservation)
        db.session.commit()

        # Send email notification to the service provider
        provider = User.query.get(provider_id)
        msg = Message('New Booking Alert!', sender='your-email@example.com', recipients=[provider.email])
        msg.body = f"Hello {provider.name},\n\nYou have a new booking on {date} at {time}.\n\nRegards,\nYour Booking System"
        mail.send(msg)

        flash('Service booked successfully!')
        return redirect(url_for('dashboard'))

       

    services = Service.query.filter_by(provider_id=provider_id).all()
    return render_template('book.html', services=services)

# 6. Main execution
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # This line should be run once to create the database tables, then commented out
    app.run(debug=True)

