import mysql.connector
from flask import Flask, request, render_template

app = Flask(__name__)

# Connect to the MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword",
  database="yourdatabase"
)

# Define a function to insert the form data into the database
def insert_data(name, surname, birth, religion, num_family_members, family_data, fingerprint_data, operator_name):
    mycursor = mydb.cursor()
    sql = "INSERT INTO food_distribution (name, surname, birth, religion, num_family_members, family_data, fingerprint_data, operator_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (name, surname, birth, religion, num_family_members, family_data, fingerprint_data, operator_name)
    mycursor.execute(sql, val)
    mydb.commit()

# Define a route for the form page
@app.route('/form')
def form():
    return render_template('form.html')

# Define a route for submitting the form data
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    surname = request.form['surname']
    birth = request.form['birth']
    religion = request.form['religion']
    num_family_members = request.form['num_family_members']
    family_data = request.form['family_data']
    fingerprint_data = request.form['fingerprint_data']
    operator_name = request.form['operator_name']
    insert_data(name, surname, birth, religion, num_family_members, family_data, fingerprint_data, operator_name)
    return "Form data submitted successfully!"

if __name__ == '__main__':
    app.run()
