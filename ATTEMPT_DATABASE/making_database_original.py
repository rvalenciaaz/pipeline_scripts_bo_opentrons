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

    # Create experiment_component_mappings table (bridge table)
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

# Function to insert a sample experiment and its components
def insert_sample_experiment():
    conn = sqlite3.connect('experiments.db')
    cursor = conn.cursor()

    # Insert a sample experiment
    cursor.execute('''
        INSERT OR REPLACE INTO experiments (experiment_code, dim, samplesper, big, batches, method)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        'EXP12345',  # Experiment code
        7,  # Number of dimensions (components)
        10,  # Samples per iteration
        True,  # Is it a big experiment?
        5,  # Number of batches (null if not a big experiment)
        'sobol'  # Sampling method
    ))

    # Define components and their concentration ranges
    m9_components = [
        ("Glucose", 0.1, 10.0),
        ("Na2HPO4", 0.5, 20.0),
        ("KH2PO4", 0.5, 20.0),
        ("NaCl", 0.05, 1.0),
        ("NH4Cl", 0.1, 5.0),
        ("MgSO4", 0.01, 0.2),
        ("CaCl2", 0.001, 0.05)
    ]

    # Insert components into the components table if they don't already exist
    for component in m9_components:
        cursor.execute('''
            INSERT OR IGNORE INTO components (component_name) VALUES (?)
        ''', (component[0],))
        
        # Get the component_id of the inserted/retrieved component
        cursor.execute('''
            SELECT component_id FROM components WHERE component_name = ?
        ''', (component[0],))
        component_id = cursor.fetchone()[0]

        # Insert into the experiment_component_mappings table
        cursor.execute('''
            INSERT INTO experiment_component_mappings (experiment_code, component_id, min_concentration, max_concentration)
            VALUES (?, ?, ?, ?)
        ''', (
            'EXP12345',  # Experiment code
            component_id,  # Component ID
            component[1],  # Min concentration
            component[2]   # Max concentration
        ))

    # Commit and close the connection
    conn.commit()
    conn.close()

# Main execution flow
if __name__ == '__main__':
    # Create the database and tables
    create_database()

    # Insert a sample experiment and its components
    insert_sample_experiment()

    print("Database created and sample experiment with components inserted successfully.")
