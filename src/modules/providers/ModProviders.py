import requests, os, zipfile
from modules import constants
from modules.providers.ModProviderAbstract import ModProviderAbstract

# ANCHOR CurseForge (Minecraft)
# TODO - Make this actually functional/useful.
class CurseForgeModProvider(ModProviderAbstract):
    def __init__(self):
        self.api_key = constants.CURSEFORGE_API_KEY

    def get_download_url(self, mod_data):
        mod_id, file_id = [
          mod_data.get('projectID'),
          mod_data.get('fileID')
        ]

        # Request file information
        mod_file_req = requests(f'https://api.curseforge.com/v1/mods/{mod_id}/files/{file_id}', headers={
          'Accept': 'application/json',
          'x-api-key': self.api_key
        })

        # Get file url and name and return
        if mod_file_req.status_code == 200:
          mod_file_json = mod_file_req.json()
          mod_download_url = mod_file_json.get('downloadUrl')
          mod_name = mod_file_json.get('displayName')
          return [mod_download_url, mod_name]
        else:
          raise Exception(f'Invalid response from CurseForge for {mod_id}:{file_id}')

    def download(self, log, mod_data, destination):
        mod_download_url, mod_name = self.get_download_url(mod_data)

        req = requests.get(mod_download_url, allow_redirects=True)

        if req.status_code == 200:
            log(f'[INFO] (D) {mod_name}')
            open(destination.get('destination'), 'wb').write(req.content)

        else:
            raise Exception(f'Invalid response from Modrinth for {mod_name}')

# ANCHOR Modrinth (Minecraft)
class ModrinthModProvider(ModProviderAbstract):
    def download(self, log, mod_data, destination):
        mod_download_url = mod_data.get('downloads')[0]
        mod_name = mod_data.get('name')

        req = requests.get(mod_download_url, allow_redirects=True)

        if req.status_code == 200:
            log(f'[INFO] (D) {mod_name}')
            open(destination, 'wb').write(req.content)

        else:
            raise Exception(f'Invalid response from Modrinth for {mod_name}')


# ANCHOR Thunderstore (Valheim)
class ThunderstoreModProvider(ModProviderAbstract):
  def download(self, log, mod_data, destination):
      plugin = mod_data['name']
      plugin_url = f"https://thunderstore.io/package/download/{plugin.replace('-', '/')}"
      plugin_zip = destination + '.zip'

      req = requests.get(plugin_url, allow_redirects=True)

      if req.status_code == 200:
          log(f'[INFO] (D) {plugin}')
          open(plugin_zip, 'wb').write(req.content)

          with zipfile.ZipFile(plugin_zip, 'r') as ref:
              ref.extractall(destination)

          os.remove(plugin_zip)
      else:
          raise Exception(f'Invalid response from Thunderstore ({plugin})')