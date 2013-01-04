# -*- coding: utf8 -*-
# for github.com/f03lipe

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url
# from django.contrib import admin
# admin.autodiscover()

from app.views import ListHandler, WordHandler, LoginHandler, SignInHandler, logout

REGEX_VARS = {
    'list_id': '[\w\d,. -]+',
    'word_id': '[\w\d,. -]+'
}

urlpatterns = patterns('',
    url(r'^$',
        'django.views.generic.simple.redirect_to', {'url': 'login/'}),
    url(r'^signin/$',
        SignInHandler()),
    url(r'^login/$',
        LoginHandler()),
    url(r'^logout/$',
        logout),
    url(r'^lists/(?P<list_id>{list_id})?$'.format(**REGEX_VARS),
        ListHandler()),
    url(r'^lists/(?P<list_id>{list_id})/words/(?P<word_id>{word_id})?$'.format(**REGEX_VARS),
        WordHandler()),
)

urlpatterns += staticfiles_urlpatterns()