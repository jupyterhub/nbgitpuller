const webpack = require('webpack');

module.exports = {
    context: __dirname + "/nbgitpuller/static/",
    entry: "./js/index.js",
    output: {
        path: __dirname + "/nbgitpuller/static/dist/",
        filename: "bundle.js",
        publicPath: '/static/dist/'
    },
    devtool: 'source-map',
    plugins: [
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
        }),
    ]
}
