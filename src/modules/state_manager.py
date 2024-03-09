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
    'geometry': '1280x720',
    'logging': True,
    'mode': 'System',
    'theme': 'Blue',
    'threadamount': 4,
    'debug': False,
    'games': {},
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
    games = state.get('games')
    if games and game in games:
        return games.get(game).get('selectedpack')
    else:
        return ''

def set_selected_pack(pack):
    if bool(pack):
        game = get_frame()
        state = get_state()
        state['games'][game].update({'selectedpack': pack})
        set_state(state)


# Game state getter/setter
def get_game_state(game=""):
    game = game.lower() or get_frame()
    state = get_state()

    if not 'games' in state or game not in state.get('games'):
        return {}

    return state.get('games').get(game)
    
def set_game_state(data, game=""):
    if bool(data):
        game = game.lower() or get_frame()
        state = get_state()
        
        # Create games object
        if not 'games' in state:
            state['games'] = {}

        # Add data to game object
        if game in state['games']:
            state['games'][game].update(data)
        else:
            state['games'][game] = data

        set_state(state)


# Pack state getter/setter
def get_pack_state(game="", pack=""):
    game = game.lower() or get_frame()
    state = get_state()
    if game in state['games']: 
        pack = pack or get_selected_pack(game)
        if pack:
            return state['games'][game][pack]
    return {}

def set_pack_state(obj, game="", pack=""):
    if bool(obj):
        game = game.lower() or get_frame()
        pack = pack or get_selected_pack(game)
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


def create_game_state(game):
    name = game.get('name')
    modpacks = game.get('modpacks')
    state = get_game_state(name)

    # Get game setting names
    game_settings = [setting.get('name') for setting in game.get('settings')]

    # Add modpacks to state
    if modpacks:
        if not state.get('selectedpack'):
            state.update({'selectedpack': modpacks[0].get('name')})

        for modpack in modpacks:
            pack = modpack.get('name')
            if not state.get(pack):
                state.update({
                    pack: {key: '' for key in game_settings}
                })

    if not state.get('selectedpack'):
        state.update({'selectedpack': ''})
    
    set_game_state(state, name)


def get_game_paths():
    state = get_state()
    games = state.get('games')
    paths = []
    if games:
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