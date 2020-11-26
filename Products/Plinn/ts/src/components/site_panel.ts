import * as d3 from "d3";
import {readCookie} from "./utils";

export class SitePanel {
    private opened: boolean;
    private panel: HTMLDivElement;
    private mainWrapper: HTMLDivElement;

    constructor(panel: HTMLDivElement, mainWrapper: HTMLDivElement) {
        this.opened = readCookie('spo') === '1';
        this.panel = panel;
        this.mainWrapper = mainWrapper;
        const handle = this.panel.querySelector('.handle a');
        handle.addEventListener('click', (evt) => {
            evt.preventDefault();
            evt.stopPropagation();
            this.toggle();
        });
    }

    toggle(): void {
        const t = d3.transition()
            .duration(500)
            .ease(d3.easeCubicOut)
        ;

        const shift = this.opened ? 0 : 300;

        d3.select(this.panel)
            .transition(t)
            .style('left', (-300 + shift) + 'px')
            .tween('attr.left', () => {
                return () => {
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
    }
}
