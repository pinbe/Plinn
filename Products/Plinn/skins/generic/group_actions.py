##parameters=

portal_url = context.portal_url()
actions = [
    {'id' : 'portal_members',
     'title' : "Manage portal's members",
     'url' : portal_url + '/portal_members'},
    {'id' : 'groups_members',
     'title' : "Manage group's members",
     'url' : portal_url + '/groups_members'},
    {'id' : 'group_data',
     'title' : "Manage group's datas",
     'url' : portal_url + '/group_data'},
    {'id' : 'portal_all_groups',
     'title' : "Manage portal's groups",
     'url' : portal_url + '/portal_all_groups'}]
return actions