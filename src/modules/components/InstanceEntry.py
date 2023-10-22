from modules import view
from modules import store
from modules.debounce import debounce

@debounce(1)
def handleKeyPress(entry, name):
    stored = store.getState(name)[0]
    value = entry.get()
    
    if (stored != value):
        store.setState({name: value})

def create(ctk, master, state):
    label = ctk.CTkLabel(master=master, text="Instance Path")
    label.grid(row=1, column=0, padx=10, sticky="w")

    instance = ctk.CTkEntry(master=master, placeholder_text="Enter the path to your Minecraft instance.", height=36)
    instance.grid(row=2, column=0, padx=(10, 5), pady=(0, 5), sticky="ew")

    # Events
    instance.bind(sequence="<KeyRelease>", command=lambda event : handleKeyPress(instance, "instance"))

    instance_search = ctk.CTkButton(master=master, text="Explore", command=lambda: view.searchForDir(instance), height=36)
    instance_search.grid(row=2, column=1, padx=(0, 10), pady=(0, 5), sticky="ew")

    if bool(state["instance"]):
        view.setEntry(instance, state["instance"])

    return [instance, instance_search]