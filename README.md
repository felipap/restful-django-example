A RESTful Django
================

A sample REST application using django and ajax.


Natively, Django makes it hard to implement a REST app. It doesn't even handle data passed to PUT/DELETE requests the same way it does with GET/POST. The projcet is just an example of a specific RESTful interface to be used with django.

I took a django project (a manager to organize lists of words in english), and re-implemented it following REST. The logic is inside app.views, app.doREST and app.helpers. The javascript, 'wordb/static/function.js', is responsible for the interface dynamics (including most of the templating work).

I chose not to use backbonejs or any client-side frameworks like that, but adding should be easy enough. For now, data is stored in the DOM (ugly, right?), using HTML5 datasets.

I've taken a look at other REST wrappers to django (such as [django-piston][1] and [toastdriven][2]), but they seemed  overly-complex for this minimalistic app. I simply re-wrote django's class-based-views with a REST api in mind.

Todo:
-----
* Implement an object fetcher for subclasses of RESTHandler in app.views.

  [1]: https://bitbucket.org/jespern/django-piston/wiki/Home "django-piston"
  [2]: https://github.com/toastdriven/django-tastypie "tastypie"
  
-----
