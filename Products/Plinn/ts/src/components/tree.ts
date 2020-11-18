// (c) Benoît PIN 2006-2017
// http://plinn.org
// Licence GPL

import * as d3 from "d3";

export class TreeMaker {
    private root: HTMLElement;
    private readonly filter: string; // comma separated list of portal_types
    private readonly tree_pre: string; // actualy SimpleTreeMaker cookie name
    static TR_DURATION = 500;
    static TR_EASE = d3.easeCubicOut;

    constructor(rootWrapper: HTMLDivElement) {
        this.root = rootWrapper;
        this.filter = this.root.getAttribute('data-filter');
        this.tree_pre = this.root.getAttribute('data-tree_pre');
        this.root.addEventListener('click', (evt) => this.refreshTree(evt));
    }

    /*
    * expand / collapse handler
    * object loading trigger
    */
    private refreshTree(evt: MouseEvent) {
        const target = <HTMLElement>evt.target;
        target.blur();

        if (target.tagName === 'I') {
            evt.preventDefault();
            evt.stopPropagation();
            target.parentElement.blur();
            const row = target.parentElement.parentElement;

            if (target.classList.contains('opened')) {
                target.classList.remove('opened');
                target.classList.add('closed');
                this.removeRows(row);
            } else if (target.classList.contains('closed')) {
                evt.preventDefault();
                evt.stopPropagation();
                target.classList.remove('closed');
                target.classList.add('opened');

                const req = new XMLHttpRequest();
                req.onreadystatechange = () => {
                    switch (req.readyState) {
                        case 1:
                            break;
                        case 4:
                            this.importRows(req, row);
                    }
                };
                const links = row.querySelectorAll('a');
                const obUrl = links[links.length - 1];
                req.open("POST", obUrl + "/xml_nav_tree", true);
                req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
                req.send("filter=" + encodeURIComponent(this.filter) +
                    "&root_name=" + encodeURIComponent(this.tree_pre) +
                    "&expansion=" + encodeURIComponent(this.getExpansion()));

            }
        }
    };


    private getExpansion() {
        let row = this.root.firstElementChild;
        const steps = [this.root.getAttribute('data-root-id')];
        let last_depth = -1;
        let expid, node_depth, dd, step;
        while (row !== null) {
            if (row.querySelector('i.opened')) {
                expid = row.getAttribute('data-id');
                node_depth = parseInt(row.getAttribute('data-depth'), 10);
                dd = last_depth - node_depth + 1;
                last_depth = node_depth;
                if (dd > 0) {
                    step = '';
                    for (let j = 0; j < dd; j++)
                        step = step + '_';
                    steps.push(step);
                }
                steps.push(expid);
            }
            row = row.nextElementSibling;
        }
        return steps.join(':');
    }


    /*
    * expand the tree: sends request and imports rows based on xml response.
    */
    private importRows(req: XMLHttpRequest, parentRow: HTMLElement) {
        const rows = req.responseXML.documentElement.getElementsByTagName("row");
        let xmlRow, state, row;
        const depth = parseInt(parentRow.getAttribute('data-depth')) + 1;
        const parentRowNextSibling = parentRow.nextElementSibling;
        const appendRow = (parentRowNextSibling) ?
            (r: HTMLElement) => this.root.insertBefore(r, parentRowNextSibling) :
            (r: HTMLElement) => this.root.appendChild(r);

        for (let i = 0; i < rows.length; i++) {
            xmlRow = rows[i];
            row = d3.select(document.createElement('div'))
                .attr('data-depth', depth)
                .attr('data-id', xmlRow.getAttribute('name'))
                .style('padding-left', (depth - 1) * 16 + 5 + 'px')
            ;

            state = parseInt(xmlRow.getAttribute('state'));
            if (state === -1)
                row.append('a')
                    .attr('class', 'toggle')
                    .attr('href', '#')
                    .append('i')
                    .attr('class', 'fa fa-caret-right closed');
            else
                row.append('i')
                    .attr('class', 'sp');
            row.append('img')
                .attr('src', xmlRow.getAttribute('icon'));

            row.append('a')
                .attr('href', xmlRow.getAttribute('url'))
                .attr('title', xmlRow.getAttribute('description'))
                .text(xmlRow.childNodes[0].nodeValue);

            appendRow(row.node());

            row.style('height', '0px')
                .transition()
                .duration(TreeMaker.TR_DURATION)
                .ease(TreeMaker.TR_EASE)
                .style('height', null);
        }
    };

    /*
    * collapse the tree: removes deeper rows after the 'baseRow' passed.
    */
    private removeRows = function (baseRow: HTMLElement) {
        const baseRowDepth = parseInt(baseRow.getAttribute('data-depth'), 10);
        let nextRow = baseRow.nextElementSibling;
        while (nextRow !== null &&
        parseInt(nextRow.getAttribute('data-depth')) > baseRowDepth) {
            d3.select(nextRow)
                .transition()
                .duration(TreeMaker.TR_DURATION)
                .ease(TreeMaker.TR_EASE)
                .style('height', '0px')
                .remove();
            nextRow = nextRow.nextElementSibling;
        }
        document.cookie = encodeURIComponent(this.tree_pre) + '-state=' +
            encodeURIComponent(this.getExpansion()) + '; path=/';
    };
}
