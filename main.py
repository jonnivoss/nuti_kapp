# box_controller.py

from admin_panel import AdminPanel
from customer_gui import CustomerGUI
from flask import Flask, render_template
import threading

##see hoiab kaste, koode ja kastide seisundit
#ja suhtleb i2c-ga

class StorageBox:
    i2c_lane = 0
    number_of_drawers = 2
    class Drawer:
        drawer_state = 0
        drawer_code = 888888

class StorageBoxes:
    def __init__(self):
        self.boxes = {}

    def add_box(self, box_number, door_code):
        self.boxes[box_number] = door_code

    def remove_box(self, box_number):
        if box_number in self.boxes:
            del self.boxes[box_number]

    def update_box(self, box_number, new_door_code):
        if box_number in self.boxes:
            self.boxes[box_number] = new_door_code

    def get_door_code(self, box_number):
        return self.boxes.get(box_number)

    def check_code(self, pin):
        if(pin == 111111):
            return True
        else:
            return False

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
    customer_gui = CustomerGUI(storage_boxes)
    #admin_panel = AdminPanel(storage_boxes)

    # Start the Flask web app in a separate thread
    #web_app_thread = threading.Thread(target=run_web_app)
    #web_app_thread.start()
    #admin_panel.start_gui()
    # Start the GUI
    customer_gui.start_gui()
