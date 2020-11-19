import {FormManager} from "./components/form_manager";

function main() {
    const fform = <HTMLFormElement>document.getElementById('factories_form');
    const fm = new FormManager(fform, undefined, undefined, true);
    let submitButton: HTMLInputElement;

    fm.onBeforeSubmit = (self: FormManager, evt: Event) => {
        if (submitButton)
            self.submitButton = submitButton;
        return '';
    };
    fm.onAfterPopulate = (req: XMLHttpRequest) => {
        const url = req.responseXML.documentElement.getAttribute('content-url');
        history.pushState(url, '', url);
    };

    const id2type = /(^[^\.]+)\.id:record$/;

    function trackFocus(evt: Event) {
        const input = <HTMLInputElement>evt.target;
        const matches: string[] = id2type.exec(input.name);
        if (matches && matches.length == 2)
            submitButton = <HTMLInputElement>fform.elements.namedItem(`${matches[1]}.type:record`);
    }

    for (let i = 0; i < fform.elements.length; i++) {
        const e = <HTMLInputElement>fform.elements[i];
        if (e.type === 'text')
            e.addEventListener('focus', trackFocus);
    }
}

main();