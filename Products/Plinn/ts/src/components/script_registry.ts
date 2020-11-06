// (c) Benoît PIN 2006-2015
// http://plinn.org
// Licence GPL
//
//

class ScriptRegistry {
    private isLoading: boolean;
    private readonly loadedScripts: {[url:string]:boolean};
    private readonly HEAD: HTMLHeadElement;
    private readonly pendingScripts: [string, string|HTMLScriptElement][];

    constructor() {
        this.loadedScripts = {};
        this.pendingScripts = [];
        this.HEAD = document.getElementsByTagName('head')[0];
        this.isLoading = false;
    }

    public loadScript(scriptOb: HTMLScriptElement) {
        let scriptUrl: string;
        if (typeof (scriptOb) === 'string')
            scriptUrl = scriptOb;
        else
            scriptUrl = scriptOb.getAttribute('src');

        if (scriptUrl) {
            if (!this.loadedScripts[scriptUrl])
                this.pendingScripts.push(['url', scriptUrl]);
        } else {
            this.pendingScripts.push(['code', scriptOb]);
        }
        if (!this.isLoading && this.pendingScripts.length)
            this._loadNextScript();
    }

    private _loadNextScript() {
        const firstScript = this.pendingScripts[0];

        switch (firstScript[0]) {
            case 'url':
                const script: HTMLScriptElement = document.createElement("script");
                script.type = "text/javascript";
                script.src = <string>firstScript[1];
                this.HEAD.appendChild(script);
                this.loadedScripts[script.src] = true;
                this.isLoading = true;
                const this_ = this;
                script.onload = function () {
                    this_._removeScriptAfterLoad();
                };
                break;
            case 'code' :
                try {
                    /* jshint ignore:start */
                    eval((<HTMLScriptElement>firstScript[1]).text);
                    /* jshint ignore:end */
                } catch (e) {
                    if (window.console) {
                        console.group('Embedded script error');
                        console.error(e);
                        console.info(firstScript[1]);
                        console.groupEnd();
                    }
                }
                this._removeScriptAfterLoad();
                break;
        }
    }

    private _removeScriptAfterLoad() {
        this.pendingScripts.shift();
        if (this.pendingScripts.length)
            this._loadNextScript();
        else
            this.isLoading = false;
    }
}

export const GLOBAL_SCRIPT_REGISTRY = new ScriptRegistry();
