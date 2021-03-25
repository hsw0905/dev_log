const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
	publicPath: 'http://0.0.0.0:8080/',
	outputDir: './dist/',

	chainWebpack: config => {
		config
			.plugin('BundleTracker')
			.use(BundleTracker, [{ filename: './webpack-stats.json' }]);

		config.output.filename('bundle.js');

		config.optimization.splitChunks(false);

		config.resolve.alias.set('__STATIC__', 'static');

		config.devServer
			.public('http://127.0.0.1:8080')
			.host('127.0.0.1')
			.port(8080)
			.hotOnly(true)
			.watchOptions({ poll: 1000 })
			.https(false)
			.disableHostCheck(true)
			.headers({ 'Access-Control-Allow-Origin': ['*'] });
	},

	// 아래 주석 코드는 배포작업(npm run build) 하기 전 해제한다
	// css: {
	//     extract: {
	//       filename: 'bundle.css',
	//       chunkFilename: 'bundle.css',
	//     },
	// }
};
