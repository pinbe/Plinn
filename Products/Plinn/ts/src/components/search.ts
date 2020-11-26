import {writeAjaxResponse} from "./utils";

export class SearchForm {
    private readonly form: HTMLFormElement;

    constructor(form: HTMLFormElement) {
        this.form = form;
        this.form.addEventListener('submit', (evt) => this.onSubmit(evt));
    }

    private onSubmit(evt: Event) {
        evt.preventDefault();
        const fdata = new FormData(this.form);
        fdata.append('ajax', '1');

        const req = new XMLHttpRequest();
        req.open('POST', this.form.action);
        req.addEventListener('load', (e) => {
            const resp = <XMLHttpRequest>e.target;
            if (resp.status === 200) {
                document.querySelector('#fixed-content').innerHTML = '';
                writeAjaxResponse(resp.responseXML);
                fdata.delete('ajax');
                const args: [string, string][] = [];
                fdata.forEach((value, key) => {
                    args.push([key, encodeURIComponent(value.toString())]);
                });
                const querystring = args.map((kv) => `${kv[0]}=${kv[1]}`).join('&');
                const url = `${this.form.action}?${querystring}`;
                history.pushState(url, '', url);
            }
        });
        req.send(fdata);
    }
}
