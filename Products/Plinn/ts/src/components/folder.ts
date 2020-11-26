import {DDFileUploaderBase, UploadedElement} from "./fileupload";
import {base_properties} from "./baseproperties";
import {FragmentImporter} from "./fragment_importer";
import {getCopyOfNode} from "./utils";

interface TargetHTMLTableRowElement extends HTMLTableRowElement {
    pos: number;
}

function getTargetRow(evt: Event): TargetHTMLTableRowElement {
    let target = <HTMLElement>evt.target;
    while (target.nodeName !== "TR") {
        target = target.parentElement;
    }
    return <TargetHTMLTableRowElement>target;
}

function raiseMouseEvent(el: HTMLElement, eventName: string) {
    const event = document.createEvent("MouseEvents");
    event.initEvent(eventName, true, true);
    el.dispatchEvent(event);
}


export class FolderDDropControler {
    readonly folderUrl: string;
    targetRow: TargetHTMLTableRowElement;
    private lastOverPosition: number;
    private prevDirUp: boolean;
    private noOver: boolean;
    private listing: HTMLTableSectionElement;
    private readonly firstItemPos: number;
    private lastCBChecked: HTMLInputElement;

    constructor(listing: HTMLTableSectionElement,
                orderable: boolean,
                firstItemPos: number) {
        this.folderUrl = document.getElementById("FolderUrl").innerHTML;
        this.targetRow = null;
        this.lastOverPosition = null;
        this.prevDirUp = null;
        this.noOver = true;
        this.listing = listing;
        this.firstItemPos = firstItemPos;
        this._updatePositions();
        this.lastCBChecked = undefined;

        if (orderable) {
            this.listing.onmousedown = (evt) => this.drag(evt);
            this.listing.onmouseover = (evt) => this.moveRow(evt);
            this.listing.onmouseup = () => this.drop();
            this.listing.addEventListener('click',
                (evt) => this.disableClickAfterDrop(evt));
        }
        this.listing.addEventListener('click',
            (evt) => this.selectCBRange(evt));
    }

    private _updatePositions() {
        const rows = this.listing.getElementsByTagName("TR");
        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            (<TargetHTMLTableRowElement>row).pos = i + this.firstItemPos;
            if (i % 2 === 0) {
                row.className = "even";
            } else {
                row.className = "odd";
            }
        }
    }

    private drag(evt: Event) {
        const target = <Element>evt.target;
        if (target.nodeName === "INPUT") {
            return true;
        }
        evt.preventDefault();
        const targetRow = getTargetRow(evt);
        targetRow.style.backgroundColor = base_properties.highLightColor;
        this.listing.style.cursor = "move";
        this.targetRow = targetRow;
        this.lastOverPosition = targetRow.pos;
    }

    private moveRow(evt: Event) {
        const targetRow = this.targetRow;
        if (targetRow !== null) {
            this.noOver = false;
            // if (browser.isIE10max) {document.selection.clear();}
            const overRow = getTargetRow(evt);

            if (overRow.pos === targetRow.pos) {
                return;
            }

            if (this.lastOverPosition < overRow.pos) { // move up
                this.listing.insertBefore(targetRow, overRow.nextSibling);
                this.prevDirUp = true;
                this.lastOverPosition = overRow.pos;
            } else if (this.lastOverPosition > overRow.pos) { // move down
                this.listing.insertBefore(targetRow, overRow);
                this.prevDirUp = false;
                this.lastOverPosition = overRow.pos;
            } else {
                if (this.prevDirUp) {
                    this.prevDirUp = false;
                    this.listing.insertBefore(targetRow, overRow);
                } else {
                    this.prevDirUp = true;
                    this.listing.insertBefore(targetRow, overRow.nextSibling);
                }
            }
        }
    }

    private drop() {
        const targetRow = this.targetRow;
        if (targetRow !== null) {
            targetRow.style.backgroundColor = "";
            this.listing.style.cursor = "";

            if (this.noOver) {
                setTimeout(() => this.reset(), 50);
                return;
            }
            if (this.lastOverPosition !== null) {
                // get new object position.
                let trim = 0;
                if (targetRow.pos < this.lastOverPosition && !this.prevDirUp) {
                    trim = -1;
                } else if (targetRow.pos > this.lastOverPosition && this.prevDirUp) {
                    trim = 1;
                }

                // construct url
                const object_id = targetRow.getElementsByTagName("INPUT")[0].getAttribute("value");
                const url = this.folderUrl + "/moveObjectIdToPosition";
                const form = "object_id=" + object_id + "&position:int=" +
                    String(this.lastOverPosition - 1 + trim);

                // reinitialize positions
                this._updatePositions();

                // send request
                const req = new XMLHttpRequest();
                req.open("POST", url, true);
                req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
                req.send(form);
                setTimeout(() => this.reset(), 50);
            }
        }
    }

    private disableClickAfterDrop(evt: Event) {
        if (!this.noOver) {
            evt.stopPropagation();
            evt.preventDefault();
        }
        this.reset();
    }

    private selectCBRange(evt: MouseEvent) {
        const target = <HTMLInputElement>evt.target;
        if (target.tagName === 'INPUT' && target.type === 'checkbox') {
            const shift = evt.shiftKey;
            if (shift && this.lastCBChecked) {
                const from = this.getCBIndex(this.lastCBChecked);
                const to = this.getCBIndex(target);
                const rows = this.listing.getElementsByTagName('TR');
                const start = Math.min(from, to);
                const stop = Math.max(from, to);
                for (let i = start; i < stop; i++) {
                    (<HTMLInputElement>rows[i].getElementsByTagName('INPUT')[0]).checked = true;
                }
            } else if (target.checked) {
                this.lastCBChecked = target;
            } else {
                this.lastCBChecked = undefined;
            }
        }
    }

    private getCBIndex(cb: HTMLInputElement) {
        let row = cb.parentElement;
        while (row.tagName !== 'TR') {
            row = row.parentElement;
        }
        return (<TargetHTMLTableRowElement>row).pos - this.firstItemPos;
    }

    reset(): void {
        this.targetRow = null;
        this.lastOverPosition = null;
        this.prevDirUp = null;
        this.noOver = true;
    }
}


export class DropTarget {
    private readonly folderDDControler: FolderDDropControler;
    private readonly batchSize: number;

    constructor(node: HTMLElement, folderDDControler: FolderDDropControler) {
        this.folderDDControler = folderDDControler;
        this.batchSize = parseInt(document.getElementById("BatchNavigationSize").innerHTML, 10);

        node.onmouseup = (evt) => this.drop(evt);
        node.onmouseover = (evt) => this.highlightTarget(evt);
        node.onmouseout = (evt) => {
            const target = <HTMLElement>evt.target;
            if (target.nodeName === "A" && target.className === "dropPageTarget") {
                target.className = "";
            }
        };
    }

    private drop(evt: Event) {
        const target = <HTMLElement>evt.target;
        if (target.nodeName === "A" &&
            target.className !== "previous" &&
            target.className !== "next") {
            const pageNumber = parseInt(target.innerHTML, 10);
            const targetRow = this.folderDDControler.targetRow;
            if (!isNaN(pageNumber) && targetRow) {
                this.folderDDControler.reset();
                const object_id = targetRow.getElementsByTagName("INPUT")[0].getAttribute("value");
                const url = this.folderDDControler.folderUrl + "/moveObjectIdToPosition";
                const form = "object_id=" + object_id + "&position:int=" + String(this.batchSize * (pageNumber - 1));
                // send request
                const req = new XMLHttpRequest();
                req.open("POST", url, true);
                req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
                req.send(form);
                req.onreadystatechange = () => {
                    if (req.readyState === 4) {
                        switch (req.status) {
                            case 200:
                            case 204:
                            case 1223:
                                raiseMouseEvent(target, "click");
                                break;
                            default:
                                alert('Error: ' + req.status);
                        }
                    }
                };
            }
        }
    }

    private highlightTarget(evt: Event) {
        // if (browser.isIE10max) {document.selection.clear();}
        const target = <HTMLElement>evt.target;
        if (this.folderDDControler.targetRow &&
            target.nodeName === "A" &&
            target.className !== "previous" &&
            target.className !== "next") {
            target.className = "dropPageTarget";
        }
    }
}


export function loadListing(evt: Event): boolean {
    const target = <HTMLElement>evt.target;
    evt.preventDefault();
    evt.stopPropagation();
    let url;
    switch (target.nodeName) {
        case "A" :
            const parts = (<HTMLAnchorElement>target).href.split('?');
            url = parts[0];
            let query = '';
            if (parts.length === 2) {
                query = parts[1];
            }

            const urlParts = url.split("/");
            url = urlParts.slice(0, urlParts.length - 1).join("/");
            if (query.search("template") === -1) {
                query += "&template=folder_contents_macros&macro=FolderListing&fragmentSelector=" +
                    encodeURIComponent("#FolderListing");
            }
            url = url + "/folder_contents?" + query;

            const fi = new FragmentImporter(url);
            fi.load();
            break;

        case "IMG" :
            if (target.id === 'SetSortingAsDefault') {
                const parent = <HTMLAnchorElement>target.parentElement;
                url = parent.href;
                url = url.replace("folder_contents", "folder_sort_control");
                parent.parentNode.removeChild(parent);

                const req = new XMLHttpRequest();
                req.open("GET", url, true);
                req.send(null);
            }
            break;
    }
    return false;
}

interface TableRowUploadedElement extends HTMLTableRowElement, UploadedElement {
    progressBar: HTMLSpanElement;
}

export class DDFolderUploader extends DDFileUploaderBase {
    private listing: HTMLTableSectionElement;
    private progressBarMaxSize: number;
    private readonly tableSpan: number;
    private lastRowClassName: string;
    private uploadedItem: TableRowUploadedElement;
    private progressBar: HTMLSpanElement;

    constructor(dropbox: HTMLElement, uploadUrl: string, listing: HTMLTableSectionElement) {
        super(dropbox, uploadUrl);
        this.listing = listing;
        this.progressBarMaxSize = listing.clientWidth;
        let thead: HTMLTableSectionElement = listing;
        do {
            thead = <HTMLTableSectionElement>thead.previousSibling;
        } while (thead.tagName !== 'THEAD');

        const cells = thead.getElementsByTagName('th');
        this.tableSpan = 0;
        for (let i = 0; i < cells.length; i++) {
            const cell = cells[i];
            this.tableSpan += cell.getAttribute('colspan') ? Number(cell.getAttribute('colspan')) : 1;
        }
        let lastRow = <HTMLTableRowElement>listing.lastChild;
        while (lastRow && lastRow.tagName !== 'TR') {
            lastRow = <HTMLTableRowElement>lastRow.previousSibling;
        }
        this.lastRowClassName = lastRow ? lastRow.className : 'even';
    }


    private createRow(file: File) {
        const row = <TableRowUploadedElement>document.createElement('tr');
        row.file = file;
        row.className = this.lastRowClassName === 'even' ? 'odd' : 'even';
        this.lastRowClassName = row.className;
        const td: HTMLTableCellElement = document.createElement('td');
        td.setAttribute('colspan', String(this.tableSpan));
        const relSpan = document.createElement('span');
        relSpan.style.position = 'relative';
        td.appendChild(relSpan);
        const progressBar = document.createElement('span');
        progressBar.className = 'upload-progress';
        row.progressBar = progressBar;
        relSpan.appendChild(progressBar);
        const fileNameSpan = document.createElement('span');
        fileNameSpan.innerHTML = file.name;
        td.appendChild(fileNameSpan);
        row.appendChild(td);
        this.listing.appendChild(row);
        this.progressBarMaxSize = row.clientWidth;
        return row;
    }

// Methods about upload
    protected handleFiles(files: FileList): void {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const row = this.createRow(file);
            this.uploadQueuePush(row);
        }
    }

    protected beforeUpload(item: TableRowUploadedElement): void {
        this.uploadedItem = item;
        this.progressBar = item.progressBar;
    }

    protected uploadCompleteHandlerCB(req: XMLHttpRequest): void {
        const item = this.uploadedItem;
        const row = <HTMLTableRowElement>getCopyOfNode(req.responseXML.documentElement.firstChild);

        if (req.status === 200) {
            // update
            this.listing.removeChild(item);
            const itemUrl = row.getElementsByTagName('a')[0].href;
            const links = this.listing.getElementsByTagName('a');
            for (let i = 0; i < links.length; i++) {
                if (links[i].href === itemUrl) {
                    const existingRow = links[i].parentElement.parentElement;
                    row.className = existingRow.className;
                    this.listing.replaceChild(row, existingRow);
                    break;
                }
            }
        } else if (req.status === 201) {
            // creation
            row.className = item.className;
            this.listing.replaceChild(row, item);
            this.progressBarMaxSize = row.clientWidth;
        }
    }

    protected progressHandlerCB(progress: number): void {
        // 0 <= progress <= 1
        let size = this.progressBarMaxSize * progress;
        size = Math.round(size);
        this.progressBar.style.width = size + 'px';
    }
}