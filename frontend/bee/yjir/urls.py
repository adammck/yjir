from django.conf.urls.defaults import *
#from django.views.generic.create_update import *

from bee.yjir.models import *
from bee.yjir.views import *

urlpatterns = patterns("",
	
	# incomming message test
	url(r'^backend-test$', backend_test, name="test"),
	
	# web api (http post to it!)
	url(r'api/(?P<scope_name>\w+)/(?P<keyword_name>\w+)', api, name="api"),
	
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

