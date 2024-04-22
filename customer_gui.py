# customer_gui.py
import tkinter as tk

class CustomerGUI:
    def __init__(self, storage_boxes):
        self.storage_boxes = storage_boxes
        self.current_box_number = None
        self.pin_length = 6  # You can adjust the PIN length as needed
        self.pin = ""

        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.title("PIN Entry")

        # Set screen width and height
        button_width = self.root.winfo_screenwidth() // 300
        button_height = self.root.winfo_screenheight() //300
        text_size = self.root.winfo_screenwidth() // 80
        font_def = ("Arial",text_size,"bold")

        # Create GUI elements
        self.label = tk.Label(self.root, text="Enter your PIN:", font=font_def)
        self.label.pack()

        self.pin_entry = tk.Entry(self.root, font=font_def, width=button_width*3,justify="center")
        self.pin_entry.pack()

        # Create number buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        for i in range(1,10):
            button = tk.Button(self.button_frame, text=str(i),width=button_width, height=button_height,font=font_def, command=lambda i=i: self.add_digit(i))
            button.grid(row=(i - 1)// 3, column=(i - 1) % 3,  sticky="nsew")

        zero_button = tk.Button(self.button_frame, text="0",width=button_width, height=button_height, font=font_def, command=lambda: self.add_digit(0))
        zero_button.grid(row=3, column=1, sticky="nsew")

        # Create Enter and Clear buttons
        enter_button = tk.Button(self.button_frame, text="Enter",width=button_width, height=button_height,font=font_def, command=self.try_unlock)
        enter_button.grid(row=3, column=0, sticky="nsew")

        clear_button = tk.Button(self.button_frame, text="Clear",width=button_width, height=button_height,font=font_def, command=self.clear_pin)
        clear_button.grid(row=3, column=2, sticky="nsew")

    def add_digit(self, digit):
        if len(self.pin) < self.pin_length:
            self.pin += str(digit)
            self.update_pin_entry()

    def update_pin_entry(self):
        self.pin_entry.delete(0, tk.END)
        self.pin_entry.insert(tk.END, self.pin)

    def clear_pin(self):
        self.pin = ""
        self.update_pin_entry()

    def try_unlock(self):
        if len(self.pin) == self.pin_length:
            box_number = self.storage_boxes.check_code(int(self.pin))
            if box_number :
                message = "Box unlocked!"
            else:
                message = "Incorrect PIN!"
            self.success_message(message)

    def success_message(self,message):
        self.pin = message
        self.update_pin_entry()


    def start_gui(self):
        self.root.mainloop()
