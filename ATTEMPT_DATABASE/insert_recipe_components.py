# insert_recipes_components.py

import sqlite3

# Function to insert recipe, components, molecular weights, and literature concentrations
def insert_recipe_and_components():
    conn = sqlite3.connect('experiments.db')
    cursor = conn.cursor()

    # Insert a sample recipe
    cursor.execute('''
        INSERT OR REPLACE INTO recipes (recipe_name, source)
        VALUES (?, ?)
    ''', (
        'M9 Minimal Medium',  # Recipe name
        'Literature source: [Broth culture medium for E. coli]'  # Recipe source
    ))

    # Get the recipe_id for the M9 Minimal Medium
    cursor.execute('''
        SELECT recipe_id FROM recipes WHERE recipe_name = ?
    ''', ('M9 Minimal Medium',))
    recipe_id = cursor.fetchone()[0]

    # Define components, species, molecular weights, and fixed literature concentrations
    m9_components = [
        ("Glucose", "anhydrous", 180.16, 4.0),    # Concentration: 4.0 g/L
        ("Na2HPO4", "anhydrous", 141.96, 6.78),   # Concentration: 6.78 g/L
        ("KH2PO4", "anhydrous", 136.09, 3.0),     # Concentration: 3.0 g/L
        ("NaCl", "anhydrous", 58.44, 0.5),        # Concentration: 0.5 g/L
        ("NH4Cl", "anhydrous", 53.49, 1.0),       # Concentration: 1.0 g/L
        ("MgSO4", "heptahydrate", 246.48, 0.12),  # Concentration: 0.12 g/L
        ("CaCl2", "dihydrate", 147.02, 0.011)     # Concentration: 0.011 g/L
    ]

    # Insert components, molecular weights, and concentrations
    for component in m9_components:
        component_name = component[0]
        species = component[1]
        molecular_weight = component[2]
        concentration = component[3]

        # Insert the component into the components table if it doesn't exist
        cursor.execute('''
            INSERT OR IGNORE INTO components (component_name) VALUES (?)
        ''', (component_name,))

        # Get the component_id for the inserted/retrieved component
        cursor.execute('''
            SELECT component_id FROM components WHERE component_name = ?
        ''', (component_name,))
        component_id = cursor.fetchone()[0]

        # Insert molecular weight and species into the molecular_weights table
        cursor.execute('''
            INSERT OR REPLACE INTO molecular_weights (component_id, molecular_weight, species)
            VALUES (?, ?, ?)
        ''', (component_id, molecular_weight, species))

        # Map the component to the recipe with a single concentration value
        cursor.execute('''
            INSERT OR IGNORE INTO recipe_component_mappings (recipe_id, component_id, concentration)
            VALUES (?, ?, ?)
        ''', (recipe_id, component_id, concentration))

    # Commit and close the connection
    conn.commit()
    conn.close()

if __name__ == '__main__':
    insert_recipe_and_components()
    print("Recipe, component, molecular weight, and concentration information inserted successfully.")
