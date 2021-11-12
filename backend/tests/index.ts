import Chai from 'chai';
import ChaiHttp from 'chai-http';
Chai.use(ChaiHttp);


describe('Endpoint Tests', () => {
  // GET /games tests
  import('./endpoint-tests/games');

  // GET /game/:id/modlist tests
  import('./endpoint-tests/game-id-modlist');

  // GET /game/:id/download/ tests
  import('./endpoint-tests/game-id-download');
});



