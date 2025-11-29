# user_dashboard.py
import customtkinter as ctk
from PIL import Image, ImageTk
import database
from database import cancel_booking
import services_window

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")


def open_user_dashboard(user, parent):
    win = ctk.CTkToplevel(parent)
    win.title("User Dashboard")
    win.geometry("1000x650")
    win.grab_set()
    win.focus_force()

    # --- General background image ---
    try:
        bg_img = ctk.CTkImage(Image.open("assets/dashboard_bg.jpg").resize((1000, 650)), size=(1000, 650))
        bg_label = ctk.CTkLabel(win, image=bg_img, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        win.configure(fg_color="#FFFFFF")  # fallback color

    # --- Header ---
    header = ctk.CTkLabel(win, text=f"Hello, {user['name']} 🌸",
                          font=("Gabriola", 30, "bold"))
    header.pack(pady=(20, 15))

    # --- Frame for horizontal options ---
    options_frame = ctk.CTkFrame(win, fg_color="#FFFFFF", corner_radius=20)
    options_frame.pack(pady=15, padx=20, fill="x")

    # --- Option definitions ---
    options = [
        {"name": "Browse Services", "img": "assets/services_icon.jpg",
         "cmd": lambda: services_window.open_services_window(win, user)},
        {"name": "My Bookings", "img": "assets/bookings_icon.jpg",
         "cmd": lambda: show_my_bookings(win, user)},
        {"name": "Logout", "img": "assets/logout_icon.png",
         "cmd": lambda: logout(win, parent)}
    ]

    # --- Horizontal layout with image + button ---
    for opt in options:
        frame = ctk.CTkFrame(options_frame, fg_color="#FFE4EC", corner_radius=15)
        frame.pack(side="left", expand=True, padx=20, pady=20)

        # Load square image
        try:
            img = Image.open(opt["img"]).resize((120, 120))
            photo = ImageTk.PhotoImage(img)
        except:
            photo = None

        if photo:
            img_label = ctk.CTkLabel(frame, image=photo, text="")
            img_label.image = photo
            img_label.pack(pady=(15, 10))
            img_label.bind("<Button-1>", lambda e, cmd=opt["cmd"]: cmd())

        # Button below image
        btn = ctk.CTkButton(frame, text=opt["name"], width=140, command=opt["cmd"])
        btn.pack(pady=(0, 15))


def logout(win, parent):
    win.destroy()
    parent.deiconify()


def show_my_bookings(parent, user):
    top = ctk.CTkToplevel(parent)
    top.title("My Bookings")
    top.geometry("950x600")
    top.grab_set()
    top.focus_force()

    # --- Background image ---
    try:
        bg_img = ctk.CTkImage(Image.open("assets/bookings_bg.jpg").resize((950, 600)), size=(950, 600))
        bg_label = ctk.CTkLabel(top, image=bg_img, text="")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        top.configure(fg_color="#FFFFFF")

    # Header
    header = ctk.CTkLabel(top, text="📖 My Bookings", font=("Poppins", 20, "bold"))
    header.pack(pady=15)

    bookings = database.list_bookings_for_user(user['user_id'])
    if not bookings:
        ctk.CTkLabel(top, text="No bookings yet.", font=("Poppins", 16)).pack(pady=20)
        return

    # --- Scrollable frame ---
    container = ctk.CTkFrame(top, fg_color="#FFFFFF")
    container.pack(fill="both", expand=True, padx=15, pady=10)

    canvas = ctk.CTkCanvas(container, borderwidth=0, highlightthickness=0)
    scroll_frame = ctk.CTkFrame(canvas)
    scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scroll_frame.bind("<Configure>", on_frame_configure)

    # --- Booking cards (3 per row) ---
    STATUS_COLOR = {"Pending": "#FFA500", "Confirmed": "#28a745", "Cancelled": "#dc3545"}
    daily_totals = {}

    columns_per_row = 3
    row = 0
    col = 0
    scroll_frame.grid_columnconfigure((0, 1, 2), weight=1)

    for i, b in enumerate(bookings):
        booking_date = b.get('booking_date')
        daily_totals[booking_date] = daily_totals.get(booking_date, 0) + (b.get('price', 0) or 0)

        card = ctk.CTkFrame(scroll_frame, corner_radius=15, fg_color="#FFE4EC", width=280, height=220)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="n")

        info_text = (
            f"Booking id: {b['booking_id']}\n"
            f"{b['service_name']} - {b.get('style_choice', '-')}\n"
            f"Vendor: {b.get('vendor_name', '-')}\n"
            f"Date: {b.get('booking_date')}"
        )
        ctk.CTkLabel(card, text=info_text, font=("Poppins", 14), justify="left").pack(anchor="w", padx=10, pady=(10, 4))

        price_val = b.get('price', 0)
        rating_val = b.get('rating', 0.0)
        try:
            rating_val = float(rating_val)
        except Exception:
            rating_val = 0.0
        ctk.CTkLabel(card, text=f"Price: ₹{price_val:,}", font=("Poppins", 14, "bold")).pack(anchor="w", padx=10, pady=(0, 2))
        ctk.CTkLabel(card, text=f"Rating: {rating_val}", font=("Poppins", 14)).pack(anchor="w", padx=10, pady=(0, 6))

        status = b.get("status", "Pending")
        color = STATUS_COLOR.get(status, "#FFA500")
        status_frame = ctk.CTkFrame(card, fg_color=color, corner_radius=10)
        status_frame.pack(anchor="e", padx=10, pady=5)
        ctk.CTkLabel(status_frame, text=status, text_color="white",
                     font=("Poppins", 12, "bold")).pack(padx=8, pady=4)

        if status == "Pending":
            ctk.CTkButton(
                card, text="Cancel Booking", width=150,
                fg_color="#dc3545", hover_color="#ff4d4d",
                command=lambda bid=b['booking_id']: cancel_booking(top, bid, user)
            ).pack(anchor="e", padx=10, pady=(0, 10))

        # move to next column/row
        col += 1
        if col == columns_per_row:
            col = 0
            row += 1

    # --- Daily Bill Section with Payment Option ---
    from tkinter import messagebox
    if daily_totals:
        bill_frame = ctk.CTkFrame(scroll_frame, fg_color="#FFF0F5", corner_radius=15)
        bill_frame.grid(row=row + 1, column=0, columnspan=3, pady=20, padx=10, sticky="ew")
        ctk.CTkLabel(bill_frame, text="💰 Daily Total Bills", font=("Poppins", 16, "bold")).pack(pady=(10, 10))

        for date, total in daily_totals.items():
            row_frame = ctk.CTkFrame(bill_frame, fg_color="#FFE4EC", corner_radius=10)
            row_frame.pack(fill="x", padx=15, pady=6)

            ctk.CTkLabel(row_frame, text=f"{date}: ₹{total:,}", font=("Poppins", 14)).pack(side="left", padx=15, pady=6)

            paid = database.check_payment_status(user['user_id'], date)
            if paid:
                ctk.CTkLabel(row_frame, text="Paid ✅", text_color="green",
                             font=("Poppins", 13, "bold")).pack(side="right", padx=15)
            else:
                ctk.CTkButton(row_frame, text="Pay Now", width=90, fg_color="#28a745",
                              hover_color="#34d058",
                              command=lambda d=date, amt=total: pay_for_day(top, user, d, amt)).pack(side="right", padx=15)


def cancel_booking(top, booking_id, user):
    from tkinter import messagebox
    if messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?"):
        database.cancel_booking(booking_id)
    

        messagebox.showinfo("Cancelled", "Booking has been cancelled.")
        top.destroy()
        show_my_bookings(top.master, user)


def pay_for_day(top, user, booking_date, amount):
    from tkinter import messagebox
    database.mark_day_as_paid(user['user_id'], booking_date)
    messagebox.showinfo("Payment Successful", f"Paid ₹{amount:,} for bookings on {booking_date}")
    top.destroy()
    show_my_bookings(top.master, user)


def check_if_paid(user_id, booking_date):
    return database.check_payment_status(user_id, booking_date)
