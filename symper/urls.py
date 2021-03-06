from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static
from comparisons import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = patterns('',
        url(r'^init/$', views.InitView.as_view(), name='init'),
	#url(r'^inittasks/$', views.InitTasksView.as_view(), name='init2'),
	#url(r'^initsets/$', views.InitTaskSetView.as_view(), name='init3'),
	url(r'^intro/$', views.IntroView.as_view(), name='intro'),
	url(r'^task/$', views.TaskView.as_view(), name='task'),
	url(r'^end/$', views.EndView.as_view(), name='end'),
	url(r'^demo/$',views.DemographicsView.as_view(), name='demo'),
	#url(r'^groupgroup/$', views.ResultsView.as_view(), name='results'),
	#url(r'^fdresults/$', views.FDResultsView.as_view(), name='fd_results'),
	#url(r'^reflresults/$', views.ReflResultsView.as_view(), name='refl_results'),
	#url(r'^rotresults/$', views.RotResultsView.as_view(), name='rot_results'),
	url(r'^results/$', views.ResultsView.as_view(), name='all_results'),
	url(r'^break/$', views.BreakView.as_view(), name='break'),
#	url(r'^media/', None)
	url(r'^validate/$', views.ValidationView.as_view(), name='validate'),
)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
