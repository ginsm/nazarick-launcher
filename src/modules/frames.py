from modules import game_list, store, utility, view
from modules.components import AppSideBar, SettingsFrame
from modules.components.common import GameFrame

generated_frames = []

def create_frames(ctk, app, pool, state, cover_frame = None):
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
    selected_frame = store.get_frame()
    for frame_data in frames:
        [name, frame] = utility.destructure(frame_data, ['name', 'frame'])
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

    # Delete all extra widgets
    children = app.winfo_children()
    for widget in children:
        if widget is not cover_frame:
            widget.destroy()

    # Clear all stored widgets
    generated_frames.clear()
    AppSideBar.clear_frame_Buttons()
    view.clear_lockable_elements()

    # Recreate the frames
    create_frames(ctk, app, pool, state, cover_frame)

    # Raise cover frame
    if cover_frame: cover_frame.tkraise()