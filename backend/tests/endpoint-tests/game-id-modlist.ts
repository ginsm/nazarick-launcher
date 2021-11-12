import { validateMod } from '../models/game-id-modlist';
import { issuer } from './utilities/test-issuer';


describe('GET /game/:id/modlist', () => {

  // Uses Ajv to validate the response
  it("should respond with a valid game's modlist", 
    issuer({
      route: '/game/game1/modlist',
      status: 200,
      callback: (res) => {
        const mods = Object.keys(res.body);
        return mods.every((mod) => validateMod(res.body[mod]));
      },
    })
  );

  it('should error given an invalid game ID', 
    issuer({
      route: '/game/gamenotfound/modlist',
      status: 400,
      error: 'Invalid game ID supplied; check /games endpoint',
    })
  );

});