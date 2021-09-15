import { Dirent, promises as fs } from 'fs';
import * as path from 'path';

import indexMod from './indexMod';
import { parseFile, hasOwnProp } from '@utilities';
import { ModList, ModInfo } from '@type/modlist';

export default async function generateModList(gamePath: string = "", game: string = "") {
  const pathTo = {
    mods: path.join(gamePath, 'mods'),
    modlist: path.join(gamePath, 'modlist.json'),
    modInfo: (mod: string = "") => path.join(pathTo.mods, mod, 'modinfo.json'),
  };

  const files: Array<Dirent> = await fs.readdir(pathTo.mods, { withFileTypes: true });
  const oldMods: ModList = await parseFile(pathTo.modlist);
  const mods: ModList = {};

  for (let dirent of files) {
    if (dirent.isDirectory()) {
      const { name } = dirent;
      const modinfo: ModInfo = await parseFile(pathTo.modInfo(name));

      const files = await indexMod(
        path.join(pathTo.mods, name), // path to the mod
        name, // used for trace, i.e. modName/dir/file.ext
      );

      // Establish when files were last updated
      let lastUpdated = null;

      if (hasOwnProp(oldMods, name)) {
        const filesRemoved = oldMods[name].files.length > files.length;
        lastUpdated = filesRemoved ? Date.now() : oldMods[name].lastUpdated;
      }

      for (let file of files) {
        const stats = await fs.stat(path.join(pathTo.mods, file));
        if (stats.mtimeMs > lastUpdated) {
          lastUpdated = stats.mtimeMs;
        }
      }

      // Add the mod to mods
      mods[name] = {
        ...modinfo,
        lastUpdated,
        files,
      };
    }
  }

  fs.writeFile(pathTo.modlist, JSON.stringify(mods, null, 2));

  return mods;
}