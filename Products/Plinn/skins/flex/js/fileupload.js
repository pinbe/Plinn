// © 2013-2017 Benoît Pin MINES ParisTech
var DDFileUploaderBase;

(function() {

    DDFileUploaderBase = function(dropbox, uploadUrl) {
        this.dropbox = dropbox;
        this.uploadUrl = uploadUrl;
        this.uploadQueue = [];
        this._uploadQueueRunning = false;
        var self = this;
        dropbox.addEventListener('dragenter', function(evt) {
            self.dragenter(evt);
        });
        dropbox.addEventListener('dragover', function(evt) {
            self.dragover(evt);
        });
        dropbox.addEventListener('drop', function(evt) {
            self.drop(evt);
        });
    };

    // Drag and drop
    DDFileUploaderBase.prototype.dragenter = function(evt) {
        evt.preventDefault();
        evt.stopPropagation();
    };

    DDFileUploaderBase.prototype.dragover = function(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        var dt = evt.dataTransfer;
        dt.dropEffect = 'copy';
    };

    DDFileUploaderBase.prototype.drop = function(evt) {
        evt.preventDefault();
        evt.stopPropagation();
        var dt = evt.dataTransfer;
        dt.dropEffect = 'copy';
        this.handleFiles(dt.files);
    };

    // Methods about upload
    DDFileUploaderBase.prototype.handleFiles = function(files) {
        // To be implemented by descendant.
    };


    DDFileUploaderBase.prototype.beforeUpload = function(item) {
        // To be implemented by decendant.
    };


    DDFileUploaderBase.prototype.upload = function(item) {
        // item.file must be the file to be uploaded
        this.beforeUpload(item);
        var reader = new FileReader();
        var req = new XMLHttpRequest();
        var file = item.file;

        var self = this;

        req.upload.addEventListener('progress', function(evt) {
            self.progressHandler(evt);
        });
        req.addEventListener('readystatechange',
            function(evt) {
                if(req.readyState === 4) {
                    self.uploadCompleteHandler(req);
                }
            });

        req.open("PUT", this.uploadUrl);
        req.setRequestHeader("Content-Type", file.type);
        req.setRequestHeader("X-File-Name", encodeURI(file.name));
        reader.addEventListener('load',
            function(evt) {
                try {
                    req.send(evt.target.result);
                }
                catch (e) {
                    console.error(`uplodad failed: ${file.name}`);
                }
            });
        reader.readAsArrayBuffer(file);
    };


    DDFileUploaderBase.prototype.uploadCompleteHandlerCB = function(req) {
        // To be implemented by descendant.
    };

    DDFileUploaderBase.prototype.uploadCompleteHandler = function(req) {
        this.uploadCompleteHandlerCB(req);
        this.uploadQueueLoadNext();
    };

    DDFileUploaderBase.prototype.progressHandlerCB = function(progress) {
        // To be implemented by descendant.
        // 0 <= progress <= 1
    };

    DDFileUploaderBase.prototype.progressHandler = function(evt) {
        if(evt.lengthComputable) {
            var progress = evt.loaded / evt.total;
            this.progressHandlerCB(progress);
        }
    };

    // Methods about queue
    DDFileUploaderBase.prototype.uploadQueuePush = function(item) {
        this.uploadQueue.push(item);
        if(!this._uploadQueueRunning) {
            this.startUploadQueue();
        }
    };

    DDFileUploaderBase.prototype.startUploadQueue = function() {
        this._uploadQueueRunning = true;
        this.uploadQueueLoadNext();
    };

    DDFileUploaderBase.prototype.uploadQueueLoadNext = function() {
        var item = this.uploadQueue.shift();
        if(item) {
            this.upload(item);
        }
        else {
            this._uploadQueueRunning = false;
        }
    };
}());
