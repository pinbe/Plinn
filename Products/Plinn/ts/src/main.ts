import * as $ from "jquery";
import {init as main_template_misc_init} from "./components/main_template_misc";
import {SitePanel} from "./components/site_panel";
import {TreeMaker} from "./components/tree";
import {SearchForm} from "./components/search";


function main() {
    main_template_misc_init();

    const siteEditePanel = document.querySelector<HTMLDivElement>('#site-edit-panel');
    const bodyWrapper = document.querySelector<HTMLDivElement>('#body-wrapper');
    if (siteEditePanel && bodyWrapper)
        new SitePanel(siteEditePanel, bodyWrapper);

    const treeRootWrapper = document.querySelector<HTMLDivElement>('#site-edit-panel .tree-view');
    if (treeRootWrapper)
        new TreeMaker(treeRootWrapper);

    const mainSearchField = document.querySelector('#top-row .searchfield-wrapper');
    if (mainSearchField)
        new SearchForm(<HTMLFormElement>mainSearchField.parentElement);
}

$(() => main());
