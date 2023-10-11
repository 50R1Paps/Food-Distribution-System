from flask import Flask, request, redirect, url_for
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Configurazione della connessione al database MySQL
config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'unix_socket': os.environ.get('DB_SOCKET'),
    'database': os.environ.get('DB_NAME'),
    'raise_on_warnings': True
}
cnx = mysql.connector.connect(**config)


@app.route('/submit_form', methods=['POST'])
def submit_form():
    name = request.form['name']
    surname = request.form['surname']
    birthdate = request.form['birthdate']
    religion = request.form['religion']
    address = request.form['address']
    city = request.form['city']
    country = request.form['country']
    family_members = request.form['family_members']
    # Usato 'get' per ottenere un valore di default
    fingerprint = request.form.get('fingerprint', 'default_value')

    # Validazione
    if not (name and surname and birthdate and religion and address and city and country and family_members):
        return "Tutti i campi sono obbligatori", 400

    # Inserimento nel database
    cursor = cnx.cursor()
    add_data = ("INSERT INTO distribuzione_cibo "
                "(nome, cognome, data_nascita, religione, indirizzo, citta, paese, numero_di_familiari, impronta_digital) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data = (name, surname, birthdate, religion, address,
            city, country, family_members, fingerprint)
    try:
        cursor.execute(add_data, data)
        cnx.commit()
    except Exception as e:
        print("Errore:", e)
        cnx.rollback()

    return redirect(url_for('success_page'))


@app.route('/success_page')
def success_page():
    return "Form inviato con successo!"


if __name__ == '__main__':
    app.run()
