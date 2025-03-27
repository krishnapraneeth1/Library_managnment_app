from customtkinter import CTkImage
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error, IntegrityError
from PIL import Image, ImageTk
import customtkinter as ctk
from datetime import datetime, timedelta
import os
from fpdf import FPDF
import re


db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123"
)
cursor = db_connection.cursor()

# Step 2: Create Database
cursor.execute("CREATE DATABASE IF NOT EXISTS library_management")
cursor.close()
db_connection.close()

# Step 3: Connect to the Database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@123",
    database="library_management"
)
cursor = db_connection.cursor()

# Step 4: Create Tables with Role Management
tables = {
    "User": """
    CREATE TABLE IF NOT EXISTS User (
        userid INT PRIMARY KEY AUTO_INCREMENT,
        firstname VARCHAR(100) NOT NULL,
        lastname VARCHAR(100) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        address1 VARCHAR(255),
        city VARCHAR(100),
        state VARCHAR(100),
        zipcode VARCHAR(10)
    )""",
    
    "Roles": """
    CREATE TABLE IF NOT EXISTS Roles (
        roleid INT PRIMARY KEY AUTO_INCREMENT,
        userid INT UNIQUE,
        role ENUM('Admin', 'User') NOT NULL DEFAULT 'User',
        FOREIGN KEY (userid) REFERENCES User(userid) ON DELETE CASCADE
    )""",

    "Book": """
    CREATE TABLE IF NOT EXISTS Book (
        bookid INT PRIMARY KEY AUTO_INCREMENT,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        category VARCHAR(100),
        author VARCHAR(255) NOT NULL
    )""",
    
    "Transaction": """
    CREATE TABLE IF NOT EXISTS Transaction (
        transactionid INT PRIMARY KEY AUTO_INCREMENT,
        userid INT,
        bookid INT,
        transactiondate DATE NOT NULL,
        returndate DATE,
        status ENUM('Pending', 'Approved', 'Rejected', 'Borrowed', 'Returned', 'Overdue') NOT NULL,
        FOREIGN KEY (userid) REFERENCES User(userid) ON DELETE CASCADE,
        FOREIGN KEY (bookid) REFERENCES Book(bookid) ON DELETE CASCADE
    )"""
}

# Step 5: Create tables if they do not exist
for table_name, create_query in tables.items():
    cursor.execute(create_query)

# Step 6: Insert Default Admin User
cursor.execute("SELECT COUNT(*) FROM User WHERE email = 'admin@library.com'")
if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO User (firstname, lastname, email, password, city, state, zipcode) VALUES "
        "('Admin', 'User', 'admin@library.com', 'Admin123', 'LibraryCity', 'LibraryState', '00000')"
    )
    admin_user_id = cursor.lastrowid
    cursor.execute("INSERT INTO Roles (userid, role) VALUES (%s, 'Admin')", (admin_user_id,))
    db_connection.commit()

cursor.close()
db_connection.close()
print("Database setup completed successfully!")

# --- GUI Application ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1200x750")
        self.resizable(False, False)
        self.home_screen()
    
    def home_screen(self):
        """Home Screen with Login and Register buttons"""
        image_path = "UI/home_screen.png"
        self.bg_image = Image.open(image_path).resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)

        login_button = ctk.CTkButton(self, text="Login", width=130, height=40, command=self.login_screen)
        login_button.place(relx=0.40, rely=0.70, anchor="center")

        register_button = ctk.CTkButton(self, text="Register", width=130, height=40, command=self.registration_screen)
        register_button.place(relx=0.60, rely=0.70, anchor="center")


        
    def login_screen(self):
        # Load and Display Background Image
        image_path = "UI/intropage.jpg"  # Ensure you have this image in the directory
        self.bg_image = Image.open(image_path)
        self.bg_image = self.bg_image.resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)
        
        # Foreground UI elements (placed directly on top of the image)
        self.heading = ctk.CTkLabel(self, text="Effortless Library Access at Your Fingertips", font=("Arial", 24, "bold"), fg_color="#FEFEF2", text_color="black")
        self.heading.place(relx=0.05, rely=0.05, anchor="nw")
        # login_label = ctk.CTkLabel(self, text="Login", font=("Arial", 20, "bold"), fg_color="#FEFEF2", text_color="black")
        # login_label.place(relx=0.5, rely=0.90, anchor="center")
        
        # Username Entry
        username_label = ctk.CTkLabel(self, text="Username", font=("Arial", 20, "bold"), fg_color="#FEFEF2", text_color="black")
        username_label.place(x=100, y=180)
        self.username_entry = ctk.CTkEntry(self, width=300, height=40, font=("Arial", 18, "bold"), corner_radius=10, fg_color="#FEFEF2")
        self.username_entry.place(x=100, y=210)
        
        # Password Entry
        password_label = ctk.CTkLabel(self, text="Password", font=("Arial", 20, "bold"), fg_color="#FEFEF2", text_color="black")
        password_label.place(x=100, y=270)
        self.password_entry = ctk.CTkEntry(self, width=300, height=40, font=("Arial", 18, "bold"), corner_radius=10, fg_color="#FEFEF2", show="*")
        self.password_entry.place(x=100, y=300)

        # Show Password Checkbox for login screen password entry
        self.show_password_var = ctk.BooleanVar()
        show_password_checkbox = ctk.CTkCheckBox(self, text="Show Password", variable=self.show_password_var,
                    font=("Arial", 12), bg_color="#FEFEF2", text_color="black", command=self.login_toggle_password)
        show_password_checkbox.place(x=410, y=310)
        
        # Forgot Password
        forgot_password = ctk.CTkLabel(self, text="Forgot Password", font=("Arial", 12, "underline"), cursor="hand2", fg_color="#FEFEF2", text_color="black")
        forgot_password.place(x=100, y=350)
        forgot_password.bind("<Button-1>", lambda e: self.forgot_password_screen())
        
        # Buttons
        login_button = ctk.CTkButton(self, text="Login", width=130, height=40, corner_radius=10, fg_color="#1E73BE", hover_color="#155A99", command=self.login_authentication)
        login_button.place(x=100, y=400)
        
        register_button = ctk.CTkButton(self, text="Home", width=130, height=40, corner_radius=10, fg_color="black", hover_color="#8C8477", command=self.home_screen)
        register_button.place(x=250, y=400)

    #login_toggle_password
    def login_toggle_password(self):
        """Toggles visibility of the password fields"""
        show = "" if self.show_password_var.get() else "*"
        self.password_entry.configure(show=show)
    
    def registration_screen(self):
        # Load and Display Background Image
        image_path = "UI/Register.png"  # Ensure you have this image in the directory
        self.bg_image = Image.open(image_path)
        self.bg_image = self.bg_image.resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)

        # Field placements
        fields = [
            ("First Name", 80, 160), ("Last Name", 460, 160), ("Email", 840, 160),
            ("Address", 80, 280), ("City", 460, 280), ("State", 840, 280),
            ("Zip Code", 80, 400), ("Password", 460, 400), ("Confirm Password", 840, 400)
        ]

        self.entries = {}

        for text, x, y in fields:
            label = ctk.CTkLabel(self, text=text, font=("Arial", 18, "bold"), fg_color="#D9D9D9", text_color="black")
            label.place(x=x, y=y)
            show_text = False if "Password" in text else True  # Hide password fields by default
            entry = ctk.CTkEntry(self, width=280, height=45, font=("Arial", 20), bg_color="#D9D9D9",
                                corner_radius=10, fg_color="#D9D9D9", show="*" if "Password" in text else "")
            entry.place(x=x, y=y + 50)
            self.entries[text] = entry

        # Show Password Checkbox
        self.show_password_var = ctk.BooleanVar()
        show_password_checkbox = ctk.CTkCheckBox(self, text="Show Password", variable=self.show_password_var,
                            font=("Arial", 14),bg_color="#D9D9D9", text_color="black", command=self.toggle_password)
        show_password_checkbox.place(x=840, y=500)

        # Sign-Up Button
        signup_button = ctk.CTkButton(self, text="Sign Up", width=220, height=55, font=("Arial", 18, "bold"),
                                    bg_color="#D9D9D9", corner_radius=10, fg_color="#1E73BE",
                                    hover_color="#155A99", command=self.register_user)
        signup_button.place(x=500, y=570)

        # Back Button as Image
        self.back_image = Image.open("UI/back.png")
        self.back_image = self.back_image.resize((60, 60), Image.LANCZOS)
        self.back_photo = CTkImage(light_image=self.back_image, size=(60, 60))
        self.back_button = ctk.CTkButton(self, image=self.back_photo, text="", width=60, height=60, fg_color="#D9D9D9", hover_color="#D9D9D9", command=self.home_screen)
        self.back_button.place(x=1050, y=600)

    def toggle_password(self):
        """Toggles visibility of the password fields"""
        show = "" if self.show_password_var.get() else "*"
        self.entries["Password"].configure(show=show)
        self.entries["Confirm Password"].configure(show=show)



    def forgot_password_screen(self):
        """Displays the forgot password screen where users can reset their password."""
        
        # Load and Display Background Image
        image_path = "UI/forgot_password.png"  # Ensure you have this image in the directory
        self.bg_image = Image.open(image_path).resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)

        # Heading
        heading_label = ctk.CTkLabel(self, text="Forgot your Password?", font=("Arial", 30, "bold"), text_color="black", bg_color="#D9D9D9")
        heading_label.place(x=85, y=80)

        # Email Label & Entry
        email_label = ctk.CTkLabel(self, text="Enter Your Email", font=("Arial", 18, "bold"), text_color="black", bg_color="#D9D9D9")
        email_label.place(x=80, y=160)

        self.email_entry = ctk.CTkEntry(self, width=300, height=40, font=("Arial", 16))
        self.email_entry.place(x=80, y=210)

        # Verify Button
        verify_button = ctk.CTkButton(self, text="Verify", width=150, height=40, font=("Arial", 18, "bold"),
                        corner_radius=10, fg_color="black", hover_color="#8C8477", command=self.verify_email)
        verify_button.place(x=80, y=270)

        # Password Fields (Initially Hidden)
        self.new_password_label = ctk.CTkLabel(self, text="New Password", font=("Arial", 18, "bold"), text_color="black", bg_color="#D9D9D9")
        self.new_password_entry = ctk.CTkEntry(self, width=300, height=40, font=("Arial", 16), show="*")

        self.confirm_password_label = ctk.CTkLabel(self, text="Confirm Password", font=("Arial", 18, "bold"), text_color="black", bg_color="#D9D9D9")
        self.confirm_password_entry = ctk.CTkEntry(self, width=300, height=40, font=("Arial", 16), show="*")

        # Reset Password Button (Initially Hidden)
        self.reset_button = ctk.CTkButton(self, text="Reset Password", width=200, height=40, font=("Arial", 18, "bold"),
                                        corner_radius=10, fg_color="black", hover_color="#8C8477",
                                        command=self.submit_new_password)

        # Back Button to Login Screen
        back_icon = Image.open("UI/back.png").resize((60, 60))
        self.back_photo = CTkImage(light_image=back_icon, size=(60, 60))
        self.back_button = ctk.CTkButton(self, image=self.back_photo, text="", width=60, height=60, fg_color="#D9D9D9",
                        hover_color="#D9D9D9", command=self.login_screen)
        self.back_button.place(x=420, y=600)


    def verify_email(self):
        """Verifies if the entered email exists in the database."""
        email = self.email_entry.get().strip()

        if not email:
            messagebox.showerror("Error", "Please enter your email address.")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            cursor.execute("SELECT userid FROM User WHERE email=%s", (email,))
            user = cursor.fetchone()

            if not user:
                messagebox.showerror("Error", "No account found with this email.")
                return

            self.verified_user_id = user[0]  # Store user ID for resetting password

            messagebox.showinfo("Success", "Email verified. Enter your new password.")

            # Show password reset fields (aligned below email fields)
            self.new_password_label.place(x=80, y=320)
            self.new_password_entry.place(x=80, y=370)

            self.confirm_password_label.place(x=80, y=430)
            self.confirm_password_entry.place(x=80, y=480)

            self.reset_button.place(x=80, y=540)

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error verifying email: {e}")

        finally:
            cursor.close()
            conn.close()

    def submit_new_password(self):
        """Updates the password in the database if the user is verified."""
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all password fields.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        # Password validation
        if len(new_password) < 8 or not re.search("[a-z]", new_password) or not re.search("[A-Z]", new_password) or not re.search("[0-9]", new_password):
            messagebox.showerror("Error", "Password must have at least 8 characters, including upper/lowercase letters and numbers.")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            # Update password
            cursor.execute("UPDATE User SET password=%s WHERE userid=%s", (new_password, self.verified_user_id))
            conn.commit()

            messagebox.showinfo("Success", "Password reset successfully! Please log in with your new password.")
            self.login_screen()  # Redirect to login screen

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error resetting password: {e}")

        finally:
            cursor.close()
            conn.close()


            

    def register_user(self):
        """Registers a New User and Assigns 'User' or 'Admin' Role"""
        first_name = self.entries["First Name"].get().strip()
        last_name = self.entries["Last Name"].get().strip()
        email = self.entries["Email"].get().strip()
        password = self.entries["Password"].get().strip()
        city = self.entries["City"].get().strip()
        state = self.entries["State"].get().strip()
        zip_code = self.entries["Zip Code"].get().strip()

        # Ensure fields are filled
        if not all([first_name, last_name, email, password, city, state, zip_code]):
            messagebox.showerror("Error", "All fields are required!")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            # Check if email already exists
            cursor.execute("SELECT email FROM User WHERE email = %s", (email,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Email already exists. Please login!")
                return

            # Determine user role
            role = "Admin" if email.endswith("admin@library.com") else "User"

            # Insert user into User table
            query = "INSERT INTO User (firstname, lastname, email, password, city, state, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (first_name, last_name, email, password, city, state, zip_code))
            user_id = cursor.lastrowid  # Get last inserted user ID

            # Assign role to user
            cursor.execute("INSERT INTO Roles (userid, role) VALUES (%s, %s)", (user_id, role))

            conn.commit()
            messagebox.showinfo("Success", f"Registration Successful! You are registered as {role}. Please log in.")

            # Redirect to login screen
            self.login_screen()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def login_authentication(self):
        """Authenticate User and Redirect Based on Role"""
        email = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showerror("Error", "Both fields are required.")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            # Validate email and password
            query = "SELECT U.userid, U.firstname, U.lastname, R.role FROM User U JOIN Roles R ON U.userid = R.userid WHERE U.email = %s AND U.password = %s"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()

            if user:
                self.user_id, self.first_name, self.last_name, role = user

                if role == "Admin":
                    messagebox.showinfo("Login Successful", "Welcome, Admin!")
                    self.admin_dashboard()
                else:
                    messagebox.showinfo("Login Successful", f"Welcome {self.first_name}!")
                    self.book_catalog_screen()
            else:
                messagebox.showerror("Error", "Invalid email or password.")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
        finally:
            cursor.close()
            conn.close()


    def book_catalog_screen(self):
        image_path = "UI/catalog.png"
        self.bg_image = Image.open(image_path).resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)

        # Fetch book data
        book_titles, self.book_data = self.fetch_book_data()

        # Create dropdowns
        self.selected_values = {}

        def create_dropdown(label_text, values, relx, rely, event_handler):
            """Creates a dropdown with dynamically updatable values."""
            label = ctk.CTkLabel(self, text=label_text, font=("Arial", 18, "bold"), fg_color="#D9D9D9", text_color="black")
            label.place(relx=relx, rely=rely-0.03, anchor="w")  # Moved label up
            dropdown = ctk.CTkComboBox(self, values=values, width=280, height=45, font=("Arial", 18), corner_radius=10, fg_color="#D9D9D9", command=event_handler if event_handler else None)
            dropdown.place(relx=relx, rely=rely+0.04, anchor="w")  # Moved dropdown up slightly
            self.selected_values[label_text] = dropdown
            return dropdown

        # Dropdowns for filtering (moved slightly down)
        self.selected_values["Book Title"] = create_dropdown("Book Title", book_titles, 0.07, 0.25, self.update_book_details)
        self.selected_values["Author"] = create_dropdown("Author", [""], 0.07, 0.40, None)
        self.selected_values["Category"] = create_dropdown("Category", [""], 0.07, 0.55, None)

        # Book Information Section (moved up & rounded corners)
        book_info_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#E0DFDF")  # Increased corner_radius for round corners
        book_info_frame.place(relx=0.6, rely=0.20, relwidth=0.35, relheight=0.5, anchor="n")  # Moved up

        book_info_label = ctk.CTkLabel(book_info_frame, text="Book Information", font=("Arial", 20, "bold"), text_color="black")
        book_info_label.place(relx=0.5, rely=0.05, anchor="n")

        self.book_description_label = ctk.CTkLabel(book_info_frame, text="", wraplength=400,
                                                font=("Arial", 16), text_color="black", fg_color="transparent")
        self.book_description_label.place(relx=0.5, rely=0.5, anchor="center")

        # Add Image as Button
        self.back_image = Image.open("UI/logout.png")
        self.back_image = self.back_image.resize((60, 60), Image.LANCZOS)
        self.back_photo = CTkImage(light_image=self.back_image, size=(60, 60))
        self.back_button = ctk.CTkButton(self, image=self.back_photo, text="", width=60, height=60, fg_color="#D9D9D9", hover_color="#D9D9D9", command=self.login_screen)
        self.back_button.place(relx=0.28, rely=0.85, anchor="w")  # Moved to the right

        # add button to request book
        request_button = ctk.CTkButton(self, text="Request Book", width=220, height=55, font=("Arial", 18, "bold"),
                        bg_color="#D9D9D9", corner_radius=10, fg_color="#1E73BE",
                        hover_color="#155A99", command=self.request_book)
        request_button.place(relx=0.09, rely=0.70, anchor="w")
     

        # add image as button to view profile
        self.profile_image = Image.open("UI/user.png")
        self.profile_image = self.profile_image.resize((35, 35), Image.LANCZOS)
        self.profile_photo = ImageTk.PhotoImage(self.profile_image)
        self.profile_button = Button(self, image=self.profile_photo, bg="#D9D9D9", bd=0, cursor="hand2", command=self.profile_screen)
        self.profile_button.place(relx=0.28, rely=0.15, anchor="w")

        #add text under the profile button
        self.profile_label = ctk.CTkLabel(self, text="View Profile", font=("Arial", 12, "bold"), fg_color="#D9D9D9", text_color="black")
        self.profile_label.place(relx=0.27, rely=0.19, anchor="w")



    def update_book_details(self, choice=None):
        """Updates Author, Category, and Description when a Book Title is selected."""
        selected_title = self.selected_values["Book Title"].get()
        print(f"Selected Title: {selected_title}")  # Debugging

        # Find the corresponding book ID
        selected_book_id = None
        for book_id, book_info in self.book_data.items():
            if book_info["title"] == selected_title:
                selected_book_id = book_id
                break

        if selected_book_id:
            book_info = self.book_data[selected_book_id]
            print(f"Book Info: {book_info}")  # Debugging

            # Update Author dropdown with only the correct author
            self.selected_values["Author"].configure(values=[book_info["author"]])
            self.selected_values["Author"].set(book_info["author"])

            # Update Category dropdown with only the correct category
            self.selected_values["Category"].configure(values=[book_info["category"]])
            self.selected_values["Category"].set(book_info["category"])

            # Update book description
            self.book_description_label.configure(text=book_info["description"])

    def fetch_book_data(self):
        """Fetch all book details from the database and return structured data."""
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            # Fetch complete book details
            cursor.execute("SELECT bookid, title, author, category, description FROM Book")
            books = cursor.fetchall()

            # Store book details in a dictionary for filtering (mapped by book ID)
            book_data = {}
            book_titles = []

            for bookid, title, author, category, description in books:
                book_data[str(bookid)] = {"title": title, "author": author, "category": category, "description": description}
                book_titles.append(title)

            return book_titles, book_data  # Only return book titles initially

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error fetching book data: {e}")
            return [], {}
        finally:
            cursor.close()
            conn.close()



    def request_book(self):
        """Handles book request from the user."""
        selected_title = self.selected_values["Book Title"].get()
        selected_author = self.selected_values["Author"].get()

        if not selected_title:
            messagebox.showerror("Error", "Please select a book title.")
            return

        if not selected_author:
            messagebox.showerror("Error", "Please select Book.")
            return

        # Retrieve Book ID based on selected title
        selected_book_id = None
        for book_id, book_info in self.book_data.items():
            if book_info["title"] == selected_title:
                selected_book_id = book_id
                break

        if selected_book_id:
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
                cursor = conn.cursor()

                # Check if book is already requested by the user
                cursor.execute("SELECT * FROM Transaction WHERE userid = %s AND bookid = %s AND status = 'Pending'", 
                            (self.user_id, selected_book_id))
                if cursor.fetchone():
                    messagebox.showerror("Error", "You have already requested this book.")
                    return

                # Insert transaction with status 'Pending' (ensure correct data type)
                query = "INSERT INTO Transaction (userid, bookid, transactiondate, status) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (self.user_id, selected_book_id, datetime.now().date(), str("Pending")))
                conn.commit()

                messagebox.showinfo("Success", "Book request sent to admin for approval!")

            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")

            finally:
                cursor.close()
                conn.close()



    def profile_screen(self):
        # Load and Display Background Image
        image_path = "UI/profile.png"
        self.bg_image = Image.open(image_path)
        self.bg_image = self.bg_image.resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)
        # Fetch user details to display on the profile screen
        user_details = f"Hello, {self.first_name} {self.last_name}!"
        user_label = ctk.CTkLabel(self, text=user_details, font=("Arial", 35, "bold"), fg_color="#D9D9D9", text_color="black")
        user_label.place(relx=0.5, rely=0.31, anchor="center")

    


        # Fetch borrowed books for the current user
        self.borrowed_books = self.fetch_borrowed_books()
        # # Treeview to display borrowed books with larger font and expanded horizontally
        # Treeview Styling
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 15, "bold"), background="#D9D9D9", foreground="black")
        style.configure("Treeview", font=("Arial", 13), rowheight=45, background="#D9D9D9", foreground="black", fieldbackground="#D9D9D9")
        # Treeview Widget
        self.books_tree = ttk.Treeview(self, columns=("Book ID", "Title", "Due Date"), show="headings")
        self.books_tree.heading("Book ID", text="Book ID")
        self.books_tree.heading("Title", text="Title")
        self.books_tree.heading("Due Date", text="Due Date")

        # Set column widths and alignment according to the resolution
        self.books_tree.column("Book ID", width=100, anchor="center")
        self.books_tree.column("Title", width=400, anchor="center")
        self.books_tree.column("Due Date", width=150, anchor="center")
        # Place the Treeview to fit the resolution
        self.books_tree.place(relx=0.5, rely=0.73, anchor="center", relwidth=0.6, relheight=0.3)



        # Populate Treeview with borrowed books
        self.populate_borrowed_books()
        # Return Book Button
        return_button = ctk.CTkButton(self, text="Return Selected Book", width=200, height=40, font=("Arial", 16, "bold"),
                corner_radius=10, fg_color="red", hover_color="#8C8477", command=self.return_selected_book)
        return_button.place(relx=0.5, rely=0.95, anchor="center")

        # Back button to go back to the book catalog screen as image
        self.back_image = Image.open("UI/back.png")
        self.back_image = self.back_image.resize((70, 70), Image.LANCZOS)
        self.back_photo = CTkImage(light_image=self.back_image, size=(55, 55))
        self.back_button = ctk.CTkButton(self, image=self.back_photo, text="", width=55, height=55, fg_color="white", hover_color="white", command=self.book_catalog_screen)
        self.back_button.place(relx=0.95, rely=0.94, anchor="e")

    def fetch_borrowed_books(self):
        """Fetch all books borrowed by the current user."""
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            query = """
                SELECT t.bookid, b.title, t.returndate 
                FROM Transaction t 
                JOIN Book b ON t.bookid = b.bookid 
                WHERE t.userid = %s AND t.status = 'Borrowed'
            """
            cursor.execute(query, (self.user_id,))
            borrowed_books = cursor.fetchall()

            return borrowed_books

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error fetching borrowed books: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def populate_borrowed_books(self):
        """Populate the Treeview with borrowed books."""
        for row in self.books_tree.get_children():
            self.books_tree.delete(row)

        for book in self.borrowed_books:
            self.books_tree.insert("", "end", values=book)

    def return_selected_book(self):
        """Return the selected borrowed book."""
        selected_item = self.books_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a book to return.")
            return

        selected_book = self.books_tree.item(selected_item, "values")
        book_id = selected_book[0]  # Get the Book ID

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            # Update transaction status to "Returned"
            update_query = "UPDATE Transaction SET status = 'Returned' WHERE bookid = %s AND userid = %s"
            cursor.execute(update_query, (book_id, self.user_id))
            conn.commit()

            messagebox.showinfo("Success", "Book returned successfully!")

            # Refresh the borrowed books list
            self.borrowed_books = self.fetch_borrowed_books()
            self.populate_borrowed_books()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error returning book: {e}")
        finally:
            cursor.close()
            conn.close()
    def admin_dashboard(self):
        # Load and Display Background Image
        image_path = "UI/admin.png"  # Ensure you have this image in the directory
        self.bg_image = Image.open(image_path)
        self.bg_image = self.bg_image.resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)

        # Admin Welcome Message
        welcome_label = ctk.CTkLabel(self, text="Welcome Library Admin", font=("Arial", 28, "bold"), text_color="black",bg_color='white')
        welcome_label.place(relx=0.5, rely=0.40, anchor="center")

        # Function to create buttons with icons
        def create_button(text, icon_path, x, y, command):
            """Creates a button with an icon and text."""
            icon = Image.open(icon_path).resize((30, 30))
            icon_photo = CTkImage(light_image=icon, size=(30, 30))
            button = ctk.CTkButton(self, text=text, image=icon_photo, compound="right", width=220, height=60,
                                font=("Arial", 18, "bold"), corner_radius=10, fg_color="#D9D9D9",
                                text_color="black", hover_color="#C0C0C0", command=command)
            button.image = icon_photo  # Keep reference to avoid garbage collection
            button.place(x=x, y=y)

        # Add Book Button
        create_button("Add Book", "UI/plus.png", 180, 400, self.add_book_screen)

        # View Books Button
        create_button("View Books", "UI/books-stack-of-three.png", 480, 400, self.library_resource_list_screen)

        # Requests Button
        create_button("Requests", "UI/email.png", 780, 400, self.book_request_list_screen)

        # User Report Button
        create_button("User Report", "UI/approved.png", 350, 520, self.generate_user_report)

        # Books Report Button
        create_button("Books Report", "UI/approved.png", 650, 520, self.generate_library_resource_report)

        # Logout Button (Back Icon)
        logout_icon = Image.open("UI/logout.png").resize((60, 60))
        logout_photo = CTkImage(light_image=logout_icon, size=(60, 60))
        logout_button = ctk.CTkButton(self, image=logout_photo, text="", width=60, height=60,
                                    fg_color="white", hover_color="#D9D9D9", command=self.login_screen)
        logout_button.image = logout_photo  # Keep reference
        logout_button.place(x=1050, y=650)


    def add_book_screen(self):
    # Load and Display Background Image
        image_path = "UI/add_book.png"  # Ensure you have this image in the directory
        self.bg_image = Image.open(image_path)
        self.bg_image = self.bg_image.resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)

        # Set Background Color
        self.configure(bg="#D6D3CB")

        # Add Book Heading
        heading_label = ctk.CTkLabel(self, text="Add Book", font=("Arial", 24, "bold"), text_color="black", fg_color="#D6D3CB")
        heading_label.place(relx=0.75, rely=0.13, anchor="center")

        subtext_label = ctk.CTkLabel(self, text="Please fill the below details for adding a new book",
                                    font=("Arial", 14), text_color="black", fg_color="#D6D3CB")
        subtext_label.place(relx=0.75, rely=0.18, anchor="center")

        # Book Fields
        fields = [
            ("Title", 0.28), ("Author", 0.38), ("Category", 0.48)
        ]
        self.entries = {}

        for text, rely in fields:
            label = ctk.CTkLabel(self, text=text, font=("Arial", 18, "bold"), text_color="black", fg_color="#D6D3CB")
            label.place(relx=0.60, rely=rely, anchor="w")
            entry = ctk.CTkEntry(self, width=250, height=40, font=("Arial", 16), corner_radius=10, fg_color="white")
            entry.place(relx=0.78, rely=rely, anchor="center")
            self.entries[text] = entry

        # Description Box
        desc_label = ctk.CTkLabel(self, text="Description", font=("Arial", 18, "bold"), text_color="black", fg_color="#D6D3CB")
        desc_label.place(relx=0.60, rely=0.58, anchor="w")

        self.description_box = ctk.CTkTextbox(self, width=350, height=120, font=("Arial", 14), fg_color="white",
                                            corner_radius=10)
        self.description_box.place(relx=0.75, rely=0.70, anchor="center")

        # Add Book Button
        add_book_button = ctk.CTkButton(self, text="Add +", width=180, height=45, font=("Arial", 18, "bold"),
                                        corner_radius=10, fg_color="black", hover_color="#8C8477", command=self.add_book)
        add_book_button.place(relx=0.77, rely=0.85, anchor="center")

        #add back button as image to go back to the admin dashboard
        self.back_image = Image.open("UI/back.png")
        self.back_image = self.back_image.resize((55, 55), Image.LANCZOS)
        self.back_photo = CTkImage(light_image=self.back_image, size=(55, 55))
        self.back_button = ctk.CTkButton(self, image=self.back_photo, text="", width=55, height=55, fg_color="white", hover_color="white", command=self.admin_dashboard)
        self.back_button.place(relx=0.98, rely=0.96, anchor="e")




    def add_book(self):
        """Handles adding a new book to the database."""
        title = self.entries["Title"].get().strip()
        author = self.entries["Author"].get().strip()
        category = self.entries["Category"].get().strip()
        description = self.description_box.get("1.0", "end").strip()

        if not title or not author or not category or not description:
            messagebox.showwarning("Incomplete Details", "Please fill in all the fields.")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            insert_query = "INSERT INTO Book (title, author, category, description) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (title, author, category, description))
            conn.commit()

            messagebox.showinfo("Success", "Book added successfully!")

            # Clear fields after adding
            for entry in self.entries.values():
                entry.delete(0, "end")
            self.description_box.delete("1.0", "end")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error adding book: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def book_request_list_screen(self):
        """Admin panel to view, approve, or reject book requests."""
        # Load and Display Background Image
        image_path = "UI/reuqets.png"
        self.bg_image = Image.open(image_path).resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)

        # Heading Label
        heading_label = ctk.CTkLabel(self, text="Book Request List", font=("Arial", 24, "bold"), text_color="black")
        heading_label.place(relx=0.5, rely=0.35, anchor="center")

        # Buttons: Accept, Reject, Back
        accept_button = ctk.CTkButton(self, text="Accept", width=150, height=45, font=("Arial", 18, "bold"),
            corner_radius=10, fg_color="green", hover_color="#8C8477", command=self.approve_request)
        accept_button.place(relx=0.35, rely=0.85, anchor="center")

        reject_button = ctk.CTkButton(self, text="Reject", width=150, height=45, font=("Arial", 18, "bold"),
            corner_radius=10, fg_color="red", hover_color="#8C8477", command=self.reject_request)
        reject_button.place(relx=0.5, rely=0.85, anchor="center")

        back_button = ctk.CTkButton(self, text="Back", width=150, height=45, font=("Arial", 18, "bold"),
            corner_radius=10, fg_color="black", hover_color="#8C8477", command=self.admin_dashboard)
        back_button.place(relx=0.65, rely=0.85, anchor="center")

        # Create Treeview Table for Book Requests
        columns = ("Transaction ID", "User", "Book Title", "Status")
        self.request_list_table = ttk.Treeview(self, columns=columns, show="headings", height=8)

        # Adjust column widths based on window resolution
        self.request_list_table.column("Transaction ID", anchor="center", width=150)
        self.request_list_table.column("User", anchor="center", width=250)
        self.request_list_table.column("Book Title", anchor="center", width=400)
        self.request_list_table.column("Status", anchor="center", width=200)

        self.request_list_table.place(relx=0.5, rely=0.59, anchor="center", relwidth=0.6, relheight=0.3)

        # Define column headings
        for col in columns:
            self.request_list_table.heading(col, text=col)
            self.request_list_table.column(col, anchor="center", width=150)

        # Fetch and display book requests
        self.fetch_book_requests()
    
    def fetch_book_requests(self):
        """Fetch book requests from the database and display them in a Treeview table for the admin."""
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            # Fetch all pending requests
            cursor.execute("SELECT transactionid, userid, bookid, status FROM Transaction WHERE status='Pending'")
            requests = cursor.fetchall()

            # Clear previous data
            for item in self.request_list_table.get_children():
                self.request_list_table.delete(item)

            if not requests:
                messagebox.showinfo("Info", "No pending book requests.")
                return

            self.request_data = {}  # Store request details

            for request in requests:
                transaction_id, user_id, book_id, status = request

                # Fetch book title
                cursor.execute("SELECT title FROM Book WHERE bookid=%s", (book_id,))
                book_title = cursor.fetchone()[0]

                # Fetch user name
                cursor.execute("SELECT firstname, lastname FROM User WHERE userid=%s", (user_id,))
                user = cursor.fetchone()
                user_name = f"{user[0]} {user[1]}"

                # Insert into Treeview
                self.request_list_table.insert("", "end", values=(transaction_id, user_name, book_title, status))

                # Store request details for quick lookup
                self.request_data[transaction_id] = (user_id, book_id)

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error fetching book requests: {e}")

        finally:
            cursor.close()
            conn.close()

    def approve_request(self):
        """Approve the selected book request."""
        selected_item = self.request_list_table.selection()
        
        if not selected_item:
            messagebox.showerror("Error", "Please select a request to approve.")
            return

        transaction_id = self.request_list_table.item(selected_item, "values")[0]

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            # Calculate return date as 15 days from today
            return_date = datetime.now().date() + timedelta(days=15)

            # Update transaction status to 'Borrowed' and set return date
            cursor.execute("UPDATE Transaction SET status='Borrowed', returndate=%s WHERE transactionid=%s", (return_date, transaction_id))
            conn.commit()

            messagebox.showinfo("Success", "Book request approved!")

            # Refresh request list
            self.fetch_book_requests()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error updating request: {e}")

        finally:
            cursor.close()
            conn.close()

    def reject_request(self):
        """Reject the selected book request."""
        selected_item = self.request_list_table.selection()
        
        if not selected_item:
            messagebox.showerror("Error", "Please select a request to reject.")
            return

        transaction_id = self.request_list_table.item(selected_item, "values")[0]

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            # Update transaction status to 'Rejected'
            cursor.execute("UPDATE Transaction SET status='Rejected' WHERE transactionid=%s", (transaction_id,))
            conn.commit()

            messagebox.showinfo("Success", "Book request rejected!")

            # Refresh request list
            self.fetch_book_requests()

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error updating request: {e}")

        finally:
            cursor.close()
            conn.close()


    def library_resource_list_screen(self):
        """Displays all books in the library and allows admin to update availability."""
        
        # Load and Display Background Image
        image_path = "UI/library_resources.png"
        self.bg_image = Image.open(image_path).resize((1200, 750))
        self.bg_photo = CTkImage(light_image=self.bg_image, size=(1200, 750))
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, width=1200, height=750, text="")
        self.bg_label.place(x=0, y=0)

        # Heading
        heading_label = ctk.CTkLabel(self, text="Library Resource List", font=("Arial", 24, "bold"),bg_color="white", text_color="black")
        heading_label.place(relx=0.5, rely=0.32, anchor="center")


        #back button to go back to the admin dashboard as image
        self.back_image = Image.open("UI/back.png")
        self.back_image = self.back_image.resize((55, 55), Image.LANCZOS)
        self.back_photo = ImageTk.PhotoImage(self.back_image)
        self.back_button = Button(self, image=self.back_photo, bg="white", bd=0, cursor="hand2", command=self.admin_dashboard)
        self.back_button.place(relx=0.95, rely=0.94, anchor="e")


        # Book List Display (Treeview)
        columns = ("Book ID", "Title", "Author", "Category")
        self.book_tree = ttk.Treeview(self, columns=columns, show="headings", height=8)

        # Set the style for the Treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"), background="black", foreground="black")
        style.configure("Treeview", font=("Arial", 12), rowheight=25, background="white", foreground="black", fieldbackground="white")
        
        self.book_tree.heading("Book ID", text="Book ID")
        self.book_tree.column("Book ID", anchor="center", width=80)
        
        self.book_tree.heading("Title", text="Title")
        self.book_tree.column("Title", anchor="center", width=100)
        
        self.book_tree.heading("Author", text="Author")
        self.book_tree.column("Author", anchor="center", width=100)
        
        self.book_tree.heading("Category", text="Category")
        self.book_tree.column("Category", anchor="center", width=100)
        
        # self.book_tree.heading("Description", text="Description")
        # self.book_tree.column("Description", anchor="center", width=900)
        
        self.book_tree.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.80, relheight=0.3)

        # Fetch and Display Books
        self.fetch_library_books()



    def fetch_library_books(self):
        """Fetches all books from the database and displays them in the treeview."""
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            cursor.execute("SELECT bookid, title, author, category FROM Book")
            books = cursor.fetchall()

            self.book_tree.delete(*self.book_tree.get_children())  # Clear existing data

            for book in books:
                self.book_tree.insert("", "end", values=book)  # Insert each book into the treeview

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error fetching book data: {e}")

        finally:
            cursor.close()
            conn.close()


    def update_book_status(self):
        """Updates the selected book's availability status."""
        selected_item = self.book_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a book to update its status.")
            return

        book_data = self.book_tree.item(selected_item)["values"]
        book_id = book_data[0]  # Extract Book ID
        new_status = self.status_dropdown.get()

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            cursor.execute("UPDATE Book SET status=%s WHERE bookid=%s", (new_status, book_id))
            conn.commit()

            messagebox.showinfo("Success", "Book status updated successfully!")
            self.fetch_library_books()  # Refresh book list

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error updating book status: {e}")

        finally:
            cursor.close()
            conn.close()

    def generate_user_report(self):
        """Generates a PDF report of all users and the books they borrowed."""
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="library_management")
            cursor = conn.cursor()

            query = """
            SELECT U.firstname, U.lastname, B.title, T.transactiondate, T.returndate
            FROM Transaction T
            JOIN User U ON T.userid = U.userid
            JOIN Book B ON T.bookid = B.bookid
            WHERE T.status = 'Borrowed'
            """
            cursor.execute(query)
            borrowed_books = cursor.fetchall()

            if not borrowed_books:
                messagebox.showinfo("Info", "No borrowed books found.")
                return

            # Initialize PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "User Borrowed Books Report", ln=True, align="C")
            pdf.ln(10)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(50, 10, "User Name", border=1)
            pdf.cell(60, 10, "Book Title", border=1)
            pdf.cell(40, 10, "Borrow Date", border=1)
            pdf.cell(40, 10, "Return Date", border=1)
            pdf.ln()

            pdf.set_font("Arial", "", 12)
            for row in borrowed_books:
                pdf.cell(50, 10, f"{row[0]} {row[1]}", border=1)
                pdf.cell(60, 10, row[2], border=1)
                pdf.cell(40, 10, str(row[3]), border=1)
                pdf.cell(40, 10, str(row[4]) if row[4] else "Not Returned", border=1)
                pdf.ln()

            # Save PDF
            pdf_output_path = os.path.join(os.getcwd(), "User_Borrowed_Books.pdf")
            pdf.output(pdf_output_path)

            messagebox.showinfo("Success", f"User Report downloaded successfully!\nSaved at: {pdf_output_path}")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error generating report: {e}")

        finally:
            cursor.close()
            conn.close()

    def generate_library_resource_report(self=None):
        """Generate a well-formatted PDF report of all books in the library."""
        try:
            # Connect to the database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root@123",
                database="library_management"
            )
            cursor = conn.cursor()

            # Fetch book data
            cursor.execute("SELECT bookid, title, author, category, description FROM Book")
            books = cursor.fetchall()

            # Initialize PDF
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Title
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(200, 8, "Library Resource Report", ln=True, align="C")
            pdf.ln(6)

            # Table Headers
            pdf.set_font("Arial", style="B", size=10)
            column_widths = [15, 40, 40, 30, 65]  # Adjusted widths for proper spacing

            headers = ["ID", "Title", "Author", "Category", "Description"]
            for i, header in enumerate(headers):
                pdf.cell(column_widths[i], 8, header, border=1, align="C")
            pdf.ln()

            # Table Content
            pdf.set_font("Arial", size=9)
            for book in books:
                book_id, title, author, category, description = book

                # Calculate height of the description text
                description_height = pdf.get_string_width(description) / column_widths[4] * 5
                row_height = max(8, description_height)  # Ensure a minimum row height of 8

                # Save current position
                y_position = pdf.get_y()

                # Print first 4 columns
                pdf.cell(column_widths[0], row_height, str(book_id), border=1, align="C")
                pdf.cell(column_widths[1], row_height, title[:25], border=1, align="L")
                pdf.cell(column_widths[2], row_height, author[:20], border=1, align="L")
                pdf.cell(column_widths[3], row_height, category[:15], border=1, align="L")

                # Move to correct position for description
                pdf.set_xy(pdf.get_x(), y_position)
                pdf.multi_cell(column_widths[4], 8, description, border=1, align="L")

                # Ensure the cursor moves to a new line for the next row
                pdf.ln()

            # Save the PDF
            pdf_output_path = os.path.join(os.getcwd(), "Library_Resources.pdf")
            pdf.output(pdf_output_path)
            messagebox.showinfo("Success", f"Library Resource Report downloaded successfully!\nSaved at: {pdf_output_path}")

        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error generating report: {e}")

        finally:
            cursor.close()
            conn.close()



        
# Run Application
if __name__ == "__main__":
    app = LibraryApp()
    app.mainloop()