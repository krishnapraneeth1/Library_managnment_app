import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import mysql.connector
from tkinter import messagebox

class BookCatalogApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Book Catalog")
        self.geometry("1200x750")
        self.book_catalog_screen()

    def book_catalog_screen(self):
        # Load and Display Background Image
        image_path = "UI/catalog.png"
        self.bg_image = Image.open(image_path).resize((1200, 750))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
        self.bg_label.place(relwidth=1, relheight=1)

        # Fetch book data
        book_titles, self.book_data = self.fetch_book_data()

        # Create dropdowns
        self.selected_values = {}

        def create_dropdown(label_text, values, x, y, event_handler):
            """Creates a dropdown with dynamically updatable values."""
            label = ctk.CTkLabel(self, text=label_text, font=("Arial", 18, "bold"), fg_color="transparent", text_color="black")
            label.place(x=x, y=y)
            dropdown = ctk.CTkComboBox(self, values=values, width=280, height=45, font=("Arial", 18), corner_radius=10, fg_color="#E0DFDF")
            dropdown.place(x=x, y=y + 40)
            if event_handler:
                dropdown.bind("<<ComboboxSelected>>", event_handler)
            self.selected_values[label_text] = dropdown
            return dropdown

        # Dropdowns for filtering
        self.selected_values["Book Title"] = create_dropdown("Book Title", book_titles, 80, 160, self.update_book_details)

        # Initially empty dropdowns for Author and Category (will be updated automatically)
        self.selected_values["Author"] = create_dropdown("Author", [""], 80, 260, None)
        self.selected_values["Category"] = create_dropdown("Category", [""], 80, 360, None)

        # Book Information Section
        book_info_frame = ctk.CTkFrame(self, width=600, height=350, corner_radius=10, fg_color="#E0DFDF")
        book_info_frame.place(x=500, y=160)
        
        book_info_label = ctk.CTkLabel(book_info_frame, text="Book Information", font=("Arial", 20, "bold"), text_color="black")
        book_info_label.place(relx=0.5, rely=0.05, anchor="n")

        self.book_description_label = ctk.CTkLabel(book_info_frame, text="", wraplength=550,
                                                font=("Arial", 16), text_color="black", fg_color="transparent")
        self.book_description_label.place(relx=0.5, rely=0.5, anchor="center")

    def update_book_details(self, event=None):
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

if __name__ == "__main__":
    app = BookCatalogApp()
    app.mainloop()