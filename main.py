# box_controller.py

from admin_panel import AdminPanel
import tkinter as tk
from flask import Flask, render_template
import threading
import random
import time
#import smbus
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple

##see hoiab kaste, koode ja kastide seisundit
#ja suhtleb i2c-ga

@dataclass
class StorageBox:
    bus: int
    number_of_door: int
    doors: List[Tuple[int,int,int]]

    @classmethod
    def __init__(self,bus_number, number):
        self.number_of_door = number
        self.bus = bus_number
        self.doors = [(0, 0, 0) for _ in range(self.number_of_door)]


class StorageBoxes:
    def __init__(self):

        self.start_threading()

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

        # Generate a random 6-digit code
    def generate_code():
        random_code = str(random.randint(100000, 999999))

        # Check if the code has been used before generating a new one
        while random_code in used_codes:
            random_code = str(random.randint(100000, 999999))
        radioBoxValue = int(radioBoxes.value)
        save_used_codes(random_code, radioBoxValue)

    def check_code(self,):

        if code == '0000':
            self.open_door(1)

    def generate_code():
        random_code = str(random.randint(100000, 999999))

        # Check if the code has been used before generating a new one
        while random_code in used_codes:
            random_code = str(random.randint(100000, 999999))
        radioBoxValue = int(radioBoxes.value)
        save_used_codes(random_code, radioBoxValue)

        adminWindow.info("INFO", "Genereeritud kapile {} kood {}".format(radioBoxValue, random_code))




class CustomerGUI:
    def __init__(self):
        self.current_box_number = None
        self.pin_length = 6  # You can adjust the PIN length as needed
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
            box_number = storage_boxes.check_code(int(self.pin))
            message = ""
            if box_number == 1 :
                message = "Box unlocked!"
            elif box_number == 2:
                message = "Admin Detected!"
            elif box_number == 0:
                message = "Incorrect PIN!"
            self.success_message(message)

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
    customer_gui = CustomerGUI()
    customer_gui.start_gui()
    #admin_panel = AdminPanel(storage_boxes)

    # Start the Flask web app in a separate thread
    #web_app_thread = threading.Thread(target=run_web_app)
    #web_app_thread.start()
    #admin_panel.start_gui()
    # Start the GUI

