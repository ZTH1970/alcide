from django.conf.urls import patterns, url, include
from calebasse.ressources.urls import ressource_patterns


user_patterns = patterns('calebasse.personnes.views',
    url(r'^$', 'user_listing'),
    url(r'^new/$', 'user_new'),
    url(r'^(?P<pk>\d+)/$', 'user_update'),
    url(r'^(?P<pk>\d+)/delete/$', 'user_delete'),
    url(r'^(?P<pk>\d+)/activate/$', 'user_activate'),
)

holiday_actions_paterns = patterns('calebasse.personnes.views',
    url(r'^$', 'worker_holidays_update', name = 'worker-holidays-update'),
    url(r'^(?P<pk>\d+)/editer/?$', 'edit_holiday', name = 'edit_holiday'),
    url(r'^(?P<pk>\d+)/supprimer/?$', 'delete_holiday', name = 'delete_holiday'),
    url(r'^ajouter/?$', 'create_holiday', name = 'create_holiday')
)

worker_patterns = patterns('calebasse.personnes.views',
    url(r'^$', 'worker_listing'),
    url(r'^new/$', 'worker_new'),
    url(r'^(?P<pk>\d+)/$', 'worker_update', name='worker_update'),
    url(r'^(?P<pk>\d+)/delete/$', 'worker_delete'),
    url(r'^(?P<pk>\d+)/(?P<weekday>\d)/$', 'worker_schedule_update'),
    url(r'^(?P<worker_pk>\d+)/holidays/', include(holiday_actions_paterns)),
)

holidays_patterns = patterns('calebasse.personnes.views',
    url(r'^$', 'holiday_listing'),
    # url(r'^groupe/$', 'group_holiday_update',
    #     name='group-holiday-update'),
    url(r'^groupe/$', 'group_holidays', name = 'group-holidays'),
    url(r'^groupe/ajouter/?$', 'create_group_holiday', name = 'create-group-holiday'),
    url(r'^groupe/(?P<pk>\d+)/editer/?$', 'edit_group_holiday', name = 'edit-group-holiday'),
    url(r'^groupe/(?P<pk>\d+)/supprimer/?$', 'delete_group_holiday', name = 'delete-group-holiday'),
    )

urlpatterns = patterns('calebasse.personnes.views',
    url(r'^$', 'homepage'),
    url(r'^acces/', include(user_patterns)),
    url(r'^gestion/', include(worker_patterns)),
    url(r'^conges/', include(holidays_patterns)),
    url(r'^(?P<model_name>[a-z-]*)/', include(ressource_patterns)),
    )
