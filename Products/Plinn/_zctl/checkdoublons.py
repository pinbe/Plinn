# -*- coding: utf-8 -*-
import os
import re
from argparse import ArgumentParser


def main(basefolder, pattern) :
    if not os.path.exists(basefolder) :
        raise SystemExit("Dossier manquant : « %s »" % basefolder)

    fichiers = {}
    for root, dirs, files in os.walk(basefolder) :
        for file in files :
            if fichiers.has_key(file) :
                fichiers[file].append(root)
            else:
                fichiers[file] = [root]

    flt = re.compile(pattern).match if pattern else lambda _ : True
    for name, paths in fichiers.items() :
        if not flt(name) :
            continue
        if len(paths) > 1 :
            print name
            print '\n'.join(paths)
            print '-'*80


if __name__ == '__main__':
    parser = ArgumentParser("De quoi chercher les fichiers en doublons")
    parser.add_argument('basefolder')
    parser.add_argument('--pattern')
    args = parser.parse_args()
    main(args.basefolder, args.pattern)