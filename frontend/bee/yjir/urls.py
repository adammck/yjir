from django.conf.urls.defaults import *
#from django.views.generic.create_update import *

from bee.yjir.models import *
from bee.yjir.views import *

urlpatterns = patterns("",
    
	# users
	(r'^users/$', view_users),
	(r'^users/add$', add_user),
	(r'^users/(?P<user_id>\w+)/edit$', edit_user),
	
    # scopes
    url(r'^add$',                      add_scope,  name="add-scope"),
    url(r'^(?P<scope_name>\w+)/edit$', edit_scope, name="edit-scope"),
    url(r'^(?P<scope_name>\w+)$',      dashboard,  name="view-scope"),
    
    # keywords
	url(r'^(?P<scope_name>\w+)/add$',                        add_keyword,  name="add-keyword"),
	url(r'^(?P<scope_name>\w+)/(?P<keyword_name>\w+)/edit$', edit_keyword, name="edit-keyword"),
	url(r'^(?P<scope_name>\w+)/(?P<keyword_name>\w+)$',      dashboard,    name="view-keyword"),
	
	# actions
	url(r'^(?P<scope_name>\w+)/(?P<keyword_name>\w+)/add$',                     add_action,  name="add-action"),
	url(r'^(?P<scope_name>\w+)/(?P<keyword_name>\w+)/(?P<action_id>\d+)/edit$', edit_action, name="edit-action"),
	url(r'^(?P<scope_name>\w+)/(?P<keyword_name>\w+)/(?P<action_id>\d+)$',      dashboard,   name="view-action"),
	
    # display views
    (r'^$', dashboard)
)

