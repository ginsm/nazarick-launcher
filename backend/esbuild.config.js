const esbuild = require('esbuild');
const { nodeExternalsPlugin } = require('esbuild-node-externals');

esbuild.build({
  platform: 'node',
  entryPoints: ['src/index.ts'],
  outfile: 'build/app.js',

  bundle: true,
  minify: true,
  sourcemap: true,

  plugins: [nodeExternalsPlugin({
    packagePath: 'package.json',
  })],
}).catch(() => process.exit(1));