import { promises as fs, Stats } from 'fs';
import * as path from 'path';


export default async function indexMod(root: string = "", trace: Array<string> = [], arr: Array<any> = []) {
  // retrieve the files
  const files = await fs.readdir(root, { withFileTypes: true });

  // iterate over the directory's files
  for (let file of files) {
    const name = file.name;
    const filePath = path.join(root, name);
    const output = {
      trace: trace.concat(name),
      lastModified: 0,
    };

    if (name === "modinfo.json") continue;

    if (file.isDirectory()) {
      arr.concat(await indexMod(
        filePath,
        output.trace,
        arr
      ));
      continue;
    }

    output.lastModified = (await fs.stat(filePath)).mtimeMs;

    arr.push(output);
  }

  // return the result
  return arr;
}
