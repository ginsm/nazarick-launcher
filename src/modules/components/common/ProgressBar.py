from customtkinter.windows.widgets.theme import ThemeManager

class ProgressBarWrapper:
    def __init__(self, progressbar):
        self.bar = progressbar
        self.current_percent = 0
        self.progress_color = ThemeManager.theme.get('CTkProgressBar').get('progress_color')
        self.fg_color = ThemeManager.theme.get('CTkProgressBar').get('fg_color')

    def _update_bar_progress(self):
        bar = self.bar
        bar.set(self.current_percent)
        bar.update_idletasks()

        if self.current_percent > 0:
            self.bar.configure(progress_color=self.progress_color)
        else:
            self.bar.configure(progress_color=self.fg_color)

    def get_current_percent(self):
        return self.current_percent

    def reset_percent(self):
        self.current_percent = 0
        self._update_bar_progress()

    def add_percent(self, percent):
        new_percent = self.current_percent + percent
        if 1 >= new_percent:
            self.current_percent = new_percent
            self._update_bar_progress()

    def remove_percent(self, percent):
        new_percent = self.current_percent - percent
        if 0 >= new_percent:
            self.current_percent = new_percent
            self._update_bar_progress()

def create(ctk, parent):
    instance = ProgressBarWrapper(ctk.CTkProgressBar(
        master=parent,
        height=24,
        corner_radius=10
    ))
    instance.reset_percent() # Default to no progress
    return instance