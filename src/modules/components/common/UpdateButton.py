from modules import gui_manager, state_manager
from modules.utility import get_modpack_data

class UpdateButton():
    def create(self, ctk, parent, pool, updater, widgets, game):
        modpack_data = get_modpack_data(game, state_manager.get_selected_pack(game))

        if updater:
            self.updater = updater(ctk, parent, pool, widgets, modpack_data)

        self.update_button = ctk.CTkButton(
            master=parent,
            text='Play',
            height=46,
            width=180,
            command=lambda: self.handle_button_press(self.updater, pool, widgets),
            border_width=0
        )

        gui_manager.add_lockable(self.update_button)

        return self.update_button


    def handle_button_press(self, updater, pool, widgets):
        button_text = self.update_button.cget('text')
        log = widgets.get('logbox').log

        if button_text == 'Play':
            # Check if updater exists
            if updater:
                pool.submit(updater.start, self.update_button)
                self.update_button.configure(text='Cancel')

            # Handle non-existent updater
            else:
                log('Update process could not start; no updater found.')
        elif button_text == 'Cancel':
            log('Stopping process, this may take a second...')
            updater.cancel_update()