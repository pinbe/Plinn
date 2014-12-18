##parameters=

portal_url = context.portal_url()

return [{'id' : 'groups_members',
         'name' : "Manage group's members",
         'url' : portal_url + '/groups_members'},         
        {'id' : 'group_data',
         'name' : "Manage group's datas",
         'url' : portal_url + '/group_data'},
        {'id' : 'portal_members',
         'name' : "Manage portal's members",
         'url' : portal_url + '/portal_members'},
        {'id' : 'portal_all_groups',
         'name' : "Manage portal's groups",
         'url' : portal_url + '/portal_all_groups'}]