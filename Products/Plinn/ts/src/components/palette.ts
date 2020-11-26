import * as d3 from "d3";

// eslint-disable-next-line @typescript-eslint/no-empty-function
const NULL_CALLBACK = () => {};

export class InspectorPalette {
    private toggleWrapper: d3.Selection<HTMLElement, null, HTMLElement, null>;
    private toggleButton: d3.Selection<HTMLAnchorElement, null, HTMLElement, null>;
    onExpand: (p: InspectorPalette) => void;
    onCollapse: (p: InspectorPalette) => void;

    constructor(paletteWrapper: HTMLElement,
                onExpand: (p: InspectorPalette) => void = NULL_CALLBACK,
                onCollapse: (p: InspectorPalette) => void = NULL_CALLBACK) {
        const palette = d3.select<HTMLElement, null>(paletteWrapper);
        this.onExpand = onExpand;
        this.onCollapse = onCollapse;
        this.toggleWrapper = palette.select<HTMLElement>('.toggle');
        this.toggleButton = this.toggleWrapper.select<HTMLAnchorElement>('a');

        this.toggleButton.node()
            .addEventListener('click', (evt: MouseEvent) => {
                    evt.preventDefault();
                    evt.stopPropagation();
                    this.toggle();
                }
            );

    }

    toggle(): void {
        const wrapperNode = this.toggleWrapper.node();
        if (wrapperNode.classList.contains('closed')) {
            wrapperNode.classList.remove('closed');
            wrapperNode.classList.add('opened');
            this.onExpand(this);
        } else {
            wrapperNode.classList.remove('opened');
            wrapperNode.classList.add('closed');
            this.onCollapse(this);
        }
    }
}
