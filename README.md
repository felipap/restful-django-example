A basic REST application using django and ajax. Really CRUD-like.

Django doesn't really support the "RESTful-way" natively.
For example, the data passed to a PUT request isn't stored inside request.PUT
(as one would expect because of request.GET and request.POST). Insted, django
stores it inside request.raw_post_data.

I took my very first django application and applied to it the "RESTful philosophy".
The design looks like crap, the javascript likewise. I have taken a look at few REST
wrappers to django (including [django-piston][1] and [toastdriven][2]), but they all
seemed too ugly or too complex to my specific case.

All the other files beside app.doREST, app.helpers and app.views are mostly unaltered,
so be careful not to wake up the monsters of terrifying programming...

Todo:
-----
* Implement auto variable fetcher for the Handlers views.

  [1]: https://bitbucket.org/jespern/django-piston/wiki/Home "django-piston"
  [2]: https://github.com/toastdriven/django-tastypie "tastypie"
