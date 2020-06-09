(function() {
    const TRANSITION_DURATION = 0.750; //seconds
    let Slideshow = function(container,
                             imgUrls,
                             width,
                             height,
                             duration /* seconds */) {
        this.container = container;
        this.imgUrls = imgUrls;
        this.width = width;
        this.height = height;
        this.duration = duration;
        this.currentIndex = 0;
        this.pendingImage = new Image();
        this.pendingImage.addEventListener('load', () => this.onImgLoaded());
        this.tr_duration = Math.min(TRANSITION_DURATION, duration/2) * 1000;
    };

    Slideshow.prototype.start = function() {
        this.pendingImage.src = `${this.imgUrls[this.currentIndex]}/getResizedImage?size=${this.width}_${this.height}`;
    };

    Slideshow.prototype.onImgLoaded = function() {
        let prevImg = this.container.querySelector('img');
        if (prevImg)
            d3.select(prevImg)
                .transition().duration(this.tr_duration)
                .style('opacity', '0')
                .remove();

        d3.select(this.container)
          .append('img')
          .style('opacity', '0')
          .attr('src', this.pendingImage.src)
          .transition().duration(this.tr_duration)
          .style('opacity', '1');

        setTimeout(() => this.loadNext(), this.duration*1000);
    };

    Slideshow.prototype.loadNext = function() {
        this.currentIndex++;
        if(this.currentIndex >= this.imgUrls.length)
            this.currentIndex = 0;
        this.pendingImage.src = `${this.imgUrls[this.currentIndex]}/getResizedImage?size=${this.width}_${this.height}`;
    };

    let connurl = portal_url() + '/ckeditor/filemanager/browser/mac_finder/connectors/plinn/connector'
    document.querySelectorAll('article.document .slideshow')
            .forEach((elt, index, all) => {
                elt.style.position = 'relative';
                elt.style.width = elt.getAttribute('data-slideshow_width');
                elt.style.height = elt.getAttribute('data-slideshow_height');
                let rect = elt.getBoundingClientRect();
                let width = rect.width;
                let height = rect.height;
                let url = elt.getAttribute('data-slideshow_url');
                let duration = parseFloat(elt.getAttribute('data-slideshow_duration'));
                duration = (isNaN(duration)) ? 4.0 : duration;
                let path = url.slice(portal_url().length);

                let req = new XMLHttpRequest();
                req.addEventListener('load', () => {
                    let doc = req.responseXML.documentElement;
                    let rows = doc.getElementsByTagName('row');
                    let imgUrls = [];
                    for (let row of rows) {
                        imgUrls.push(row.getAttribute('link'));
                    }
                    let sh = new Slideshow(elt, imgUrls, width, height, duration);
                    sh.start();
                });
                req.open('POST', connurl, true);
                req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
                req.send("command=ls&Type=Image&path=" + encodeURIComponent(path));
            });
}());