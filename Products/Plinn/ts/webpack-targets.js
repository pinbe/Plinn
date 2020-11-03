const names = [
    'main',
];

module.exports = {
    targets : names.map(name => {
        return {
            entry: `./src/${name}.ts`,
            output: {
                filename: `${name}.js`
            }
        }
    })
};
