// (c) Benoît PIN 2006-2007
// http://plinn.org
// Licence GPL
//
//

const isTextMime = /^text\/.+/i;
const NULL_CALLBACK=()=>{};

export class FragmentImporter {
    private readonly url: string;
    onAfterPopulate: () => void;
    private fallBackUrl: string;

    constructor(url: string, onAfterPopulate: () => void = NULL_CALLBACK, fallbackUrl = '') {
        this.url = url;
        this.onAfterPopulate = onAfterPopulate;
        this.fallBackUrl = fallbackUrl;
    }

    private _load(url: string) {
        const req = new XMLHttpRequest();
        req.onreadystatechange = () => {
            switch (req.readyState) {
                case 2 :
                    try {
                        if (!isTextMime.exec(req.getResponseHeader('Content-Type'))) {
                            req.onreadystatechange = null;
                            req.abort();
                            window.location.href = this.fallBackUrl;
                        }
                    } catch (e) {
                    }
                    break;

                case 4 :
                    if (req.status === 200) {
                        this.populateBaseElement(req);
                    } else {
                        alert('Error: ' + req.status);
                    }
                    break;
            }
        };

        req.open("GET", url, true);
        req.send(null);
    }

    load(fallBackUrl='') {
        if (fallBackUrl) {
            this.fallBackUrl = fallBackUrl;
        } else {
            this.fallBackUrl = this.url;
        }
        this._load(this.url);
    }

    useMacro(template: string, macro: string, fragmentSelector: string, queryString: string = '') {
        let url = this.url +
            "/use_macro?template=" + encodeURIComponent(template) +
            "&macro=" + encodeURIComponent(macro) +
            "&fragmentSelector=" + encodeURIComponent(fragmentSelector);
        if (queryString) {
            url += '&' + queryString;
        }
        this._load(url);
    }

    private populateBaseElement(req: XMLHttpRequest) {
        const contentType = req.getResponseHeader('Content-Type');
        if (!isTextMime.exec(contentType)) {
            window.location.href = this.fallBackUrl;
            return;
        }

        if (contentType.indexOf('text/xml') !== -1) {
            const fragments = req.responseXML.documentElement.childNodes;
            // var element, dest, scripts, i, j;
            for (let i = 0; i < fragments.length; i++) {
                const element = fragments[i];
                switch (element.nodeName) {
                    case 'fragment' :
                        // dest = document.getElementById(element.getAttribute('id'));
                        const dest = document.querySelector((<Element>element).getAttribute('selector'));
                        if (dest) {
                            dest.innerHTML = element.firstChild.nodeValue;
                            const scripts = dest.getElementsByTagName('script');
                            for (let j = 0; j < scripts.length; j++) {
                                console.warn('TODO:', scripts[j]);
                                // globalScriptRegistry.loadScript(scripts[j]);
                            }
                        }
                        break;

                    case 'base' :
                        const headBase = document.getElementsByTagName('base');
                        if (headBase.length > 0) {
                            headBase[0].setAttribute('href', (<Element>element).getAttribute('href'));
                        } else {
                            const newBase = document.createElement('base');
                            newBase.setAttribute('href', (<Element>element).getAttribute('href'));
                            document.head.appendChild(newBase);
                        }
                        break;
                }
            }
        }
        this.onAfterPopulate();
    }
}