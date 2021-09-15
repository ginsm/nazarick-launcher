import * as path from 'path';
import { parseFile, hasProperties } from '@utilities';

export default async function getGamelist(req, res) {
  const gamesDirectory = process.env.GAMES_ROOT;
  const games = await parseFile(path.join(gamesDirectory, 'gamelist.json'));

  if (hasProperties(games)) {
    return res.json(games);
  }

  res.status(500).send({ error: "Missing or empty: gamelist.json; has it been generated?" });
}
