'use strict';
const JavaScriptObfuscator = require('webpack-obfuscator');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const path = require("path");
const BundleTracker = require('webpack-bundle-tracker');
const webpack = require('webpack');
// const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

const TerserPlugin = require("terser-webpack-plugin");


module.exports = (env, argv) => {

    const isDevelopment = argv.mode === 'development';

    const plugins = [
            // new ExtractTextPlugin("bundle.min.css"),
            new MiniCssExtractPlugin({
                // Options similar to the same options in webpackOptions.output
                // both options are optional
                // filename: isDevelopment ? '[name].css' : '[name].[hash].css',
                // chunkFilename: isDevelopment ? '[id].css' : '[id].[hash].css'

                filename: '[name]/[name]-bundle.css',
                chunkFilename: '[name]/[id].css'
            }),
            new BundleTracker({filename: './webpack-stats.json'}),
            new webpack.DefinePlugin({
                LOG_LEVEL: JSON.stringify('__DEBUG__'),
                VERSION: JSON.stringify('1.0'),

            })
        ]
    ;
    if (!isDevelopment) {
        // plugins.push(
        //     new JavaScriptObfuscator(
        //         {
        //             // domainLock: ['www.example.com'],
        //             // identifierNamesGenerator: 'mangled',
        //             // identifiersPrefix: 'mp',
        //             // stringArray: true,
        //             // rotateStringArray: true,
        //             //stringArrayEncoding: 'base64',
        //             // transformObjectKeys: true,
        //             //rotateUnicodeArray: false // if set to true then app returns regexp error
        //         },
        //         ['not_to_be_obfuscated_js_file.js'] // list of files we don't want to be obfuscated
        //     )
        // )
    }

    let opts = {

        devtool: 'eval-source-map', // https://webpack.js.org/configuration/devtool/
        entry: {
            _temp: [
                path.resolve(__dirname, './_temp/index'),
                path.resolve(__dirname, './_temp/scss/styles.scss')
            ],
            _controls: [
                path.resolve(__dirname, './_core/scss/controls.scss')
            ],
            login: [
                path.resolve(__dirname, './login/index'),
                path.resolve(__dirname, './login/scss/styles.scss')
            ],

            home: [
                path.resolve(__dirname, './home/js/index'),
                path.resolve(__dirname, './home/scss/styles.scss')
            ],

            hierarchy: [
                path.resolve(__dirname, './hierarchy/js/index'),
                path.resolve(__dirname, './hierarchy/scss/styles.scss')
            ],

            main: [
                path.resolve(__dirname, './index'),
                path.resolve(__dirname, './scss/globals.scss')
            ],
            newDocument: [
                path.resolve(__dirname, './document/add/js/index'),
                path.resolve(__dirname, './document/add/scss/styles.scss'),
            ],
            documentType: [
                path.resolve(__dirname, './documentType/js/index'),
                path.resolve(__dirname, './documentType/scss/styles.scss'),
            ],
            document: [
                path.resolve(__dirname, './document/js/index'),
                path.resolve(__dirname, './document/scss/styles.scss'),
            ],
            document_process_flow: [
                path.resolve(__dirname, './document/scss/document-process-flow.scss'),
            ],
            report: [
                path.resolve(__dirname, './report/js/index'),
                path.resolve(__dirname, './report/scss/styles.scss'),
            ],
            fileRepository: [
                path.resolve(__dirname, './fileRepository/js/index'),
                path.resolve(__dirname, './fileRepository/scss/styles.scss'),
            ],
            documentDefinition: [
                path.resolve(__dirname, './document/definition/js/index'),
                path.resolve(__dirname, './document/definition/scss/styles.scss'),
            ],
            product: [
                path.resolve(__dirname, './product/js/index'),
                path.resolve(__dirname, './product/scss/styles.scss'),
            ],
            productListAll: [
                path.resolve(__dirname, './product/js/list-all')
            ],

            productInterestGlobal: [
                path.resolve(__dirname, './product/js/financePack/interest-global/js/index'),
                path.resolve(__dirname, './product/js/financePack/interest-global/scss/styles.scss'),
            ],
            user: [
                path.resolve(__dirname, './user/js/index'),
                path.resolve(__dirname, './user/scss/styles.scss'),
            ],
            userCurrentContacts: [
                path.resolve(__dirname, './user/client/js/current-contacts'),
                path.resolve(__dirname, './user/client/scss/current-contacts.scss'),
            ],
            userClient: [
                path.resolve(__dirname, './user/client/js/index'),
                path.resolve(__dirname, './user/client/scss/styles.scss'),
            ],
            userBroker: [
                path.resolve(__dirname, './user/broker/js/index'),
                path.resolve(__dirname, './user/broker/scss/styles.scss'),
            ],
            userDetails: [
                path.resolve(__dirname, './user/userDetails/js/user-details'),
                path.resolve(__dirname, './user/userDetails/scss/user-details.scss'),
            ],

            coreControls: [
                path.resolve(__dirname, './_core/scss/controls.scss'),
            ],
            widget: [
                path.resolve(__dirname, './widget/js/index.js'),
                path.resolve(__dirname, './widget/scss/styles.scss'),
            ],

            scheduleApp: [
                path.resolve(__dirname, './scheduleApp/index.js'),
                path.resolve(__dirname, './scheduleApp/styles.scss'),
            ]
        },
        output: {
            path: path.resolve('../_staticBuild/dist/'),
            filename: "[name]/[name]-bundle.js"
        },
        module: {
            rules: [
                {
                    test: /\.js(x)?$/,
                    exclude: [/node_modules/, /jstree/],
                    use: {
                        loader: "babel-loader",
                        options: {
                            presets: ['@babel/preset-env']
                        }
                    }
                },
                // {
                //     test: /\.(png|woff|woff2|eot|ttf|svg|jpg|gif|ico|jpeg)$/,
                //     use: [{
                //         loader: 'url-loader',
                //         options: {
                //             limit: 10000000,
                //             mimetype: 'application/font-ttf',
                //             name: "[hash].[ext]",
                //             publicPath: 'font/',
                //             outputPath: 'main/font/',
                //         }
                //     }
                //     ]
                // },
                {
                    test: /\.(png|svg|jpg|gif|ico|jpeg)$/,
                    use: [{
                        loader: 'url-loader',
                        options: {
                            limit: 10000000,
                            mimetype: 'image',
                            name: "[name].[ext]",
                            publicPath: 'img/',
                            outputPath: '../_staticBuild/img/',
                        }
                    }
                    ]
                },
                {
                    test: /\.css$/,
                    use: [MiniCssExtractPlugin.loader, "css-loader"]
                },
                {
                    test: /\.s(a|c)ss$/,
                    use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"]
                },
                {
                    test: /\.(woff(2)?|ttf|eot)(\?v=\d+\.\d+\.\d+)?$/,
                    use: [
                        {
                            loader: "file-loader",
                            options: {
                                name: "[name].[ext]",
                                publicPath: '/static/font/',
                                outputPath: "../../_staticBuild/font/",
                            },
                        },
                    ],
                }
            ]
        },
        plugins: plugins,

        resolve: {
            extensions: ['.js', '.jsx', '.scss', '.css']
        }
    };
    if (!isDevelopment) {

        opts.optimization = {
            minimize: true,
            minimizer: [new TerserPlugin()]
            // },

            // opts.optimization = {
            //  minimizer: [

            // new UglifyJsPlugin({
            //     uglifyOptions: {
            //         mangle: {
            //             keep_fnames: true,
            //         },
            //     },
            // }),

            // new UglifyJsPlugin({
            //     cache: true,
            //     parallel: true,
            //     sourceMap: false,
            //     extractComments: 'all',
            //     uglifyOptions: {
            //         compress: true,
            //         output: null
            //     }
            // })
            // ],
        }
    }

    return opts;
};
