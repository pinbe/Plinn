// (c) Benoît PIN 2006-2014
// http://plinn.org
// Licence GPL
//
//

import SubmitEvent = JQuery.SubmitEvent;
import {shake, smoothScroll, writeAjaxResponse} from "./utils";
import {GLOBAL_SCRIPT_REGISTRY} from "./script_registry";

function raiseMouseEvent(ob: HTMLElement, eventName: string) {
    const event = document.createEvent("MouseEvents");
    event.initEvent(eventName, true, true);
    ob.dispatchEvent(event);
}

export class FormManager {
    private readonly form: HTMLFormElement;
    private responseTextDest: HTMLElement;
    private readonly lazy: boolean;
    private readonly noHistory: boolean;
    public onBeforeSubmit: (fm: this, evt: Event) => string;
    public onResponseLoad: (resp: XMLHttpRequest) => void;
    onAfterPopulate: (resp: XMLHttpRequest) => void;
    public submitButton: HTMLInputElement | HTMLButtonElement | {name: string, value: string};
    private readonly lazyListeners: {
        element: HTMLInputElement|HTMLTextAreaElement,
        eventName: string,
        handler: (evt: Event) => void }[];
    private hasFile: boolean;
    private liveFormField: HTMLInputElement | HTMLTextAreaElement;
    private pendingEvent: [HTMLElement, string];
    private fieldTagName: string;

    constructor(form: HTMLFormElement,
                responseTextDest: HTMLElement=undefined,
                lazy = false,
                noHistory = false) {
        if (form.elements.namedItem("noAjax"))
            return;

        this.form = form;
        this.responseTextDest = responseTextDest;
        this.lazy = lazy;
        this.noHistory = noHistory;

        this.form.addEventListener('submit', (evt) => this.submit(evt));
        this.form.addEventListener('click', (evt) => this.click(evt));

        /* raised on form submit */
        this.onBeforeSubmit = null;
        /* raised after xmlhttp response */
        this.onResponseLoad = null;
        /* raised when the responseText is added inside the main element.
         * (onResponseLoad may have the default value) */
        this.onAfterPopulate = null;
        this.submitButton = null;

        if (this.lazy) {
            this.form.addEventListener('click', (evt) => {
                this.replaceElementByField(evt);
                this.click(evt);
            });
            this.form.onfocus = this.form.onclick;
            this.onResponseLoad = (req) => this.restoreField(req);
            this.lazyListeners = [];
        }
    }

    public submit(evt: Event = null) {
        const form = this.form;

        let bsMessage: string; // before submit message
        if (this.onBeforeSubmit) {
            bsMessage = this.onBeforeSubmit(this, evt);
        }

        if (bsMessage === 'cancelSubmit') {
            try {
                evt.preventDefault();
            } catch (e) {
            }
            return;
        }

        if (!this.onResponseLoad) {
            this.onResponseLoad = this.loadResponse;
        }

        const submitButton = this.submitButton;
        const queryInfo = this.formData2QueryString();
        let query = queryInfo.query;
        this.hasFile = queryInfo.hasFile;


        if (!this.onAfterPopulate) {
            this.onAfterPopulate = () => null;
        }

        if (submitButton) {
            query += submitButton.name + '=' + submitButton.value + '&';
        }

        if (form.method.toLowerCase() === 'post')
            this._post(query);
        else
            this._get(query);

        try {
            evt.preventDefault();
        } catch (e2) {
        }
    }

    private _post(query: string) {
        // send form by XmlHttpRequest
        query += "ajax=1";

        const req = new XMLHttpRequest();
        req.addEventListener('load', (e) => {
                const resp = <XMLHttpRequest>e.target;
                if (resp.status === 200 || req.status === 204) {
                    this.onResponseLoad(req);
                } else {
                    console.error('Error: ' + req.status);
                }
            }
        );
        req.open("POST", this.form.action, true);
        req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
        req.send(query);
    }

    private _get(query: string) {
        let url = this.form.action;
        url += '?' + query;
        // TODO:
        // AjaxLinkHandler.prototype.loadUrl(url);
    }

    private click(evt: MouseEvent) {
        const target = <HTMLInputElement>evt.target;
        if (target.type === "submit" || target.type === "image") {
            this.submitButton = target;
            evt.stopPropagation();
        } else if (target.tagName === 'I') {
            const parent = target.parentElement;
            if (parent.tagName === 'BUTTON' && (<HTMLButtonElement>parent).type === 'submit') {
                this.submitButton = <HTMLButtonElement>parent;
                evt.stopPropagation();
            }
        }
    }

    private replaceElementByField(evt: Event) {
        const ob = <HTMLElement>evt.target;
        const eventType = evt.type;
        if (eventType === 'focus' || eventType === 'focusin') {
            if (this.liveFormField && ob.tagName !== 'INPUT') {
                this.pendingEvent = [ob, 'click'];
            }
            return;
        }
        const fieldName = ob.getAttribute('id');
        if (fieldName) {
            this.fieldTagName = ob.tagName;
            const tabIndex = ob.tabIndex;
            let text: string;
            if (ob.firstElementChild && ob.firstElementChild.className === 'hidden_value') {
                text = ob.firstElementChild.innerHTML;
            } else {
                text = ob.innerHTML;
            }
            evt.stopPropagation();
            let parent: HTMLElement;

            switch (ob.tagName) {
                case 'SPAN' :
                    // create input element
                    const inputText = document.createElement("input");
                    inputText.setAttribute("type", "text");
                    text = text.replace(/\n/g, ' ');
                    text = text.replace(/\s+/g, ' ');
                    text = text.replace(/^ /, '');
                    text = text.replace(/ $/, '');
                    inputText.setAttribute("value", text);
                    let inputWidth = text.length / 1.9;
                    inputWidth = (inputWidth > 5) ? inputWidth : 5;
                    inputText.style.width = inputWidth + 'em';

                    // replacement
                    parent = ob.parentElement;
                    parent.replaceChild(inputText, ob);

                    inputText.focus();
                    inputText.select();
                    inputText.setAttribute('name', fieldName);
                    inputText.tabIndex = tabIndex;
                    inputText.className = 'live_field';
                    this.liveFormField = inputText;
                    this.lazyListeners.push(
                        {
                            element: inputText,
                            eventName: 'blur',
                            handler: () => this.submit()
                        }
                    );
                    this.lazyListeners.push(
                        {
                            element: inputText,
                            eventName: 'keypress',
                            handler: (evt) => this._fitField(evt)
                        }
                    );
                    this._addLazyListeners();
                    break;

                case 'DIV' :
                case 'P' :
                    // create textarea
                    const ta = document.createElement('textarea');
                    ta.style.display = 'block';
                    ta.className = 'live_field';
                    text = text.replace(/^\s*/, '');
                    text = text.replace(/\s*$/, '');
                    ta.value = text;

                    // replacement
                    parent = ob.parentElement;
                    parent.replaceChild(ta, ob);

                    ta.focus();
                    ta.select();
                    ta.setAttribute('name', fieldName);
                    ta.tabIndex = tabIndex;
                    this.liveFormField = ta;
                    this.lazyListeners.push(
                        {
                            element: ta,
                            eventName: 'blur',
                            handler: () =>this.submit()
                        }
                    );
                    this._addLazyListeners();
                    break;
            }
        }
    }

    private _addLazyListeners() {
        for (let i = 0; i < this.lazyListeners.length; i++) {
            const handlerInfo = this.lazyListeners[i];
            handlerInfo.element.addEventListener(handlerInfo.eventName, handlerInfo.handler);
        }
    }

    private _removeLazyListeners() {
        for (let i = 0; i < this.lazyListeners.length; i++) {
            const handlerInfo = this.lazyListeners[i];
            handlerInfo.element.removeEventListener(handlerInfo.eventName, handlerInfo.handler);
        }
    }


    private restoreField(resp: XMLHttpRequest) {
        let text: string;
        const input = this.liveFormField;
        if (resp.status === 200) {
            if (resp.getResponseHeader('Content-Type').indexOf('text/xml') !== -1) {
                let out = '..........';
                if (resp.responseXML.documentElement.firstChild)
                    out = resp.responseXML.documentElement.firstChild.nodeValue;

                switch (resp.responseXML.documentElement.nodeName) {
                    case 'computedField':
                        text = out;
                        break;
                    case 'error':
                        this._removeLazyListeners();
                        alert(out);
                        this.pendingEvent = null;
                        input.focus();
                        this._addLazyListeners();
                        return false;
                }
            } else {
                text = resp.responseText;
            }
        } else {
            text = '';
        }

        if (!text.match(/\w/)) {
            text = '..........';
        }

        const field = document.createElement(this.fieldTagName);
        field.innerHTML = text;
        field.setAttribute('id', input.getAttribute('name'));
        field.className = 'editable';
        field.tabIndex = input.tabIndex;

        const parent = input.parentNode;
        parent.replaceChild(field, input);
        this.liveFormField = null;

        if (this.pendingEvent) {
            raiseMouseEvent(this.pendingEvent[0], this.pendingEvent[1]);
        }
        return true;
    }


    private formData2QueryString() {
        // http://www.onlamp.com/pub/a/onlamp/2005/05/19/xmlhttprequest.html
        const form = this.form;
        let strSubmit = '', formElem, elements;
        let hasFile = false;

        if (!this.lazy) {
            elements = form.elements;
        } else {
            elements = [];
            let formElements = form.elements;
            for (let i = 0; i < formElements.length; i++) {
                formElem = <HTMLInputElement>formElements[i];
                switch (formElem.type) {
                    case 'hidden':
                        elements.push(formElem);
                        break;
                    default :
                        if (formElem === this.liveFormField) {
                            elements.push(formElem);
                        }
                }
            }
        }

        for (let i = 0; i < elements.length; i++) {
            formElem = <HTMLInputElement>elements[i];
            switch (formElem.type) {
                // text, select, hidden, password, textarea elements
                case 'text':
                case 'select-one':
                case 'hidden':
                case 'password':
                case 'textarea':
                    strSubmit += formElem.name + '=' + encodeURIComponent(formElem.value) + '&';
                    break;
                case 'radio':
                case 'checkbox':
                    if (formElem.checked) {
                        strSubmit += formElem.name + '=' + encodeURIComponent(formElem.value) + '&';
                    }
                    break;
                case 'select-multiple':
                    let options = formElem.getElementsByTagName("OPTION"), option;
                    for (let j = 0; j < options.length; j++) {
                        option = <HTMLOptionElement>options[j];
                        if (option.selected) {
                            strSubmit += formElem.name + '=' + encodeURIComponent(option.value) + '&';
                        }
                    }
                    break;
                case 'file':
                    if (formElem.value) {
                        hasFile = true;
                    }
                    break;
            }
        }
        return {'query': strSubmit, 'hasFile': hasFile};
    }

    loadResponse(resp: XMLHttpRequest) {
        if (resp.getResponseHeader('Content-Type').indexOf('text/xml') !== -1) {
            switch (resp.responseXML.documentElement.nodeName) {
                case 'fragments' :
                    writeAjaxResponse(resp.responseXML);
                    break;

                case 'error':
                    alert(resp.responseXML.documentElement.firstChild.nodeValue);
                    return;
            }
        } else {
            this.responseTextDest.innerHTML = resp.responseText;
            this.responseTextDest.querySelectorAll<HTMLScriptElement>('script')
                .forEach((script)=>GLOBAL_SCRIPT_REGISTRY.loadScript(script));
        }

        this.onAfterPopulate(resp);
        this.scrollToPortalMessage();
        const url = this.form.action;
        if (!this.noHistory) {
            history.pushState(url, document.title, url);
        }
    }

    private scrollToPortalMessage() {
        const psm = document.getElementById('status-message');
        if (psm) {
            const msgOffset = psm.offsetTop;
            smoothScroll(window.scrollY, msgOffset);
            shake(psm, 10, 1000);
        }
    }

    private _fitField(evt: Event) {
        const ob = <HTMLInputElement>evt.target;
        let inputWidth = ob.value.length / 1.9;
        inputWidth = (inputWidth > 5) ? inputWidth : 5;
        ob.style.width = inputWidth + 'em';
    }
}

export function initForms(baseElement: HTMLElement|Document, lazy:boolean) {
    if (!baseElement) {
        baseElement = document;
    }
    const dest = document.getElementById("content-wrapper");
    baseElement.querySelectorAll("form")
        .forEach((form)=>new FormManager(form, dest, lazy))
}
