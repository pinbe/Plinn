import * as $ from "jquery";
import {MetadataEditManager} from "./components/metadata_editor";

function main() {
    document.querySelectorAll<HTMLElement>('.palette')
        .forEach((el) => {
            new MetadataEditManager(el);
        });
}

$(() => main());