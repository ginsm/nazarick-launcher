from modules import view
from modules.components.common import ExplorerSearch, LogBox, UpdateButton


def create(ctk, app, pool, name, settings, updater):
    frame = ctk.CTkFrame(master=app, corner_radius=0, border_width=0)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    # Textbox component
    textbox = LogBox.create(
        ctk=ctk,
        master=frame,
        game=name
    )

    textbox['get']().grid(row=0, columnspan=2, pady=(15, 5), padx=10, sticky='nsew')

    # Setting component(s)
    for index, setting in enumerate(settings):
        entry = ExplorerSearch.create(
            ctk=ctk,
            master=frame,
            game=name.lower(),
            app=app,
            label=setting.get('label'),
            placeholder=setting.get('placeholder'),
            name=setting.get('name'),
            find=setting.get('type')
        )

        entry[-1].grid( row=index + 1, padx=1, sticky='ew', columnspan=2)
        view.add_lockable([*entry[:-1]])

    # Update button component
    update_button = UpdateButton.create(
        ctk=ctk,
        master=frame,
        textbox=textbox,
        pool=pool,
        update_fn=updater.start
    )

    update_button.grid(
        row=len(settings) + 1,
        padx=10,
        pady=(14, 15),
        columnspan=2,
        sticky='ew'
    )

    return [frame, textbox]