from Products.CMFCore.FSPropertiesObject import FSPropertiesObject
from argparse import ArgumentParser
import json


def main(inputfile, outputfile) :
    fsprops = FSPropertiesObject('base_properties', inputfile)

    with open(outputfile, 'w') as f :
        print >> f, 'export const %s =' % fsprops.getId()
        print >> f, json.dumps(dict(fsprops.propertyItems()), indent=2)
        print >> f, ';'


if __name__ == '__main__':
    parser = ArgumentParser("Property manager sheet to javascript")
    parser.add_argument('inputfile')
    parser.add_argument('outputfile')
    args = parser.parse_args()
    main(args.inputfile, args.outputfile)
