import {writeAjaxResponse} from "./utils";

export class SearchForm {
    private readonly form: HTMLFormElement;

    constructor(form: HTMLFormElement) {
        this.form = form;
        this.form.addEventListener('submit', (evt)=>this.onSubmit(evt));
    }

    private onSubmit(evt: Event) {
        evt.preventDefault();
        const fdata = new FormData(this.form);
        fdata.append('ajax', '1');

        const req = new XMLHttpRequest();
        req.open('POST', this.form.action);
        req.addEventListener('load', (e) => {
            const resp = <XMLHttpRequest>e.target;
            if(resp.status === 200){
                writeAjaxResponse(resp.responseXML);
            }
        });
        req.send(fdata);
    }
}
