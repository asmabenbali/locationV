from flask import Flask, render_template, request, redirect, url_for,jsonify , session, flash
import sqlite3 as sql
import sqlite3
from voiture import Voiture
from manager import Manager
from client import Client
import time
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
# Define the upload folder
UPLOAD_FOLDER = 'static/photo'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if the upload folder exists, if not, create it
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file:
        # Generate a unique filename using timestamp
        filename = secure_filename(file.filename)
        unique_filename = 'image' + str(int(time.time())) + os.path.splitext(filename)[1]

        # Save the file to the upload folder with the unique filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

        return 'File uploaded successfully'

    return 'Something went wrong'

app.secret_key = 'your_secret_key'



def fetch_cars_from_database():
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voiture")
    cars = cursor.fetchall()
    conn.close()
    return cars

def fetch_cars_from_database_filtered(min_price=None, max_price=None, brand=None, category=None, search=None):
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()

    # Construct the SQL query with optional filters
    sql_query = "SELECT * FROM voiture WHERE 1=1"
    params = []

    if min_price:
        sql_query += " AND prix >= ?"
        params.append(min_price)
    if max_price:
        sql_query += " AND prix <= ?"
        params.append(max_price)
    if brand:
        sql_query += " AND marque = ?"
        params.append(brand)
    if category:
        sql_query += " AND categorie = ?"
        params.append(category)
    if search:
        sql_query += " AND (marque LIKE ? OR modele LIKE ?)"
        params.append('%' + search + '%')
        params.append('%' + search + '%')

    # Execute the SQL query with parameters
    cursor.execute(sql_query, params)
    cars = cursor.fetchall()
    
    conn.close()
    return cars

@app.route("/cars")
def get_cars():
    cars = fetch_cars_from_database()
    cars_list = []
    for car in cars:
        car_dict = {
            "id": car[0],
            "marque": car[1],
            "modele": car[2],
            "immatriculation": car[3],
            "categorie": car[4],
            "prix": car[5],
            "disponibilite": car[6],
            "image_url": car[7]
        }
        cars_list.append(car_dict)
    return jsonify(cars_list)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/car_detail/<int:car_id>")
def car_detail(car_id):
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voiture WHERE id_voiture = ?", (car_id,))
    car_data = cursor.fetchone()
    conn.close()
    if car_data:
        car_obj = Voiture(*car_data)
        return render_template("detail.html", car=car_obj)
    else:
        return "Car not found", 404


@app.route("/reservation_form/<int:car_id>")
def reservation_form(car_id):
    return render_template("reservation_form.html", car_id=car_id)



@app.route("/submit_reservation/<int:car_id>", methods=["POST"])
def submit_reservation(car_id):
    if request.method == "POST":
        # Extract the form data
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        conn = sqlite3.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM client")
        conn.commit()
        data = cursor.fetchall()
        conn.close()
        for client in data:
            if client[3] == email:
                id= client[0]
                break
        if not id :
            id = data[-1][0]+1
       
        # Update car availability to 'Non disponible'
        conn = sqlite3.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE voiture SET disponibilite = ? WHERE id_voiture = ?", ('Non disponible', car_id))
        conn.commit()

        # Insert the reservation into the database
        cursor.execute("INSERT INTO reservation (id_client, id_voiture, status) VALUES (?, ?, ?)", (id, car_id, 'Pending'))
        conn.commit()
        conn.close()

        # Redirect to a confirmation page
        return redirect(url_for("reservation_confirmation"))

    
@app.route("/reservation_confirmation")
def reservation_confirmation():
    return  render_template('reservation_confirmation.html')

@app.route("/cars_html")
def display_cars_html():
    # Get filter parameters from the URL query string
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    brand = request.args.get('brand')
    category = request.args.get('category')
    search = request.args.get('search')

    # Fetch cars from the database with applied filters
    cars = fetch_cars_from_database_filtered(min_price, max_price, brand, category, search)

    return render_template("cars.html", cars=cars)
@app.route("/home")
def home():
    if 'email' in session:
        # Render the home page for logged-in managers
        return render_template("home.html")
    else:
        return redirect(url_for('login'))


@app.route("/manager_dashboard")
def manager_dashboard():
    cars = manager.get_cars()
    if 'email' in session :
         return render_template(
        "add_car.html",
        cars=cars
    )
    else:
        return 'You are not authorized to access this page.'
   

@app.route("/manager_cars")
def manager_cars():
    cars = manager.get_cars()  # Assuming manager has a method to get the list of cars managed by the manager
    return render_template("manager_cars.html", cars=cars)


@app.route("/add_car", methods=["POST"])
def add_car():
    if request.method == "POST":
        # Get other car details from the form
        car_details = {
            "marque": request.form["marque"],
            "modele": request.form["modele"],
            "immatriculation": request.form["immatriculation"],
            "categorie": request.form["categorie"],
            "prix": request.form["prix"],
            "disponibilite": request.form["disponibilite"]
        }
        
        # Handle image upload
        if 'image_url' in request.files:
            image_file = request.files['image_url']
            # Save the image file to a folder
            image_filename = secure_filename(image_file.filename)  # Use secure_filename to sanitize the filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
            # Save the path to the image in the car_details dictionary
            car_details["image_url"] = image_path

        # Add the car to the database with other details
        manager.add_car(car_details) 
        return redirect(url_for("manager_dashboard"))

@app.route("/modify_car/<int:car_id>", methods=["GET"])
def modify_car(car_id):
    # Fetch the car details from the database based on the car_id
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voiture WHERE id_voiture = ?", (car_id,))
    car = cursor.fetchone()
    conn.close()
    
    # Check if the car exists
    if car:
        # Construct a car object from the fetched data
        car_obj = Voiture(*car)
        # Render the template for modifying the car and pass the car object to it
        return render_template("modify_car.html", car=car_obj)
    else:
        return "Car not found", 404

@app.route("/modify_car/<int:car_id>", methods=["POST"])
def modify_car_post(car_id):
    if request.method == "POST":
        # Get car details from the form
        car_details = {
            "marque": request.form["marque"],
            "modele": request.form["modele"],
            "immatriculation": request.form["immatriculation"],
            "categorie": request.form["categorie"],
            "prix": request.form["prix"],
            "disponibilite": request.form["disponibilite"]
        }
        # Modify the car in the database
        manager.modify_car(car_id, car_details)
        return redirect(url_for("manager_cars"))


@app.route("/delete_car/<int:car_id>", methods=["POST"])
def delete_car(car_id):
    if request.method == "POST":
        # Delete the car from the database
        manager.delete_car(car_id)
        return redirect(url_for("manager_cars"))
    
manager = Manager(idManager="manager_id", nom="John", prenom="Doe", email="john@example.com", mot_de_passe="password")

def verify_manager_credentials(email, password):
    conn = sqlite3.connect("loc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM manager WHERE email = ? AND mot_de_passe = ?", (email, password))
    manager = cursor.fetchone()
    conn.close()
    return manager

@app.route("/reservations")
def get_reservations():
    manager_instance = Manager(idManager="manager_id", nom="John", prenom="Doe", email="john@example.com", mot_de_passe="password")
    reservations = manager_instance.get_reservations()
    return render_template("reservations.html", reservations=reservations)


@app.route("/accept_reservation/<int:reservation_id>", methods=["POST"])
def accept_reservation(reservation_id):
    if request.method == "POST":
        # Call the accept_reservation method directly on the existing Manager instance
        manager.accept_reservation(reservation_id)
        return redirect(url_for("get_reservations"))

@app.route("/refuse_reservation/<int:reservation_id>", methods=["POST"])
def refuse_reservation(reservation_id):
    if request.method == "POST":
        # Get the car_id associated with the reservation
        conn = sqlite3.connect("loc.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id_voiture FROM reservation WHERE id_reservation = ?", (reservation_id,))
        car_id = cursor.fetchone()[0]
        
        # Update the car's availability to 'disponible' in the database
        cursor.execute("UPDATE voiture SET disponibilite = ? WHERE id_voiture = ?", ('disponible', car_id))
        
        # Update the reservation status to 'Refused' in the database
        cursor.execute("UPDATE reservation SET status = ? WHERE id_reservation = ?", ('Refused', reservation_id))
        
        conn.commit()
        conn.close()

        # Redirect to the page where reservations are listed
        return redirect(url_for("get_reservations"))



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        manager = verify_manager_credentials(email, password)
        if manager:
            session['email'] = email
            return redirect(url_for('home'))
        else:
            return "Invalid email or password"
    return render_template("login.html")

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form['email']
        # Validate the email and authenticate the user
        # For simplicity, let's assume authentication is successful
        session['logged_in'] = True
        session['email'] = email
        return redirect('/reservation_status')
    return render_template('cus_login.html')

@app.route('/reservation_status')
def reservation_status():
    if 'logged_in' in session:
        email = session['email']
        client_info = retrieve_client_info(email)
        if client_info:
            # Pass client information and reservations to the template
            return render_template('reservation_status.html', client=client_info)
        else:
            flash("Client information not found", "error")
            return redirect('/cus_login')
    else:
        return redirect('/cus_login')


def retrieve_client_info(email):
    conn = sqlite3.connect('loc.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client WHERE email=?", (email,))
    client_info = cursor.fetchone()
    if client_info:
        # Extract client information
        client_id, nom, prenom, _, telephone = client_info
        # Fetch reservations for the client
        cursor.execute("SELECT * FROM reservation inner join voiture on reservation.id_voiture = voiture.id_voiture WHERE reservation.id_client=?", (client_id,))
        reservations = cursor.fetchall()
        conn.close()
        return [
             client_id,
            nom,
             prenom,
            telephone,
             reservations
        ]
    else:
        conn.close()
        return None

@app.route("/cancel_reservation/<int:reservation_id>", methods=["POST"])
def cancel_reservation(reservation_id):
    if request.method == "POST":
        # Check if the user is logged in
        if 'logged_in' in session:
            # Retrieve the client's email from the session
            email = session['email']
            
            # Retrieve the reservation from the database
            conn = sqlite3.connect('loc.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reservation WHERE id_reservation=? AND id_client=(SELECT id_client FROM client WHERE email=?)", (reservation_id, email))
            reservation = cursor.fetchone()
            
            if reservation:
                # Cancel the reservation by updating its status in the database
                cursor.execute("UPDATE reservation SET status='Cancelled' WHERE id_reservation=?", (reservation_id,))
                conn.commit()
                conn.close()
                
                flash("Reservation canceled successfully", "success")
            else:
                flash("Reservation not found or you do not have permission to cancel it", "error")
            
            return redirect(url_for("reservation_status"))
        else:
            flash("Please log in to cancel reservations", "error")
            return redirect(url_for("customer_login"))
# Assuming you have an instance of the Client class named 'client'
client = Client(id_client=1, nom="John", prenom="Doe", email="john@example.com", telephone="123456789")

# Now call the get_reservations() method on the 'client' instance
reservations = client.get_reservations()
  

if __name__ == "__main__":
 app.run(debug=True)
