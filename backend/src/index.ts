require('dotenv').config();
const PORT = process.env.EXPRESS_PORT;

// SECTION - Imports
import * as fs from 'fs';
import * as path from 'path';

import Express from 'express';
import RateLimit from 'express-rate-limit';
import Morgan from 'morgan';
import Helmet from 'helmet';

import generateGameList from './generator/gamelist';
const {
  getGamelist,
  getGameModlist,
  downloadGameMods,
} = require('./routes');

// SECTION - Generate gameslist & modlists
const gamesDirectory = process.env.GAMES_ROOT;
generateGameList(gamesDirectory)
  .catch(console.error);


// SECTION - Initialize Express
const app = Express();

app.use(Helmet());

// Limit API call rates
app.use(RateLimit({
  windowMs: process.env.RATELIMIT_TIME,
  max: process.env.RATELIMIT,
}));

// Set up morgan (logger)
const accessLogStream = fs.createWriteStream(
  path.join(__dirname, 'access.log'), { flags: 'a' }
);
const morganTokens = '[:date[web]] (:remote-addr) :method :url (:status) "HTTP/:http-version - :user-agent"';

app.use(Morgan(morganTokens)); // log to console
app.use(Morgan(morganTokens, { stream: accessLogStream })); // save to access.log


// SECTION - Routes
app.get('/games', getGamelist);
app.get('/game/:id/modlist', getGameModlist);
app.get('/game/:id/download/:mods', downloadGameMods);


// SECTION - Start the server! :)
app.listen(PORT, () => {
  console.log(`Express: Listening on port ${PORT}`);
});
