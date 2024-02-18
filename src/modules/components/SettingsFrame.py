import os
from modules import store, theme_list, frames
from customtkinter.windows.widgets.theme import ThemeManager

from modules.components.common import CoverFrame

def create(ctk, parent, pool, state):
    frame = ctk.CTkFrame(master=parent, corner_radius=0, border_width=0)
    h2_size=24

    options = {
        'mode': ctk.StringVar(value=state.get('mode') or 'System'),        
        'theme': ctk.StringVar(value=state.get('theme') or 'blue'),
        'autoclose': ctk.BooleanVar(value=state.get('autoclose') or False),
        'autorestart': ctk.BooleanVar(value=state.get('autorestart') or False),
        'threadamount': ctk.IntVar(value=state.get('threadamount') or 4),
        'logging': ctk.BooleanVar(value=state.get('logging') or True),
        'debug': ctk.BooleanVar(value=state.get('debug') or False)
    }

    # ---- Appearance ---- #
    appearance_label = ctk.CTkLabel(master=frame, text='Appearance')
    appearance_label.cget('font').configure(size=h2_size)

    # Mode
    mode_label = ctk.CTkLabel(master=frame, text="Mode")
    mode_dropdown = ctk.CTkOptionMenu(
        master=frame, 
        values=['System', 'Dark', 'Light'],
        command=lambda _: set_mode(ctk, parent, options, pool),
        variable=options['mode'],
        width=200,
    )

    # Theme
    themes = theme_list.get_themes()

    theme_label = ctk.CTkLabel(master=frame, text="Theme")
    theme_dropdown = ctk.CTkOptionMenu(
        master=frame,
        values=list(map(lambda theme: theme['title'], themes)),
        command=lambda theme: set_theme(ctk, parent, theme_list.get_theme_from_title(theme), options, pool),
        variable=options['theme'],
        width=200
    )


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


    # ---- Developer---- #
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


    # Position widgets
    padx = 25
    pady_h2 = (25, 5)
    pady_h3 = (5, 0)
    pady_widget = (2, 5)

    appearance_label.grid(row=0, column=0, padx=padx, pady=pady_h2, sticky='w')
    mode_label.grid(row=1, column=0, padx=padx, pady=pady_h3, sticky='w')
    mode_dropdown.grid(row=2, column=0, padx=padx, pady=pady_widget, sticky='w')
    theme_label.grid(row=3, column=0, padx=padx, pady=pady_h3, sticky='w')
    theme_dropdown.grid(row=4, column=0, padx=padx, pady=pady_widget, sticky='w')

    functionality_label.grid(row=5, column=0, padx=padx, pady=pady_h2, sticky='w')
    automation_label.grid(row=6, column=0, padx=padx, pady=pady_h3, sticky='w')
    autoclose_checkbox.grid(row=7, column=0, padx=padx, pady=pady_widget, sticky='w')
    autorestart_checkbox.grid(row=8, column=0, padx=padx, pady=pady_widget, sticky='w')
    thread_label.grid(row=9, column=0, padx=padx, pady=pady_h3, sticky='w')
    thread_slider.grid(row=10, column=0, padx=padx, pady=pady_widget, sticky='w')

    developer_label.grid(row=11, column=0, padx=padx, pady=pady_h2, sticky='w')
    logging_checkbox.grid(row=12, column=0, padx=padx, pady=pady_widget, sticky='w')
    debug_checkbox.grid(row=13, column=0, padx=padx, pady=pady_widget, sticky='w')

    return frame


def set_mode(ctk, app, options, pool):
    # This frame essentially makes the app look pretty whilst loading/switching themes
    cover_frame = CoverFrame.create(ctk, app)
    cover_frame.grid(row=0, column=0, rowspan=5, columnspan=5, sticky='nsew')

    # Set the mode
    ctk.set_appearance_mode(options['mode'].get())
    store.set_menu_option('mode', options)

    # Reload the widgets
    frames.reload_widgets(ctk, app, pool, store.get_state(), cover_frame)

    # Delete the cover frame
    cover_frame.destroy()


def set_theme(ctk, app, theme, options, pool):
    # This frame essentially makes the app look pretty whilst loading/switching themes
    cover_frame = CoverFrame.create(ctk, app)
    cover_frame.grid(row=0, column=0, rowspan=5, columnspan=5, sticky='nsew')

    # Store new theme
    options['theme'] = ctk.StringVar(value=theme['title'])
    store.set_menu_option('theme', options)

    # Set theme and reload widgets
    ctk.set_default_color_theme(theme['name'])
    frames.reload_widgets(ctk, app, pool, store.get_state(), cover_frame)

    # Set app background
    app.configure(fg_color=ThemeManager.theme.get('CTk').get('fg_color'))

    # Delete the cover frame
    cover_frame.destroy()



def set_thread_count(options, value, label):
    options['threadamount'] = value
    label.configure(text=f"Thread Amount: {value.get()}/{os.cpu_count()}")
    store.set_menu_option('threadamount', options)