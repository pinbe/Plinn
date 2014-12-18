##parameters=

object_url = context.absolute_url()

return [{'id' : 'view_locals_roles',
         'name' : "View local roles",
         'url' : object_url + '/folder_localrole_form'},
        {'id' : 'ar_groups',
         'name' : "Append or remove groups",
         'url' : object_url + '/local_roles_ar_groups'},         
        {'id' : 'group_data',
         'name' : "Append or remove members",
         'url' : object_url + '/local_roles_ar_members'},]