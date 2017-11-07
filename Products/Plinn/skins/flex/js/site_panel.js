var SitePanel;
(function() {
    SitePanel = function(panelSelector, mainWrapperSelector) {
        this.opened = readCookie('spo') === '1';
        this.panel = document.querySelector(panelSelector);
        this.mainWrapper = document.querySelector(mainWrapperSelector);
        var handle =this.panel.querySelector('.handle a');
        var self = this;
        handle.addEventListener('click', function(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            self.toggle();
        });
    };

    SitePanel.prototype.toggle = function() {
        var self = this;
        var t = d3.transition()
            .duration(500)
            .ease(d3.easeCubicOut)
        ;

        var targetWidth = this.opened ? '0px' : '300px';

        d3.select(this.panel)
            .transition(t)
            .style('width', targetWidth)
        ;

        d3.select(this.mainWrapper)
            .transition(t)
            .style('margin-left', targetWidth)
            .style('width', 'calc(100vw - ' + targetWidth + ')')
        ;

        this.opened = !this.opened;
        document.cookie = 'spo=' + ((this.opened) ? '1' : '0');
    };
}());