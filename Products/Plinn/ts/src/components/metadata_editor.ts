var MetadataEditManager;
(function() {
    MetadataEditManager = function(paletteSelector) {
        var paletteMain = document.querySelector(paletteSelector + ' .main');
        var inspector = new InspectorPalette(paletteSelector);

        inspector.onExpand = function() {
            var fi = new FragmentImporter(absolute_url());
            fi.onAfterPopulate = function() {
                var form = paletteMain.querySelector('form');
                var fm = new FormManager(form);
                fm.onResponseLoad = function() {
                    inspector.toggle();
                };
            };

            fi.useMacro('header_widgets', 'titleAndDescForm', paletteSelector + ' .main');
        };

        inspector.onCollapse = function() {
            var fi = new FragmentImporter(absolute_url());
            fi.useMacro('header_widgets', 'viewTitleAndDesc', paletteSelector + ' .main');
        };
    };
}());