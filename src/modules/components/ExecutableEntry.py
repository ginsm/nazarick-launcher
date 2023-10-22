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
    label = ctk.CTkLabel(master=master, text="Launcher's Executable Path")
    label.grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")

    executable = ctk.CTkEntry(master=master, placeholder_text="Enter the path to your launcher's executable.", height=36)
    executable.grid(row=4, column=0, padx=(10, 5), pady=(0, 5), sticky="ew")
    executable.bind(sequence="<KeyRelease>", command=lambda event : handleKeyPress(executable, "executable"))

    executable_search = ctk.CTkButton(master=master, text="Explore", command=lambda: view.searchForFile(executable), height=36)
    executable_search.grid(row=4, column=1, padx=(0, 10), pady=(0, 5), sticky="ew")

    if bool(state["executable"]):
        view.setEntry(executable, state["executable"])

    return [executable, executable_search]