from modules import view
from modules.components.common import ChangesBox, ExplorerSearch, LogBox, ProgressBar, UpdateButton
from customtkinter.windows.widgets.theme import ThemeManager


def create(ctk, app, pool, name, settings, updater):
    frame = ctk.CTkFrame(master=app, corner_radius=0, border_width=0)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    # ---- Tab View ---- #
    # Create the tabview that changes, logs, and settings will live in
    tabs = ctk.CTkTabview(master=frame, anchor='nw', border_width=0, corner_radius=0)

    # Add tabs
    tabs.add('Changes')
    tabs.add('Logs')
    tabs.add('Settings')

    # Configure how tabs rows/columns
    tabs.tab('Changes').grid_columnconfigure(0, weight=1)
    tabs.tab('Changes').grid_rowconfigure(0, weight=1)
    tabs.tab('Logs').grid_columnconfigure(0, weight=1)
    tabs.tab('Logs').grid_rowconfigure(0, weight=1)
    tabs.tab('Settings').grid_columnconfigure(0, weight=1)

    # Configure segmented button appearance (hacky, may break)
    segmented_buttons = tabs._segmented_button
    segmented_buttons.configure(
        height=36,
        corner_radius=10,
        fg_color=ThemeManager.theme.get('CTkFrame').get('fg_color')
    )

    tabs.grid(row=0, columnspan=2, padx=10, sticky='nsew')

    # ---- Changes Tab ---- #
    changes = ChangesBox.create(ctk=ctk, parent=tabs.tab('Changes'), game=name)
    changes.grid(row=0, columnspan=2, pady=5, padx=5, sticky='nsew')

    # ---- Logs Tab ---- #
    textbox = LogBox.create(
        ctk=ctk,
        master=tabs.tab('Logs'),
        game=name
    )
    textbox['get']().grid(row=0, columnspan=2, pady=5, padx=5, sticky='nsew')

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
    progress = ProgressBar.create(ctk, progress_frame)
    progress_label.grid(row=0, sticky='w')
    progress.bar.grid(row=1, pady=(2,0), sticky='we')

    # Position progress frame
    progress_frame.grid(row=len(settings) + 1, column=0, sticky='nswe', pady=5, padx=(15, 5))

    # ---- Update button ---- #
    update_button = UpdateButton.create(
        ctk=ctk,
        master=frame,
        textbox=textbox,
        pool=pool,
        progress=progress,
        update_fn=updater.start
    )
    update_button.grid( row=len(settings) + 1, column=1, padx=(10, 15), pady=15, sticky='ew')

    return [frame, textbox]