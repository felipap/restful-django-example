# -*- coding: utf8 -*-

# Django stuff
from django.http import Http404
from django.shortcuts import get_object_or_404

# Project stuff
from app.models import User


def get_user_or_404(request):
	""" Attempt to get the user object or redirect to logout. """
	try:
		return User.objects.get(id=request.session['userid'])
	except (User.DoesNotExist, KeyError):
		# logger.warning("User %s not found. Redirecting ip %s to logout." % (request.session.get('userid'), request.META['REMOTE_ADDR']))
		raise Http404, "User not found"


def get_object_or_json404(*args, **kwargs):
	"""
	Uses get_object_or_404() to get an object or returns an 404 as Json.
	It's safer to catch the exception than to copy their code from django.shortcuts.
	"""

	try:
		return get_object_or_404(*args, **kwargs)
	except Http404:
		return Json404


## CUSTOM EXCEPTIONS

class BadProgramming (Exception):
	""" Do use it. """


class Json404(Exception):   
	"""
	Returns 404 as Json data.
	This is catched by the CustomMiddleware.
	"""


class RaisableRedirect(Exception):
	"""
	Redirects to a given url when raised.
	This is catched by the CustomMiddleware.
	Not pythonic or wtever? No fucks given.
	Usage: "raise RaisableRedirect('/logout')"
	"""

	def __init__(self, url):
		try:
			reverse(url)
		except NoReverseMatch:
			raise BadProgramming, "The given url is not reversible."
		else:
			self.url = url


class CustomMiddleware(object):
	""" Custom middleware to catch custom exceptions by the application. """

	def process_exception(self, request, exception):
		if isinstance(exception, Json404):
			return HttpResponse("{404, tá?}")
		elif isinstance(exception, RaisableRedirect):
			return redirect(exception.url)


### 
# source: https://bitbucket.org/offline/django-annoying/src/tip/annoying/decorators.py
def render_to(template=None, mimetype=None):
    """
    Decorator for Django views that sends returned dict to render_to_response 
    function.

    Template name can be decorator parameter or TEMPLATE item in returned 
    dictionary.  RequestContext always added as context instance.
    If view doesn't return dict then decorator simply returns output.

    Parameters:
     - template: template name to use
     - mimetype: content type to send in response headers

    Examples:
    # 1. Template name in decorator parameters

    @render_to('template.html')
    def foo(request):
        bar = Bar.object.all()  
        return {'bar': bar}

    # equals to 
    def foo(request):
        bar = Bar.object.all()  
        return render_to_response('template.html', 
                                  {'bar': bar}, 
                                  context_instance=RequestContext(request))


    # 2. Template name as TEMPLATE item value in return dictionary.
         if TEMPLATE is given then its value will have higher priority 
         than render_to argument.

    @render_to()
    def foo(request, category):
        template_name = '%s.html' % category
        return {'bar': bar, 'TEMPLATE': template_name}
    
    #equals to
    def foo(request, category):
        template_name = '%s.html' % category
        return render_to_response(template_name, 
                                  {'bar': bar}, 
                                  context_instance=RequestContext(request))

    """
    def renderer(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            tmpl = output.pop('TEMPLATE', template)

            # custom addition of csrf_token on every page!
            
            if not 'csrf_token' in output:
	            output['csrf_token'] = csrf(request)['csrf_token']
            
            return render_to_response(tmpl, output, \
                        context_instance=RequestContext(request), mimetype=mimetype)
        return wrapper
    return renderer