import * as path from 'path';
import { parseFile, isValidGame } from '@utilities';

export default async function getGameModlist(req, res) {
  const gamesDirectory = process.env.GAMES_ROOT;
  const game = req.params.id.toLowerCase();

  if (await isValidGame(game)) {
    const modlistPath = path.join(gamesDirectory, game, 'modlist.json');
    return res.json(await parseFile(modlistPath));
  }

  res.status(400).send({ error: "Invalid game ID supplied; check /games endpoint" });
}
