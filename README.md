##Distributed System Simulation with Concurrent Insertions##

This project simulates a distributed system where data is stored in separate SQLite databases for different models: Users, Products, and Orders. The system uses Python's concurrent.futures.ThreadPoolExecutor for handling concurrent insertions into the databases.

##Overview

The program demonstrates:

1. Storing Users, Products, and Orders data in separate SQLite databases (users.db, products.db, orders.db).
2. Concurrent insertions of data using ThreadPoolExecutor.
3. Application-level validations (no database-level constraints).
4. Simulated simultaneous insertions (10 per model) and results output in a single command.

##Prerequisites

1. Python: Ensure Python 3.8+ is installed.
2. SQLite: SQLite library is part of Python's standard library, so no additional installation is required.
3. Threading and Concurrency: Use Python's built-in concurrent.futures module for concurrent insertions.

##Setup Instructions

1. Clone the repository:

git clone https://github.com/anshaduk/Tradexa_cuncurrent_insertions.git
cd Tradexa

2. Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate

3. Install required dependencies:

pip install -r requirements.txt

4. To perform makemigration and migrate

python manage.py makemigrations

python manage.py migrate --database=users_db
python manage.py migrate --database=products_db
python manage.py migrate --database=orders_db

5. Run the simulation:

python manage.py run_insertions.py