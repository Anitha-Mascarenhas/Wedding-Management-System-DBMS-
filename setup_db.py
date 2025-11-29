# setup_db.py
from database import seed_sample_data

if __name__ == "__main__":
    seed_sample_data()
    print("Seeding finished.")
