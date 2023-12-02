import os
import webbrowser
from modules.tufup import BASE_DIR
from customtkinter.windows.widgets.theme import ThemeManager
from markdown2 import Markdown
from tkinterweb import HtmlFrame


def create(ctk, parent, game):
    # Colors
    colors = {
        'background_color': ThemeManager.theme.get('CTkTextbox').get('fg_color'),
        'text_color': ThemeManager.theme.get('CTkTextbox').get('text_color'),
        'faint_text_color': ThemeManager.theme.get('CTkFrame').get('fg_color')
    }

    # Create the frame
    changes = ctk.CTkFrame(
        master=parent,
        corner_radius=6,
        border_width=0,
        fg_color=colors.get('background_color'),
    )

    # Configure rows/columns
    changes.grid_columnconfigure(0, weight=1)
    changes.grid_rowconfigure(0, weight=1)

    # Check if CHANGELOG.md exists
    changelog_path = os.path.join(BASE_DIR, 'assets', game, 'CHANGELOG.md')

    if os.path.exists(changelog_path):
        with open(changelog_path, 'rb') as f:
            contents = f.read().decode('UTF-8')
            md2html = Markdown()

            # Get color mode
            mode = 1 if ctk.get_appearance_mode() == 'Dark' else 0

            html_frame = HtmlFrame(master=changes, messages_enabled=False, vertical_scrollbar=False)
            html_frame.load_html(get_stylesheet(colors, mode) + md2html.convert(contents))
            html_frame.on_link_click(webbrowser.open)
            html_frame.grid(row=0, column=0, padx=12, pady=(10, 6), sticky='nsew')
            html_frame.yview_scroll(1, 'units')

            html_scrollbar = ctk.CTkScrollbar(master=changes, command=html_frame.yview)
            html_scrollbar.grid(row=0, column=1, pady=10, padx=5, sticky='ns')

            html_frame.bind_all("<MouseWheel>", lambda e: update_scrollbar(e, html_scrollbar, html_frame))
            # FIXME - Incorrect value being passed to scrollbar
            html_frame.on_done_loading(lambda: html_scrollbar.set(*html_frame.yview()))
    
    else:
        label = ctk.CTkLabel(
            master=changes,
            text='Changes cannot be shown for this game.',
            text_color=colors.get('text_color'),
        )
        label.grid(row=0, column=0, padx=12, pady=6, sticky='nsew')

    return changes


def update_scrollbar(event, scrollbar, frame):
    scrollbar.set(*frame.yview())
    frame.scroll(event)


def get_stylesheet(colors, mode):
    background_color, faint_text_color, text_color = [
        colors.get('background_color'),
        colors.get('faint_text_color'),
        colors.get('text_color')
    ]

    return f"""
        <style>
        html, body {{
            padding: 0 0 10px 0;
            background: {background_color[mode]};
            scrollbar-color: red orange;
            scrollbar-width: thin;
        }}

        hr {{
            border: 1px solid {faint_text_color[mode]};
            margin: 40px 0;
        }}

        h1 {{
            font-size: 24px;
            margin: 0;
        }}

        h2 {{
            font-size: 16px;
        }}

        h2, h3 {{
            margin: 24px 0 16px 0;
        }}

        ul, ol {{
            margin: 0 0 10px 30px;
            padding: 0;
        }}

        li {{
            font-size: 13px;
            margin-top: 8px;
        }}

        h1, h2, h3, li, p, div, a {{
            color: {text_color[mode]};
        }}
    </style>
    """