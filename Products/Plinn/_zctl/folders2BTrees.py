# -*- coding: utf-8 -*-
from argparse import ArgumentParser
import os.path
from Acquisition import aq_base
from zope.site.hooks import setSite
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
import transaction
from OFS.interfaces import IObjectManager
from zope.interface import providedBy
from Products.Plinn.Folder import PlinnFolder
from Products.Plinn.HugePlinnFolder import HugePlinnFolder
from Products.Plinn.migration.folder import migrateFolder

def recurseMigrateFolders(parent) :
    for child in parent.objectValues() :
        if IObjectManager.providedBy(child) :
            recurseMigrateFolders(child)
            if isinstance(child, PlinnFolder) and \
               not isinstance(child, HugePlinnFolder) :
                migrated = migrateFolder(child, parent)
                # pseudo _finishContrsuction to preserve dates.
                migrated._setPortalTypeName('Huge Plinn Folder')
                migrated.reindexObject()
                




parser = ArgumentParser(description="Convert all regular Plinn Folder to Huge Plinn Folder")
parser.add_argument('portal_path')
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()
portal = app.unrestrictedTraverse(args.portal_path)
setSite(portal)

recurseMigrateFolders(portal)

if not args.dry_run :
    transaction.commit()