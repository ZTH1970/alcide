from django.conf.urls import patterns, url, include

act_patterns = patterns('calebasse.actes.views',
        url(r'^$', 'act_listing', name='act-listing'),
)

urlpatterns = patterns('calebasse.actes.views',
        url(r'^$', 'redirect_today'),
        url(r'^(?P<date>[^/]*)/', include(act_patterns))
)
