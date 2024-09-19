# create_database.py

import sqlite3

# Function to create the database and tables
def create_database():
    conn = sqlite3.connect('experiments.db')
    cursor = conn.cursor()

    # Create experiments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            experiment_code TEXT PRIMARY KEY,
            dim INTEGER NOT NULL,
            samplesper INTEGER NOT NULL,
            big BOOLEAN NOT NULL,
            batches INTEGER,
            method TEXT NOT NULL
        )
    ''')

    # Create components table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS components (
            component_id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_name TEXT UNIQUE NOT NULL
        )
    ''')

    # Create recipes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT NOT NULL,
            source TEXT
        )
    ''')

    # Create molecular_weights table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS molecular_weights (
            component_id INTEGER NOT NULL,
            molecular_weight REAL NOT NULL,
            species TEXT NOT NULL,
            PRIMARY KEY (component_id, species),
            FOREIGN KEY (component_id) REFERENCES components (component_id) ON DELETE CASCADE
        )
    ''')

    # Create recipe_component_mappings table (now with a single concentration value)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_component_mappings (
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            component_id INTEGER NOT NULL,
            concentration REAL NOT NULL,  -- Single concentration value
            FOREIGN KEY (recipe_id) REFERENCES recipes (recipe_id) ON DELETE CASCADE,
            FOREIGN KEY (component_id) REFERENCES components (component_id) ON DELETE CASCADE,
            UNIQUE (recipe_id, component_id)
        )
    ''')

    # Create experiment_component_mappings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiment_component_mappings (
            mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_code TEXT NOT NULL,
            component_id INTEGER NOT NULL,
            min_concentration REAL NOT NULL,
            max_concentration REAL NOT NULL,
            FOREIGN KEY (experiment_code) REFERENCES experiments (experiment_code) ON DELETE CASCADE,
            FOREIGN KEY (component_id) REFERENCES components (component_id) ON DELETE CASCADE,
            UNIQUE (experiment_code, component_id)
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database tables created successfully.")
