import os
from modules.tufup import BASE_DIR
from customtkinter.windows.widgets.theme import ThemeManager


def create(ctk, parent, game):
    changes = ctk.CTkFrame(
        master=parent,
        corner_radius=6,
        fg_color=ThemeManager.theme.get('CTkTextbox').get('fg_color'),
    )

    # Configure rows/columns
    changes.grid_columnconfigure(0, weight=1)
    changes.grid_rowconfigure(0, weight=1)

    # Check if CHANGELOG.md exists
    changelog_path = os.path.join(BASE_DIR, 'assets', game, 'CHANGELOG.md')

    if os.path.exists(changelog_path):
        print("Changelog found!")
    
    else:
        label = ctk.CTkLabel(
            master=changes,
            text='Changes cannot be shown for this game.',
            text_color=ThemeManager.theme.get('CTkTextbox').get('text_color'),
        )
        label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

    return changes