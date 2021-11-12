import * as path from 'path';

import Archiver from 'archiver';

import { parseFile, isValidGame, hasOwnProp } from 'src/utilities';
import { ModList } from '@type/modlist';


export default async function downloadGameMods(req, res) {
  const gamesDirectory = process.env.GAMES_ROOT;
  const game = req.params.id.toLowerCase();

  if (await isValidGame(game)) {
    const modlistPath = path.join(gamesDirectory, game, 'modlist.json');
    const mods: ModList = await parseFile(modlistPath);

    try {
      const requestedMods = Object.keys(req.body)
          .filter((mod) => hasOwnProp(mods, mod));


      if (!requestedMods.length) {
        return res.status(400).json({
          error: `No valid mod names supplied; check /game/${game}/modlist endpoint`,
        });
      }

      res.writeHead(200, {
        "Content-Type": "application/zip",
        "Content-disposition": `attachment; filename=${game}-requested-mods.zip`,
      });

      const zip = Archiver("zip", { zlib: { level: 9 } });
      zip.pipe(res);

      for (let mod of requestedMods) {
        const files = mods[mod].files.map(({trace}) => trace);
        const sanitizer = (val) => typeof val === 'number' && isFinite(val);
        
        for (let id of req.body[mod].filter(sanitizer)) {
          if (files.length - 1 >= Number(id)) { // Ensure the index is within bounds
            zip.file(
              path.join(gamesDirectory, game, "mods", mod, ...files[id]),
              { name: files[id].join("/") }
            );
          }
        }
      }

      return zip.finalize();
    }

    catch (error) {
      return res.status(500).json({ error: 'Error occured while trying to zip requested mods.' });
    }
  } 

  res.status(400).json({ error: "Invalid game ID supplied; check /games endpoint" });
}