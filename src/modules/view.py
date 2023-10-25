from tkinter import filedialog
from .store import setState
from .debounce import debounce

window_width = 0
window_height = 0

def addText(message, textbox):
    textbox.configure(state="normal")
    textbox.insert(index="end", text=message + "\n")
    textbox.configure(state="disabled")
    textbox.see("end")

@debounce(0.4)
def resize(app):
    global window_width, window_height
    if (window_width != app.winfo_width() or window_height != app.winfo_height()):
        # Store new width/height in memory
        window_width = app.winfo_width()
        window_height = app.winfo_height()
        
        # Store geometry in persistent database
        setState({"geometry": f"{window_width}x{window_height}"})