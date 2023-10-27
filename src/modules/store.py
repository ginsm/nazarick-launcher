import os
from tinydb import TinyDB
from .utility import destructure

# The default state for the store
default_state={
    "autoclose": False,
    "game": "minecraft",
    "frame": "minecraft",
    "games": {
        "minecraft": {
            "selectedpack": "nazarick-smp",
            "nazarick-smp": { "instance": "", "executable": "" }
        },
        "valheim": {
            "selectedpack": "nazarick-smp",
            "nazarick-smp": { "instance": "", "executable": "" }
        }
    },
    "geometry": "1280x720",
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
    else:
        updatedState = update(state.get(doc_id=1))
        if state.get(doc_id=1) != updatedState:
            print("Ran")
            setStateDoc(updatedState)


# State doc getter/setter
def getStateDoc():
    global database
    return database.table('state')

def setStateDoc(data):
    if bool(data):
        state = getStateDoc()
        state.remove(doc_ids=[1])
        state.insert(data)


# Game getter/setter
def getGame():
    state = getState()
    return state['game']

def setGame(game):
    if bool(game):
        setState({'game': game})


# Pack getter/setter
def getSelectedPack():
    state = getState()
    game = getGame()
    return state['games'][game]['selectedpack']

def setSelectedPack(pack):
    if bool(pack):
        game = getGame()
        state = getState()
        state['games'][game].update({'selectedpack': pack})
        setState(state)


# Game state getter/setter
def getGameState():
    game = getGame()
    pack = getSelectedPack()
    state = getState()
    return state['games'][game][pack]

def setGameState(obj):
    if bool(obj):
        game = getGame()
        pack = getSelectedPack()
        state = getState()
        state['games'][game][pack].update(obj)
        setState(state)


# Generic state getter/setter
def getState(*args):
    state = getStateDoc().get(doc_id=1)
    output = destructure(state, args=args)
    return output if bool(output) else state

def setState(data={}):
    state = getStateDoc()
    if bool(data):
        state.update(data, doc_ids=[1])


# Set menu option
def setMenuOption(name, options):
    setState({name: options[name].get()})


# ---- State updates ----
def update(state):
    state = update_107(state)
    return state

# Version 1.0.7 state updater
def update_107(state):
    # Check if the state is old 1.0.6 format
    if state.get('executable'):
        executable = state['executable']
        instance = state['instance']

        # Update data
        stateUpdate = {
            'game': 'minecraft',
            'frame': 'minecraft',
            'games': {
                'minecraft': {
                    'selectedpack': 'nazarick-smp',
                    'nazarick-smp': {
                        'instance': instance,
                        'executable': executable
                    }
                },
                'valheim': {
                    'selectedpack': 'nazarick-smp',
                    'nazarick-smp': {
                        'instance': '',
                        'executable': ''
                    }
                }
            }
        }

        # Remove old unused keys
        del state['executable']
        del state['instance']

        # Update the state
        state.update(stateUpdate)

    # Return the updated state
    return state