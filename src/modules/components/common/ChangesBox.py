import os
import webbrowser
from modules.tufup import BASE_DIR
from customtkinter.windows.widgets.theme import ThemeManager
from markdown2 import Markdown
from tkinterweb import HtmlFrame

stylesheet = ''

def create(ctk, parent, game):
    # Theme information
    mode = 1 if ctk.get_appearance_mode() == 'Dark' else 0
    colors = {
        'background_color': ThemeManager.theme.get('CTkTextbox').get('fg_color'),
        'text_color': ThemeManager.theme.get('CTkTextbox').get('text_color'),
        'faint_text_color': ThemeManager.theme.get('CTkFrame').get('fg_color')
    }

    # Initialize the stylesheet
    global stylesheet
    stylesheet = get_stylesheet(colors, mode)

    # Create the container frame
    changes = ctk.CTkFrame(
        master=parent,
        corner_radius=6,
        border_width=0,
        fg_color=colors.get('background_color'),
    )

    # Configure rows/columns
    changes.grid_columnconfigure(0, weight=1)
    changes.grid_rowconfigure(0, weight=1)

    # Create the HTML frame
    html_frame = HtmlFrame(master=changes, messages_enabled=False, vertical_scrollbar=False)
    html_frame.on_link_click(webbrowser.open)
    html_frame.grid(row=0, column=0, padx=12, pady=(10, 6), sticky='nsew')

    # Load changelog
    load_changelog(ctk, changes, game, html_frame)

    return [changes, html_frame]


def load_changelog(ctk, changes, game, html_frame):
    # Check if CHANGELOG.md exists
    changelog_path = os.path.join(BASE_DIR, 'assets', game, 'CHANGELOG.md')
    if os.path.exists(changelog_path):
        with open(changelog_path, 'rb') as f:
            contents = f.read().decode('UTF-8')
            md2html = Markdown()

            # Set HTML
            html_frame.load_html(stylesheet + md2html.convert(contents))

            # Create scrollbar and bind necessary events
            scrollbar = ctk.CTkScrollbar(
                master=changes,
                command=lambda _, dist, unit: scroll_scrollbar(html_frame, scrollbar, dist, unit)
            )
            scrollbar.grid(row=0, column=1, pady=12, padx=12, sticky='ns')
            scrollbar.set(*html_frame.yview()) # Set initial value

            # Event handling (scrolling)
            html_frame.bind('<Enter>', lambda _: bind_to_mousewheel(html_frame, scrollbar, html_frame))
            html_frame.bind('<Leave>', lambda _: unbind_to_mousewheel(html_frame))
    else:
        html_frame.load_html(stylesheet + '<div>There is no change log available for this game.</div>')


def bind_to_mousewheel(frame, scrollbar, widget):
    widget.bind_all("<MouseWheel>", lambda e: scroll_event(e, frame, scrollbar))

def unbind_to_mousewheel(widget):
    widget.unbind_all("<MouseWheel>")

def scroll_event(event, frame, scrollbar):
    scrollbar.set(*frame.yview())
    frame.scroll(event)

def scroll_scrollbar(frame, scrollbar, dist, unit):
    frame.yview_scroll(dist, unit)
    scrollbar.set(*frame.yview())


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
            font-family: Roboto, 'Open Sans', Arial;
            font-size: 13px;
        }}

        hr {{
            border: 1px solid {faint_text_color[mode]};
            margin: 40px 0;
        }}

        h1 {{
            font-size: 20px;
            margin: 0;
        }}

        h2 {{
            font-size: 14px;
        }}

        h2, h3 {{
            margin: 24px 0 16px 0;
        }}

        ul, ol {{
            margin: 0 0 10px 15px;
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