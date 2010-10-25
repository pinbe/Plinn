##parameters=size

ko = 1
unitIndex=0
units = ['o', 'Ko', 'Mo', 'Go']
while float(size) / ko >= 1024 :
	ko = ko * 1024
	unitIndex = unitIndex + 1
	
return {'value' : round(float(size)/ko, 2), 'unit' : units[unitIndex]}