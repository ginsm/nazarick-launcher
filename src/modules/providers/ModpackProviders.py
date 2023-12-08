import json
import os
import requests
from modules.providers.ModpackProviderAbstract import ModpackProviderAbstract

# ANCHOR Self Hosted (Multiple Games)
class SelfHostedModpackProvider(ModpackProviderAbstract):
    def download(self, variables):
        req = super().download(variables)

        if req.status_code != 200:
            raise Exception('Invalid response from SelfHosted (modpack)')
        
    def extract(self, variables, game):
        super().extract(variables, game)

    def get_latest_version(self, game, pack):
        # TODO - Probably make a constants file and put this in there
        website = 'https://mgin.me/nazarick-launcher/'
        req = requests.get(f'{website}/modpacks/manifest.json')

        if (req.status_code != 200):
            return False
        
        content = json.loads(req.text)

        version_data = content.get(game).get(pack).get('versions')[0]
        version_data.update({'url': f'{website}{version_data.get('url')}'})

        return content.get(game).get(pack).get('versions')[0]

    def initial_install(self):
        pass
        
# ANCHOR Self Hosted (Minecraft)
class SelfHostedMinecraftModpackProvider(SelfHostedModpackProvider):
    def initial_install(self, variables):
        inst_path = variables['instpath']
        configpath = os.path.join(inst_path, 'config')
        modspath = os.path.join(inst_path, 'mods')

        def move_existing_files(path):
            if os.path.exists(path):
                os.rename(path, f'{path}-old')

        move_existing_files(configpath)
        move_existing_files(modspath)


# ANCHOR Thunderstore (Valheim)
class ThunderstoreModpackProvider(ModpackProviderAbstract):
    def download(self, variables):
        req = super().download(variables)
        
        if req.status_code != 200:
            raise Exception('Invalid response from Thunderstore (modpack)')

    def extract(self, variables, game):
        super().extract(variables, game)

    # In order to keep the providers consistent, I'll be passing 'game' and 'pack'
    # to this method in valheim_updater. *_ just denotes that any arguments passed
    # are unused.
    def get_latest_version(self, *_):
        req = requests.get('https://thunderstore.io/api/experimental/package/Syh/Nazarick_Core/')

        if (req.status_code != 200):
            return False
        
        content = json.loads(req.text)

        return {
            'name': content['full_name'],
            'version': content['latest']['version_number'],
            'url': content['latest']['download_url']
        }
    
    def initial_install(self):
        pass