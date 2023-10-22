from modules import view
from modules import store
from modules import updater

def create(ctk, master, instance, executable, textbox):
    update = ctk.CTkButton(master=master, text="Start Game", command=lambda: updater.start(app=master, ctk=ctk, instance=instance, executable=executable, update_button=update, textbox=textbox, options=store.getState()), height=36)
    update.grid(row=5, padx=10, pady=14, columnspan=2, sticky="ew")