#! /bin/sh

i18nextract --path . --site_zcml /export/zope_instances/jma/etc/site.zcml --domain plinn -o locales

cat locales/plinn.pot locales/plinn-manual.pot > locales/plinn-all.pot
mv locales/plinn-all.pot locales/plinn.pot

msgmerge --update --no-fuzzy-matching locales/fr/LC_MESSAGES/plinn.po locales/plinn.pot
msgmerge --update --no-fuzzy-matching locales/en/LC_MESSAGES/plinn.po locales/plinn.pot
