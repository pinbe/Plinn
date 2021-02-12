// typescript targets
const tsTargets = [
    'main',
    'slideshow_helper',
    'metadata_helper',
    'folder_contents',
    'folder_factories',
];

const targets = tsTargets.map(name => {
    return {
        entry: `./src/${name}.ts`,
        output: {
            filename: `${name}.js`
        }
    };
});

// scss targets
targets.push(
    {
        entry: './src/custom.scss',
        output: {
            filename: 'plinn-all.css'
        }
    }
);

module.exports = {
    targets: targets
};
