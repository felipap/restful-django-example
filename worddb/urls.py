# -*- coding: utf8 -*-

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib import admin
admin.autodiscover()

# from app/views.py
urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': 'login/'}),
    url(r'^login/$', 'app.views.login'),
    url(r'^signin/$', 'app.views.signin'),
    url(r'^logout/$', 'app.views.logout'),

#    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
)

from app import views
from app.views import ListHandler, WordHandler

REGEX_VARS = {
    'list_id': '[\w\d,. -]+',
    'word_id': '[\w\d,. -]+'
}

urlpatterns += patterns('',
    url(r'^lists/(?P<list_id>{list_id})?$'.format(**REGEX_VARS),
        ListHandler()),
    url(r'^lists/(?P<list_id>{list_id})/words/(?P<word_id>{word_id})?$'.format(**REGEX_VARS),
        WordHandler()),
)

urlpatterns += staticfiles_urlpatterns()

# GET /users: Uma lista com todos os usuários;
# POST /users: Cria um usuário;
# GET /users/<id>: Visualização dos detalhes de um usuário;
# PUT /users/<id>: Atualiza os dados de um usuário;
# DELETE /users/<id>: Apaga um usuário.

# API Calls
# create new list
## views.add_list => ^lists/api/addlist?label=...
# remove list
## views.remove_list => ^lists/api/removelist?label=...
# add new word
## views.add_word => ^lists/api/addword?list=...&word=... (allow more arguments in the future)
# remove word
## views.remove_word => ^lists/api/removeword?list=...&word=...
