export interface ModInfo {
  required: boolean,
  link?: string,
  icon?: string,
  replaces?: string,
};

export interface Mod extends ModInfo {
  lastModified
  : number | null,
  files: Array<string>,
};


export type ModList = Record<string, Mod>;
