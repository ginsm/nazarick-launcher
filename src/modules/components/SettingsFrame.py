import os
from app import reload_widgets
from modules import store
from customtkinter.windows.widgets.theme import ThemeManager

def create(ctk, master, pool, state):
    frame = ctk.CTkFrame(master=master, corner_radius=0, fg_color=('#dbdbdb', '#2b2b2b'))
    h2_size=24

    options = {
        'theme': ctk.StringVar(value=state.get('theme') or 'System'),        
        'accent': ctk.StringVar(value=state.get('accent') or 'blue'),
        'autoclose': ctk.BooleanVar(value=state.get('autoclose') or False),
        'autorestart': ctk.BooleanVar(value=state.get('autorestart') or False),
        'threadamount': ctk.IntVar(value=state.get('threadamount') or 4),
        'logging': ctk.BooleanVar(value=state.get('logging') or True),
        'debug': ctk.BooleanVar(value=state.get('debug') or False)
    }

    # ---- Appearance ---- #
    appearance_label = ctk.CTkLabel(master=frame, text='Appearance')
    appearance_label.cget('font').configure(size=h2_size)

    # Theme
    theme_label = ctk.CTkLabel(master=frame, text="Theme")
    theme = ctk.CTkOptionMenu(
        master=frame, 
        values=['System', 'Dark', 'Light'],
        command=lambda _: set_theme(ctk, options),
        variable=options['theme'],
        width=200,
    )

    # Accent Color
    colors = [
        {'name': 'blue', 'title': 'Blue', 'hex': '#1f6aa5'},
        {'name': 'dark-blue', 'title': 'Dark Blue', 'hex': '#1f538d'},
        {'name': 'green', 'title': 'Green', 'hex': '#2fa572'},
    ]

    accent_label = ctk.CTkLabel(master=frame, text="Accent Color")
    accent_frame = ctk.CTkFrame(master=frame, fg_color='transparent')
    for index, color in enumerate(colors):
        create_accent_color_buttons(ctk, master, accent_frame, pool, color, index, options)


    # ---- Functionality ---- #
    functionality_label = ctk.CTkLabel(master=frame, text="Functionality")
    functionality_label.cget('font').configure(size=h2_size)

    # Automation
    automation_label = ctk.CTkLabel(master=frame, text="Automation")

    # Auto Close
    autoclose_checkbox = ctk.CTkCheckBox(
        master=frame,
        text='Close after launching game',
        command=lambda: store.set_menu_option('autoclose', options),
        variable=options['autoclose'],
        onvalue=True,
        offvalue=False,
        width=200
    )

    # Auto Restart
    autorestart_checkbox = ctk.CTkCheckBox(
        master=frame,
        text='Restart after updating the launcher',
        command=lambda: store.set_menu_option('autorestart', options),
        variable=options['autorestart'],
        onvalue=True,
        offvalue=False,
        width=200
    )

    # Amount of Threads
    if (os.cpu_count() > 4):
        thread_label = ctk.CTkLabel(master=frame, text=f"Thread Amount: {options['threadamount'].get()}/{os.cpu_count()}")
        thread_slider = ctk.CTkSlider(
            master=frame,
            from_=4,
            to=os.cpu_count(),
            number_of_steps=os.cpu_count() - 4,
            command=lambda value: set_thread_count(options, ctk.IntVar(value=int(value)), thread_label)
        )
        thread_slider.set(options['threadamount'].get())

    # ---- Debugging ---- #
    developer_label = ctk.CTkLabel(master=frame, text="Developer")
    developer_label.cget('font').configure(size=h2_size)

    # Logging
    logging_checkbox = ctk.CTkCheckBox(
        master=frame,
        text='Store application logs',
        command=lambda: store.set_menu_option('logging', options),
        variable=options['logging'],
        onvalue=True,
        offvalue=False,
        width=200
    )
    # Debug Enabled
    debug_checkbox = ctk.CTkCheckBox(
        master=frame,
        text='Run in debug mode',
        command=lambda: store.set_menu_option('debug', options),
        variable=options['debug'],
        onvalue=True,
        offvalue=False,
        width=200
    )


    appearance_label.grid(row=0, column=0, padx=15, pady=(20, 5), sticky='w')
    theme_label.grid(row=1, column=0, padx=15, pady=(5, 0), sticky='w')
    theme.grid(row=2, column=0, padx=15, pady=5, sticky='w')
    accent_label.grid(row=3, column=0, padx=15, pady=(10, 0), sticky='w')
    accent_frame.grid(row=4, column=0, padx=15, pady=(5, 0), sticky='w')

    functionality_label.grid(row=5, column=0, padx=15, pady=(35, 5), sticky='w')
    automation_label.grid(row=6, column=0, padx=15, pady=(5, 0), sticky='w')
    autoclose_checkbox.grid(row=7, column=0, padx=15, pady=(10, 5), sticky='w')
    autorestart_checkbox.grid(row=8, column=0, padx=15, pady=5, sticky='w')
    thread_label.grid(row=9, column=0, padx=15, pady=(10, 0), sticky='w')
    thread_slider.grid(row=10, column=0, padx=15, pady=5, sticky='w')

    developer_label.grid(row=11, column=0, padx=15, pady=(30, 5), sticky='w')
    logging_checkbox.grid(row=12, column=0, padx=15, pady=(10, 5), sticky='w')
    debug_checkbox.grid(row=13, column=0, padx=15, pady=5, sticky='w')

    return frame


def create_accent_color_buttons(ctk, app, master, pool, color, index, options):
    current_theme = ThemeManager._currently_loaded_theme
    selected = current_theme == color['name']

    button = ctk.CTkButton(
        master=master,
        text='',
        height=20,
        width=20,
        border_width=2 if selected else 0,
        border_color=('#1d1e1e', '#ffffff') if selected else color['hex'],
        fg_color=color['hex'],
        hover=False,
        command=lambda: set_accent(ctk, app, color, options, pool)
    )

    button.grid(row=0, column=index, padx=2 if index != 0 else (0, 2))


def set_accent(ctk, app, color, options, pool):
    # Store new accent color
    options['accent'] = ctk.StringVar(value=color['name'])
    store.set_menu_option('accent', options)

    # Set color and reload widgets
    ctk.set_default_color_theme(color['name'])
    reload_widgets(ctk, app, pool, store.get_state())


def set_theme(ctk, options):
    ctk.set_appearance_mode(options['theme'].get())
    store.set_menu_option('theme', options)


def set_thread_count(options, value, label):
    options['threadamount'] = value
    label.configure(text=f"Thread Amount: {value.get()}/{os.cpu_count()}")
    store.set_menu_option('threadamount', options)