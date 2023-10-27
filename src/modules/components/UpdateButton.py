from modules import view
from modules import store
from modules import updater

def create(ctk, master, instance, executable, textbox):
    update = ctk.CTkButton(master=master, text="Start Game", command=lambda: updater.start(app=master, ctk=ctk, textbox=textbox, options=store.getState(), lockable=[*instance[:-1], *executable[:-1], update]), height=36)

    return update