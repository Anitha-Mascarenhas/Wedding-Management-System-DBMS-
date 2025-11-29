# main.py - Modern Wedding UI with CustomTkinter 💒
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import database
import user_dashboard
import admin_dashboard

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")  # Wedding theme

def center(win):
    """Center a window on screen (optional, not needed for fullscreen)"""
    win.update_idletasks()
    w = win.winfo_width()
    h = win.winfo_height()
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws//2) - (w//2)
    y = (hs//2) - (h//2)
    win.geometry(f'+{x}+{y}')

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wedding Management - Login")

        # Fullscreen window
        self.state('zoomed')  # maximized
        self.minsize(900, 550)

        # Background Image
        try:
            bg = ctk.CTkImage(Image.open("assets/bg_login.jpg"), size=(self.winfo_screenwidth(), self.winfo_screenheight()))
            bg_label = ctk.CTkLabel(self, image=bg, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            self.configure(fg_color="#FFE4EC")

        self.build_ui()

    def build_ui(self):
        frame = ctk.CTkFrame(self, width=380, height=450, corner_radius=25)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(frame, text="Wedding Management System",
                             font=("Gabriola", 30, "bold"))
        title.pack(pady=(25, 10))

        subtitle = ctk.CTkLabel(frame, text="Login",
                                font=("Poppins", 18, "bold"))
        subtitle.pack(pady=(0, 20))

        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Email", width=280)
        self.email_entry.pack(pady=8)

        self.pw_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=280)
        self.pw_entry.pack(pady=8)

        login_btn = ctk.CTkButton(frame, text="Login", width=280, height=38, command=self.login)
        login_btn.pack(pady=15)

        register_btn = ctk.CTkButton(frame, text="Register", width=280,
                                     fg_color="#FFC9DA", hover_color="#F4A4BE",
                                     text_color="black",
                                     command=self.open_register)
        register_btn.pack(pady=6)

        seed_btn = ctk.CTkButton(frame, text="Seed Sample Data", width=280,
                                 fg_color="#FFF3F8", text_color="black",
                                 hover_color="#FBDDE9",
                                 command=self.seed_data)
        seed_btn.pack(pady=10)

    def login(self):
        email = self.email_entry.get().strip()
        pw = self.pw_entry.get().strip()

        if not (email and pw):
            messagebox.showwarning("Input Missing", "Enter email & password")
            return

        user = database.authenticate_user(email, pw)
        if user:
            messagebox.showinfo("Success", f"Welcome {user['name']} 💐")
            self.withdraw()

            if user.get("is_admin") == 1:
                admin_dashboard.open_admin_dashboard(user, parent=self)
            else:
                user_dashboard.open_user_dashboard(user, parent=self)
        else:
            messagebox.showerror("Error", "Invalid login details")

    def open_register(self):
        reg = ctk.CTkToplevel(self)
        reg.title("Register")

        # Fullscreen registration window
        reg.state('zoomed')
        reg.minsize(500, 400)
        reg.grab_set()
        reg.focus_force()
        reg.transient(self)

        # Registration background image
        try:
            bg = ctk.CTkImage(Image.open("assets/bg_register.png"), size=(reg.winfo_screenwidth(), reg.winfo_screenheight()))
            bg_label = ctk.CTkLabel(reg, image=bg, text="")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            reg.configure(fg_color="#FFE4EC")

        frame = ctk.CTkFrame(reg, width=360, height=360, corner_radius=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="Register",
                     font=("Poppins", 22, "bold")).pack(pady=12)

        name_e = ctk.CTkEntry(frame, placeholder_text="Name", width=240)
        name_e.pack(pady=6)

        email_e = ctk.CTkEntry(frame, placeholder_text="Email", width=240)
        email_e.pack(pady=6)

        pw_e = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=240)
        pw_e.pack(pady=6)

        def do_register():
            name = name_e.get().strip()
            em = email_e.get().strip()
            pw = pw_e.get().strip()

            if not (name and em and pw):
                messagebox.showwarning("Incomplete", "Fill all fields")
                return

            ok = database.create_user(name, em, pw, is_admin=0)
            if ok:
                messagebox.showinfo("Success", "Registered! Login now ✅")
                reg.destroy()
            else:
                messagebox.showerror("Error", "Registration failed (Email exists?)")

        ctk.CTkButton(frame, text="Create Account", width=240,
                      command=do_register).pack(pady=15)

        center(reg)

    def seed_data(self):
        if messagebox.askyesno("Confirm", "Seed sample data? (Run once)"):
            database.seed_sample_data()
            messagebox.showinfo("Done", "Sample data inserted ✅")


if __name__ == "__main__":
    app = LoginApp()
    center(app)
    app.mainloop()
