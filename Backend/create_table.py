import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


# Configurazione della connessione
config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'unix_socket': os.environ.get('DB_SOCKET'),
    'database': os.environ.get('DB_NAME'),
    'raise_on_warnings': True
}
# Stabilisci la connessione
cnx = mysql.connector.connect(**config)

# Crea un cursore
cursor = cnx.cursor()

# Crea una tabella
create_table_query = """
CREATE TABLE IF NOT EXISTS distribuzione_cibo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cognome VARCHAR(255) NOT NULL,
    data_nascita DATE,
    religione VARCHAR(50),
    indirizzo VARCHAR(255),
    citta VARCHAR(50),
    paese VARCHAR(50),
    numero_di_familiari INT,
    impronta_digital VARCHAR(255)
);
"""

cursor.execute(create_table_query)

# Chiudi il cursore e la connessione
cursor.close()
cnx.close()
