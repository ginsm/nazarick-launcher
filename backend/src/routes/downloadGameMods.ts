import * as path from 'path';

import Archiver from 'archiver';

import { parseFile, isValidGame, hasOwnProp } from '@utilities';


export default async function downloadGameMods(req, res) {
  const gamesDirectory = process.env.GAMES_ROOT;
  const game = req.params.id.toLowerCase();

  if (await isValidGame(game)) {
    const modlistPath = path.join(gamesDirectory, game, 'modlist.json');
    const mods = await parseFile(modlistPath);

    try {
      const requestedMods = Object.keys(req.body)
          .filter((mod) => hasOwnProp(mods, mod));


      if (!requestedMods.length) {
        return res.status(400).send({
          error: `No valid mod names supplied; check /game/${game}/modlist endpoint`
        });
      }

      res.writeHead(200, {
        "Content-Type": "application/zip",
        "Content-disposition": `attachment; filename=${game}-updated-mods.zip`
      });

      const zip = Archiver("zip", { zlib: { level: 9 } });
      zip.pipe(res);

      for (let mod of requestedMods) {
        const files = mods[mod].files.map(({trace}) => trace);
        
        for (let id of req.body[mod].filter(Number)) {
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
      return res.status(500).send({ error: 'Error occured while trying to zip requested mods.' });
    }
  } 

  res.status(400).send({ error: "Invalid game ID supplied; check /games endpoint" });
}