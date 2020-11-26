import {GLOBAL_SCRIPT_REGISTRY} from "./script_registry";

export function readCookie(name: string): string | null {
    // from w3schools.com
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(nameEQ) !== -1) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

export function writeAjaxResponse(doc: Document): void {
    if (doc.documentElement.tagName !== 'fragments')
        return;

    for (let i = 0; i < doc.documentElement.children.length; i++) {
        const elt = doc.documentElement.children[i];
        switch (elt.tagName) {
            case 'base':
                let base: HTMLBaseElement = document.querySelector<HTMLBaseElement>('head base');
                if (!base) {
                    const head = document.querySelector<HTMLHeadElement>('head');
                    base = document.createElement('base');
                    head.appendChild(base);
                }
                base.href = elt.getAttribute('href');
                break;

            case 'fragment' :
                const selector = (elt.hasAttribute('id')) ?
                    `#${elt.getAttribute('id')}` :
                    elt.getAttribute('selector') || '';
                const dest = document.querySelector(selector);
                if (dest) {
                    dest.innerHTML = elt.firstChild.nodeValue; // eg. content text carried by a CDATA
                    dest.querySelectorAll('script')
                        .forEach((script: HTMLScriptElement) => GLOBAL_SCRIPT_REGISTRY.loadScript(script));
                } else {
                    console.warn('dest element not found:', selector);
                    console.log(elt.firstChild.nodeValue);
                }
                break;
        }
    }
}

/* adapted from http://xahlee.info/js/js_shake_box.html */
export function shake(e: HTMLElement, distance = 5, time = 500): void {
    // Save the original style of e, Make e relatively positioned, Note the animation start time, Start the animation
    const originalStyle = e.style.cssText;
    e.style.position = "relative";
    const start = (new Date()).getTime();

    // This function checks the elapsed time and updates the position of e.
    // If the animation is complete, it restores e to its original state.
    // Otherwise, it updates e's position and schedules itself to run again.
    function animate() {
        const now = (new Date()).getTime();
        // Get current time
        const elapsed = now - start;
        // How long since we started
        const fraction = elapsed / time;
        // What fraction of total time?
        if (fraction < 1) {
            // If the animation is not yet complete
            // Compute the x position of e as a function of animation
            // completion fraction. We use a sinusoidal function, and multiply
            // the completion fraction by 4pi, so that it shakes back and
            // forth twice.
            const x = distance * Math.sin(fraction * 8 * Math.PI);
            e.style.left = x + "px";
            // Try to run again in 25ms or at the end of the total time.
            // We're aiming for a smooth 40 frames/second animation.
            setTimeout(animate, Math.min(25, time - elapsed));
        } else {
            // Otherwise, the animation is complete
            e.style.cssText = originalStyle; // Restore the original style
        }
    }

    animate();
}

export function smoothScroll(from: number, to: number): void {
    const step = 25;
    let pos = from;
    const dir: number = (to > from) ? 1 : -1;

    // eslint-disable-next-line prefer-const
    let intervalId: number;

    function jump() {
        window.scroll(0, pos);
        pos = pos + step * dir;
        if ((dir === 1 && pos >= to) ||
            (dir === -1 && pos <= to)) {
            window.clearInterval(intervalId);
            window.scroll(0, to);
        }
    }

    intervalId = window.setInterval(jump, 10);
}

export function getCopyOfNode(node: Node): Node {
    const ELEMENT_NODE = 1;
    const TEXT_NODE = 3;
    switch (node.nodeType) {
        case ELEMENT_NODE:
            const attributes = (<Element>node).attributes;
            const childs = node.childNodes;

            const e = document.createElement(node.nodeName);

            for (let i = 0; i < attributes.length; i++) {
                const attribute = attributes[i];
                e.setAttribute(attribute.name, attribute.value);
            }

            for (let i = 0; i < childs.length; i++) {
                e.appendChild(getCopyOfNode(childs[i]));
            }
            return e;

        case TEXT_NODE:
            return document.createTextNode(node.nodeValue);
    }
}

export function absolute_url(): string {
    let e = document.getElementById("Object_URL");
    if (e)
        return e.innerText;
    else {
        e = document.getElementById("BC_Object_URL");
        if (e)
            return e.innerText;
        else
            return document.body.getAttribute('data-absolute_url');
    }
}

export function portal_url(): string {
    return document.body.getAttribute('data-portal_url');
}

export const getWindowScrollY = (window.scrollY !== undefined) ?
    () => window.scrollY :
    () => document.documentElement.scrollTop;

export const getWindowHeight = (window.innerHeight !== undefined) ?
    () => window.innerHeight :
    () => document.documentElement.clientHeight;

export const clearSelection = function (): void {
    if (window.getSelection) {
        if (window.getSelection().empty) {  // Chrome
            window.getSelection().empty();
        } else if (window.getSelection().removeAllRanges) {  // Firefox
            window.getSelection().removeAllRanges();
        }

    } else {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        if (document.selection) {  // IE?
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            document.selection.empty();
        }
    }
};
