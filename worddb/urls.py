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

    url(r'^$', 'app.views.login'),
    url(r'^login/$', 'app.views.login'),
    url(r'^signin/$', 'app.views.signin'),
    url(r'^logout/$', 'app.views.logout'),

    url(r'^lists/$', 'app.views.listspanel'),
    url(r'^lists/(?P<listname>[\w\d,. -]+)$(?!^lists/api$)', 'app.views.listpage', name="listpage"),

    url(r'^lists/api/add_list', 'app.views.add_list'),
    url(r'^lists/api/change_list', 'app.views.change_list'),
    url(r'^lists/api/remove_list', 'app.views.remove_list'),


    url(r'^lists/api/add_word$', 'app.views.add_word'),
    url(r'^lists/api/change_word', 'app.views.change_word'),
    url(r'^lists/api/remove_word$', 'app.views.remove_word'),
)

# implement:
# rename of lists, rename of words

# PAGES
# the panel of lists (template: listspanel.html)
## views.listspanel => ^lists/$
# the page of a list (template: listpage.html)
## views.listpage => ^lists/<listname>$

# API Calls
# create new list
## views.add_list => ^lists/api/addlist?label=...
# remove list
## views.remove_list => ^lists/api/removelist?label=...
# add new word
## views.add_word => ^lists/api/addword?list=...&word=... (allow more arguments in the future)
# remove word
## views.remove_word => ^lists/api/removeword?list=...&word=...
