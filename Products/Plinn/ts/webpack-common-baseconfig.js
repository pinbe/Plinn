let baseConfig = {
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                loader: "ts-loader"
            },
            {enforce: "pre", test: /\.js$/, loader: "source-map-loader"},
            {
                test: /\.css$/,
                use: [
                    'style-loader',
                    'css-loader']
            },
            {
                test: /\.(scss)$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: 'css/[name].build.css'
                        }
                    },
                    {
                        loader: 'extract-loader',
                    },
                    // {
                    //     loader: 'style-loader', // inject CSS to page
                    // },
                    {
                        loader: 'css-loader', // translates CSS into CommonJS modules
                    },
                    {
                        loader: 'postcss-loader', // Run postcss actions
                    },
                    {
                        loader: 'sass-loader' // compiles Sass to CSS
                    },
                ]
            },
            {
                test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                use: {
                    loader: 'url-loader',
                    options: {
                        name: '[path][name].[ext]'
                    }
                }
            },
            {
                test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                use: "file-loader"
            }
        ]
    },
    resolve: {
        extensions: ['.tsx', '.ts', '.js']
    },
};
module.exports = {baseConfig: baseConfig};