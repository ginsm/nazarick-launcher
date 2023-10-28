from modules.store import set_state
from modules.debounce import debounce

window_width = 0
window_height = 0

def log(message, textbox):
    textbox.configure(state='normal')
    textbox.insert(index='end', text=message + '\n')
    textbox.configure(state='disabled')
    textbox.see('end')

@debounce(0.4)
def resize(app):
    global window_width, window_height
    if (window_width != app.winfo_width() or window_height != app.winfo_height()):
        # Store new width/height in memory
        window_width = app.winfo_width()
        window_height = app.winfo_height()
        
        # Store geometry in persistent database
        set_state({'geometry': f'{window_width}x{window_height}'})