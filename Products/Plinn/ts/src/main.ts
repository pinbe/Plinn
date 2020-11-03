import * as $ from "jquery";
import {init as main_template_misc_init} from "./components/main_template_misc";
import {SitePanel} from "./components/site_panel";
import {TreeMaker} from "./components/tree";


function main() {
    main_template_misc_init();
    new SitePanel('#site-edit-panel', '#body-wrapper');
    new TreeMaker('#site-edit-panel .tree-view');
}

$(() => main());
