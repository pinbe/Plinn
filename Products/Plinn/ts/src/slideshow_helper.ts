import {portal_url} from "./components/utils";
import {Slideshow} from "./components/slideshow";

const connurl = portal_url() + '/ckeditor/filemanager/browser/mac_finder/connectors/plinn/connector'
document.querySelectorAll<HTMLDivElement>('div.slideshow')
    .forEach((elt) => {
        elt.style.position = 'relative';
        elt.style.width = elt.getAttribute('data-slideshow_width');
        elt.style.height = elt.getAttribute('data-slideshow_height');
        let rect = elt.getBoundingClientRect();
        let width = Math.round(rect.width);
        let height = Math.round(rect.height);
        let url = elt.getAttribute('data-slideshow_url');
        let duration = parseFloat(elt.getAttribute('data-slideshow_duration'));
        duration = (isNaN(duration)) ? 4.0 : duration;
        let path = url.slice(portal_url().length);

        let req = new XMLHttpRequest();
        req.addEventListener('load', () => {
            if (req.status === 200) {
                let doc = req.responseXML.documentElement;
                let rows = doc.getElementsByTagName('row');
                let imgUrls = [];
                for (let i = 0; i < rows.length; i++) {
                    const row = rows[i];
                    imgUrls.push(row.getAttribute('link'));
                }
                let sh = new Slideshow(elt, imgUrls, width, height, duration);
                sh.start();
            } else {
                console.error('Slide show HTTP error', req.status, req.statusText);
            }
        });
        req.open('POST', connurl, true);
        req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
        req.send("command=ls&Type=Image&path=" + encodeURIComponent(path));
    });