A very simple REST application using django and ajax. Really CRUD-like.

Django, natively, makes it hard to implement a RESTful application (it doesn't even
handle data passed in PUT/DELETE requests as it does in GET/POST ones). This project
is just an example of a basic "problem-specific" RESTful interface to django.

I took my very first crappy django project, a manager to organize lists of words in
english, and re-implemented it following RESTs principles. The application logic is
inside app.views, app.doREST and app.helpers. The javascript, 'wordb/static/function.js',
is responsible for the interface dynamics (including most of the templating work).

I've taken a look at other REST wrappers to django (including [django-piston][1] and 
[toastdriven][2]), but they all seemed either too ugly or too complex to this little,
useless application. In a way, this was simply rewrote django's class-based-views with
a REST api in mind.

Todo:
-----
* Implement auto variable fetcher for the Handlers views.

  [1]: https://bitbucket.org/jespern/django-piston/wiki/Home "django-piston"
  [2]: https://github.com/toastdriven/django-tastypie "tastypie"
