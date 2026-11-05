const esbuild = require('esbuild');

esbuild.build({
  entryPoints: ['static/js/src/main.js'],
  bundle: true,
  outfile: 'static/js/dist/app.min.js',
  minify: false,
  sourcemap: true,
  target: ['es2020'],
}).then(() => {
  console.log('✅ FALK Build successful: static/js/dist/app.min.js created.');
}).catch((err) => {
  console.error('❌ Build failed with errors:');
  process.exit(1);
});
