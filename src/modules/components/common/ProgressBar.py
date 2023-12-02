class ProgressBarWrapper:
    def __init__(self, progressbar):
        self.bar = progressbar
        self.current_percent = 0

    def _update_bar_progress(self):
        bar = self.bar
        bar.set(self.current_percent)
        bar.update_idletasks()

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
    instance = ProgressBarWrapper(ctk.CTkProgressBar(master=parent, height=24, corner_radius=0))
    instance.bar.set(0) # Default to no progress
    return instance