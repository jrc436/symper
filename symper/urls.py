from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static
from comparisons import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = patterns('',
        url(r'^init/$', views.InitView.as_view(), name='init'),
	url(r'^intro/$', views.IntroView.as_view(), name='intro'),
	url(r'^task/$', views.TaskView.as_view(), name='task'),
	url(r'^end/$', views.EndView.as_view(), name='end'),
#	url(r'^images/$', None),
#	url(r'^media/', None)
)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
