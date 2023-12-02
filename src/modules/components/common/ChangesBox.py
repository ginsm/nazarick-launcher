import os
from modules.tufup import BASE_DIR
from customtkinter.windows.widgets.theme import ThemeManager
from markdown2 import Markdown
from tkhtmlview import HTMLLabel


def create(ctk, parent, game):
    background_color = ThemeManager.theme.get('CTkTextbox').get('fg_color')
    text_color = ThemeManager.theme.get('CTkTextbox').get('text_color')

    # Check if CHANGELOG.md exists
    changelog_path = os.path.join(BASE_DIR, 'assets', game, 'CHANGELOG.md')

    if os.path.exists(changelog_path):
        changes = ctk.CTkScrollableFrame(
            master=parent,
            corner_radius=6,
            fg_color=background_color,
        )

        # Configure rows/columns
        changes.grid_columnconfigure(0, weight=1)
        changes.grid_rowconfigure(0, weight=1)

        with open(changelog_path, 'rb') as f:
            contents = f.read().decode('UTF-8')
            md2html = Markdown()

            # Get color mode
            mode = 1 if ctk.get_appearance_mode() == 'Dark' else 0
            contents = style_tags(
                html=md2html.convert(contents), 
                tags=['h1', 'h2', 'h3', 'h4', 'h5', 'li', 'p', 'div'],
                mode=mode
            )

            html = HTMLLabel(
                changes,
                background=background_color[mode],
                html=contents
            )
            html.config(spacing3=6)
            html.grid(row=0, column=0, padx=12, pady=(10, 6), sticky='nsew')
            html.fit_height()
    
    else:
        changes = ctk.CTkFrame(
            master=parent,
            corner_radius=6,
            fg_color=background_color,
        )

        # Configure rows/columns
        changes.grid_columnconfigure(0, weight=1)
        changes.grid_rowconfigure(0, weight=1)

        label = ctk.CTkLabel(
            master=changes,
            text='Changes cannot be shown for this game.',
            text_color=text_color,
        )
        label.grid(row=0, column=0, padx=12, pady=6, sticky='nsew')

    return changes

def style_tags(html, tags, mode):
    font_sizes = {
        'h1': 18,
        'h2': 12,
        'h3': 11,
        'h4': 10,
        'h5': 10,
        'li': 10,
        'p': 10
    }

    prominent = ThemeManager.theme.get('CTkTextbox').get('text_color')
    faint = ThemeManager.theme.get('CTkFrame').get('fg_color')

    font_colors = {
        'h1': prominent,
        'h2': prominent,
        'h3': prominent,
        'h4': prominent,
        'h5': prominent,
        'li': prominent,
        'p': prominent,
        'div': faint,
    }

    for tag in tags:
        if tag in font_sizes:
            html = html.replace(f'<{tag}', f'<{tag} style="color: {font_colors[tag][mode]}; font-size: {font_sizes[tag]}px;"')
        else:
            html = html.replace(f'<{tag}', f'<{tag} style="color: {font_colors[tag][mode]}; "')
    return html