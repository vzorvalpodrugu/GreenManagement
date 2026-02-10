sql_create_databases="""
    CREATE TABLE IF NOT EXISTS incomes(
        id SERIAL PRIMARY KEY,
        amount DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS costs(
        id SERIAL PRIMARY KEY,
        category VARCHAR(20) NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS balance(
        amount DECIMAL(10,2) 
    );
"""

