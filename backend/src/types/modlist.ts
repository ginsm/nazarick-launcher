export interface ModInfo {
  required: boolean,
  link?: string,
  icon?: string,
  replaces?: string,
};

export interface File {
  trace: Array<string>,
  lastModified: number
}

export interface Mod extends ModInfo {
  lastModified
  : number | null,
  files: Array<File>,
};

export type ModName = string;
export type ModList = Record<ModName, Mod>;
