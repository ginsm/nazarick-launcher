import os

def create(ctk, state, root, APP_NAME):
    app = ctk.CTk()

    # Configure geometry and constraints
    app.geometry(state['geometry'])
    app.minsize(height=600, width=600)

    app.configure(fg_color=('#1d1e1e', '#1d1e1e'))

    # Configure grid
    app.grid_columnconfigure(1, weight=1)
    app.grid_rowconfigure(1, weight=1)

    # Configure title and icons
    app.title(APP_NAME.replace('_', ' '))
    app.wm_iconbitmap(os.path.join(root, 'nazaricklauncher.ico'))
    
    return app