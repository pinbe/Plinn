// (c) Benoît PIN 2006-2007
// http://plinn.org
// Licence GPL


function initEventJsCalendars() {
	var startDate = [];
	
	// setup startDate calendar
	startDate["inputField"]		=	"startDate";		// id of the input field
	startDate["ifFormat"]		=	"%Y %m %d %H %M";   // format of the input field	startDate["date"]			=	function() { return builDateFromInputs("startDate"); };	startDate["showsTime"]		=	true;               // will display a time selector	startDate["button"]			=	"showStartCal";     // trigger for the calendar (button ID)	startDate["singleClick"]	=	false;              // double-click mode	startDate["showOthers"]		=	true;               // show overlapping months	startDate["weekNumbers"]	=	false;	startDate["firstDay"]		=	1;	startDate["onSelect"]		=	splitDate;

	Calendar.setup(startDate);
	
	var endDate = [];
	
	// setup endDate calendar
	endDate["inputField"]	=	"endDate";		// id of the input field
	endDate["ifFormat"]		=	"%Y %m %d %H %M";   // format of the input field	endDate["date"]			=	function() { return builDateFromInputs("endDate"); };	endDate["showsTime"]	=	true;               // will display a time selector	endDate["button"]		=	"showEndCal";     // trigger for the calendar (button ID)	endDate["singleClick"]	=	false;              // double-click mode	endDate["showOthers"]	=	true;               // show overlapping months	endDate["weekNumbers"]	=	false;	endDate["firstDay"]		=	1;	endDate["onSelect"]		=	splitDate;

	Calendar.setup(endDate);
}