export interface UploadedElement {
    file: File;
}

export class DDFileUploaderBase {
    protected dropbox: HTMLElement;
    private readonly uploadUrl: string;
    private uploadQueue: any[];
    private _uploadQueueRunning: boolean;

    constructor(dropbox: HTMLElement, uploadUrl: string) {
        this.dropbox = dropbox;
        this.uploadUrl = uploadUrl;
        this.uploadQueue = [];
        this._uploadQueueRunning = false;

        dropbox.addEventListener('dragenter', (evt) => this.dragenter(evt));
        dropbox.addEventListener('dragover', (evt) => this.dragover(evt));
        dropbox.addEventListener('drop', (evt) => this.drop(evt));
    }

    // Drag and drop
    private dragenter(evt: DragEvent) {
        evt.preventDefault();
        evt.stopPropagation();
    }

    private dragover(evt: DragEvent) {
        evt.preventDefault();
        evt.stopPropagation();
        evt.dataTransfer.dropEffect = 'copy';
    }

    private drop(evt: DragEvent) {
        evt.preventDefault();
        evt.stopPropagation();
        const dt = evt.dataTransfer;
        dt.dropEffect = 'copy';
        this.handleFiles(dt.files);
    }

    // Methods about upload
    protected handleFiles(files: FileList) {
        // To be implemented by descendant.
    }


    protected beforeUpload(item: UploadedElement) {
        // To be implemented by decendant.
    };


    private upload(item: UploadedElement) {
        // item.file must be the file to be uploaded
        this.beforeUpload(item);
        const reader = new FileReader();
        const req = new XMLHttpRequest();
        const file = item.file;

        req.upload.addEventListener('progress', (evt) => this.progressHandler(evt));
        req.addEventListener('readystatechange',
            (evt) => {
                if (req.readyState === 4) {
                    this.uploadCompleteHandler(req);
                }
            });

        req.open("PUT", this.uploadUrl);
        req.setRequestHeader("Content-Type", file.type);
        req.setRequestHeader("X-File-Name", encodeURI(file.name));
        reader.addEventListener('load',
            function (evt) {
                try {
                    req.send(evt.target.result);
                } catch (e) {
                    console.error(`uplodad failed: ${file.name}`);
                }
            });
        reader.readAsArrayBuffer(file);
    };


    protected uploadCompleteHandlerCB(req: XMLHttpRequest) {
        // To be implemented by descendant.
    }

    private uploadCompleteHandler(req: XMLHttpRequest) {
        this.uploadCompleteHandlerCB(req);
        this.uploadQueueLoadNext();
    }

    protected progressHandlerCB(progress: number) {
        // To be implemented by descendant.
        // 0 <= progress <= 1
    }

    private progressHandler(evt: ProgressEvent) {
        if (evt.lengthComputable) {
            this.progressHandlerCB(evt.loaded / evt.total);
        }
    }

    // Methods about queue
    protected uploadQueuePush(item: UploadedElement) {
        this.uploadQueue.push(item);
        if (!this._uploadQueueRunning) {
            this.startUploadQueue();
        }
    }

    private startUploadQueue() {
        this._uploadQueueRunning = true;
        this.uploadQueueLoadNext();
    }

    private uploadQueueLoadNext() {
        const item = this.uploadQueue.shift();
        if (item) {
            this.upload(item);
        } else {
            this._uploadQueueRunning = false;
        }
    }
}
