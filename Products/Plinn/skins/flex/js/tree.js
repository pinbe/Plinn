// (c) Benoît PIN 2006-2017
// http://plinn.org
// Licence GPL

var TreeMaker;

(function() {
    /* rootSelector -> selector to base node
    *  filter -> comma separated list of portal_types
    */
    TreeMaker = function(rootSelector, filter, tree_pre) {
        this.root = document.querySelector(rootSelector);
        this.filter = filter;
        this.tree_pre = tree_pre; // actualy SimpleTreeMaker cookie name
        var self = this;
        this.root.addEventListener('click',
            function(evt) {
                self.refreshTree(evt);
            });
        this.depthCpt = [];
    };

    /*
    * expand / collapse handler
    * object loading trigger
    */
    TreeMaker.prototype.refreshTree = function(evt) {
        var target = evt.target;
        target.blur();

        if(target.tagName === 'I') {
            evt.preventDefault();
            evt.stopPropagation();
            target.parentNode.blur();
            var row = target.parentNode.parentNode;

            if(target.classList.contains('opened')) {
                target.classList.remove('opened');
                target.classList.add('closed');
                this.removeRows(row);
            }
            else if(target.classList.contains('closed')) {
                evt.preventDefault();
                evt.stopPropagation();
                target.classList.remove('closed');
                target.classList.add('opened');

                var self = this;
                var req = new XMLHttpRequest();
                req.onreadystatechange = function() {
                    switch(req.readyState) {
                        case 1:
                            break;
                        case 4:
                            self.importRows(req, row);
                    }
                };
                var links = row.querySelectorAll('a');
                var obUrl = links[links.length - 1];
                req.open("POST", obUrl + "/xml_nav_tree", true);
                req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
                req.send("filter=" + encodeURIComponent(this.filter) +
                         "&root_name=" + encodeURIComponent(this.tree_pre) +
                         "&expansion=" + encodeURIComponent(this.getExpansion()));

            }
            return;

            var srcParts = target.src.split("/");
            var imgId = srcParts[srcParts.length - 1];
            var parentTd = target.parentNode.parentNode;
            var parentRow = parentTd.parentNode;
            var self = this;

            switch(imgId) {
                case "pl.png" :
                case "pl_ani.png" :
                    var linkCell = parentTd.nextSibling;
                    while(linkCell.nodeType !== 1)
                        linkCell = linkCell.nextSibling;

                    var obUrl = linkCell.getElementsByTagName("A")[0].href;

                    var req = new XMLHttpRequest();
                    req.onreadystatechange = function() {
                        switch(req.readyState) {
                            case 1:
                                showProgressImage();
                                break;
                            case 4:
                                hideProgressImage();
                                self.importRows(req, parentRow);
                        }
                    };
                    target.src = this.baseImgUrl + "mi_ani.png";
                    this._lastAniImg = target;
                    window.setTimeout(function() {
                        self._removeLastAniImg();
                    }, 500);

                    req.open("POST", obUrl + "/xml_nav_tree", true);
                    req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
                    req.send("filter=" + encodeURIComponent(this.filter) +
                        "&root_name=" + encodeURIComponent(this.root.id) +
                        "&expansion=" + encodeURIComponent(this.getExpansion()));

                    break;

                case "mi.png" :
                case "mi_ani.png" :
                    this.removeRows(parentRow);
                    target.src = this.baseImgUrl + "pl_ani.png";
                    this._lastAniImg = target;
                    window.setTimeout(function() {
                        self._removeLastAniImg();
                    }, 500);
                    document.cookie = encodeURIComponent(this.root.id) + '-state=' + encodeURIComponent(this.getExpansion()) +
                        ';path=/';
                    break;
            } // end switch (imgId)
            evt.preventDefault();
            evt.stopPropagation();
        }
    };


    TreeMaker.prototype._removeLastAniImg = function() {
        if(this._lastAniImg) {
            this._lastAniImg.src = this._lastAniImg.src.replace("_ani", "");
        }
    };

    TreeMaker.prototype.getExpansion = function() {
        var row = this.root.firstElementChild;
        var steps = [this.root.getAttribute('data-root-id')];
        var last_depth = -1;
        var expid, node_depth, dd, step;
        while(row !== null) {
            if (row.querySelector('i.opened')) {
                expid = row.getAttribute('data-id');
                node_depth = parseInt(row.getAttribute('data-depth'), 10);
                dd = last_depth - node_depth + 1;
                last_depth = node_depth;
                if(dd > 0) {
                    step = '';
                    for(var j = 0; j < dd; j++)
                        step = step + '_';
                    steps.push(step);
                }
                steps.push(expid);
            }
            row = row.nextElementSibling;
        }
        return steps.join(':');
    };


    /*
    * expand the tree: sends request and imports rows based on xml response.
    */
    TreeMaker.prototype.importRows = function(req, parentRow) {
        var rows = req.responseXML.documentElement.getElementsByTagName("row");
        var xmlRow, state, row;
        var depth = parseInt(parentRow.getAttribute('data-depth')) + 1;
        var parentRowNextSibling = parentRow.nextElementSibling;
        var self = this;
        var appendRow = (parentRowNextSibling) ?
                        function(r){self.root.insertBefore(r, parentRowNextSibling);} :
                        function(r){self.root.appendChild(r);};

        for(var i = 0; i < rows.length; i++) {
            xmlRow = rows[i];
            row = d3.select(document.createElement('div'))
                .attr('data-depth', depth)
                .attr('data-id', xmlRow.getAttribute('name'))
                .style('padding-left', (depth - 1) * 16 + 5 + 'px')
            ;

            state = parseInt(xmlRow.getAttribute('state'));
            if(state === -1)
                row.append('a')
                    .attr('href', '#')
                    .append('i')
                    .attr('class', 'fa fa-caret-right closed');
            else
                row.append('i')
                    .text(' ');
            row.append('img')
                .attr('src', xmlRow.getAttribute('icon'));

            row.append('a')
                .attr('href', xmlRow.getAttribute('url'))
                .attr('title', xmlRow.getAttribute('description'))
                .text(xmlRow.childNodes[0].nodeValue);

            appendRow(row.node());
        }
    };

    /*
    * collapse the tree: removes deeper rows after the 'baseRow' passed.
    */
    TreeMaker.prototype.removeRows = function(baseRow) {
        var baseRowDepth = parseInt(baseRow.getAttribute('data-depth'), 10);
        var nextRow = baseRow.nextElementSibling;
        var t = d3.transition()
            .duration(500)
            .ease(d3.easeCubicOut)
        ;
        while(nextRow !== null &&
              parseInt(nextRow.getAttribute('data-depth')) > baseRowDepth) {
            d3.select(nextRow)
                .transition(t)
                .style('height', '0px')
                .remove();
            nextRow = nextRow.nextElementSibling;
        }
        document.cookie = encodeURIComponent(this.tree_pre) + '-state=' +
            encodeURIComponent(this.getExpansion()) + '; path=/';
    };
})();