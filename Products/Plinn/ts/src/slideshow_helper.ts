import {portal_url} from "./components/utils";
import {Slideshow} from "./components/slideshow";
import "./custom.scss";
import "bootstrap";
import * as $ from "jquery";

const connurl = portal_url() + '/ckeditor/filemanager/browser/mac_finder/connectors/plinn/connector'
document.querySelectorAll<HTMLDivElement>('div.slideshow')
    .forEach((elt) => {
        elt.style.position = 'relative';
        elt.style.width = elt.getAttribute('data-slideshow_width');
        elt.style.height = elt.getAttribute('data-slideshow_height');
        const rect = elt.getBoundingClientRect();
        const width = Math.round(rect.width);
        const height = Math.round(rect.height);
        const url = elt.getAttribute('data-slideshow_url');
        let duration = parseFloat(elt.getAttribute('data-slideshow_duration'));
        duration = (isNaN(duration)) ? 4.0 : duration;
        const path = url.slice(portal_url().length);

        const req = new XMLHttpRequest();
        req.addEventListener('load', () => {
            if (req.status === 200) {
                const doc = req.responseXML.documentElement;
                const rows = doc.getElementsByTagName('row');
                const imgUrls = [];
                for (let i = 0; i < rows.length; i++) {
                    const row = rows[i];
                    imgUrls.push(row.getAttribute('link'));
                }
                const sh = new Slideshow(elt, imgUrls, width, height, duration);
                sh.start();
            } else {
                console.error('Slide show HTTP error', req.status, req.statusText);
            }
        });
        req.open('POST', connurl, true);
        req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
        req.send("command=ls&Type=Image&path=" + encodeURIComponent(path));
    });

// $('.carousel')
//     .carousel({interval: 100000})
//     .carousel('pause');