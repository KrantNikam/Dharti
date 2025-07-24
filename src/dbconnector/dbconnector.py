from config.config import config
import psycopg2
from datetime import datetime

def connect():
    try:
        # read connection parameters
        params = config['postgres']
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        global connection
        connection = conn
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def get_pgconn_string():
    try:
        # read connection parameters
        params = config['postgres']
        host = params['host']
        database = params['database']
        user = params['user']
        password = params['password']
        port = params['port']

        CONNECTION_STRING = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        #CONNECTION_STRING = "postgresql+psycopg2://postgres:postgres@localhost:5434/vector_db"
        print("\n\nConnection String for Postgres\n\n")
        print(CONNECTION_STRING)

        return CONNECTION_STRING
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def save_market_data(data):
    # Connect to PostgreSQL database
    params = config['postgres']
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_prices (
            id SERIAL PRIMARY KEY,
            state TEXT,
            district TEXT,
            market TEXT,
            commodity TEXT,
            variety TEXT,
            arrival_date TEXT,
            min_price REAL,
            max_price REAL,
            modal_price REAL,
            grade TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert records into the table
    for record in data:
        cursor.execute('''
            INSERT INTO market_prices (
                state, district, market, commodity, variety, arrival_date, min_price, max_price, modal_price, grade, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            record.get('state'),
            record.get('district'),
            record.get('market'),
            record.get('commodity'),
            record.get('variety'),
            record.get('arrival_date'),
            float(record.get('min_price', 0)),
            float(record.get('max_price', 0)),
            float(record.get('modal_price', 0)),
            record.get('grade'),
            datetime.now()
        ))

    conn.commit()
    cursor.close()
    conn.close()

def get_market_trend_data(state, commodity, district=None, market=None, variety=None, type_of_trend="weekly"):
    params = config['postgres']
    conn = psycopg2.connect(**params)
    cursor = conn.cursor()

    query = f"""SELECT state, district, market, commodity, variety, arrival_date, min_price, max_price, modal_price, created_at
      FROM market_prices WHERE state = '{state}' AND commodity = '{commodity}'"""
    if type_of_trend == "weekly":
        query = f"{query} AND CAST(arrival_date AS TIMESTAMP) >= NOW() - INTERVAL '7 days'"
    elif type_of_trend == "monthly":
        query = f"{query} AND CAST(arrival_date AS TIMESTAMP) >= NOW() - INTERVAL '30 days'"

    if district:
        query += f" AND district = '{district}'"
    if variety:
        query += f" AND variety = '{variety}'"
    if market:
        query += f" AND market = '{market}'"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

# if __name__ == '__main__':
#     connect()