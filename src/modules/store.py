import os
from tinydb import TinyDB
from modules.utility import destructure

# The default state for the store
default_state={
    'autoclose': False,
    'accent': 'blue',
    'game': 'minecraft',
    'games': {
        'minecraft': {
            'selectedpack': 'nazarick-smp',
            'nazarick-smp': { 'instance': '', 'executable': '' }
        },
        'valheim': {
            'selectedpack': 'nazarick-smp',
            'nazarick-smp': { 'install': '' }
        }
    },
    'geometry': '1280x720',
    'logging': True,
    'theme': 'System',
    'threadamount': 4,
    'debug': False,
}


def init(path):
    # Make the path
    if (not os.path.exists(path)):
        os.makedirs(path)

    # Assign database variable globally (module scope)
    global database
    database = TinyDB(os.path.join(path, 'state.json'))
    
    # Initialize the state
    state = database.table('state')
    if state.get(doc_id=1) is None:
        state.insert(default_state)
    else:
        updated_state = update(state.get(doc_id=1))
        if state.get(doc_id=1) != updated_state:
            set_state_doc(updated_state)


# State doc getter/setter
def get_state_doc():
    global database
    return database.table('state')

def set_state_doc(data):
    if bool(data):
        state = get_state_doc()
        state.remove(doc_ids=[1])
        state.insert(data)


# Game getter/setter
def get_game():
    state = get_state()
    return state['game']

def set_game(game):
    if bool(game):
        set_state({'game': game})


# Pack getter/setter
def get_selected_pack(game=""):
    state = get_state()
    game = game or get_game()
    return state['games'][game]['selectedpack']

def set_selected_pack(pack):
    if bool(pack):
        game = get_game()
        state = get_state()
        state['games'][game].update({'selectedpack': pack})
        set_state(state)


# Game state getter/setter
def get_game_state(game=""):
    game = game or get_game()
    pack = get_selected_pack(game)
    state = get_state()
    return state['games'][game][pack]

def set_game_state(obj):
    if bool(obj):
        game = get_game()
        pack = get_selected_pack()
        state = get_state()
        state['games'][game][pack].update(obj)
        set_state(state)


# Generic state getter/setter
def get_state(*args):
    state = get_state_doc().get(doc_id=1)
    output = destructure(state, args=args)
    return output if bool(output) else state

def set_state(data={}):
    state = get_state_doc()
    if bool(data):
        state.update(data, doc_ids=[1])


# Set menu option
def set_menu_option(name, options):
    set_state({name: options[name].get()})


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
                        'install': ''
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