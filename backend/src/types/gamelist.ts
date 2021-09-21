export interface GameInfo {
  altname: string,
  icon: string,
  desiredFilesInPath?: Array<string>,
}

export interface Game extends GameInfo {
  lastModified: number,
};

export type GameList = Record<string, Game>;
