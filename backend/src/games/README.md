# Data Directory

This directory is meant to serve as an example file structure for the games and their mods/files. It is important to replicate this structure to ensure proper functionality. The `gameslist.json` and each game's `modlist.json` are generated utilizing this file structure.


 
## File: `gameinfo.json`

Each game **must** be accompanied by a `gameinfo.json` at its top level. It is what is served to the client when a request is made to the `/game/:id/gameinfo` endpoint.


```ts
// gameinfo.json schematic
{
  "name": String,
  "icon": String // base64, path, or url
}
```


 
## File: `modinfo.json`

Each mod **must** be accompanied by a `modinfo.json` at its top level. It is used to generate the `modlist.json` that is served at the `/game/:id/modlist` endpoint.


```ts
// modinfo.json schematic
{
  "required": Boolean,
  "link": String // external url to mod page
}
```