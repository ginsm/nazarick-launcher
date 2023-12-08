from abc import ABC, abstractmethod

class ModProviderAbstract(ABC):
    @abstractmethod
    def download(self, log, mod_data, paths):
        raise NotImplementedError