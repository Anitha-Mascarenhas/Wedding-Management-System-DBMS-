# database.py
import pymysql
import hashlib
from datetime import datetime

# MySQL credentials
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql_password",
    "database": "wedding_management",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# ---------- Users ----------
def create_user(name, email, plain_password, is_admin=0):
    pw = hash_password(plain_password)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (name, email, password, is_admin) VALUES (%s,%s,%s,%s)",
                        (name, email, pw, is_admin))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("create_user error:", e)
        return False
    finally:
        conn.close()

def authenticate_user(email, plain_password):
    pw = hash_password(plain_password)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, name, email, is_admin FROM users WHERE email=%s AND password=%s", (email, pw))
            return cur.fetchone()
    finally:
        conn.close()

# ---------- Services / Vendors ----------
def list_services():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM services ORDER BY service_id")
            return cur.fetchall()
    finally:
        conn.close()

def get_service(service_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM services WHERE service_id=%s", (service_id,))
            return cur.fetchone()
    finally:
        conn.close()

def list_vendors_by_service(service_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # CHANGED: include price & rating by selecting all columns
            cur.execute("SELECT * FROM vendors WHERE service_id=%s", (service_id,))
            return cur.fetchall()
    finally:
        conn.close()

def get_vendor(vendor_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vendors WHERE vendor_id=%s", (vendor_id,))
            return cur.fetchone()
    finally:
        conn.close()

# CHANGED: add price and rating parameters to add_vendor
def add_vendor(name, service_id, contact="", details="", image_path=None, price=0, rating=0.0):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vendors (vendor_name, service_id, contact, details, image_path, price, rating)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (name, service_id, contact, details, image_path, price, rating))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("add_vendor error:", e)
        return False
    finally:
        conn.close()

def update_vendor(vendor_id, name, service_id, contact="", details="", image_path=None, price=0, rating=0.0):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE vendors
                SET vendor_name=%s, service_id=%s, contact=%s, details=%s, image_path=%s, price=%s, rating=%s
                WHERE vendor_id=%s
            """, (name, service_id, contact, details, image_path, price, rating, vendor_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("update_vendor error:", e)
        return False
    finally:
        conn.close()


def add_service(name, description=""):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO services (service_name, description) VALUES (%s,%s)", (name, description))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("add_service error:", e)
        return False
    finally:
        conn.close()

def update_service(service_id, new_name, new_desc):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE services
                SET service_name=%s, description=%s
                WHERE service_id=%s
            """, (new_name, new_desc, service_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("update_service error:", e)
        return False
    finally:
        conn.close()


# ---------- Bookings & Notifications ----------
def create_booking(user_id, vendor_id, service_id, style_choice, booking_date):
    conn = get_connection()
    created_at = datetime.now().replace(microsecond=0)
    try:
        with conn.cursor() as cur:
            # 1️⃣ Check if vendor is already booked on this date
            cur.execute("""
                SELECT * FROM bookings
                WHERE vendor_id=%s AND booking_date=%s
            """, (vendor_id, booking_date))
            existing = cur.fetchone()
            if existing:
                # Vendor already booked on that date
                print(f"Booking failed: Vendor #{vendor_id} is already booked on {booking_date}.")
                return None  # or return False if you prefer

            # 2️⃣ Fetch vendor price & rating
            cur.execute("SELECT price, rating FROM vendors WHERE vendor_id=%s", (vendor_id,))
            row = cur.fetchone()
            price = row.get('price', 0) if row else 0
            rating = row.get('rating', 0.0) if row else 0.0

            # 3️⃣ Insert booking
            cur.execute("""
                INSERT INTO bookings (user_id, vendor_id, service_id, style_choice, booking_date, created_at, price, rating)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (user_id, vendor_id, service_id, style_choice, booking_date, created_at, price, rating))

            booking_id = cur.lastrowid

            # 4️⃣ Create notification
            msg = f"New booking #{booking_id} for service {service_id} on {booking_date} (style: {style_choice})"
            cur.execute("INSERT INTO notifications (vendor_id, booking_id, message, created_at) VALUES (%s,%s,%s,%s)",
                        (vendor_id, booking_id, msg, created_at))
        conn.commit()
        return booking_id
    except Exception as e:
        conn.rollback()
        print("create_booking error:", e)
        return None
    finally:
        conn.close()


def list_bookings_for_user(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT b.*, v.vendor_name, s.service_name
                FROM bookings b
                LEFT JOIN vendors v ON b.vendor_id = v.vendor_id
                LEFT JOIN services s ON b.service_id = s.service_id
                WHERE b.user_id=%s
                ORDER BY b.created_at DESC
            """, (user_id,))
            return cur.fetchall()
    finally:
        conn.close()

def list_all_bookings():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT b.*, u.name as customer_name, v.vendor_name, s.service_name
                FROM bookings b
                LEFT JOIN users u ON b.user_id = u.user_id
                LEFT JOIN vendors v ON b.vendor_id = v.vendor_id
                LEFT JOIN services s ON b.service_id = s.service_id
                ORDER BY b.created_at DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()

def update_booking_status(booking_id, new_status):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE bookings SET status=%s WHERE booking_id=%s", (new_status, booking_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("update_booking_status error:", e)
        return False
    finally:
        conn.close()

def list_notifications():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT n.*, v.vendor_name FROM notifications n
                LEFT JOIN vendors v ON n.vendor_id = v.vendor_id
                ORDER BY n.created_at DESC
            """)
            return cur.fetchall()
    finally:
        conn.close()

def mark_day_as_paid(user_id, booking_date):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE bookings 
                SET payment_status='Paid' 
                WHERE user_id=%s AND booking_date=%s
            """, (user_id, booking_date))
        conn.commit()
    except Exception as e:
        print("mark_day_as_paid error:", e)
        conn.rollback()
    finally:
        conn.close()


def check_payment_status(user_id, booking_date):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) AS paid_count
                FROM bookings
                WHERE user_id=%s AND booking_date=%s AND payment_status='Paid'
            """, (user_id, booking_date))
            result = cur.fetchone()
            return result and result.get('paid_count', 0) > 0
    except Exception as e:
        print("check_payment_status error:", e)
        return False
    finally:
        conn.close()





# ---------- Admin helpers (CHANGED/ADDED) ----------
def delete_service(service_id):
    # CHANGED: use get_connection + proper handling
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM services WHERE service_id=%s", (service_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("delete_service error:", e)
        return False
    finally:
        conn.close()

def delete_vendor(vendor_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM vendors WHERE vendor_id=%s", (vendor_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("delete_vendor error:", e)
        return False
    finally:
        conn.close()

def service_has_bookings(service_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM bookings WHERE service_id=%s", (service_id,))
            r = cur.fetchone()
            return (r and r.get('cnt', 0) > 0)
    finally:
        conn.close()

def vendor_has_bookings(vendor_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM bookings WHERE vendor_id=%s", (vendor_id,))
            r = cur.fetchone()
            return (r and r.get('cnt', 0) > 0)
    finally:
        conn.close()

def list_vendors():
    # CHANGED: return basic vendor list used in admin UI etc.
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT vendor_id, vendor_name, service_id, contact, details, image_path, price, rating FROM vendors ORDER BY vendor_id")
            return cur.fetchall()
    finally:
        conn.close()

def cancel_booking(booking_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM bookings WHERE booking_id=%s", (booking_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print("cancel_booking error:", e)
        return False
    finally:
        conn.close()


# ---------- Seeder (run once) ----------
def seed_sample_data():
    if list_services():
        print("Services already exist — skipping seed.")
        return
    print("Seeding services and vendors...")
    add_service("Venue", "Banquets, lawns and elegant halls")
    add_service("Photography", "Candid, Cinematic and Traditional")
    add_service("Catering", "Buffet, plated meals and live counters")
    add_service("Makeup", "Bridal and guest makeup")
    add_service("Music/DJ", "DJ and live music")

    services = list_services()
    for s in services:
        if s['service_name'] == "Venue":
            add_vendor("Royal Venue Palace", s['service_id'], "9000001111", "Large palace with stage", "assets/venue1.jpg", price=80000, rating=4.6)
            add_vendor("Garden Greens Lawn", s['service_id'], "9000001212", "Outdoor lawn with fairy lights", "assets/venue2.jpg", price=45000, rating=4.2)
            add_vendor("Crystal Banquet Hall", s['service_id'], "9000001313", "Luxurious indoor banquet hall", "assets/venue3.jpg", price=95000, rating=4.8)
            add_vendor("Sunset Lawn", s['service_id'], "9000001414", "Open-air lawn with sunset view", "assets/venue4.jpg", price=39000, rating=4.1)
        if s['service_name'] == "Photography":
            add_vendor("LensQueen Photography", s['service_id'], "9000003333", "Candid & cinematic", "assets/photo1.jpg", price=40000, rating=4.7)
            add_vendor("CineShots Studio", s['service_id'], "9000003334", "Traditional & cinematic", "assets/photo2.jpg", price=32000, rating=4.4)
        if s['service_name'] == "Catering":
            add_vendor("Gourmet Catering Co", s['service_id'], "9000006666", "Buffet & plated menus", "assets/cater1.jpg", price=70000, rating=4.3)
        if s['service_name'] == "Makeup":
            add_vendor("BeautyPro Makeup", s['service_id'], "9000004444", "Bridal makeup experts", "assets/makeup1.jpg", price=12000, rating=4.5)
        if s['service_name'] == "Music/DJ":
            add_vendor("BeatWave DJs", s['service_id'], "9000005555", "Top DJs and sound systems", "assets/dj1.jpg", price=25000, rating=4.0)

    # create admin user if not exists
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email=%s", ("admin@wms.local",))
            if not cur.fetchone():
                create_user("Admin", "admin@wms.local", "adminpass", is_admin=1)
                print("Admin created: admin@wms.local / adminpass")
    finally:
        conn.close()
