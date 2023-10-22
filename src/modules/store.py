import os
from tinydb import TinyDB
from .utility import destructure, getenv

# The default state for the store
default_state={
    "autoclose": False,
    "executable": "",
    "geometry": "1280x720",
    "instance": "",
    "logging": True,
    "theme": "System",
    "debug": False,
}

def init(path):
    # Make the path
    if (not os.path.exists(path)):
        os.makedirs(path)

    # Assign database variable globally (module scope)
    global database
    database = TinyDB(os.path.join(path, "state.json"))
    
    # Initialize the state
    state = database.table("state")
    if state.get(doc_id=1) is None:
        state.insert(default_state)

def setState(data={}):
    global database
    state = database.table("state")
    if bool(data):
        state.update(data, doc_ids=[1])

def getState(*args):
    global database
    state = database.table("state").get(doc_id=1)
    output = destructure(state, args=args)
    return output if bool(output) else state

def setMenuOption(name, options):
    setState({name: options[name].get()})