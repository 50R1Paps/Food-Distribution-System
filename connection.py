from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib

app = Flask(__name__)

# create a connection to the database
conn = sqlite3.connect('food_distribution.db')
c = conn.cursor()

# create a table to store the information
c.execute('CREATE TABLE IF NOT EXISTS recipients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, surname TEXT, birthdate TEXT, religion TEXT, address TEXT, city TEXT, country TEXT, family_members INTEGER, fingerprint TEXT)')

# create a table to track families that have received food packages
c.execute('CREATE TABLE IF NOT EXISTS family_tracking (id INTEGER PRIMARY KEY AUTOINCREMENT, family_hash TEXT, num_packages INTEGER, last_package_date TEXT)')

# function to calculate the hash of a family's information
def hash_family_info(name, surname, birthdate, religion, address, city, country, family_members):
    hash_object = hashlib.sha256(f'{name}{surname}{birthdate}{religion}{address}{city}{country}{family_members}'.encode())
    return hash_object.hexdigest()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # retrieve the form data
        name = request.form['name']
        surname = request.form['surname']
        birthdate = request.form['birthdate']
        religion = request.form['religion']
        address = request.form['address']
        city = request.form['city']
        country = request.form['country']
        family_members = request.form['family_members']
        fingerprint = request.form['fingerprint']
        
        # insert the data into the database
        c.execute('INSERT INTO recipients (name, surname, birthdate, religion, address, city, country, family_members, fingerprint) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (name, surname, birthdate, religion, address, city, country, family_members, fingerprint))
        conn.commit()
        
        # check if the family has already received a package
        family_hash = hash_family_info(name, surname, birthdate, religion, address, city, country, family_members)
        c.execute('SELECT * FROM family_tracking WHERE family_hash = ?', (family_hash,))
        result = c.fetchone()
        if result:
            # update the existing record
            num_packages = result[2] + 1
            c.execute('UPDATE family_tracking SET num_packages = ?, last_package_date = datetime("now") WHERE family_hash = ?', (num_packages, family_hash))
            conn.commit()
        else:
            # insert a new record for the family
            c.execute('INSERT INTO family_tracking (family_hash, num_packages, last_package_date) VALUES (?, ?, datetime("now"))', (family_hash, 1))
            conn.commit()
        
        return redirect(url_for('success'))
    else:
        return render_template('index.html')

@app.route('/success')
def success():
    return 'Data successfully submitted.'

if __name__ == '__main__':
    app.run(debug=True)
