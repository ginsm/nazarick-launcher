import { promises as fs } from 'fs';
import * as path from 'path';

export function isObject(obj: Record<string, any> = {}): boolean {
  return obj === Object(obj);
}


export function hasOwnProp(obj: Record<string, any> = {}, prop: string = ''): boolean {
  if (isObject(obj)) {
    return Object.prototype.hasOwnProperty.call(obj, prop);
  }
  return false;
}


async function fileParser(filePath: string = '') {
  try {
    return JSON.parse((await fs.readFile(filePath)).toString());
  } catch (error) {
    return {};
  };
}


// Memoize and export fileParser as parseFile
export const parseFile: typeof fileParser = memoize(
  fileParser,
  parseInt(`${process.env.RECACHE_TIME}`, 10),
);


export async function isValidGame(game: string = ''): Promise<boolean> {
  const gamesDirectory = process.env.GAMES_ROOT;
  const games = await parseFile(path.join(gamesDirectory, 'gamelist.json'));
  return hasOwnProp(games, game);
}


export function memoize(func: Function, maxAge: number = 0) {
  const cache = {};

  return function () {
    const key = JSON.stringify(arguments);

    if (hasOwnProp(cache, key) && cache[key]) {
      if (maxAge && (Date.now() - cache[key].age > maxAge)) {
        cache[key].age = Date.now();
      } else {
        return cache[key].value;
      }
    } else {
      cache[key] = { value: null, age: Date.now() };
    }

    return cache[key].value = func.apply(null, arguments);
  };
}