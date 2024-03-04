import os
from tinydb import TinyDB
from modules.utility import destructure

# The default state for the store
default_state={
    'autoclose': False,
    'frame': 'minecraft',
    'tab': {
        'minecraft': 'Settings',
        'valheim': 'Settings'
    },
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
    'mode': 'System',
    'theme': 'Blue',
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


# State doc getter/setter
def get_state_doc():
    global database
    return database.table('state')

def set_state_doc(data):
    if bool(data):
        state = get_state_doc()
        state.remove(doc_ids=[1])
        state.insert(data)


# Frame getter/setter
def get_frame():
    state = get_state()
    return state['frame']

def set_frame(frame):
    if bool(frame):
        set_state({'frame': frame})


# Tab getter/setter
def get_tab(frame):
    if bool(frame):
        frame = frame.lower()
        state = get_state()
        return state.get('tab').get(frame)
    return False

def set_tab(tab):
    if bool(tab):
        frame = get_frame()
        state = get_state()
        state['tab'][frame] = tab
        set_state(state)


# Pack getter/setter
def get_selected_pack(game=""):
    state = get_state()
    game = game.lower() or get_frame()
    return state['games'][game]['selectedpack'] if game in state['games'] else 'nazarick-smp'

def set_selected_pack(pack):
    if bool(pack):
        game = get_frame()
        state = get_state()
        state['games'][game].update({'selectedpack': pack})
        set_state(state)


# Game state getter/setter
def get_game_state(game=""):
    game = game or get_frame()
    state = get_state()
    if game in state['games']: 
        pack = get_selected_pack(game)
        return state['games'][game][pack]
    else:
        return {}

def set_game_state(obj):
    if bool(obj):
        game = get_frame()
        pack = get_selected_pack()
        state = get_state()
        if game in state['games']:
            state['games'][game][pack].update(obj)
        else:
            state['games'].update({
                game: 
                {
                    "selectedpack": pack,
                    pack: obj}
            })
        set_state(state)

def get_game_paths():
    state = get_state()
    games = state.get('games')
    paths = []

    for game in games:
        game_data = games.get(game)
        for pack in game_data:
            # Ignore selectedpack key
            if pack != 'selectedpack':
                pack_data = game_data.get(pack)
                for path in pack_data:
                    # TODO normalize to just install
                    if path in ['instance', 'install']:
                        paths.append(pack_data.get(path))

    return paths


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