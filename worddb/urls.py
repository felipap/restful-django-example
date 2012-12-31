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

    # remove
    # url(r'^lists/$', 'listspanel'), # lists panel for the user (template: listspanel.html)
    # url(r'^lists/(?P<listname>[\w\d,. -]+)$(?!^lists/api$)', 'listpage'), # list page (template: listpage.html)

    # action in ('add', 'change', 'removes')
    # url(r'^api/lists/(?P<action>\w+)$', 'api_lists_redirect'),
    # url(r'^api/words/(?P<action>\w+)$', 'api_words_redirect'),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
)

from app import views
from app.views import ListHandler, WordHandler

urlpatterns += patterns('',
    url(r'^lists/(?P<list_id>[\w\d,. -]+)?$', ListHandler()),
    url(r'^lists/(?P<list_id>[\w\d,. -]+)/words/(?P<word_id>[\w\d,. -]+)?$', WordHandler()),
#        serveREST({'GET': views.listspanel, 'POST': views.add_list})),
#    url(r'^lists/(?P<list_id>[\w\d,. -]+)$',
#        serveREST({'GET': views.listpage, 'PUT': views.change_list, 'DELETE': views.remove_list})),

   # url(r'^lists/(?P<list_id>[\w\d,. -]+)/words',
     #   serveREST({'POST': views.add_word})),
    # url(r'^lists/(?P<listname>[\w\d,. -]+)/words/', )
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
