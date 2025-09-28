class MissingModNameError(Exception):
  pass

class MissingModDownloadUrlError(Exception):
  pass

class InvalidProviderResponseError(Exception):
  pass

class InvalidGameSettingTypeError(Exception):
  pass

class MissingAppIDError(Exception):
  pass

class InvalidAppIDTypeError(Exception):
  pass

class MissingSteamPathError(Exception):
  pass

class PowerShellCommandError(Exception):
  pass