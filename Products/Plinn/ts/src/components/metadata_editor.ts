import {InspectorPalette} from "./palette";
import {FragmentImporter} from "./fragment_importer";
import {absolute_url} from "./utils";
import {FormManager} from "./form_manager";

export class MetadataEditManager {
    private readonly wrapper: HTMLElement;

    constructor(wrapper: HTMLElement) {
        this.wrapper = wrapper;
        const paletteMain = wrapper.querySelector('.main');
        const inspector = new InspectorPalette(wrapper);

        inspector.onExpand = () => {
            const fi = new FragmentImporter(absolute_url());

            fi.onAfterPopulate = () => {
                const form = paletteMain.querySelector('form');
                const fm = new FormManager(form);
                fm.onResponseLoad = function () {
                    inspector.toggle();
                };
            };

            fi.useMacro('header_widgets', 'titleAndDescForm', `#${this.wrapper.id} .main`);
        };

        inspector.onCollapse = () => {
            const fi = new FragmentImporter(absolute_url());
            fi.useMacro('header_widgets', 'viewTitleAndDesc', `#${this.wrapper.id} .main`);
        };
    }
}