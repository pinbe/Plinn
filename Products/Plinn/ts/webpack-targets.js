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
        entry: './src/bs-plinn.scss',
        output: {
            filename: 'bs-plinn.css'
        }
    }
);

module.exports = {
    targets: targets
};
