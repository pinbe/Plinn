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
        var t = d3.transition()
            .duration(500)
            .ease(d3.easeCubicOut)
        ;

        var shift = this.opened ? 0 : 300;

        d3.select(this.panel)
          .transition(t)
          .style('left', (-300 + shift) + 'px')
          .tween('attr.left', function() {
              return function(t) {
                  window.dispatchEvent(new Event('resize'));
              };
          })
        ;

        d3.select(this.mainWrapper)
            .transition(t)
            .style('margin-left', shift + 'px')
            .style('width', 'calc(100vw - ' + shift + 'px)')
        ;

        this.opened = !this.opened;
        document.cookie = 'spo=' + ((this.opened) ? '1' : '0') + '; path=/';
    };
}());