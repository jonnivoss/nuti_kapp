# admin_panel.py

import tkinter as tk

class AdminPanel:
    def __init__(self, storage_boxes):
        self.storage_boxes = storage_boxes
        self.root = tk.Tk()
        self.root.title("Admin Panel")

        # Create GUI elements
        self.label = tk.Label(self.root, text="Admin Panel")
        self.label.pack()

        self.box_number_label = tk.Label(self.root, text="Box Number:")
        self.box_number_label.pack()
        self.box_number_entry = tk.Entry(self.root)
        self.box_number_entry.pack()

        self.door_code_label = tk.Label(self.root, text="Door Code:")
        self.door_code_label.pack()
        self.door_code_entry = tk.Entry(self.root)
        self.door_code_entry.pack()

        self.update_button = tk.Button(self.root, text="Update Door Code", command=self.update_door_code)
        self.update_button.pack()

        self.status_button = tk.Button(self.root, text="Show Box Status", command=self.show_boxes_status)
        self.status_button.pack()

    def update_door_code(self):
        box_number = int(self.box_number_entry.get())
        new_code = self.door_code_entry.get()
        self.storage_boxes.update_box(box_number, new_code)
        self.box_number_entry.delete(0, tk.END)
        self.door_code_entry.delete(0, tk.END)

    def show_boxes_status(self):
        status_window = tk.Toplevel(self.root)
        status_window.title("Box Status")

        status_label = tk.Label(status_window, text="Box Status")
        status_label.pack()

        for box_number, door_code in self.storage_boxes.boxes.items():
            box_status = "Occupied" if door_code else "Vacant"
            box_info = f"Box {box_number}: {box_status}"
            box_info_label = tk.Label(status_window, text=box_info)
            box_info_label.pack()

    def start_gui(self):
        self.root.mainloop()
