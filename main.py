from guizero import App, Text, TextBox, PushButton, Box, Window
from flask import Flask, render_template, request, jsonify
from flask.views import MethodView
import threading
import random
import time
#import smbus
from datetime import datetime, timedelta
import os
import json


class StorageBoxes:
    def __init__(self):
        self.units = []
        self.pin_len = 6
        #self.units.append(UnitInfo(21,1,1234))
        #self.units.append(UnitInfo(21,2,4321))
        self.units = self.load_unit_info_list()
        #self.save_unit_info_list(self.units)
        self.run_admin_web()
        self.open_customer_gui()

    def save_unit_info_list(self,unit_info_list):
        with open("andmed.txt", 'w') as file:
            dict_list = [unit_info.__dict__ for unit_info in unit_info_list]
            json.dump(dict_list, file, indent=4)

    def load_unit_info_list(self):
        with open("andmed.txt", 'r') as file:
            dict_list = json.load(file)
            return [UnitInfo(**unit_dict) for unit_dict in dict_list]


    def add_unit(self, id, code_):
        new_unit = UnitInfo(21, id, code_)
        self.units.append(new_unit)

    def run_admin_web(self):
        self.admin_web_service = AdminWeb(self)

    def open_customer_gui(self):
        self.customer_gui = CustomerGUI(self)
        custom_thread = threading.Thread(target=self.customer_gui.start_gui())

    def open_admin(self):
        self.admin_panel = AdminPanel(self,self.customer_gui)


    # Annab STM-ile teada mis uksed tema peab lahti tegema. data_size on mitu ust tehakse lahti
    def open_door(self, data_):
        command = 0x02
        data_size = 1
        data = [data_size, data_]
        slave_address = 21
#        bus = smbus.SMBus(1)
        print("Sending to address:", slave_address)
        #see peaks hear beati minema
        if data_ == self.units[0].id:
            print("leitud id 1")
            self.units[0].door_state = 1
        elif data_ == self.units[1].id:
            print("leitud id 2")
            self.units[1].door_state = 1

#        bus.write_i2c_block_data(slave_address, command, data)

    def reboot_slave(self):
        command = 0x09
        data_size = 1
        data = [data_size, 0]
        slave_address = 21
        bus = smbus.SMBus(1)
        print("Sending to address:", slave_address)
        bus.write_i2c_block_data(slave_address, command, data)

    # See hetkel ei tööta, aga siin küsitakse kappide staatust. Kutsutake ka interpret_status_bytes()
    def request_response_from_slave(self):
        command = 0x02
        data_size = 1
        data = [data_size, 11]
        slave_address = 21
        bus = smbus.SMBus(1)
        slave_address = 21
        received_data = bus.read_i2c_block_data(slave_address, 11)
        print("Received data:")
        print(received_data)
        self.interpret_status_bytes(received_data)

    # Vastusaadud info tehakse arusaadavaks infoks ja muudetakse globaalseid muutujaid, ei ole testitud
    # Näide: 1 5 2 2
    # 1. byte door id
    # 2. byte status. näiteks kui lock on 1, magnet on 0 ja IR on 1 tuleb 101 mis on 5
    # 3. byte door id
    # 4. byte status. näiteks kui lock on 0, magnet on 1 ja IR on 0 tuleb 010 mis on 2
    def interpret_status_bytes(self,status_bytes):
        i = 0
        while i < len(status_bytes) - 1:  # Subtract 1 to ensure there's at least one complete pair
            door_id = status_bytes[i]
            door_status = status_bytes[i + 1]  # Assuming door status byte follows door ID byte
            lock_status = bool(door_status & 0b1)
            magnet_status = bool(door_status & 0b10)
            ir_sensor_status = bool(door_status & 0b100)

            self.units[door_id - 1].door_state = magnet_status
            self.units[door_id - 1].ir_sensor = ir_sensor_status
            self.units[door_id - 1].lock_state = lock_status

            i += 2

    # Annab STM-ile teada mis uksed tema peab haldama. data_size on mitu ust hallatakse
    def send_data_to_slave(self):
        command = 0x08
        data_size = 2
        data = [data_size, 1, 2]  # hetkel on pandud 1 ja 2, kuidagi peaks tegema lihtsasti skaleeritavaks
        slave_address = 21
        bus = smbus.SMBus(1)
        print("Sending to address:", slave_address)
        bus.write_i2c_block_data(slave_address, command, data)

    # iga sekundi tagant küsime infot
    def heartbeat_loop(self):
        while True:
            # Perform any necessary tasks here
            print("Heartbeat")
            # Request response from the slave
            self.request_response_from_slave()
            if self.is_admin == True:
                self.admin_panel.update_door_condition(1,self.box_1.get("door_state"))
                self.admin_panel.update_door_condition(2, self.box_1.get("door_state"))
            # Sleep for 1 second
            time.sleep(1)

    def start_threading(self):
        print("starting hearbeats")
        #Heartbeat init
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop)
        heartbeat_thread.daemon = True
        heartbeat_thread.start()

    def load_used_codes(self):
        used_codes = {}
        filename = "codes.txt"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                for line in file:
                    code, door = line.strip().split(":")
                    used_codes[code] = int(door)
        return used_codes

    def check_code(self,code_):
        if code_ == "001337":
            self.open_admin()
            return -2
        for unit in self.units:
            if int(code_) == unit.code:
                self.open_door(unit.id)
                return unit.id  #tagastab kapi ukse id
        return -1 #ei leitud, vigane kood

    def generate_code(self,door):
        self.new_code = str(random.randint(0, 999999))
        while len(self.new_code) < self.pin_len:
            self.new_code = "0" + self.new_code
        for unit in self.units:
            if str(unit.code) == self.new_code:
                self.new_code = str(random.randint(0, 999999))
                while len(self.new_code) < self.pin_len:
                    self.new_code = "0" + self.new_code
        self.units[door-1].code = self.new_code
        return self.new_code


    def view_codes(self):
        try:
            with open('codes.txt', 'r') as file:
                codes = file.read()
            return codes
        except FileNotFoundError:
            return 'Error: codes.txt not found', 404


class AdminWeb:
    def __init__(self, storage):
        self.storage = storage
        self.app = Flask(__name__)
        self.setup_routes()
        self.run_admin_web()
        print("veeb on avatud")

    def sensor_data(self):
        # Define a route to provide sensor data, seda pole GUI-s. See näitab leheküljel kas midagi on sees
        @self.app.route('/get_sensor_data')
        def get_sensor_data(self):
            self.ir_1 = self.units[0].ir_sensor
            self.ir_2 = self.units[1].ir_sensor
            # Return sensor data as JSON
            return jsonify({'ir_sensor_state_1': self.ir_1, 'ir_sensor_state_2': self.ir_2})

    def run_admin_web(self):
        # Start the Flask web app in a separate thread
        self.web_app_thread = threading.Thread(target=self.run_web_app)
        self.web_app_thread.start()

    def run_web_app(self):
        # Run the Flask web app
        self.app.run(host='0.0.0.0', port=5000)

    def veiw_codes_admin(self):
        @self.app.route('/view_codes')
        def view_codes():
            try:
                with open('codes.txt', 'r') as file:
                    codes = file.read()
                return codes
            except FileNotFoundError:
                return 'Error: codes.txt not found', 404

    def admin_door_open(self):
        @self.app.route('/open_door', methods=['POST'])
        def open_door_route():
            door_number = int(request.form['door_number'])
            self.storage.open_door(door_number)

    def generate_code(self):
        @self.app.route('/generate_new_code', methods=['POST'])
        def generate_code_for_door():
            self.selected_door_str = request.form.get('selected_door')
            try:
                self.selected_door = int(self.selected_door_str)
            except ValueError:
                return jsonify({'message': 'Invalid door number'})
            self.new_generated_code = self.storage.generate_code(self.selected_door)
            return jsonify({'message': 'New code generated', 'code': self.new_generated_code, 'door': self.selected_door})

    def data_process(self):
        @self.app.route('/process_data', methods=['POST'])
        def data_sender():
            self.entered_code = request.form['code']
            self.number = self.storage.check_code(self.entered_code)

            if self.number == -2:
                return jsonify({'message': 'Admin panel activated', 'show_admin_panel': True})

            if self.storage.units[self.number - 1].lock_state == 0:
                return jsonify({'message': f'Door {self.storage.units[self.number - 1].id} did not open'})

            if self.storage.units[self.number - 1].lock_state == 1:
                return jsonify({'message': f'Door {self.storage.units[self.number - 1].id} did not close again'})

            elif self.storage.units[self.number - 1].lock_state == 0:
                return jsonify({'message': f'Everything is OK for Door {self.storage.units[self.number - 1].id}'})

            else:
                return jsonify({'message': 'Incorect code'})

    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

class AdminPanel:
    def __init__(self,storage_boxes,customer):
        self.storage_boxes=storage_boxes
        self.custom = customer

        self.admin_window = Window(self.custom.app_gui,title ="ADMIN", width= 720, height = 480,visible=True)
        self.frame = Box(self.admin_window, layout="grid")

        # Create the first box
        self.box1 = Box(self.frame, border=True, grid=[0, 0],width=144,height=256)
        self.number1 = Text(self.box1, text="1", grid=[0, 0])
        self.box1_door = Text(self.box1, text="Closed", grid=[1, 0])
        self.box1_content = Text(self.box1, text="Empty", grid=[2, 0])
        self.code1 = Text(self.box1, text=self.storage_boxes.units[0].code, grid=[3, 0])
        self.door_button_1 = PushButton(self.box1, text="Ava", grid=[4, 0], command=self.open_door, args=[1])
        self.generage_button_1 = PushButton(self.box1, text="Genereeri", grid=[5, 0], command=self.generate_code, args=[1])

        # Create the second box
        self.box2 = Box(self.frame, border=True, grid=[1, 0],width=144,height=256)
        self.number2 = Text(self.box2, text="2", grid=[1, 0])
        self.box2_door = Text(self.box2, text="Closed", grid=[2, 0])
        self.box2_content = Text(self.box2, text="Full", grid=[3, 0])
        self.code2 = Text(self.box2, text=self.storage_boxes.units[1].code, grid=[4, 0])
        self.door_button_2 = PushButton(self.box2, text="Ava", grid=[5, 0], command=self.open_door, args=[2])
        self.generage_button_2 = PushButton(self.box2, text="Genereeri", grid=[6, 0], command=self.generate_code, args=[2])

        self.quit_button = PushButton(self.admin_window, text="Close", pady=20, command=self.quit_admin)
        self.update_door_condition()

    def generate_code(self,door):
        new_code = self.storage_boxes.generate_code(door)
        self.update_door_condition()
        return new_code

    def open_door(self,door_id):
        self.storage_boxes.open_door(door_id)
        self.update_door_condition()

    def quit_admin(self):
        print("quitriong adminer")
        self.admin_window.destroy()

    def update_door_condition(self):
        for unit in self.storage_boxes.units:
            if unit.id == 1:
                self.code1.value = str(unit.code)
                if unit.door_state == 1:
                    self.box1_door.value = "Open"
                else:
                    self.box1_door.value = "Closed"
            if unit.id == 2:
                self.code2.value = str(unit.code)
                if unit.door_state == 1:
                    self.box2_door.value = "Open"
                else:
                    self.box2_door.value = "Closed"


class CustomerGUI:
    def __init__(self,storage_box):
        self.storage_boxes = storage_box
        self.current_box_number = 0
        self.pin_length = 6  # You can adjust the PIN length as needed
        self.pin = ""

        self.app_gui = App(title ="NUTIKAPP", width= 720, height = 480)
        #self.app_gui.full_screen = True
        # Create GUI elements
        self.label = Text(self.app_gui, text="Enter your PIN:",align="top")
        self.label.text_size = 20
        self.pin_entry = TextBox(self.app_gui, width=10, align="top")
        self.pin_entry.text_size = 20

        # Create a box to contain the buttons
        self.button_box = Box(self.app_gui, layout="grid")

        # Create number buttons
        for i in range(1, 10):
            self.button = PushButton(self.button_box, text=str(i), width=5, height=2, grid=[(i - 1) % 3, (i - 1) // 3], command=self.add_digit, args=[i])
            self.button.text_size = 10

        self.zero_button = PushButton(self.button_box, text="0",width=5,height=2, grid=[1, 4], command=self.add_digit, args=[0])
        self.zero_button.text_size = 10
        # Create Enter and Clear buttons
        self.enter_button = PushButton(self.button_box, text="Enter",width=5,height=2, grid=[0, 4], command=self.try_unlock)
        self.enter_button.text_size = 10
        self.clear_button = PushButton(self.button_box, text="Clear",width=5,height=2, grid=[2, 4], command=self.clear_pin)
        self.clear_button.text_size = 10

    def start_gui(self):
        self.app_gui.display()

    def add_digit(self, digit):
        if len(self.pin) < self.pin_length:
            self.pin += str(digit)
            self.update_pin_entry()

    def update_pin_entry(self):
        self.pin_entry.value = str(self.pin)

    def clear_pin(self):
        self.pin = ""
        self.update_pin_entry()

    def try_unlock(self):
        if len(self.pin) < self.pin_length:
            self.app_gui.error("VIGA", "     Liiga lühike kood!     ")
        if len(self.pin) == self.pin_length:
            self.box_number = self.storage_boxes.check_code(self.pin)
            self.clear_pin()
        if self.box_number == -1:
            self.app_gui.error("VIGA", "     Vale kood!     ")
        else:
            self.app_gui.info("INFO",f"     Kapp avanes!     ")


class UnitInfo:
    def __init__(self,i2c, id, code,lock_state,door_state,ir_sensor):
        self.i2c = i2c ##
        self.id = id  #kapi ukse id
        self.code = code #kood millega kappi saab avada
        self.lock_state = 0 #closed 1 open
        self.door_state = 0 #closed 1 open
        self.ir_sensor = 1 #occupied 0 empty

    def __repr__(self):
        return f"UnitInfo(i2c_lane={self.i2c}, id={self.id}, current_code={self.code})"

    def get_code(self):
        return self.current_code

    def update_code(self, new_code):
        self.current_code = new_code




if __name__ == "__main__":
    storage_boxes = StorageBoxes()
