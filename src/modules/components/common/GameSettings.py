from modules import gui_manager, state_manager
from modules.components.common import ExplorerSearch
from modules.path_finder.autodetect import autodetect_settings


def create(ctk, parent, game, app, pool, settings):
    game_state = state_manager.get_pack_state(game)

    if settings:
        for index, setting in enumerate(settings):
            match setting.get('type'):
                # File & directory search settings
                case 'directory' | 'file':
                    entry = ExplorerSearch.create(
                        ctk=ctk,
                        master=parent,
                        game=game.lower(),
                        app=app,
                        label=setting.get('label'),
                        placeholder=setting.get('placeholder'),
                        name=setting.get('name'),
                        find=setting.get('type'),
                        elevate_check=setting.get('elevate_check')
                    )
                    entry[-1].grid(row=index, columnspan=2, pady=(2, 6), padx=(10, 6), sticky='ew')
                    gui_manager.add_lockable([*entry[:-1]])

                # Dropdown settings
                case 'dropdown':
                    dropdown_var = ctk.StringVar(value=game_state.get(setting.get('name')) or 'Steam')
                    name = setting.get('name')

                    # Create widgets
                    dropdown_frame = ctk.CTkFrame(master=parent, fg_color='transparent', border_width=0)
                    dropdown_label = ctk.CTkLabel(master=dropdown_frame, text=setting.get('label'))
                    dropdown = ctk.CTkOptionMenu(
                        master=dropdown_frame,
                        values=setting.get('choices'),
                        command=lambda value: state_manager.set_pack_state({name: value}),
                        variable=dropdown_var,
                        width=200
                    )

                    # Position widgets
                    dropdown_label.grid(row=0, columnspan=2, pady=2, sticky='w')
                    dropdown.grid(row=1, columnspan=2, pady=0, padx=0, sticky='w')
                    dropdown_frame.grid(row=index, columnspan=2, pady=(2, 6), padx=(10, 6), sticky='ew')

                    # Add to lockable widgets
                    gui_manager.add_lockable(dropdown)

                # Invalid setting type
                case _:
                    raise Exception(f"Invalid setting type provided for {game}'s '{setting.get('name')}' setting: {setting.get('type')}.")
                
        autodetect = ctk.CTkButton(
            master=parent,
            text='Auto Detect',
            command=autodetect_settings(ctk, app, game, settings, pool)
        )

        autodetect.grid(row=len(settings), columnspan=2, pady=12, padx=(10, 6), sticky='w')

    else:
        label = ctk.CTkLabel(parent, text="This game has no settings.")
        label.grid(row=0, columnspan=2, pady=6, padx=(10, 6), sticky='w')

