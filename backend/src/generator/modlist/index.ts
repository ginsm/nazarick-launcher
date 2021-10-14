import { Dirent, promises as fs } from 'fs';
import * as path from 'path';

import indexMod from './indexMod';
import { parseFile, hasOwnProp } from 'src/utilities';
import { ModList, ModInfo } from 'src/types/modlist';

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
      );

      // Establish when files were last updated
      let lastModified = null;
      
      if (hasOwnProp(oldMods, name)) {
        const filesRemoved = oldMods[name].files.length > files.length;
        lastModified = filesRemoved ? Date.now() : oldMods[name].lastModified;
      }

      for (let file of files) {
        if (file.lastModified > lastModified) {
          lastModified = file.lastModified;
        }
      }

      // Add to the mod object
      mods[name] = {
        ...modinfo,
        lastModified,
        files,
      };
    }
  }

  fs.writeFile(pathTo.modlist, JSON.stringify(mods, null, 2));

  return mods;
}