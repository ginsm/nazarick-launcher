from modules import utility
from modules.components.common import InfoModal
from customtkinter.windows.widgets.theme import ThemeManager

def create(ctk, text, app):
  # Do not run if the laucnher is already running as admin
  if utility.running_as_admin():
    return None

  def destroy_modal(modal):
    modal.destroy()

  def elevate_launcher(_):
    utility.elevate_launcher(app)

  border_color = ThemeManager.theme.get('CTkCheckBox').get('border_color')
  modal = InfoModal.create(
      ctk,
      text=text,
      buttons=[
          {'text': 'Cancel', 'command': destroy_modal},
          {'text': 'Elevate', 'command': elevate_launcher, 'border': border_color},
      ],
      title='Run as Administrator',
      parent=app
  )

  return modal