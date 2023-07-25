import subprocess
import customtkinter
import webbrowser
import threading
from tkinter import *

customtkinter.set_appearance_mode("System")
# customtkinter.set_default_color_theme("dark-blue.json")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Face Recognition!")
        self.geometry("400x250")
        self.resizable(False, False)  # Fix the window size

        self.button = customtkinter.CTkButton(
            self, text="Trand Modes", command=self.button_trand)
        self.button.pack(padx=15, pady=15)

        self.button = customtkinter.CTkButton(
            self, text="Register", command=self.button_register)
        self.button.pack(padx=15, pady=15)

        self.button = customtkinter.CTkButton(
            self, text="Recognition", command=self.button_recog)
        self.button.pack(padx=15, pady=15)

        self.button = customtkinter.CTkButton(
            self, text="Exit", command=self.button_exit)
        self.button.pack(padx=15, pady=15)

        self.cancel_button = None  # Placeholder for the cancel button

    def button_trand(self):
        # Execute trand.py file in a separate thread
        self.create_cancel_button()  # Create the cancel button
        trand_thread = threading.Thread(target=self.run_trand)
        trand_thread.start()

    def run_trand(self):
        subprocess.run(["python", "btnTrand.py"])
        self.remove_cancel_button()  # Remove the cancel button

    def button_register(self):
        webbrowser.open("http://localhost:3000")

    def button_recog(self):
        # Execute btnRecognition.py file in a separate thread
        self.create_cancel_button()  # Create the cancel button
        recog_thread = threading.Thread(target=self.run_recognition)
        recog_thread.start()

    def run_recognition(self):
        subprocess.run(["python", "btnRecognitionForVideo.py"])
        self.remove_cancel_button()  # Remove the cancel button

    def button_exit(self):
        self.cancel_process()  # Call the cancel_process method to kill all operations
        self.quit()

    def create_cancel_button(self):
        self.cancel_button = customtkinter.CTkButton(
            self, text="Cancel", command=self.cancel_process)
        self.cancel_button.pack(padx=15, pady=15)
        self.cancel_button.update()  # Update the GUI to display the cancel button

    def remove_cancel_button(self):
        if self.cancel_button:
            self.cancel_button.pack_forget()  # Remove the cancel button from the GUI
            self.cancel_button = None

    def cancel_process(self):
        # Kill the subprocess when cancel button is clicked
        subprocess.run(["taskkill", "/f", "/im", "python.exe"])


app = App()
app.mainloop()
