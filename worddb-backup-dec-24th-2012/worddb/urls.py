
from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

from django.conf.urls.defaults import patterns, include, url

# from app/views.py
urlpatterns = patterns('app.views',    
    url(r'^$', 'login'),
    url(r'^login/$', 'login'),
    url(r'^signin/$', 'signin'),
    url(r'^logout/$', 'logout'),

    url(r'^lists/$', 'listspanel'), # lists panel for the user (template: listspanel.html)
    url(r'^lists/(?P<listname>[\w\d,. -]+)$(?!^lists/api$)', 'listpage'), # list page (template: listpage.html)

    # action in ('add', 'change', 'removes')
    url(r'^api/lists/(?P<action>\w+)$', 'api_lists_redirect'),
    url(r'^api/words/(?P<action>\w+)$', 'api_words_redirect'),


    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),

)

urlpatterns += staticfiles_urlpatterns()

# API Calls
# create new list
## views.add_list => ^lists/api/addlist?label=...
# remove list
## views.remove_list => ^lists/api/removelist?label=...
# add new word
## views.add_word => ^lists/api/addword?list=...&word=... (allow more arguments in the future)
# remove word
## views.remove_word => ^lists/api/removeword?list=...&word=...
