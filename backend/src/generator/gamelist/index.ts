import { Dirent, promises as fs } from 'fs';
import * as path from 'path';


import generateModList from '../modlist';
import { parseFile, hasOwnProp } from '@utilities';
import { Mod } from '@type/modlist';
import { GameList, GameInfo } from '@type/gamelist';


export default async function generateGameList(gamesDirectory: string = "") {
  const files: Array<Dirent> = await fs.readdir(gamesDirectory, { withFileTypes: true });
  const games: GameList = {};

  for (let dirent of files) {
    if (dirent.isDirectory()) {
      const { name } = dirent;
      const gameinfo: GameInfo = await parseFile(path.join(gamesDirectory, name, 'gameinfo.json'));

      const modlist = await generateModList(path.join(gamesDirectory, name), name);

      // Helps the initializer determine whether it should check for
      // updated mods
      const lastUpdated: number = Object.values(modlist).reduce((latest: number, mod: Mod) => {
        if (hasOwnProp(mod, 'lastUpdated')) {
          return latest > mod.lastUpdated ? latest : mod.lastUpdated;
        }
        return latest;
      }, 0);

      games[name] = {
        ...gameinfo,
        lastUpdated: lastUpdated,
      };
    }
  }

  fs.writeFile(
    path.join(gamesDirectory, 'gamelist.json'),
    JSON.stringify(games),
  );

  return games;
}