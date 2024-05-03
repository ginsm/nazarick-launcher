import logging
from modules import gui_manager, state_manager
from modules.components.common import ChangesBox, CoverFrame, ExplorerSearch, GameSettings, ProgressBar
from modules.components.common.UpdateButton import UpdateButton
from customtkinter.windows.widgets.theme import ThemeManager


def create(ctk, app, pool, name, settings, updater, modpacks = False):
    frame = ctk.CTkFrame(master=app, corner_radius=0, border_width=0)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    # ---- Tab View ---- #
    # Create the tabview that changes, logs, and settings will live in
    tabs = ctk.CTkTabview(
        master=frame,
        anchor='nw',
        border_width=0,
        corner_radius=0,
        fg_color='transparent',
        command=lambda: state_manager.set_tab(tabs.get())
    )

    # Add tabs
    for tab in ['Changes', 'Logs', 'Settings']:
        tabs.add(tab)
        # Configure all tabs columns to occupy entire space
        tabs.tab(tab).grid_columnconfigure(0, weight=1)

    # Configure some tabs rows to occupy entire space
    tabs.tab('Changes').grid_rowconfigure(0, weight=1)
    tabs.tab('Logs').grid_rowconfigure(0, weight=1)

    # Configure segmented button appearance (hacky, may break when ctk updates)
    segmented_buttons = tabs._segmented_button
    segmented_buttons.configure(
        height=36,
        corner_radius=10,
        fg_color=ThemeManager.theme.get('CTkFrame').get('fg_color')
    )

    tabs.grid(row=0, columnspan=2, padx=10, sticky='nsew')

    # Add modpack dropdown
    if modpacks and len(modpacks) > 1:
        def select_pack(value):
            current_pack = state_manager.get_selected_pack(name)
            if value != current_pack:
                state_manager.set_selected_pack(value)
                cover_frame = CoverFrame.create(ctk, app)
                gui_manager.reload_frame(ctk, app, pool, name, cover_frame)
                cover_frame.destroy()

        modpack_dropdown = ctk.CTkOptionMenu(
            master=tabs,
            values=[modpack.get('name') for modpack in modpacks],
            command=select_pack,
            width=200
        )

        modpack_dropdown.set(state_manager.get_selected_pack(name))
        modpack_dropdown.place(rely=0.0, relx=1.0, x=-5, y=14, anchor='ne')
        gui_manager.add_lockable(modpack_dropdown)

    # Set the selected tab
    tabs.set(state_manager.get_tab(name) or 'Settings')

    # ---- Changes Tab ---- #
    [changebox, html_frame] = ChangesBox.create(ctk=ctk, parent=tabs.tab('Changes'), game=name)
    changebox.grid(row=0, columnspan=2, pady=5, padx=5, sticky='nsew')

    # ---- Logs Tab ---- #
    logbox = logging.getHandlerByName('logbox').get_logbox(
        ctk=ctk,
        parent=tabs.tab('Logs'),
        game=name.lower(),
        pack=state_manager.get_selected_pack(name)
    )
    logbox.grid(row=0, columnspan=2, pady=5, padx=5, sticky='nsew')

    # ---- Settings Tab ---- #
    GameSettings.create(
        ctk=ctk,
        parent=tabs.tab('Settings'),
        game=name,
        app=app,
        settings=settings
    )

    # ---- Progress Bar ---- #
    progress_frame = ctk.CTkFrame( master=frame, fg_color='transparent', border_width=0)
    progress_frame.grid_columnconfigure(0, weight=1)

    # Create progress frame contents and position them
    progress_label = ctk.CTkLabel(master=progress_frame, text='Update Progress')
    progressbar = ProgressBar.create(ctk, progress_frame)

    progress_label.grid(row=0, sticky='w')
    progressbar.bar.grid(row=1, pady=(2,0), sticky='we')

    # Position progress frame
    progress_frame.grid(row=len(settings) + 1, column=0, sticky='nswe', pady=5, padx=(15, 5))

    # ---- Update button ---- #
    update_button = UpdateButton().create(
        ctk=ctk,
        parent=frame,
        pool=pool,
        updater=updater,
        widgets={
            'logbox': logbox,
            'changebox': changebox,
            'html_frame': html_frame,
            'progressbar': progressbar,
            'tabs': tabs
        },
        game=name
    )
    update_button.grid(row=len(settings) + 1, column=1, padx=(10, 15), pady=15, sticky='ew')

    return [frame, logbox]