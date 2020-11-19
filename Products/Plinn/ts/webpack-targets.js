const names = [
    'main',
    'slideshow_helper',
    'metadata_helper',
    'folder_contents',
    'folder_factories',
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
