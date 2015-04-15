#! /bin/sh

if [ !$1 ]; then
    ZCML=$INSTANCE_HOME/etc/site.zcml
else
    ZCML=$1
fi

i18nextract --path . --site_zcml $ZCML --domain plinn -o locales

cat locales/plinn-manual.pot >> locales/plinn.pot

msgmerge --update --no-fuzzy-matching locales/fr/LC_MESSAGES/plinn.po locales/plinn.pot
msgmerge --update --no-fuzzy-matching locales/en/LC_MESSAGES/plinn.po locales/plinn.pot
