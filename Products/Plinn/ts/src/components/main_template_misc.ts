import {getWindowScrollY} from "./utils";
import * as d3 from "d3";

function fixTopBar() {
    const topBar = document.getElementById('top-bar');
    const topBarRect = topBar.getBoundingClientRect();
    topBar.style.position = 'fixed';
    document.getElementById('content-outer').style.paddingTop = topBarRect.height + 'px';
    fitTopBar();
}

function fitTopBar() {
    const topBar = document.getElementById('top-bar');
    const content = document.getElementById('content-outer');
    const contentCStyle = getComputedStyle(content);
    topBar.style.width =
        content.getBoundingClientRect().width +
        parseInt(contentCStyle.marginLeft) +
        parseInt(contentCStyle.marginRight) +
        'px';
}

function stretchLogo() {
    const logo = <HTMLImageElement>document.getElementById('portal-logo');
    const natHeight = logo.naturalHeight;
    const menu = document.getElementById('site-menu');
    const minTopbarheight = (menu) ?
        parseInt(window.getComputedStyle(menu).fontSize) :
        natHeight / 2;
    logo.height = Math.min(natHeight,
        Math.max(natHeight - getWindowScrollY(),
            minTopbarheight));
    logo.width = logo.height * (logo.naturalWidth / natHeight);
}

function initUserMenu() {
    d3.select('#user-menu i')
        .on('click', (evt: MouseEvent) => {
                const menu = <HTMLElement>d3.select('#user-menu ul').node();
                const body = d3.select('body');
                if (menu.classList.contains('hidden')) {
                    menu.classList.remove('hidden');
                    evt.stopPropagation();
                    body.on('click.cancel-user-menu',
                        () => {
                            menu.classList.add('hidden');
                            body.on('click.cancel-user-menu', null);
                        }
                    );
                }
            }
        );
}

export function init() {
    if (document.body.getAttribute('data-isAnon') === 'True') {
        fixTopBar();
        window.addEventListener('resize', fitTopBar);
        window.addEventListener('scroll', stretchLogo);
    }
    initUserMenu();
}