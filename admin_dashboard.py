# admin_dashboard.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import database


def open_admin_dashboard(admin_user, parent=None):
    win = tk.Toplevel(parent) if parent else tk.Tk()
    win.title("Admin Dashboard")
    win.geometry("1000x900")
    win.resizable(True, True)

    # ---- Load Background Image ----
    try:
        bg_img = Image.open("assets/admin_bg.jpg")
        bg_img = bg_img.resize((1000, 650))  # ✅ Not fullscreen
        bg = ImageTk.PhotoImage(bg_img)
        bg_label = tk.Label(win, image=bg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.image = bg
    except:
        win.configure(bg="#FFF8E1")

    # ---- Title ----
    tk.Label(
        win,
        text=f"Admin Dashboard — {admin_user['name']}",
        font=("Georgia", 26, "bold"),
        fg="#4B2C20",
        bg="#F9E5C8",
        padx=16, pady=8
    ).pack(pady=20)

    # ---- Button Frame ----
    btn_frame = tk.Frame(win, bg="", highlightthickness=0)
    btn_frame.pack(expand=True)

    def make_button(text, cmd):
        return tk.Button(
            btn_frame,
            text=text,
            command=cmd,
            font=("Century Gothic", 16, "bold"),
            bg="#D4AF37", fg="black",
            activebackground="#EEDC82",
            relief="raised", bd=4,
            padx=20, pady=10,
            cursor="hand2"
        )

    buttons = [
        ("📋 View Bookings", lambda: show_bookings(win)),
        ("🔔 View Notifications", lambda: show_notifications(win)),
        ("➕ Add Service", lambda: add_service_ui(win)),
        ("👨‍🍳 Add Vendor", lambda: add_vendor_ui(win)),
        ("✏ Update Service", lambda: update_service_ui(win)),
        ("🛠 Update Vendor", lambda: update_vendor_ui(win)),
        ("🗑 Delete Service", lambda: delete_service_ui(win)),  # ✅ Added
        ("❌ Delete Vendor", lambda: delete_vendor_ui(win)),    # ✅ Added
        ("🚪 Logout", lambda: logout(win, parent))
    ]

    for txt, cmd in buttons:
        make_button(txt, cmd).pack(pady=12)

       
def logout(win, parent):
    win.destroy()
    if parent:
        parent.deiconify()


# --------- Bookings & Notifications (Unchanged) ---------
def show_bookings(parent):
    top = tk.Toplevel(parent)
    top.title("All Bookings")
    top.state('zoomed')
    top.geometry("900x600")
    top.configure(bg="#fce4ec")  # Soft pink fallback background

    # Background image optional
    try:
        bg_img_raw = Image.open("background_floral.jpg")
        bg_img_raw = bg_img_raw.resize((1000, 800))
        bg_img = ImageTk.PhotoImage(bg_img_raw)
        bg_label = tk.Label(top, image=bg_img)
        bg_label.image = bg_img
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        pass

    tk.Label(top,
             text="All Bookings",
             font=("Poppins", 18, "bold"),
             bg="#fce4ec",
             fg="#880e4f"
             ).pack(pady=10)

    canvas = tk.Canvas(top, bg="#fce4ec", highlightthickness=0)
    scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#fce4ec")
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=10)
    scrollbar.pack(side="right", fill="y")

    rows = database.list_all_bookings()

    col = 0
    row = 0
    for b in rows:
        card = tk.Frame(scroll_frame,
                        bg="#ffffff",
                        bd=2,
                        relief="groove",
                        padx=18,
                        pady=16)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="n")

        tk.Label(card,
                 text=f"Booking ID: {b['booking_id']}",
                 font=("Poppins", 14, "bold"),
                 bg="#ffffff").pack(anchor="w")
        tk.Label(card,
                 text=f"Service: {b['service_name']}",
                 font=("Poppins", 14),
                 bg="#ffffff").pack(anchor="w")
        tk.Label(card,
                 text=f"Style: {b.get('style_choice', '-')}",
                 font=("Poppins", 14),
                 bg="#ffffff").pack(anchor="w")
        tk.Label(card,
                 text=f"Customer: {b.get('customer_name')} ",
                 font=("Poppins", 14),
                 bg="#ffffff").pack(anchor="w")
        tk.Label(card,
                 text=f"Vendor: {b.get('vendor_name')} ",
                 font=("Poppins", 14),
                 bg="#ffffff").pack(anchor="w")
        tk.Label(card,
                 text=f"Date: {b.get('booking_date')} ",
                 font=("Poppins", 14),
                 bg="#ffffff").pack(anchor="w")

        # Display price from bookings table
        tk.Label(card,
                 text=f"Price: ₹{b.get('price', 0):,}",
                 font=("Poppins", 14, "bold"),
                 bg="#ffffff").pack(anchor="w")

        tk.Label(card,
                 text=f"Status: {b['status']}",
                 font=("Poppins", 14, "bold"),
                 fg="#d81b60",
                 bg="#ffffff").pack(anchor="w", pady=(5, 2))

        btn_frame = tk.Frame(card, bg="#ffffff")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame,
                  text="Approve ✅",
                  font=("Poppins", 12, "bold"),
                  bg="#c8e6c9",
                  command=lambda bid=b['booking_id'], p=top: update_status(bid, "Approved", p)
                  ).pack(side="left", padx=6)

        tk.Button(btn_frame,
                  text="Reject ❌",
                  font=("Poppins", 12, "bold"),
                  bg="#ffcdd2",
                  command=lambda bid=b['booking_id'], p=top: update_status(bid, "Rejected", p)
                  ).pack(side="left", padx=6)

        col += 1
        if col == 6:
            col = 0
            row += 1


def update_status(booking_id, new_status, parent):
    ok = database.update_booking_status(booking_id, new_status)
    if ok:
        messagebox.showinfo("Status Updated", f"Booking {booking_id} set to {new_status}")
        parent.destroy()
        show_bookings(parent.master)
    else:
        messagebox.showerror("Error", "Failed to update booking status")


def show_notifications(parent):
    top = tk.Toplevel(parent)
    top.title("Notifications")
    top.geometry("1000x650")
    top.configure(bg="#fce4ec")
    try:
        bg_img_raw = Image.open("background_floral.jpg")
        bg_img_raw = bg_img_raw.resize((1400, 900))
        bg_img = ImageTk.PhotoImage(bg_img_raw)
        bg_label = tk.Label(top, image=bg_img)
        bg_label.image = bg_img
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        pass

    tk.Label(top,
             text="Notifications",
             font=("Poppins", 22, "bold"),
             bg="#fce4ec",
             fg="#880e4f"
             ).pack(pady=10)

    canvas = tk.Canvas(top, bg="#fce4ec", highlightthickness=0)
    scrollbar = tk.Scrollbar(top, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#fce4ec")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    rows = database.list_notifications()

    col = 0
    row = 0
    for n in rows:
        card = tk.Frame(scroll_frame,
                        bg="#ffffff",
                        bd=2,
                        relief="groove",
                        padx=16,
                        pady=12)
        card.grid(row=row, column=col, padx=18, pady=18, sticky="n")

        tk.Label(card,
                 text=f"Notification #{n['notification_id']}",
                 font=("Poppins", 14, "bold"),
                 bg="#ffffff",
                 fg="#d81b60").pack(anchor="w")

        tk.Label(card,
                 text=f"Vendor: {n.get('vendor_name', '-')} ",
                 font=("Poppins", 13),
                 bg="#ffffff").pack(anchor="w")

        tk.Label(card,
                 text=f"Message: {n.get('message', '-')} ",
                 font=("Poppins", 13),
                 wraplength=280,
                 justify="left",
                 bg="#ffffff").pack(anchor="w", pady=4)

        tk.Label(card,
                 text=f"Sent: {n.get('sent', '-')} ",
                 font=("Poppins", 12, "italic"),
                 bg="#ffffff").pack(anchor="w")

        col += 1
        if col == 4:
            col = 0
            row += 1


# ------------------- Services -------------------
def add_service_ui(parent):
    top = tk.Toplevel(parent)
    top.title("Add New Service")
    top.geometry("1000x650")
    top.configure(bg="#fce4ec")

    tk.Label(top,
             text="Add Service",
             font=("Poppins", 20, "bold"),
             bg="#fce4ec",
             fg="#880e4f"
             ).pack(pady=12)

    form_frame = tk.Frame(top, bg="white", bd=2, relief="ridge")
    form_frame.pack(fill="both", expand=True, padx=25, pady=10)

    tk.Label(form_frame,
             text="Service Name",
             font=("Poppins", 14, "bold"),
             bg="white"
             ).pack(pady=(18, 5))
    entry_name = tk.Entry(form_frame,
                          font=("Poppins", 13),
                          width=30,
                          relief="solid",
                          bd=1)
    entry_name.pack(ipady=5)

    tk.Label(form_frame,
             text="Short Description",
             font=("Poppins", 14, "bold"),
             bg="white"
             ).pack(pady=(18, 5))
    entry_desc = tk.Text(form_frame,
                         font=("Poppins", 13),
                         width=35,
                         height=7,
                         relief="solid",
                         bd=1)
    entry_desc.pack()

    def save_service():
        name = entry_name.get().strip()
        desc = entry_desc.get("1.0", "end").strip()
        if not name:
            messagebox.showwarning("Missing", "Service name required!")
            return
        database.add_service(name, desc)
        messagebox.showinfo("Success", "Service Added Successfully ✅")
        top.destroy()

    tk.Button(top,
              text="Add Service",
              command=save_service,
              font=("Poppins", 14, "bold"),
              fg="white",
              bg="#d81b60",
              activebackground="#ad1457",
              padx=20,
              pady=8
              ).pack(pady=15)


# ------------------- Vendors -------------------
def add_vendor_ui(parent):
    services = database.list_services()
    if not services:
        messagebox.showwarning("No Services", "Add a service first!")
        return

    top = tk.Toplevel(parent)
    top.title("Add Vendor")
    top.geometry("1000x700")  # Increased height
    top.configure(bg="#fce4ec")

    tk.Label(top,
             text="Add Vendor",
             font=("Poppins", 20, "bold"),
             bg="#fce4ec",
             fg="#880e4f"
             ).pack(pady=12)

    form_frame = tk.Frame(top, bg="white", bd=2, relief="ridge")
    form_frame.pack(fill="both", expand=True, padx=25, pady=10)

    # Vendor Name
    tk.Label(form_frame, text="Vendor Name", font=("Poppins", 14, "bold"), bg="white").pack(pady=(15, 5))
    e_name = tk.Entry(form_frame, font=("Poppins", 13), width=30, relief="solid", bd=1)
    e_name.pack(ipady=5)

    # Service Dropdown
    tk.Label(form_frame, text="Service", font=("Poppins", 14, "bold"), bg="white").pack(pady=(15, 5))
    svc_ids = [s['service_id'] for s in services]
    svc_var = tk.IntVar(value=svc_ids[0])
    svc_menu = tk.OptionMenu(form_frame, svc_var, *svc_ids)
    svc_menu.config(font=("Poppins", 12), width=20, bg="white")
    svc_menu.pack(ipady=3)

    # Contact
    tk.Label(form_frame, text="Contact", font=("Poppins", 14, "bold"), bg="white").pack(pady=(15, 5))
    e_contact = tk.Entry(form_frame, font=("Poppins", 13), width=30, relief="solid", bd=1)
    e_contact.pack(ipady=5)

    # Details
    tk.Label(form_frame, text="Details", font=("Poppins", 14, "bold"), bg="white").pack(pady=(15, 5))
    e_det = tk.Entry(form_frame, font=("Poppins", 13), width=30, relief="solid", bd=1)
    e_det.pack(ipady=5)

    # Image Path
    tk.Label(form_frame, text="Image Path (optional)", font=("Poppins", 13), bg="white").pack(pady=(10, 5))
    e_img = tk.Entry(form_frame, font=("Poppins", 12), width=30, relief="solid", bd=1)
    e_img.pack(ipady=4)

    # Price
    tk.Label(form_frame, text="Price (₹)", font=("Poppins", 14, "bold"), bg="white").pack(pady=(10, 5))
    e_price = tk.Entry(form_frame, font=("Poppins", 13), width=20, relief="solid", bd=1)
    e_price.pack(ipady=4)

    # Rating
    tk.Label(form_frame, text="Rating (0.0 - 5.0)", font=("Poppins", 14, "bold"), bg="white").pack(pady=(10, 5))
    e_rating = tk.Entry(form_frame, font=("Poppins", 13), width=20, relief="solid", bd=1)
    e_rating.pack(ipady=4)

    def do_add():
        vn = e_name.get().strip()
        contact = e_contact.get().strip()
        det = e_det.get().strip()
        img = e_img.get().strip()
        sid = svc_var.get()

        try:
            price = int(e_price.get().strip())
        except:
            price = 0
        try:
            rating = float(e_rating.get().strip())
        except:
            rating = 0.0

        database.add_vendor(vn, sid, contact, det, img if img else None, price, rating)
        messagebox.showinfo("Added ✅", "Vendor Added Successfully")
        top.destroy()

    tk.Button(top, text="Add Vendor", command=do_add,
              font=("Poppins", 14, "bold"), fg="white", bg="#d81b60", activebackground="#ad1457",
              padx=20, pady=8).pack(pady=15)


def update_vendor_ui(parent):
    vendors = database.list_vendors()
    services = database.list_services()
    if not vendors:
        messagebox.showwarning("No Vendors", "No vendors to update!")
        return

    top = tk.Toplevel(parent)
    top.title("Update Vendor")
    top.geometry("900x700")
    top.configure(bg="#fce4ec")

    tk.Label(top, text="Select Vendor to Update", font=("Poppins", 16, "bold"), bg="#fce4ec", fg="#880e4f").pack(pady=15)

    ven_map = {f"{v['vendor_id']} - {v['vendor_name']}": v for v in vendors}
    ven_var = tk.StringVar(value=list(ven_map.keys())[0])
    svc_map = {s['service_id']: s['service_name'] for s in services}

    dropdown = tk.OptionMenu(top, ven_var, *ven_map.keys())
    dropdown.config(font=("Poppins", 14), width=35, bg="white")
    dropdown.pack(ipady=10, pady=10)

    # Editable fields
    e_name = tk.Entry(top, font=("Poppins", 13), width=30)
    e_name.pack(pady=8)

    svc_var_inner = tk.IntVar()
    svc_dropdown = tk.OptionMenu(top, svc_var_inner, *svc_map.keys())
    svc_dropdown.config(font=("Poppins", 12), width=20, bg="white")
    svc_dropdown.pack(pady=8)

    contact = tk.Entry(top, font=("Poppins", 13), width=30)
    contact.pack(pady=8)

    details = tk.Entry(top, font=("Poppins", 13), width=35)
    details.pack(pady=8)

    image_path = tk.Entry(top, font=("Poppins", 12), width=35)
    image_path.pack(pady=8)

    price_entry = tk.Entry(top, font=("Poppins", 13), width=20)
    price_entry.pack(pady=8)

    rating_entry = tk.Entry(top, font=("Poppins", 13), width=20)
    rating_entry.pack(pady=8)

    def load_data(*args):
        v = ven_map[ven_var.get()]
        e_name.delete(0, "end")
        e_name.insert(0, v['vendor_name'])
        svc_var_inner.set(v['service_id'])
        contact.delete(0, "end")
        contact.insert(0, v.get('contact', ''))
        details.delete(0, "end")
        details.insert(0, v.get('details', ''))
        image_path.delete(0, "end")
        image_path.insert(0, v.get('image_path', ''))
        price_entry.delete(0, "end")
        price_entry.insert(0, v.get('price', 0))
        rating_entry.delete(0, "end")
        rating_entry.insert(0, v.get('rating', 0.0))

    ven_var.trace("w", load_data)
    load_data()

    def save_update():
        v = ven_map[ven_var.get()]
        vid = v['vendor_id']

        try:
            price = int(price_entry.get().strip())
        except:
            price = 0
        try:
            rating = float(rating_entry.get().strip())
        except:
            rating = 0.0

        database.update_vendor(
            vid,
            e_name.get().strip(),
            svc_var_inner.get(),
            contact.get().strip(),
            details.get().strip(),
            image_path.get().strip(),
            price,
            rating
        )
        messagebox.showinfo("Updated ✅", "Vendor Updated Successfully")
        top.destroy()

    tk.Button(top, text="Save Changes",
              font=("Poppins", 14, "bold"),
              bg="#d81b60", fg="white",
              padx=20, pady=8,
              command=save_update).pack(pady=15)



# ------------------- Delete & Update Services (unchanged) -------------------
# delete_service_ui(), delete_vendor_ui(), update_service_ui() remain unchanged except database.add_vendor/update_vendor now accept price and rating



def delete_service_ui(parent):
    services = database.list_services()
    if not services:
        messagebox.showwarning("No Services", "No services to delete!")
        return

    top = tk.Toplevel(parent)
    top.title("Delete Service")
    top.geometry("800x450")
    top.configure(bg="#fce4ec")

    tk.Label(top, text="Select Service to Delete",
             font=("Poppins", 16, "bold"),
             bg="#fce4ec", fg="#880e4f").pack(pady=15)

    svc_map = {f"{s['service_id']} - {s['service_name']}": s['service_id']
               for s in services}
    svc_var = tk.StringVar(value=list(svc_map.keys())[0])

    dropdown = tk.OptionMenu(top, svc_var, *svc_map.keys())
    dropdown.config(
        font=("Poppins", 14),   # Increase font
        width=35,               # Increase width (# of characters)
        bg="white",
        fg="#4a148c"
    )
    dropdown["menu"].config(
        font=("Poppins", 14),   # Increase menu item font
        bg="white"
    )
    dropdown.pack(ipady=10, pady=10)  # More internal padding

    
    def delete():
        selected = svc_var.get()
        sid = svc_map[selected]

        if database.service_has_bookings(sid):
            messagebox.showerror("Cannot Delete",
                                 "This service has active bookings!")
            return

        database.delete_service(sid)
        messagebox.showinfo("Deleted ✅", "Service Deleted Successfully")
        top.destroy()

    tk.Button(top, text="Delete Service",
              command=delete,
              font=("Poppins", 14, "bold"),
              bg="#d81b60", fg="white",
              padx=20, pady=8).pack(pady=15)


def delete_vendor_ui(parent):
    vendors = database.list_vendors()
    if not vendors:
        messagebox.showwarning("No Vendors", "No vendors to delete!")
        return

    top = tk.Toplevel(parent)
    top.title("Delete Vendor")
    top.geometry("800x450")
    top.configure(bg="#fce4ec")

    tk.Label(top, text="Select Vendor to Delete",
             font=("Poppins", 16, "bold"),
             bg="#fce4ec", fg="#880e4f").pack(pady=15)

    ven_map = {f"{v['vendor_id']} - {v['vendor_name']}":
               v['vendor_id'] for v in vendors}
    ven_var = tk.StringVar(value=list(ven_map.keys())[0])

    dropdown = tk.OptionMenu(top, ven_var, *ven_map.keys())
    dropdown.config(
        font=("Poppins", 14),   # Increase font size
        width=35,               # Bigger width
        bg="white",
        fg="#4a148c"            # Nice dark purple font color
    )
    dropdown["menu"].config(
        font=("Poppins", 14),   # Menu item font size
        bg="white"
    )
    dropdown.pack(ipady=10, pady=10)


    def delete():
        selected = ven_var.get()
        vid = ven_map[selected]

        if database.vendor_has_bookings(vid):
            messagebox.showerror("Cannot Delete",
                                 "This vendor has assigned bookings!")
            return

        database.delete_vendor(vid)
        messagebox.showinfo("Deleted ✅", "Vendor Deleted Successfully")
        top.destroy()

    tk.Button(top, text="Delete Vendor",
              command=delete,
              font=("Poppins", 14, "bold"),
              bg="#d81b60", fg="white",
              padx=20, pady=8).pack(pady=15)


def update_service_ui(parent):
    services = database.list_services()
    if not services:
        messagebox.showwarning("No Services", "No services to update!")
        return

    top = tk.Toplevel(parent)
    top.title("Update Service")
    top.geometry("900x500")
    top.configure(bg="#fce4ec")

    tk.Label(top, text="Select Service to Update",
             font=("Poppins", 16, "bold"),
             bg="#fce4ec", fg="#880e4f").pack(pady=15)

    svc_map = {f"{s['service_id']} - {s['service_name']}": s for s in services}
    svc_var = tk.StringVar(value=list(svc_map.keys())[0])

    dropdown = tk.OptionMenu(top, svc_var, *svc_map.keys())
    dropdown.config(font=("Poppins", 14), width=35, bg="white")
    dropdown.pack(ipady=10, pady=10)

    # --- Editable fields ---
    name_entry = tk.Entry(top, font=("Poppins", 13), width=30)
    name_entry.pack(pady=8)
    desc_entry = tk.Text(top, font=("Poppins", 13), width=40, height=6)
    desc_entry.pack(pady=8)

    # Load selected details
    def load_data(*args):
        selected = svc_var.get()
        svc = svc_map[selected]
        name_entry.delete(0, "end")
        name_entry.insert(0, svc['service_name'])
        desc_entry.delete("1.0", "end")
        desc_entry.insert("1.0", svc['description'])

    svc_var.trace("w", load_data)
    load_data()

    # Save updates
    def save_update():
        selected = svc_var.get()
        svc = svc_map[selected]
        sid = svc['service_id']

        new_name = name_entry.get().strip()
        new_desc = desc_entry.get("1.0", "end").strip()

        if not new_name:
            messagebox.showwarning("Missing", "Service name required!")
            return

        database.update_service(sid, new_name, new_desc)
        messagebox.showinfo("Updated ✅", "Service Updated Successfully")
        top.destroy()

    tk.Button(top, text="Save Changes",
              font=("Poppins", 14, "bold"),
              bg="#d81b60", fg="white",
              padx=20, pady=8,
              command=save_update).pack(pady=15)

