// (c) Benoît PIN 2006-2007
// http://plinn.org
// Licence GPL
// 
// 


function initHeaderScript() {
    var toggleButton = document.getElementById("ToggleFormButton");
    if(!toggleButton) return;
    var ob_url = absolute_url();
    var metadataInspector = new InspectorPalette(portal_url(),
        document.getElementById("ToggleFormButton").childNodes[0],
        document.getElementById("HeaderArea"));

    metadataInspector.onExpand = function(inspector) {
        var onAfterPopulate = function() {
            // init simple metadata form manager
            var metadataForm = inspector.contentNode.getElementsByTagName('FORM')[0];
            var fm = new FormManager(metadataForm);
            fm.onResponseLoad = function() {
                inspector.collapse();
            };

            // init event handler to show full metadata form
            var showFullMetadataForm = function(evt) {
                disableDefault(evt);
                disablePropagation(evt);

                var initFullMetadataForm = function() {
                    var metadataForm = inspector.contentNode.getElementsByTagName('FORM')[0];
                    var fm = new FormManager(metadataForm);
                    fm.onResponseLoad = function() {
                        inspector.collapse();
                    };

                    addListener(document.getElementById('showSimpleMetadataForm'),
                        'click',
                        function(evt) {
                            inspector.expand();
                            disableDefault(evt);
                            disablePropagation(evt);
                        });
                };
                var fi = new FragmentImporter(absolute_url(), initFullMetadataForm);
                fi.useMacro('header_widgets', 'fullMetadataForm', 'HeaderArea');
            };
            addListener(document.getElementById('showFullMetadataForm'), 'click', showFullMetadataForm);
        };
        var fi = new FragmentImporter(ob_url, onAfterPopulate);
        fi.useMacro('header_widgets', 'titleAndDescForm', 'HeaderArea');
    };

    metadataInspector.onCollapse = function(inspector) {
        var fi = new FragmentImporter(ob_url);
        fi.useMacro('header_widgets', 'viewTitleAndDesc', 'HeaderArea');
    };
}


function MetadataDateManager(baseFieldName, defaultDate) {
    var thisManager = this;
    this.baseFieldName = baseFieldName;
    this.defaultDate = defaultDate;
    this._previousDate = new Date();

    var calConfig = [];
    // setup js calendar
    calConfig["inputField"] = baseFieldName;		// id of the input field
    calConfig["ifFormat"] = "%Y %m %d %H %M";   // format of the input field
    calConfig["date"] = function() {
        return thisManager.builDateFromInputs();
    };
    calConfig["showsTime"] = true;               // will display a time selector
    calConfig["button"] = "show_" + baseFieldName + "_cal";     // trigger for the calendar (button ID)
    calConfig["singleClick"] = false;              // double-click mode
    calConfig["showOthers"] = true;               // show overlapping months
    calConfig["weekNumbers"] = false;
    calConfig["firstDay"] = 1;
    calConfig["onSelect"] = thisManager.splitDate;

    Calendar.setup(calConfig);

    //init event listener on checkbox
    var cb = document.getElementById(baseFieldName + "_cb");
    if(cb) {
        addListener(cb, 'click', function() {
            thisManager.toggleDisplay();
        });
        if(this.builDateFromInputs().valueOf() == this.defaultDate.valueOf()) {
            document.getElementById(baseFieldName + "_fields").style.display = "none";
            cb.checked = true;
        }
    }
}

MetadataDateManager.prototype.builDateFromInputs = function() {
    var baseFieldName = this.baseFieldName;
    var year = document.getElementById(baseFieldName + "_year").value;
    var month = document.getElementById(baseFieldName + "_month").value;
    var day = document.getElementById(baseFieldName + "_day").value;
    var hour = document.getElementById(baseFieldName + "_hour").value;
    var minute = document.getElementById(baseFieldName + "_minute").value;

    if((year && month && day && hour && minute) != "") {
        var dateStr = month + "/" + day + "/" + year + " " + hour + ":" + minute + ":00";
        return new Date(dateStr);
    }
    else
        return new Date();
};

MetadataDateManager.prototype.splitDate = function(calendar, date) {
    var inputId = (typeof calendar == "string") ? this.baseFieldName : calendar.params['inputField'].id;

    var tokens;
    if(typeof date == "object") {
        tokens = new Array(5);
        tokens[0] = String(date.getFullYear());
        var month = date.getMonth() + 1;
        tokens[1] = (month < 10) ? "0" + String(month) : String(month);
        var day = date.getDate()
        tokens[2] = (day < 10) ? "0" + String(day) : String(day);
        var hours = date.getHours();
        tokens[3] = (hours < 10) ? "0" + String(hours) : String(hours);
        var minutes = date.getMinutes();
        tokens[4] = (minutes < 10) ? "0" + String(minutes) : String(minutes);
    }
    else
        tokens = date.split(" ");

    document.getElementById(inputId + "_year").value = tokens[0];
    document.getElementById(inputId + "_month").value = tokens[1];
    document.getElementById(inputId + "_day").value = tokens[2];
    document.getElementById(inputId + "_hour").value = tokens[3];
    document.getElementById(inputId + "_minute").value = tokens[4];
};


MetadataDateManager.prototype.toggleDisplay = function() {
    var cb = document.getElementById(this.baseFieldName + '_cb');
    var fields = document.getElementById(this.baseFieldName + '_fields');
    if(cb.checked) {
        fields.style.display = "none";
        this._previousDate = this.builDateFromInputs();
        this.splitDate('', this.defaultDate)
    }
    else {
        this.splitDate('', this._previousDate);
        fields.style.display = "block";
    }
};