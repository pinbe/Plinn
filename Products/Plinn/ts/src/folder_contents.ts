import {DDFolderUploader, DropTarget, FolderDDropControler, loadListing} from "./components/folder";
import {absolute_url} from "./components/utils";

function main() {
    const firsItemPosElement = document.getElementById('FirstItemPos');
    const listing = <HTMLTableSectionElement>document.getElementById("FolderListingBody");
    const orderable = firsItemPosElement ? true : false;
    const firstItemPos = orderable ? parseInt(firsItemPosElement.innerHTML, 10) : 1;
    const fDDcontroler = new FolderDDropControler(listing, orderable, firstItemPos);
    let topNavBatchBar, bottomNavBatchBar;
    if (orderable) {
        topNavBatchBar = document.getElementById("topNavBatchBar");
        bottomNavBatchBar = document.getElementById("bottomNavBatchBar");
        if (topNavBatchBar && bottomNavBatchBar) {
            new DropTarget(topNavBatchBar, fDDcontroler);
            new DropTarget(bottomNavBatchBar, fDDcontroler);
        }
    }
    document.getElementById("FolderListingHeader")
        .addEventListener("click", loadListing);
    if (topNavBatchBar && bottomNavBatchBar) {
        topNavBatchBar.addEventListener("click", loadListing);
        bottomNavBatchBar.addEventListener("click", loadListing);
    }

    if (listing.getAttribute('data-items_add_allowed') === '1') {
        const uploadUrl = absolute_url() + '/put_upload';
        new DDFolderUploader(
            document.getElementById('content-outer'),
            uploadUrl,
            <HTMLTableSectionElement>document.getElementById("FolderListingBody"));

    }
}

main();