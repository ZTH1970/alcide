from django.conf.urls import url, patterns

import views

urlpatterns = patterns('',
            url(r'^test$', views.test, name='agenda'),
            )
