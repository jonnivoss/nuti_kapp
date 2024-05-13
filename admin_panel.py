# admin_panel.py

import tkinter as tk
import random
from time import sleep

class AdminPanel:

    def generate_code(self):
        return ''.join(str(random.randint(0, 9)) for _ in range(6))

    def  update_door_condition(self,door,state):
        state_text = {1:"Open", 0:"Closed"}
        print(state_text.get(state))
        if door == 1:
            self.box1_door.config(text="Open")
        if door == 2:
            self.box2_door.config(text="Open")

    def __init__(self):
        print("loll")
        self.root = tk.Tk()
        self.root.title("Admin Panel")

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=20, pady=20)

        # Create the first box
        self.box1 = tk.LabelFrame(self.frame, text="Box 1", padx=10, pady=10)
        self.box1.grid(row=0, column=0, padx=10, pady=10)

        self.number1 = tk.Label(self.box1, text="1")
        self.number1.grid(row=0, column=0, padx=5, pady=5)

        self.box1_door = tk.Label(self.box1, text="Closed")
        self.box1_door.grid(row=1, column=0, padx=5, pady=5)

        self.box1_content = tk.Label(self.box1, text="Empty")
        self.box1_content.grid(row=2, column=0, padx=5, pady=5)

        self.code1 = tk.Label(self.box1, text=self.generate_code())
        self.code1.grid(row=3, column=0, padx=5, pady=5)

        # Create the second box
        self.box2 = tk.LabelFrame(self.frame, text="Box 2", padx=10, pady=10)
        self.box2.grid(row=0, column=1, padx=10, pady=10)

        self.number2 = tk.Label(self.box2, text="2")
        self.number2.grid(row=0, column=0, padx=5, pady=5)

        self.box2_door = tk.Label(self.box2, text="Closed")
        self.box2_door.grid(row=1, column=0, padx=5, pady=5)

        self.box2_content = tk.Label(self.box2, text="Full")
        self.box2_content.grid(row=2, column=0, padx=5, pady=5)

        self.code2 = tk.Label(self.box2, text=self.generate_code())
        self.code2.grid(row=3, column=0, padx=5, pady=5)



    def start_gui(self):
        self.root.mainloop()

