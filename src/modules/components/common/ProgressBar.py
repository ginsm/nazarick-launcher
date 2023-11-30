class ProgressBarStepper:
    def __init__(self, progressbar, step_amount):
        self.bar = progressbar
        self.steps = step_amount
        self.step_percent = 1 / step_amount
        self.current_step = 0

    def get_current_step(self):
        return self.current_step

    def _update_progress(self):
        bar = self.bar
        bar.set(self.current_step * self.step_percent)
        bar.update_idletasks()

    def reset_progress(self):
        self.current_step = 0
        self._update_progress()

    def step_to(self, step):
        if self.steps >= step and step > 0:
            self.current_step = step
            self._update_progress()

    def step_forward(self):
        if self.steps > self.current_step:
            self.current_step += 1
            self._update_progress()

    def step_backward(self):
        if self.current_step > 0:
            self.current_step -= 1
            self._update_progress()

def create(ctk, parent, steps):
    instance = ProgressBarStepper(ctk.CTkProgressBar(master=parent), steps)
    instance.bar.set(0) # Default to no progress
    return instance