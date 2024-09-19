# insert_experiment_data.py

import sqlite3

# Function to insert experiment-related data
def insert_experiment_data():
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
        5,  # Number of batches
        'sobol'  # Sampling method
    ))

    # Define components and their concentration ranges
    m9_components_concentrations = [
        ("Glucose", 0.1, 10.0),
        ("Na2HPO4", 0.5, 20.0),
        ("KH2PO4", 0.5, 20.0),
        ("NaCl", 0.05, 1.0),
        ("NH4Cl", 0.1, 5.0),
        ("MgSO4", 0.01, 0.2),
        ("CaCl2", 0.001, 0.05)
    ]

    # Insert concentration ranges into the experiment_component_mappings table
    for component in m9_components_concentrations:
        component_name = component[0]
        min_concentration = component[1]
        max_concentration = component[2]

        # Get the component_id for the component
        cursor.execute('''
            SELECT component_id FROM components WHERE component_name = ?
        ''', (component_name,))
        component_id = cursor.fetchone()[0]

        # Insert into the experiment_component_mappings table
        cursor.execute('''
            INSERT INTO experiment_component_mappings (experiment_code, component_id, min_concentration, max_concentration)
            VALUES (?, ?, ?, ?)
        ''', (
            'EXP12345',  # Experiment code
            component_id,  # Component ID
            min_concentration,  # Min concentration
            max_concentration   # Max concentration
        ))

    # Commit and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    insert_experiment_data()
    print("Experiment data inserted successfully.")
