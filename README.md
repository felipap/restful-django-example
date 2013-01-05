A very simple REST application using django and ajax. Really CRUD-like.

Django doesn't really support the "RESTful way" natively.
For example, data passed to a PUT request isn't stored inside request.PUT
(as one would expect because of request.GET and request.POST). Insted, django
stores it inside request.raw_post_data.

This project is an example of a custom REST interface in django, therefore not
intended to be used as a independent wrapper. The application logic is inside
app.views, app.helpers and app.doREST.

'templates/function.js' is responsible for a great deal of the app inner workings;
specially since I tried to use django-template as little as possible. As I see it,
the best approach to CRUD applications is moving the template engines towards the
client-side.

I took my very first django application and applied to it the "RESTful philosophy".
The design looks like crap, the javascript likewise. I have taken a look at few REST
wrappers to django (including [django-piston][1] and [toastdriven][2]), but they all
seemed too ugly or too complex to my specific case.

In a way, this was simply rewriting django's native class based views RESTfully.

I used [jQuery][3] and [Bootstrap][4].

Todo:
-----
* Implement auto variable fetcher for the Handlers views.

  [1]: https://bitbucket.org/jespern/django-piston/wiki/Home "django-piston"
  [2]: https://github.com/toastdriven/django-tastypie "tastypie"
  [3]: http://twitter.github.com/bootstrap
  [4]: http://jquery.com/
