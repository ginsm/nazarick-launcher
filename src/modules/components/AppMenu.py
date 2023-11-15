from modules import store
from tkinter import Menu

def setTheme(ctk, options):
    ctk.set_appearance_mode(options['theme'].get())
    store.set_menu_option('theme', options)

def create(ctk, master, state):
    master.option_add('*tearOff', False)
    menu = Menu(master=master)

    # ----- File submenu ----- #
    app_submenu = Menu(master=menu, tearoff=0)
    app_submenu.add_command(label='Exit', command=master.quit)


    # ----- Options submenu ----- #
    options_submenu = Menu(master=menu, tearoff=0)
    options={
        'autorestart': ctk.BooleanVar(value=state.get('autorestart') or False),
        'autoclose': ctk.BooleanVar(value=state['autoclose']),
        'logging': ctk.BooleanVar(value=state['logging']),
        'theme': ctk.StringVar(value=state['theme']),
        'debug': ctk.BooleanVar(value=state['debug']),
    }
    
    # Theme submenu
    theme_submenu = Menu(master=options_submenu, tearoff=0)
    theme_submenu.add_radiobutton(label='System', variable=options['theme'], command=lambda: setTheme(ctk, options))
    theme_submenu.add_radiobutton(label='Light', variable=options['theme'], command=lambda: setTheme(ctk, options))
    theme_submenu.add_radiobutton(label='Dark', variable=options['theme'], command=lambda: setTheme(ctk, options))

    # ----- Standalone options ----- #
    options_submenu.add_checkbutton(label='Auto Restart', variable=options['autorestart'], onvalue=True, offvalue=False, command=lambda: store.set_menu_option('autorestart', options))
    options_submenu.add_checkbutton(label='Auto Close', variable=options['autoclose'], onvalue=True, offvalue=False, command=lambda: store.set_menu_option('autoclose', options))
    options_submenu.add_checkbutton(label='Logs', variable=options['logging'], onvalue=True, offvalue=False, command=lambda: store.set_menu_option('logging', options))
    options_submenu.add_cascade(label='Theme', menu=theme_submenu)
    options_submenu.add_checkbutton(label='Debug', variable=options['debug'], onvalue=True, offvalue=False, command=lambda: store.set_menu_option('debug', options))

    # ----- Add submenus ----- #
    menu.add_cascade(label='App', menu=app_submenu)
    menu.add_cascade(label='Options', menu=options_submenu)

    # ----- Add menu to master ----- #
    master.config(menu=menu)