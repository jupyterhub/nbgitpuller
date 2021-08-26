const webpack = require('webpack');
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");

var mode = process.env.NODE_ENV || 'development';

module.exports = {
    context: __dirname + "/nbgitpuller/static/",
    entry: "./js/index.js",
    output: {
        path: __dirname + "/nbgitpuller/static/dist/",
        filename: "[name].js",
        publicPath: '/static/dist/'
    },
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: [MiniCssExtractPlugin.loader, 'css-loader']
            },
        ]
    },
    devtool: (mode === 'development') ? 'inline-source-map' : false,
    mode: mode,
    optimization: {
        minimize: true,
        minimizer: [
            `...`,
            new CssMinimizerPlugin(),
        ],
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
        }),
        new MiniCssExtractPlugin({
            filename: "[name].css",
            chunkFilename: "[id].css",
        }),
    ]
}
