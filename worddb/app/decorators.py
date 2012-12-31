
# decorators.py
# the decorators used by the views of the app

from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf

from functools import wraps

def require_logged(function):
	# requires user to be logged to continue, redirects to '/login' otherwise
	@wraps(function)
	def wrapper(request, *args, **kwargs):
		logged = bool('userid' in request.session.keys())
		if logged: # then continue
			return function(request, *args, **kwargs)
		return redirect('/login')
	return wrapper


def require_not_logged(function):
	# requires user not to be logged to continue, redirects to '/lists' otherwise
	@wraps(function)
	def wrapper(request, *args, **kwargs):
		logged = bool('userid' in request.session.keys())
		if not logged: # then continue
			return function(request, *args, **kwargs)
		return redirect('/lists')
	return wrapper


def require_method(*r_methods):
	
	# requires http method used in the request to be in 'r_methods'
	## returns HttpResponseForbidden("invalid http method used.") otherwise

	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):
			for m in r_methods:
				if request.method == m: break
			else: return HttpResponseForbidden("invalid http method used.")
			return func(request, *args, **kwargs)
		return wrapper

	return decorator


def require_args(*required_args):
	
	# requires http args to be in 'desired_args'

	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):
			request_method = request.method
			if request_method == 'POST': d = request.POST
			elif request_method == 'GET': d = request.GET
			else:
				raise Exception('invalid request_method passed')
			
			for arg in required_args:
				if not arg in d.keys():
					return HttpResponseForbidden("invalid request arguments.")
			return func(request, *args, **kwargs)
		return wrapper

	return decorator

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