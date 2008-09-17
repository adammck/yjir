from django.conf.urls.defaults import *
from django.views.generic.simple import *
from django.conf import settings

urlpatterns = patterns("",
	(r'^$', redirect_to, {"url": "/yjir/"}),
	(r'^yjir/', include("bee.yjir.urls")),
)

# only serve static files in debug mode,
# to make sure we don't forget to set it
# up properly (via apache) in production
if settings.DEBUG:
	urlpatterns += patterns("",
		(r'^static/(?P<path>.*)$',
		"django.views.static.serve",
#		{"document_root": "/home/adammck/Projects/Unicef/yjir/frontend/bee/static"})
		{"document_root": "/home/adam/yjir2/frontend/bee/static"})
	)

