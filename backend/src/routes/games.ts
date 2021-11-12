import * as path from 'path';
import { parseFile } from 'src/utilities';

export default async function getGamelist(req, res) {
  const gamesDirectory = process.env.GAMES_ROOT;
  const games = await parseFile(path.join(gamesDirectory, 'gamelist.json'));
  return res.json(games);
}
