import { issuer } from './utilities/test-issuer';
import { validateGame } from '../models/games';


describe('GET /games', () => {
  
  // Uses Ajv to validate the response
  it('should retrieve list of games', 
    issuer({ 
      route: '/games',
      status: 200,
      callback: (res) => {
        const games = Object.keys(res.body);
        return games.every((game) => validateGame(res.body[game]));
      },
    })
  );

});