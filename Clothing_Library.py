import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ttkbootstrap as ttkboot
from PIL import Image, ImageTk
import os
import random
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



# Global lists
rented_items = []
transaction_items = []


def create_db():
    """Create and populate the SQLite database with initial data."""
    conn = sqlite3.connect('clothing_library.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clothes (
            ID INTEGER PRIMARY KEY, 
            Gender TEXT, 
            Type TEXT, 
            Size TEXT, 
            Status TEXT, 
            Price_per_Week TEXT
        )
    ''')
    cursor.execute("DELETE FROM clothes")

    genders = ['Male', 'Female']
    clothing_types = {
        'Male': ['T-shirt', 'Pull', 'Jeans'],
        'Female': ['T-shirt', 'Pull', 'Dress', 'Jeans']
    }
    sizes = ['S', 'M', 'L']
    statuses = ['Available', 'Rented'] 

    for i in range(500):
        gender = random.choice(genders)
        clothing_item = random.choice(clothing_types[gender])
        size = random.choice(sizes)
        status = random.choice(statuses)
        price = f'CHF {random.randint(5, 15)}'
        cursor.execute(
            "INSERT INTO clothes (Gender, Type, Size, Status, Price_per_Week) VALUES (?, ?, ?, ?, ?)",
            (gender, clothing_item, size, status, price)
        )
    conn.commit()
    conn.close()

create_db()



'''
    RETURN WINDOW CLASS
'''

class ReturnWindow(tk.Toplevel):
    """Class for return window functionality."""
    def __init__(self, master):
        super().__init__(master)
        self.geometry("1200x600")
        self.title("Rented Clothes")
        self.title_label = ttkboot.Label(self, text="My clothes", font=('Helvetica', 40))
        self.title_label.pack(side='top', pady=10)

        # Treeview setup
        self.treeview = ttk.Treeview(self, columns=('ID', 'Gender', 'Type', 'Size', 'Status', 'Price per Week'), show="headings")
        for col in ('ID', 'Gender', 'Type', 'Size', 'Status', 'Price per Week'):
            self.treeview.heading(col, text=col)
            self.treeview.column(col, anchor='center')
        self.treeview.pack(expand=True, fill='both')
        self.protocol("WM_DELETE_WINDOW", self.hide_window)
        self.refresh_treeview()

        # Event binding for selection
        self.treeview.bind("<<TreeviewSelect>>", self.on_item_selected)

        # Add a back button
        self.back_button = ttk.Button(self, text="Back to Home", command=self.close_window, bootstyle='secondary')
        self.back_button.pack(pady=20)


    def refresh_treeview(self):
        """Refresh the Treeview with rented items."""
        self.treeview.delete(*self.treeview.get_children())
        for item in rented_items:
            self.treeview.insert('', 'end', values=item)


    def on_item_selected(self, event):
        """Handle selection of an item, showing its details for possible rental."""
        selection = self.treeview.selection()
        if selection:
            selected_item = selection[0]  # Get the first (and only) item selected
            item = self.treeview.item(selected_item, 'values')
            self.show_item_details(item)
        else:
            print("No item selected")


    def show_item_details(self, item):
        detail_window = tk.Toplevel(self)
        detail_window.title("Item Details")
        detail_window.geometry("400x300")
        detail_label = (
            f"ID: {item[0]}\n"
            f"Gender: {item[1]}\n"
            f"Type: {item[2]}\n"
            f"Size: {item[3]}\n"
            f"Status: {item[4]}\n"
            f"Price per Week: {item[5]}")
        detail_label = ttkboot.Label(detail_window, text=detail_label,bootstyle='body')
        detail_label.pack(pady=10)

        return_button = ttkboot.Button(
            detail_window, text="Return Item", 
            command=lambda: self.return_item(item, detail_window),
            bootstyle="success")
        return_button.pack(side='left', padx=10, pady=10)

        report_loss_button = ttkboot.Button(
            detail_window, text="Report Loss/Damage", 
            command=lambda: self.report_loss_or_damage(item[0], detail_window),
            bootstyle="danger")
        report_loss_button.pack(side='right', padx=10, pady=10)
    

    def return_item(self, item, detail_window):
        self.update_item_status_in_db(item[0], 'Available')
        detail_window.destroy() 
        rented_items.remove(item) # Remove the item from global list rented_items
        self.refresh_treeview() # Refresh the Treeview in ReturnWindow
        messagebox.showinfo("Return Completed", f"Item ID {item[0]} - '{item[2]}' has been returned.")


    def update_item_status_in_db(self, item_id, new_status):
        conn = sqlite3.connect('clothing_library.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE clothes SET Status = ? WHERE ID = ?", (new_status, item_id))
        conn.commit()
        conn.close()


    def report_loss_or_damage(self, item_id, detail_window):
        """Displays a dialog for reporting damage or loss with selectable options."""
        detail = tk.Toplevel(self)
        detail.title("Report Loss or Damage")
        detail.geometry("400x300")

        # Main frame to hold all contents and center them
        main_frame = ttkboot.Frame(detail)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
       
        # Label for instructions
        instruction_label = ttkboot.Label(
            main_frame, text="Please select the type of loss or damage:", 
            bootstyle='body')
        instruction_label.pack(pady=(20, 10))

        # Frame to hold radio buttons
        radio_frame = ttkboot.Frame(main_frame)
        radio_frame.pack(fill ='both', expand=True)

        # Variable to hold the selection
        damage_type_var = tk.StringVar(value="")

        # Radio buttons for different types of loss/damage        
        options = ["Lost", "Stained", "Torn", "Button Missing", "Zipper Broken", "Other"]
        for option in options:
            radio = ttkboot.Radiobutton(radio_frame, text=option, value=option, variable=damage_type_var)
            radio.pack(anchor=tk.W)  

        # Button frame
        button_frame = ttkboot.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        # Submit button
        submit_button = ttkboot.Button(
            button_frame, text="Submit Report", 
            command=lambda: submit_damage_report(),
            bootstyle="success")
        submit_button.pack(side='left', padx=10, expand=True)

        # Cancel button to close the dialog without proceeding
        cancel_button = ttkboot.Button(
            button_frame, text="Cancel", 
            command=detail.destroy, 
            bootstyle="danger")
        cancel_button.pack(side='left', padx=10, expand=True)
       
        # Function to handle submission
        def submit_damage_report():
            damage_type = damage_type_var.get()
            if damage_type:
                update_item_status_in_db(item_id, "In Repair")
                messagebox.showinfo(
                    "Report Submitted", f"Report for '{damage_type}' has been submitted for item ID {item_id}."
                    f"EcoWardrobe will contact you to organize the next steps."
                )
                detail.destroy()  
                detail_window.destroy() 
                remove_item_from_list(item_id)  # Remove the item from rented_items
                self.refresh_treeview()
            else:
                messagebox.showerror(
                    "Selection Required", "Please select a type of loss or damage.", parent=detail)
                
        def update_item_status_in_db(item_id, new_status):
            """Updates the item status in the database and ensures consistency across the application."""
            conn = sqlite3.connect('clothing_library.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE clothes SET Status = ? WHERE ID = ?", (new_status, item_id))
            conn.commit()
            conn.close()
            print(f"Updated item {item_id} in database to {new_status}")

        def remove_item_from_list(item_id):
            global rented_items
            rented_items = [item for item in rented_items if item[0] != item_id]
        

    def close_window(self):
        self.master.deiconify()
        self.destroy()


    def hide_window(self):
        """Hide the window instead of closing it."""
        self.withdraw()
    


'''
    RENTAL WINDOW CLASS
'''

class RentalWindow(tk.Toplevel):
    def __init__(self, master, return_window):
        super().__init__(master)
        self.master = master # Reference to the HomePage window
        self.return_window = return_window  # Reference to BaseWindow

        self.title("Rental Window")
        self.state('zoomed') # Maximize the window

        self.create_widgets()
        self.load_data()

    
    def create_widgets(self):
        """Create widgets for the rental window."""
        self.title_label = ttkboot.Label(self, text="Stock of Clothes", font=('Helvetica', 40))
        self.title_label.pack(side='top', pady=20)

        self.subtitle_label = ttkboot.Label(self, 
            text="Explore our collection and click on any item to rent it !", 
            font=('Helvetica', 20))
        self.subtitle_label.pack(side='top', pady=10)   

        # Treeview setup
        self.columns = ('ID', 'Gender', 'Type', 'Size', 'Status', 'Price per Week')
        self.treeview = ttk.Treeview(self, columns=self.columns, show="headings")
        for col in self.columns:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, anchor='center')
        self.treeview.pack(expand=True, fill='both')
        self.treeview.bind("<<TreeviewSelect>>", self.on_item_selected) # Event binding for selection

        # Bind the column headers to the sort_items method
        for col in self.columns:
            self.treeview.heading(col, text=col, command=lambda _col=col: self.sort_items(_col))

        # Search functionality
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack(side='top', padx=10, pady=10)
        self.search_button = ttk.Button(self, text="Search", command=self.search)
        self.search_button.pack(side='top', pady=10)

        # Treeview for rented clothes
        self.rented_title_label = ttkboot.Label(self, text="My Rented Clothes", font=('Helvetica', 30))
        self.rented_title_label.pack(pady=20)
        self.rented_treeview = ttk.Treeview(self, columns=self.columns,show="headings")
        for col in self.columns:
            self.rented_treeview.heading(col, text=col)
            self.rented_treeview.column(col, anchor='center')
        self.rented_treeview.pack(expand=True, fill='both')
        self.refresh_rented_treeview()

        # Back button to go to home
        self.back_button = ttk.Button(self, text="Back to Home", command=self.close_window, bootstyle='secondary')
        self.back_button.pack(pady=20)


    def load_data(self):
        """Load available clothes from the database into the Treeview."""
        self.treeview.delete(*self.treeview.get_children()) # Clear current items
        conn = sqlite3.connect('clothing_library.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clothes")
        for row in cursor.fetchall():
            self.treeview.insert('', 'end', values=row)
        conn.close()


    def refresh_rented_treeview(self):
        """Refreshes the Treeview that display rented items."""
        self.rented_treeview.delete(*self.rented_treeview.get_children())
        # Assuming 'rented_items' is a list of tuples that match the columns in the treeview
        for item in rented_items:
            self.rented_treeview.insert('', 'end', values=item)


    def on_item_selected(self, event):
        """Handle selection of an item, showing its details for possible rental."""
        selection = self.treeview.selection()
        if selection:
            selected_item = selection[0]  # Get the first (and only) item selected
            item = self.treeview.item(selected_item, 'values')
            self.show_item_details(item)
        else:
            print("No item selected")


    def sort_items(self, col):
        """Sort Treeview items by the given column."""
        # Get the current items and their values, and sort them by the given column
        items = sorted(
            ((item, self.treeview.item(item, 'values')) for item in self.treeview.get_children()),
            key=lambda item_values: item_values[1][self.columns.index(col)])

        # Clear the current items
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Insert the sorted items
        for item, values in items:
            self.treeview.insert('', 'end', values=values)


    def show_item_details(self, item):
        """Show details of the selected item and provide an option to rent it if available."""
        detail = tk.Toplevel(self)
        detail.title("Item Details")
        detail.geometry("600x700")

        # Load and display the clothing image
        image_path = os.path.expanduser(f"~/Desktop/Clothing/{item[2]}_{item[1]}.png")
        original_image = Image.open(image_path)
        resized_image = original_image.resize((300, 300), Image.Resampling.LANCZOS)  # Resize to fit the frame size
        display_image = ImageTk.PhotoImage(resized_image)
        image_label = ttk.Label(detail, image=display_image)
        image_label.image = display_image  # Keep a reference to the image object
        image_label.pack(side='top', pady=10)

        detail_text =  (
            f"ID: {item[0]}\n"
            f"Gender: {item[1]}\n"
            f"Type: {item[2]}\n"
            f"Size: {item[3]}\n"
            f"Status: {item[4]}\n"
            f"Price per Week: {item[5]}")
        detail_label = ttkboot.Label(detail, text=detail_text, bootstyle='body')
        detail_label.pack(expand=True, padx=20, pady=10)

        if item[4] == 'Available': # Check if the item is available
            rent_button = ttkboot.Button(detail, text="Rent This Item",
                                         command=lambda: self.rental_duration(item, detail), 
                                         bootstyle="secondary")
            rent_button.pack(pady=10)
        else:
            sorry_label = ttkboot.Label(detail, text="Sorry, this item has already been rented.", bootstyle='body')
            sorry_label.pack(pady=10)

        close_button = ttkboot.Button(detail, text="Close",command=detail.destroy, bootstyle='danger')
        close_button.pack(pady=10)


    def rental_duration(self, item, detail_window):
        """Ask the user to enter the duration for which they want to rent the item."""
        rental_duration = tk.Toplevel(detail_window)
        rental_duration.title("Enter Rental Duration")
        rental_duration.geometry("400x200")

        # Instruction label
        label = ttkboot.Label(rental_duration, text="How many weeks would you like to rent this item?", bootstyle='body')
        label.pack(pady=10)

        # Entry widget for inputting number of weeks
        weeks_var = tk.IntVar()
        weeks_entry = ttkboot.Entry(rental_duration, textvariable=weeks_var)
        weeks_entry.pack(pady=10)

        # Function to handle the proceed action
        def proceed():
            weeks = weeks_var.get()
            if 1 <= weeks <= 10:
                weekly_price = int(item[5].split()[1])
                total_price = weekly_price * weeks
                self.show_payment_details(item, weeks, total_price, detail_window)
                rental_duration.destroy()
            else:
                messagebox.showerror("Invalid Input", "Items can be rented for periods ranging from 1 to 10 weeks",
                                        parent=rental_duration)

        # Proceed button
        proceed_button = ttkboot.Button(rental_duration, text="Proceed", command=proceed, bootstyle="success")
        proceed_button.pack(pady=10)

        # Cancel button
        cancel_button = ttkboot.Button(rental_duration, text="Close", command=rental_duration.destroy, bootstyle="danger")
        cancel_button.pack(pady=10)


    def show_payment_details(self, item, weeks, total_price, detail):
        """Calculate total price and show payment options."""
        detail_text = (f"You have chosen to rent: {item[2]} (ID: {item[0]}) for {weeks} weeks.\n"
                       f"Total price: CHF {total_price}")
        detail_label = ttkboot.Label(detail, text=detail_text, bootstyle='body')  # Make sure this label is added to the `detail` window
        detail_label.pack(pady=10)   

        # Button to proceed to payment
        proceed_button = ttkboot.Button(detail, text="Proceed to Payment",
                                        command=lambda: self.rent_item(item, weeks, total_price, detail),
                                        bootstyle="success")
        proceed_button.pack(pady=20)


    def rent_item(self, item, weeks, total_price, detail):
        """Update item status in the database to 'Rented' and add to BaseWindow."""
        self.update_item_status_in_db(item[0], 'Rented')
        self.update_item_status(item[0], 'Rented')

        # Add the item to the global list if not already present and if available
        if item not in rented_items and item[4] == 'Available':
            self.update_item_status_in_db(item[0], 'Rented') 
            updated_item = item[:4] + ('Rented',) + item[5:]
            rented_items.append(updated_item) # Add the updated item to the rented_items list
            transaction_items.append(updated_item) # Add the updated item to the transaction_items list

        self.return_window.refresh_treeview()  
        self.refresh_rented_treeview() 
        self.load_data()

        # Confirm purchase and display message
        self.confirm_purchase(item, weeks, total_price, detail)
        detail.destroy() 


    def confirm_purchase(self, item, weeks, total_price, detail):
        """Confirms the rental and purchase, displaying a final message and closing the detail window."""
    
        # This message will be displayed in a message box
        purchase_confirmation_message = (
        f"Thank you for your purchase! You have rented '{item[2]}' (ID: {item[0]}) for {weeks} weeks.  "
        f"The total price is CHF {total_price}.")

        # Additional message for user instructions
        return_instructions_message = (
        "Please make sure to return the item within the rental period using the return option on EcoWardrobe.")

        # Displaying the message box with the purchase confirmation
        messagebox.showinfo(
            "Purchase Confirmed",
            f"{purchase_confirmation_message}\n\n{return_instructions_message}",
            parent=detail)        
    

    def update_item_status_in_db(self, item_id, new_status):
        conn = sqlite3.connect('clothing_library.db')
        c = conn.cursor()
        c.execute("UPDATE clothes SET Status = ? WHERE ID = ?", (new_status, item_id))
        conn.commit()
        conn.close()
        print(f"Updated item {item_id} in database to {new_status}")

        
    def update_item_status(self, item_id, new_status):
        for child in self.treeview.get_children():
            values = list(self.treeview.item(child, 'values'))
            if int(values[0]) == item_id:
                values[4] = new_status
                self.treeview.item(child, values=values)
        self.treeview.update_idletasks()  


    def close_window(self):
        self.master.deiconify()
        self.destroy()


    def search(self):
        """Filters the Treeview items based on the search query."""
        query = self.search_var.get()
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        conn = sqlite3.connect('clothing_library.db')
        c = conn.cursor()
        c.execute("SELECT * FROM clothes WHERE Status='Available'")
        for row in c.fetchall():
            if row and query.lower() in str(row).lower():
                self.treeview.insert('', 'end', values=row)
        conn.close()


'''
    ECO-COMPARATOR CLASS
'''

class EcoComparator(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.state('zoomed')
        self.title("My Eco-Comparator")

        # Title label
        self.title_label = ttkboot.Label(self, text="My Eco-Comparator", font=('Helvetica', 40))
        self.title_label.pack(side='top', pady=20)

        # Treeview setup
        self.treeview = ttk.Treeview(self, columns=('ID', 'Gender', 'Type', 'Size', 'Status', 'Price per Week'), show="headings")
        for col in ('ID', 'Gender', 'Type', 'Size', 'Status', 'Price per Week'):
            self.treeview.heading(col, text=col)
            self.treeview.column(col, anchor='center')
        self.treeview.pack(expand=True, fill='both')

        # Text label
        self.text_label = ttkboot.Label(self,
        text="Renting instead of buying prevents the need to producing new items, reducing your environmental footprint. "
         "Below, you can see two graphs showing the amount of CO2 emissions and water usage you have saved by renting items.",
        font=('Helvetica', 16), wraplength=800, justify='center')
        self.text_label.pack(side='top', pady=20, expand=True)

        # Set up the figures and canvas for plotting
        self.setup_graphs()

        # Data for environmental savings
        self.savings_data = {
            "Jeans": {"CO2": 33.4, "Water": 7500},
            "Pull": {"CO2": 25, "Water": 3350},
            "T-shirt": {"CO2": 12, "Water": 1500},
            "Dress": {"CO2": 22, "Water": 2500}
        }

        # Button frame
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(side='bottom', fill='x', pady=10)
        self.back_button = ttk.Button(self.button_frame, text="Back to Home Page", command=self.close_window, bootstyle='secondary')
        self.back_button.pack(side='top', pady=10) 

        # Refresh the Treeview which also updates the graphs
        self.refresh_treeview()


    def setup_graphs(self):
        # Graph frame to control size and layout of graphs
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.pack(side='top', fill='both', expand=True, padx=20, pady=20)

        # Figures for CO2 and water savings
        self.fig1 = plt.Figure(figsize=(5, 3), dpi=100)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.graph_frame)
        self.canvas1.get_tk_widget().pack(side='left', padx=10, pady=5)

        self.fig2 = plt.Figure(figsize=(6, 3), dpi=100)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.graph_frame)
        self.canvas2.get_tk_widget().pack(side='right', padx=10, pady=5)


    def refresh_treeview(self):
        """Refresh the Treeview with rented items and update the graphs."""
        self.treeview.delete(*self.treeview.get_children())
        total_co2 = 0
        total_water = 0
        for item in transaction_items:  
            self.treeview.insert('', 'end', values=item)
            item_type = item[2]  # Assuming 'Type' is at index 2
            total_co2 += self.savings_data.get(item_type, {}).get('CO2', 0)
            total_water += self.savings_data.get(item_type, {}).get('Water', 0)

        self.update_display_co2(total_co2)
        self.update_display_water(total_water)


    def update_display_co2(self, total_co2):
        """Update the CO2 equivalent graph with new data."""
        self.fig1.clear()
        ax = self.fig1.add_subplot(111)
        comparative_data = {"Car (300km)": 102, "Flight (2500km)": 200}
        categories = ['Rented Items', 'Car (300km)', 'Flight (2500km)']
        values = [total_co2, comparative_data['Car (300km)'], comparative_data['Flight (2500km)']]
        ax.bar(categories, values, color=['green', 'gray', 'gray'])
        ax.set_ylabel('CO2 (kg)')
        ax.set_title('CO2 Emissions Comparison')
        self.canvas1.draw()

        # Flight Zurich - Madrid and back (2'500km) : 200kg CO2 per passenger (Guardian).
        # Driving a car (300km): 100kg CO2 per car (Myclimate).

    def update_display_water(self, total_water):
        """Update the water saved graph with new data."""
        self.fig2.clear()
        ax = self.fig2.add_subplot(111)
        comparative_data = {"Washing Machine (25 loads)": 50000, "Pool (75m3)": 75000}
        categories = ['Rented Items', 'Washing Machine (25 loads)', 'Pool (75m3)']
        values = [total_water, comparative_data['Washing Machine (25 loads)'], comparative_data['Pool (75m3)']]
        ax.bar(categories, values, color=['blue', 'gray', 'gray'])
        ax.set_ylabel('Water (liters)')
        ax.set_title('Water Usage Comparison')
        self.canvas2.draw()
        
        # Washing machine (25 loads) = 50'000 liters (Swiss Federal Office for the Environment
        # Swimming pool (75m3) = 75'000 liters (Swiss Federal Office for the Environment).

    def close_window(self):
        self.master.deiconify()
        self.destroy()


    def hide_window(self):
        """Hide the window instead of closing it."""
        self.withdraw()


'''
    STATISTICS WINDOW
'''

class StatisticsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Statistics")
        self.state('zoomed')

        # Title label
        self.title_label = ttkboot.Label(
            self, text="Statistics", font=('Helvetica', 40))
        self.title_label.pack(side='top', pady=20)

        # Text label
        self.text_label = ttkboot.Label(self,
            text="Explore key insights about EcoWardrobe with the statistics displayed below !",
            font=('Helvetica', 18))
        self.text_label.pack(side='top', pady=20)

        # Database connection
        self.conn = sqlite3.connect('clothing_library.db')
        self.c = self.conn.cursor()

        # Frame to hold all the graphs
        self.graph_frame = ttk.Frame(self)
        self.graph_frame.pack(fill='both', expand=True)

        # Generate all the statistics and plots
        self.display_statistics()

        # Back button
        self.back_button = ttk.Button(self, text="Back to Home", command=self.close_window, bootstyle='secondary')
        self.back_button.pack(pady=20)


    def display_statistics(self):
        """Create and position four graphs."""
        self.plot_gender_distribution(0, 0)
        self.plot_rental_status(0, 1)
        self.plot_most_rented_items(1, 0)
        self.plot_price_sensitivity(1, 1)


    def plot_most_rented_items(self, row, column):
        """Plot a bar chart of the most rented items."""
        data = self.fetch_most_rented_items()
        fig, ax = plt.subplots(figsize = (5, 3))
        categories = [item[0] for item in data]
        counts = [item[1] for item in data]
        ax.bar(categories, counts, color='skyblue')
        ax.set_title("Most Rented Items")
        ax.set_xlabel("Items")
        ax.set_ylabel("Count")
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=column, sticky='nsew', padx=5, pady=5)


    def plot_price_sensitivity(self, row, column):
        """Plot a bar chart of rental frequency by price."""
        data = self.fetch_price_sensitivity()
        fig, ax = plt.subplots(figsize=(7, 3))
        prices = [item[0] for item in data]
        counts = [item[1] for item in data]
        ax.bar(prices, counts, color='orange')
        ax.set_title("Price Sensitivity")
        ax.set_xlabel("Price per Week")
        ax.set_ylabel("Rental Frequency")
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=column, sticky='nsew', padx=5, pady=5)


    def plot_rental_status(self, row, column):
        """Plot a pie chart for rental status."""
        rented, available = self.fetch_rental_status()
        fig, ax = plt.subplots(figsize = (4, 2))
        ax.pie([rented, available], labels=['Rented', 'Available'], autopct='%1.1f%%', colors=['tomato', 'green'])
        ax.set_title("Rental Status")
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=column, sticky='nsew', padx=5, pady=5)


    def plot_gender_distribution(self, row, column):
        """Plot a pie chart showing the distribution of items by gender."""
        male, female = self.fetch_gender_distribution()
        fig, ax = plt.subplots(figsize=(4, 2))
        ax.pie([male, female], labels=['Male', 'Female'], autopct='%1.1f%%', colors=['blue', 'pink'])
        ax.set_title("Gender Distribution")
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=row, column=column, sticky='nsew', padx=5, pady=5)
    
    
    def close_window(self):
        self.master.deiconify()
        self.destroy()


    # Assume these methods are implemented to interact with the database
    def fetch_most_rented_items(self):
        """Fetch data for most rented items."""
        self.c.execute("SELECT Type, COUNT(*) FROM clothes WHERE Status = 'Rented' GROUP BY Type ORDER BY COUNT(*) DESC")
        return self.c.fetchall()


    def fetch_price_sensitivity(self):
        """Fetch data for rental frequency by price."""
        self.c.execute("SELECT Price_per_Week, COUNT(*) FROM clothes WHERE Status = 'Rented' GROUP BY Price_per_Week ORDER BY CAST(SUBSTR(Price_per_Week, 5) AS INTEGER)")
        return self.c.fetchall()


    def fetch_rental_status(self):
        """Fetch rental status counts."""
        self.c.execute("SELECT COUNT(*) FROM clothes WHERE Status = 'Rented'")
        rented = self.c.fetchone()[0]
        self.c.execute("SELECT COUNT(*) FROM clothes WHERE Status = 'Available'")
        available = self.c.fetchone()[0]
        return rented, available


    def fetch_gender_distribution(self):
        """Fetch item counts by gender."""
        self.c.execute("SELECT Gender, COUNT(*) FROM clothes GROUP BY Gender")
        results = self.c.fetchall()
        # Return counts in correct order
        male_count = next((count for gender, count in results if gender == 'Male'), 0)
        female_count = next((count for gender, count in results if gender == 'Female'), 0)
        return male_count, female_count




'''
    HOME PAGE CLASS
'''

class HomePage(ttkboot.Window):
    def __init__(self):
        """Initialize the HomePage window with a given title and theme"""
        super().__init__(title="EcoWardrobe - Sustainable Clothing Library", themename="superhero")
        self.geometry("800x650")
        self.create_widgets()
        self.return_window = ReturnWindow(self)  # Create and initially hide ReturnWindow
        self.return_window.withdraw()
        self.ecocomparator_window = EcoComparator(self)  # Create and initially hide EcoComparator
        self.ecocomparator_window.withdraw()


    def create_widgets(self):
        """Create widgets for the home page layout"""
        # Top frame for logo and title
        self.top_frame = ttkboot.Frame(self)
        self.top_frame.pack(side='top', fill='x', pady=10)

        # Load and display the logo
        logo_path = os.path.expanduser("~/Desktop/Logo.png")
        logo_image = Image.open(logo_path)
        logo_photo = ImageTk.PhotoImage(logo_image.resize((150, 150), Image.Resampling.LANCZOS))
        self.logo_label = ttkboot.Label(self.top_frame, image=logo_photo)
        self.logo_label.image = logo_photo 
        self.logo_label.pack(side='left', padx=20)
        
        # Main title of the application
        self.title_label = ttkboot.Label(self.top_frame, text="EcoWardrobe", 
                                         font=('Helvetica', 54))
        self.title_label.pack(side='top', pady=10)

        # Subtitle below the main title
        self.subtitle_label = ttkboot.Label(self.top_frame, text="Step into a world where fashion meets sustainability!", 
                                            font=('Helvetica', 18))
        self.subtitle_label.pack(side='top', pady=10)

        # Frame for the main content
        self.content_frame = ttkboot.Frame(self, padding=(10, 10))
        self.content_frame.pack(expand=True, fill='both')

        # Frame for the clothing image
        self.image_frame = ttkboot.Frame(self.content_frame, width=300, height=300)
        self.image_frame.pack(side='left', padx=10)
        self.image_frame.pack_propagate(False)  

        # Load and display the clothing image
        self.image_path = os.path.expanduser("~/Desktop/Clothing.png")
        self.original_image = Image.open(self.image_path)
        self.resized_image = self.original_image.resize((300, 300), Image.Resampling.LANCZOS)  # Resize to fit the frame size
        self.display_image = ImageTk.PhotoImage(self.resized_image)
        self.image_display_label = ttkboot.Label(self.image_frame, image=self.display_image)
        self.image_display_label.pack(side='top', pady=10)

         # Frame for the introductory text
        self.text_frame = ttkboot.Frame(self.content_frame, width=500, height=300)
        self.text_frame.pack(side='left', padx=10, pady=10)
        self.text_frame.pack_propagate(False)

        self.intro_text = ("Welcome to EcoWardrobe ! Borrow from a wide range of styles without the need to buy. "
                           "Participating helps reduce fashion waste and positively impacts the environment.")
        self.intro_label = ttkboot.Label(self.text_frame, text=self.intro_text, font=('Avenir', 14), wraplength=400)
        self.intro_label.pack(side='top', fill='x', padx=10, pady=10)

        self.impact_text = ("The fashion industry contributes to 10% of global annual carbon emissions, according to UNEP. "
                             "Additionally, in some countries, up to 40% of purchased clothes are never worn.")
        self.impact_label = ttkboot.Label(self.text_frame, text=self.impact_text, font=('Avenir', 14), wraplength=400)
        self.impact_label.pack(side='top', fill='x', padx=10, pady=10)

        self.how_it_works_text = ("EcoWardrobe aims to revolutionize the way we consume fashion. It’s simple! Choose your "
                                  "favorite items from our collection, keep them as long as you need, and return them for others "
                                  "to enjoy. This approach saves resources and promotes a sharing economy, leading us towards a "
                                  "more sustainable future for fashion.")
        self.how_it_works_label = ttkboot.Label(self.text_frame, text=self.how_it_works_text, font=('Avenir', 14), wraplength=400)
        self.how_it_works_label.pack(side='top', fill='x', padx=10, pady=10)

        # Button frame setup
        self.button_frame = ttkboot.Frame(self)
        self.button_frame.pack(side='bottom', fill='x', padx=20, pady=10)

        # Top row buttons
        self.top_buttons_frame = ttkboot.Frame(self.button_frame)
        self.top_buttons_frame.pack(fill='x', expand=True)
        self.button_width=20

        self.rental_button = ttkboot.Button(self.top_buttons_frame, 
                                            text="Rent clothes", 
                                            command=self.open_rental_window, 
                                            width=self.button_width,
                                            bootstyle='secondary')
        self.rental_button.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        
        self.return_button = ttkboot.Button(self.top_buttons_frame, 
                                         text="Return clothes", 
                                         command=self.open_return_window, 
                                         width=self.button_width,
                                         bootstyle='secondary')
        self.return_button.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        # Bottom row buttons
        self.bottom_buttons_frame = ttkboot.Frame(self.button_frame)
        self.bottom_buttons_frame.pack(fill='x', expand=True)

        self.stat_button = ttkboot.Button(self.bottom_buttons_frame, 
                                          text="Statistics", 
                                          command=self.stat_window, 
                                          width=self.button_width,
                                          bootstyle='secondary')
        self.stat_button.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        self.ecocomparator_button = ttkboot.Button(self.bottom_buttons_frame, 
                                                   text="Eco Comparator", 
                                                   command=self.ecocomparator_window, 
                                                   width=self.button_width,
                                                   bootstyle='secondary')
        self.ecocomparator_button.pack(side='left', expand=True, fill='x', padx=5, pady=5)


    def open_rental_window(self):
        self.withdraw()
        RentalWindow(self, self.return_window)  # Create and show RentalWindow


    def open_return_window(self):
        self.withdraw()
        ReturnWindow(self)
    

    def stat_window(self):
        self.withdraw()
        StatisticsWindow()


    def ecocomparator_window(self):
        self.withdraw()
        EcoComparator(self)


if __name__ == "__main__":
    app = HomePage()
    app.mainloop()


