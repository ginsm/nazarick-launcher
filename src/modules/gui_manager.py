from tktooltip import ToolTip
from modules import game_list, state_manager
from modules.decorators.debounce import debounce
from modules.components import AppSideBar, SettingsFrame
from modules.components.common import GameFrame

generated_frames = []
lockable_elements = []
window_width = 0
window_height = 0

def create_gui(ctk, app, pool, state, cover_frame = None):
    global generated_frames

    # Create frames and add their data to frames
    games = game_list.LIST
    for game in games:
        [frame, textbox] = GameFrame.create(ctk, app, pool, **game)
        generated_frames.append({'name': game.get('name'), 'frame': frame, 'textbox': textbox})
        frame.grid(row=0, column=1, rowspan=len(games) + 2, sticky='nsew')

        # Raise cover frame whenever grid changes
        if cover_frame: cover_frame.tkraise()

    settings_frame = SettingsFrame.create(ctk, app, pool, state)
    generated_frames.append({'name': 'Settings', 'frame': settings_frame, 'textbox': None})

    sidebar = AppSideBar.create(ctk, app, generated_frames)
    generated_frames.append({'name': 'Sidebar', 'frame': sidebar, 'textbox': None})

    # Position frames
    sidebar.grid(row=0, column=0, sticky='ns', rowspan=2)
    settings_frame.grid(row=0, column=1, rowspan=len(generated_frames), sticky='nsew')

    # Raise cover frame
    if cover_frame: cover_frame.tkraise()

    # Raise selected frame and set color
    raise_selected_frame(generated_frames)


def raise_selected_frame(frames):
    selected_frame = state_manager.get_frame()
    for frame_data in frames:
        name, frame = [
            frame_data.get('name'),
            frame_data.get('frame')
        ]
        if name.lower() == selected_frame:
            frame.tkraise()
            AppSideBar.color_buttons(name)


def broadcast(message):
    global generated_frames

    for data in generated_frames:
        textbox = data['textbox']
        if textbox:
            textbox['log'](message, broadcast=True)


def reload_widgets(ctk, app, pool, state, cover_frame = None):
    global generated_frames

    # Delete all frames
    for data in generated_frames:
        frame = data['frame']
        frame.destroy()

    # Prevents an issue with tooltips when reloading
    cleanup_tooltips(app)

    # Clear all stored widgets
    generated_frames.clear()
    AppSideBar.clear_frame_Buttons()
    clear_lockable_elements()

    # Recreate the frames
    create_gui(ctk, app, pool, state, cover_frame)

    # Raise cover frame
    if cover_frame: cover_frame.tkraise()


def reload_frame(ctk, app, pool, name, cover_frame = None):
    global generated_frames
    found = False

    # Search for frame
    for index, frame in enumerate(generated_frames):
        if frame.get('name') == name:
            found = True
            frame.get('frame').destroy()
            generated_frames.pop(index)

    # Destroy and rebuild frame
    if found:
        games = game_list.LIST
        
        for game in games:
            if game.get('name') == name:
                # Rebuild the frame
                [frame, textbox] = GameFrame.create(ctk, app, pool, **game)
                generated_frames.append({'name': game.get('name'), 'frame': frame, 'textbox': textbox})
                frame.grid(row=0, column=1, rowspan=len(games) + 2, sticky='nsew')

                # Reconfigure AppSideBar
                AppSideBar.update_button_frame(game.get('name'), frame)

                # Raise the cover frame
                if cover_frame: cover_frame.tkraise()

    # Clean up unused widgets
    cleanup_tooltips(app)
    cleanup_lockable_elements()

    # Raise selected frame and set color
    raise_selected_frame(generated_frames)


def cleanup_tooltips(app):
    children = app.winfo_children()
    for child in children:
        if isinstance(child, ToolTip):
            master_exists = child.widget.master.winfo_exists()
            if master_exists:
                child.on_leave()
            else:
                child.destroy()


def add_lockable(lockable):
    global lockable_elements

    if isinstance(lockable, list):
        for element in lockable:
            lockable_elements.append(element)
    else:
        lockable_elements.append(lockable)


def cleanup_lockable_elements():
    global lockable_elements
    element_exists = lambda element: element.winfo_exists()
    lockable_elements = list(filter(element_exists, lockable_elements))


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
        state_manager.set_state({'geometry': f'{window_width}x{window_height}'})