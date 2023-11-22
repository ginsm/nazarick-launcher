from modules.store import set_state
from modules.debounce import debounce

window_width = 0
window_height = 0
lockable_elements = []

def add_lockable(lockable):
    global lockable_elements

    if type(lockable) is list:
        for element in lockable:
            lockable_elements.append(element)
    else:
        lockable_elements.append(lockable)

def lock(should_lock):
    global lockable_elements

    if should_lock:
        for element in lockable_elements:
            element.configure(state='disabled')
    else:
        for element in lockable_elements:
            element.configure(state='normal')

def clear_lockable_elements():
    global lockable_elements
    lockable_elements.clear()

@debounce(0.4)
def resize(app):
    global window_width, window_height
    if (window_width != app.winfo_width() or window_height != app.winfo_height()):
        # Store new width/height in memory
        window_width = app.winfo_width()
        window_height = app.winfo_height()
        
        # Store geometry in persistent database
        set_state({'geometry': f'{window_width}x{window_height}'})