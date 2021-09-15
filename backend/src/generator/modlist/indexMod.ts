import { promises as fs } from 'fs';
import * as path from 'path';


export default async function indexMod(root: string = "", trace: string = "", arr: Array<any> = []) {
  // retrieve the files
  const files = await fs.readdir(root, { withFileTypes: true });

  // iterate over the directory's files
  for (let file of files) {
    const name = file.name;

    if (name === "modinfo.json") continue;

    if (file.isDirectory()) {
      arr.concat(await indexMod(
        path.join(root, name),
        path.join(trace, name),
        arr
      ));
      continue;
    }

    arr.push(path.join(trace, name));
  }

  // return the result
  return arr;
}
