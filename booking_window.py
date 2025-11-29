# booking_window.py
import tkinter as tk
from tkinter import messagebox
from database import create_booking
from datetime import datetime

def open_booking_window(parent, user, service, vendor, styles):
    win = tk.Toplevel(parent)
    win.title("Book Service")
    win.geometry("540x500")
    win.configure(bg="#FDE2E4")  # Soft pastel pink background

    # Heading
    tk.Label(
        win, 
        text=f"Booking: {service['service_name']} with {vendor['vendor_name']}", 
        font=("Poppins", 16, "bold"), 
        bg="#FDE2E4", 
        fg="#880E4F"  # Deep pink accent
    ).pack(pady=15)

    # Display vendor price & numeric rating for clarity
    price_val = vendor.get('price', 0)
    rating_val = vendor.get('rating', 0.0)
    try:
        rating_val = float(rating_val)
    except Exception:
        rating_val = 0.0

    info_frame = tk.Frame(win, bg="#FDE2E4")
    info_frame.pack(pady=(0,15))

    tk.Label(
        info_frame, 
        text=f"Price: ₹{price_val:,}", 
        font=("Poppins", 14, "bold"), 
        bg="#FDE2E4", 
        fg="#AD1457"  # Slightly softer pink
    ).pack(pady=4)

    tk.Label(
        info_frame, 
        text=f"Rating: {rating_val} ★", 
        font=("Poppins", 13), 
        bg="#FDE2E4", 
        fg="#880E4F"
    ).pack(pady=2)

    # Style choice
    tk.Label(win, text="Choose style", font=("Poppins", 13, "bold"), bg="#FDE2E4", fg="#880E4F").pack(anchor="w", padx=20)
    style_var = tk.StringVar(value=styles[0] if styles else "")
    style_menu = tk.OptionMenu(win, style_var, *styles)
    style_menu.config(font=("Poppins", 12), bg="#F8BBD0", fg="#4A148C", width=20, relief="raised")  # Pastel pink dropdown
    style_menu.pack(padx=20, pady=8)

    # Booking date
    tk.Label(win, text="Booking Date (YYYY-MM-DD)", font=("Poppins", 13, "bold"), bg="#FDE2E4", fg="#880E4F").pack(anchor="w", padx=20)
    date_entry = tk.Entry(win, font=("Poppins", 12), width=22, bg="#FFE4E1", fg="#880E4F", relief="solid", bd=1)
    date_entry.pack(padx=20, pady=8)
    date_entry.insert(0, datetime.now().date().isoformat())

    def do_book():
        sd = date_entry.get().strip()
        try:
            booking_date = datetime.strptime(sd, "%Y-%m-%d").date()
        except Exception:
            messagebox.showerror("Error", "Enter date as YYYY-MM-DD")
            return

        bid = create_booking(user['user_id'], vendor['vendor_id'], service['service_id'], style_var.get(), booking_date)
        if bid:
            messagebox.showinfo("Booked", f"Booking #{bid} successful!\nPrice: ₹{price_val:,}\nWe will notify the vendor.")
            win.destroy()
        else:
            messagebox.showerror("Error", "Booking failed.")

    tk.Button(
        win, 
        text="Confirm Booking", 
        command=do_book, 
        bg="#FF80AB",  # Pastel pink button
        fg="white", 
        font=("Poppins", 14, "bold"), 
        activebackground="#F48FB1", 
        activeforeground="white", 
        relief="raised", 
        bd=2, 
        padx=12, 
        pady=6
    ).pack(pady=20)
