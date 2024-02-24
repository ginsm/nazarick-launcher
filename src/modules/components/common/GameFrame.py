from modules import store, view
from modules.components.common import ChangesBox, ExplorerSearch, LogBox, ProgressBar, UpdateButton
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
        command=lambda: store.set_tab(tabs.get())
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
    if modpacks:
        modpack_dropdown = ctk.CTkOptionMenu(
            master=tabs,
            values=[modpack.get('name') for modpack in modpacks],
            command=store.set_selected_pack,
            width=200
        )

        modpack_dropdown.place(rely=0.0, relx=1.0, x=-5, y=14, anchor='ne')

    # Set the selected tab
    tabs.set(store.get_tab(name) or 'Settings')

    # ---- Changes Tab ---- #
    [changebox, html_frame] = ChangesBox.create(ctk=ctk, parent=tabs.tab('Changes'), game=name)
    changebox.grid(row=0, columnspan=2, pady=5, padx=5, sticky='nsew')

    # ---- Logs Tab ---- #
    logbox = LogBox.create(
        ctk=ctk,
        master=tabs.tab('Logs'),
        game=name
    )
    logbox['get']().grid(row=0, columnspan=2, pady=5, padx=5, sticky='nsew')

    # ---- Settings Tab ---- #
    for index, setting in enumerate(settings):
        entry = ExplorerSearch.create(
            ctk=ctk,
            master=tabs.tab('Settings'),
            game=name.lower(),
            app=app,
            label=setting.get('label'),
            placeholder=setting.get('placeholder'),
            name=setting.get('name'),
            find=setting.get('type')
        )
        entry[-1].grid(row=index, columnspan=2, pady=(2, 6), padx=(10, 6), sticky='ew')
        view.add_lockable([*entry[:-1]])

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
    update_button = UpdateButton.create(
        ctk=ctk,
        parent=frame,
        pool=pool,
        update_fn=updater.start,
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