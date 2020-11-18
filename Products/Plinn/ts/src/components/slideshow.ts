import * as d3 from "d3";

const TRANSITION_DURATION = 0.750; //seconds

export class Slideshow {
    private container: HTMLElement;
    private readonly imgUrls: string[];
    private readonly width: number;
    private readonly height: number;
    private readonly duration: number;
    private currentIndex: number;
    private pendingImage: HTMLImageElement;
    private tr_duration: number;

    constructor(container: HTMLElement,
                imgUrls: string[],
                width: number,
                height: number,
                duration: number /* seconds */) {
        this.container = container;
        this.imgUrls = imgUrls;
        this.width = width;
        this.height = height;
        this.duration = duration;
        this.currentIndex = 0;
        this.pendingImage = new Image();
        this.pendingImage.addEventListener('load', () => this.onImgLoaded());
        this.tr_duration = Math.min(TRANSITION_DURATION, duration / 2) * 1000;
    }

    public start() {
        this.pendingImage.src = `${this.imgUrls[this.currentIndex]}/getResizedImage?size=${this.width}_${this.height}`;
    }

    private onImgLoaded() {
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

        setTimeout(() => this.loadNext(), this.duration * 1000);
    }

    private loadNext() {
        this.currentIndex++;
        if (this.currentIndex >= this.imgUrls.length)
            this.currentIndex = 0;
        this.pendingImage.src = `${this.imgUrls[this.currentIndex]}/getResizedImage?size=${this.width}_${this.height}`;
    }


}
