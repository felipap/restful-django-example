from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'worddb.views.home', name='home'),
    # url(r'^worddb/', include('worddb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

# from app/views.py
urlpatterns += patterns('app.views', 
    
    url(r'^$', 'login'),
    url(r'^login/$', 'login'),
    url(r'^signin/$', 'signin'),
    url(r'^logout/$', 'logout'),

    url(r'^lists/$', 'listspanel'), # lists panel for the user (template: listspanel.html)
    url(r'^lists/(?P<listname>[\w\d,. -]+)$(?!^lists/api$)', 'listpage'), # list page (template: listpage.html)

    # action in ('add', 'change', 'removes')
    url(r'^api/lists/(?P<action>\w+)$', 'api_lists_redirect'),
    url(r'^api/words/(?P<action>\w+)$', 'api_words_redirect'),
)

# API Calls
# create new list
## views.add_list => ^lists/api/addlist?label=...
# remove list
## views.remove_list => ^lists/api/removelist?label=...
# add new word
## views.add_word => ^lists/api/addword?list=...&word=... (allow more arguments in the future)
# remove word
## views.remove_word => ^lists/api/removeword?list=...&word=...
