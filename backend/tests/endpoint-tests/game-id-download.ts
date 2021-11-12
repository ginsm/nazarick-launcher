import { Response } from 'express';
import { TestObject } from './utilities/test-issuer';
import { issuer } from './utilities/test-issuer';


const validateZipFileStructure = (res: Response, test: TestObject) => {
  const dataString: string = res.body.toString('utf8');
  const { expectedFiles } = test;
  return expectedFiles.every((file) => dataString.includes(file));
}


describe('GET /game/:id/download/', () => {

  it('should serve valid requested mod files', 
    issuer({
      route: '/game/game1/download',
      status: 200,
      payload: {
        mod1: [1], // valid file request
        mod3: [0, 2], // valid file requests
      },
      parse: true,
      expectedFiles: [
        'mods/mod1.mod',
        'config/mod3.cfg',
        'patches/mod3.patch',
      ],
      callback: validateZipFileStructure,
    })
  );

  it('should serve valid requested mod files and ignore invalid ones',
    issuer({
      route: '/game/game2/download',
      status: 200,
      payload: {
        mod1: [0], // valid file request
        mod2: [0, 3, 5], // file 0 and 3 are valid; 5 is not
        mod5: [1, 9], // this mod doesn't exist
      },
      parse: true,
      expectedFiles: [
        'config/mod1.cfg',
        'config/mod2.cfg',
        'patches/mod2.patch',
      ],
      callback: validateZipFileStructure,
    })
  );

  it('should error when requesting invalid mod files',
    issuer({
      route: '/game/game1/download/',
      status: 400,
      payload: { "mod4": [0, 2] },
      error: 'No valid mod names supplied; check /game/game1/modlist endpoint',
    }),
  );

  it('should error when given an invalid game',
    issuer({
      route: '/game/gamenotfound/download/',
      status: 400,
      payload: { "mod1": [1, 4] },
      error: 'Invalid game ID supplied; check /games endpoint',
    }),
  );

});