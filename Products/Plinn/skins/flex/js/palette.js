var InspectorPalette;
(function() {
    InspectorPalette = function(paletteSelector, onExpand, onCollapse) {
        var palette = d3.select(paletteSelector);
        this.toggleWrapper = palette.select('.toggle');
        this.toggleButton = this.toggleWrapper.select('a');
        var self = this;


        this.toggleButton.node()
            .addEventListener('click',
                function(evt) {
                    evt.preventDefault();
                    self.toggle(evt);
                }
            );

            // just for debug purpose
        this.onExpand = onExpand ? onExpand : function() {
            console.log('expanded:', palette.node());
        };

        this.onCollapse = onCollapse ? onCollapse : function() {
            console.log('collapsed:', palette.node());
        };
    };

    InspectorPalette.prototype.toggle = function() {
        var wrapperNode = this.toggleWrapper.node();
        if(wrapperNode.classList.contains('closed')) {
            wrapperNode.classList.remove('closed');
            wrapperNode.classList.add('opened');
            this.onExpand(this);
        }
        else {
            wrapperNode.classList.remove('opened');
            wrapperNode.classList.add('closed');
            this.onCollapse(this);
        }
    };
}());
