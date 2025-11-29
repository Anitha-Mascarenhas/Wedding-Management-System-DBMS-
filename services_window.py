# services_window.py
import tkinter as tk
from tkinter import messagebox
import database
import booking_window
from PIL import Image, ImageTk
import os

def open_services_window(parent, user):
    win = tk.Toplevel(parent)
    win.title("Services")
    win.geometry("1100x700")
    win.resizable(True, True)
    win.lift()
    win.focus_force()

    # Center the window on screen
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()
    x = (screen_w // 2) - (1100 // 2)
    y = (screen_h // 2) - (700 // 2)
    win.geometry(f"+{x}+{y}")

    # Background image (optional)
    try:
        bg_img = Image.open("assets/services_bg.jpg")
        bg_img = bg_img.resize((1100, 700))
        bg_img = ImageTk.PhotoImage(bg_img)
        bg_label = tk.Label(win, image=bg_img)
        bg_label.image = bg_img
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception:
        win.configure(bg="#fff")

    header = tk.Label(win, text="Choose a Service 🌸",
                      font=("Poppins", 24, "bold"),
                      bg="#ffffff")
    header.pack(pady=10)

    services = database.list_services()
    if not services:
        tk.Label(win, text="No services available.",
                 bg="#fff", font=("Poppins", 18)).pack(pady=20)
        return

    # Scrollable Frame (services grid)
    canvas = tk.Canvas(win, bg="#ffffff", highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#ffffff")

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")

    # Arrange services in a 2-column grid WITHOUT images (clean look)
    row, col = 0, 0
    for svc in services:
        frame_bg = "#FFF0F4"  # soft frame color
        svc_frame = tk.Frame(scroll_frame, bg=frame_bg,
                             relief="ridge", bd=2, padx=18, pady=18)
        svc_frame.grid(row=row, column=col, padx=30, pady=20, sticky="nsew")
        scroll_frame.grid_columnconfigure(col, weight=1)

        # Service title
        tk.Label(svc_frame, text=svc['service_name'],
                 font=("Poppins", 18, "bold"), bg=frame_bg).pack(pady=(6,4))

        # Service description centered and larger
        tk.Label(svc_frame, text=svc.get('description',''),
                 font=("Poppins", 13),
                 wraplength=380,
                 justify="center",
                 bg=frame_bg).pack(pady=(2,12))

        # Elegant 'View Options' button
        vbtn = tk.Button(svc_frame, text="View Options",
                         bg="#D81B60", fg="white",
                         font=("Poppins", 13, "bold"),
                         activebackground="#FF6EA8",
                         relief="raised", bd=3,
                         padx=12, pady=8,
                         command=lambda s=svc: open_vendor_list(win, s, user))
        vbtn.pack(pady=(4,2))

        # column increment & wrap
        col += 1
        if col > 1:
            col = 0
            row += 1

def open_vendor_list(parent, service, user):
    win = tk.Toplevel(parent)
    win.title(service['service_name'] + " Options")
    win.geometry("1100x700")
    win.resizable(True, True)
    win.lift()
    win.focus_force()

    # Background
    try:
        bg_img = Image.open("assets/vendor_bg.jpg")
        bg_img = bg_img.resize((1100, 700))
        bg_img = ImageTk.PhotoImage(bg_img)
        bg_label = tk.Label(win, image=bg_img)
        bg_label.image = bg_img
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception:
        win.configure(bg="#fff")

    tk.Label(win, text=service['service_name'],
             font=("Poppins", 22, "bold"),
             bg="#fff").pack(pady=12)

    vendors = database.list_vendors_by_service(service['service_id'])
    if not vendors:
        tk.Label(win, text="No vendors for this service yet.",
                 font=("Poppins", 16), bg="#fff").pack(pady=20)
        return

    # Scrollable vendor list
    canvas = tk.Canvas(win, bg="#ffffff", highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#ffffff")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")

    for v in vendors:
        frame_bg = "#FFF8F9"  # luxury tone
        card = tk.Frame(scroll_frame, bg=frame_bg, relief="raised", bd=2, padx=14, pady=14)
        card.pack(fill="x", pady=14, padx=22)

        # Left: image (if exists)
        left = tk.Frame(card, bg=frame_bg)
        left.pack(side="left", padx=(4,12))
        imgpath = v.get('image_path')
        if imgpath and os.path.exists(imgpath):
            try:
                img = Image.open(imgpath)
                img.thumbnail((240,160))
                tkimg = ImageTk.PhotoImage(img)
                lbl = tk.Label(left, image=tkimg, bg=frame_bg)
                lbl.image = tkimg
                lbl.pack()
            except Exception:
                tk.Label(left, text="[Image error]", width=32, height=8, bg="#eee").pack()
        else:
            tk.Label(left, text="[No image]", width=32, height=8, bg="#eee").pack()

        # Right: info
        right = tk.Frame(card, bg=frame_bg)
        right.pack(side="left", fill="x", expand=True, padx=(10,6))

        tk.Label(right, text=v['vendor_name'],
                 font=("Poppins", 18, "bold"),
                 fg="#880E4F", bg=frame_bg).pack(anchor="w")

        tk.Label(right, text=v.get('details',''), font=("Poppins", 13),
                 wraplength=600, justify="left", bg=frame_bg).pack(anchor="w", pady=(6,8))

        # Price and numeric rating row
        price_display = f"Price: ₹{v.get('price', 0):,}"
        rating_display = f"Rating: {v.get('rating', 0.0)}"  # <--- ONLY CHANGE HERE
        info_row = tk.Frame(right, bg=frame_bg)
        info_row.pack(anchor="w", pady=(0,8))
        tk.Label(info_row, text=price_display, font=("Poppins", 13, "bold"), bg=frame_bg, fg="#4a148c").pack(side="left", padx=(0,18))
        tk.Label(info_row, text=rating_display, font=("Poppins", 14), bg=frame_bg, fg="#f57c00").pack(side="left")

        # styles & book button
        styles = sample_styles_for_service(service['service_name'])
        tk.Label(right, text="Styles: " + ", ".join(styles), font=("Poppins", 12), bg=frame_bg).pack(anchor="w", pady=(4,8))

        bbtn = tk.Button(right, text="Book This Vendor",
                         bg="#D81B60", fg="white",
                         font=("Poppins", 13, "bold"),
                         activebackground="#FF6EA8",
                         relief="raised",
                         command=lambda ven=v, svc=service, st=styles: booking_window.open_booking_window(win, user, svc, ven, st))
        bbtn.pack(anchor="e", pady=6, padx=6)

def sample_styles_for_service(service_name):
    mapping = {
        "Venue": ["Royal", "Garden", "Minimal", "Traditional"],
        "Photography": ["Candid", "Cinematic", "Traditional", "Pre-wedding"],
        "Catering": ["Veg Buffet", "Non-Veg Buffet", "Live Counters", "Plated Meal"],
        "Makeup": ["Bridal", "Guest", "Reception", "Trial Session"],
        "Music/DJ": ["DJ Night", "Live Band", "Classical", "Bollywood Hits"],
        "Decoration": ["Floral", "LED", "Traditional", "Elegant"]
    }
    return mapping.get(service_name, ["Standard", "Premium"])
