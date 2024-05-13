# box_controller.py

import tkinter as tk
from flask import Flask, render_template
import threading
import random
import time
#import smbus
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple
import os

##see hoiab kaste, koode ja kastide seisundit
#ja suhtleb i2c-ga

class StorageBoxes:
    def __init__(self):
        self.box_1 = {"code":0000, "door_state":0,"contains":0}
        self.box_2 = {"code": 1234, "door_state": 0, "contains": 0}
        self.used_codes = self.load_used_codes()
        self.is_admin = False
        self.start_threading()
        self.open_customer()

    def open_admin(self):
        if self.is_admin == False:
            self.set_admin()
            self.admin_panel = AdminPanel(self)
            thread_2 = threading.Thread(target=self.admin_panel.start_gui())
            thread_2.start()

    def set_admin(self):
        self.is_admin = not self.is_admin

    def open_customer(self):
        self.customer_gui = CustomerGUI(self)
        thread = threading.Thread(target=self.customer_gui.start_gui())
        thread.start()

    # Annab STM-ile teada mis uksed tema peab lahti tegema. data_size on mitu ust tehakse lahti
    def open_door(self, data_):
        command = 0x02
        data_size = 1
        data = [data_size, data_]
        slave_address = 21
        #bus = smbus.SMBus(1)
        print("Sending to address:", slave_address)
        #bus.write_i2c_block_data(slave_address, command, data)

    def reboot_slave(self):
        command = 0x09
        data_size = 1
        data = [data_size, 0]
        slave_address = 21
        #bus = smbus.SMBus(1)
        print("Sending to address:", slave_address)
        #bus.write_i2c_block_data(slave_address, command, data)

    # See hetkel ei tööta, aga siin küsitakse kappide staatust. Kutsutake ka interpret_status_bytes()
    def request_response_from_slave(self):
        command = 0x02
        data_size = 1
        data = [data_size, 11]
        slave_address = 21
        #bus = smbus.SMBus(1)
        slave_address = 21
        #received_data = bus.read_i2c_block_data(slave_address, 11)
        print("Received data:")
        #print(received_data)
        #self.interpret_status_bytes(received_data)

    # Vastusaadud info tehakse arusaadavaks infoks ja muudetakse globaalseid muutujaid, ei ole testitud
    # Näide: 1 5 2 2
    # 1. byte door id
    # 2. byte status. näiteks kui lock on 1, magnet on 0 ja IR on 1 tuleb 101 mis on 5
    # 3. byte door id
    # 4. byte status. näiteks kui lock on 0, magnet on 1 ja IR on 0 tuleb 010 mis on 2
    def interpret_status_bytes(self,status_bytes):
        global door1_data, door2_data
        print("Door statuses:")
        i = 0
        while i < len(status_bytes) - 1:  # Subtract 1 to ensure there's at least one complete pair
            door_id = status_bytes[i]
            door_status = status_bytes[i + 1]  # Assuming door status byte follows door ID byte
            lock_status = bool(door_status & 0b1)
            magnet_status = bool(door_status & 0b10)
            ir_sensor_status = bool(door_status & 0b100)

            if door_id == 1:
                door1_data = {"lock_status": lock_status, "magnet_status": magnet_status,
                              "ir_sensor_status": ir_sensor_status}
            elif door_id == 2:
                door2_data = {"lock_status": lock_status, "magnet_status": magnet_status,
                              "ir_sensor_status": ir_sensor_status}
            else:
                print(f"Unknown door ID: {door_id}")

            i += 2

        print("Door 1 data:", door1_data)
        print("Door 2 data:", door2_data)

    # Annab STM-ile teada mis uksed tema peab haldama. data_size on mitu ust hallatakse
    def send_data_to_slave(self):
        command = 0x08
        data_size = 2
        data = [data_size, 1, 2]  # hetkel on pandud 1 ja 2, kuidagi peaks tegema lihtsasti skaleeritavaks
        slave_address = 21
        #bus = smbus.SMBus(1)
        print("Sending to address:", slave_address)
        #bus.write_i2c_block_data(slave_address, command, data)

    # iga sekundi tagant küsime infot
    def heartbeat_loop(self):
        while True:
            # Perform any necessary tasks here
            print("Heartbeat")

            # Request response from the slave
            self.request_response_from_slave()

            # Sleep for 1 second
            time.sleep(1)

    def start_threading(self):
        print("starting hearbeats")
        #Heartbeat init
        #heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        #heartbeat_thread.daemon = True
        #heartbeat_thread.start()

    def load_used_codes(self):
        used_codes = {}
        filename = "codes.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                for line in file:
                    code, door = line.strip().split(":")
                    used_codes[code] = int(door)
        return used_codes
        # Generate a random 6-digit code
    def generate_code(self,box_id):
        random_code = str(random.randint(100000, 999999))

        # Check if the code has been used before generating a new one
        while random_code in self.used_codes:
            random_code = str(random.randint(100000, 999999))
        self.save_used_codes(random_code, box_id)
    # Save used codes to a file
    def save_used_codes(self,code_, door):
        filename = "codes.txt"
        with open(filename, "a") as file:
            file.write(f"{code_}:{door}\n")

    # Removes the code once it has been used
    def remove_code_from_file(code):
        filename = "codes.txt"
        temp_filename = "temp_codes.txt"  # Temporary file to store modified contents

        with open(filename, "r") as input_file, open(temp_filename, "w") as output_file:
            for line in input_file:
                if not line.startswith(code + ":"):  # Skip the line with the code to be removed
                    output_file.write(line)

        # Rename temporary file to original filename to replace it
        os.replace(temp_filename, filename)

    def check_code(self,code_):
        self.customer_gui.clear_pin()
        if code_ == "0000":
            print("uritan sitta keeta", self.is_admin)
            if self.is_admin == True:
                self.admin_panel.update_door_condition(1,1)
            self.open_door(1)
            return 1
        if code_ == "1337":
            self.open_admin()
            return 2
        return 0

class AdminPanel:
    def __init__(self,storage_boxes):
        self.storage_boxes=storage_boxes
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

        self.quit_button = tk.Button(self.root, text="Close",command=self.quit_admin)
        self.quit_button.pack(pady=20)

    def generate_code(self):
        return self.storage_boxes.generate_code(1)

    def quit_admin(self):
        print("quitriong adminer")
        self.storage_boxes.set_admin()
        self.root.destroy()

    def update_door_condition(self,door,state):
        state_text = {1:"Open", 0:"Closed"}
        print(state_text.get(state))
        if door == 1:
            self.box1_door.config(text="Open")
        if door == 2:
            self.box2_door.config(text="Open")
    def start_gui(self):
        self.root.mainloop()


class CustomerGUI:
    def __init__(self,storage_box):
        self.storage_boxes = storage_box
        self.current_box_number = None
        self.pin_length = 4  # You can adjust the PIN length as needed
        self.pin = ""

        self.root = tk.Tk()
        #self.root.attributes('-fullscreen', True)
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
            box_number = self.storage_boxes.check_code(self.pin)
            message = ""
            if box_number == 1 :
                message = "Box unlocked!"
            elif box_number == 2:
                message = "Admin Detected!"
            elif box_number == 0:
                message = "Incorrect PIN!"
            print(message)
            self.clear_pin()

    def success_message(self,message):
        self.pin = message
        self.update_pin_entry()


    def start_gui(self):
        self.root.mainloop()


app = Flask(__name__)

@app.route('/')
def index():
    # Render the admin panel template
    return render_template('admin_panel.html', text="abua")

def run_web_app():
    # Run the Flask web app
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    storage_boxes = StorageBoxes()
    # Create instances of GUI and AdminPanel



    # Start the Flask web app in a separate thread
    #web_app_thread = threading.Thread(target=run_web_app)
    #web_app_thread.start()
    #admin_panel.start_gui()
    # Start the GUI

