
# decorators.py
# the decorators used by the views of the app

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from functools import wraps

def require_login(want_logged=None):

	# if want_logged is True
	## rederer is executed if user is logged, redirect to '/login' otherwise
	# elif want_logged is False
	## rederer is executed if user is not logged, redirect to '/lists' otherwise
	
	if want_logged is None:
		want_logged = True
	# is this way too much defensive programming?
	assert want_logged in (True, False), 'invalid decorator parameter: must be True of False'
	
	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):
			logged = bool('userid' in request.session.keys())
			if logged == want_logged:
				return func(request, *args, **kwargs)
			elif want_logged and not logged:
				return redirect('/login')
			else: # logged and not want_logged
				return redirect('/lists')
		return wrapper

	return decorator


def require_method(*r_methods):
	
	# requires http method used in the request to be in 'r_methods'
	## returns HttpResponseForbidden("invalid http method used.") otherwise

	# make it always iterable, shall we?
	for t in (tuple, list, set):
		if isinstance(r_methods, t): break
	else: r_methods = [r_methods, ]

	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):
			for m in r_methods:
				if request.method == m: break
			else: return HttpResponseForbidden("invalid http method used.")
			return func(request, *args, **kwargs)
		return wrapper

	return decorator


def require_args(desired_method, *desired_args):
	
	# requires http args in 'desired_args' to 

	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):
			if not desired_method: pass # remove this for security sake (?)
			elif request.method != desired_method:
				return HttpResponseForbidden('invalid request method.')
			
			if not desired_method:
				c = request.POST or request.GET
			elif desired_method == 'POST': c = request.POST
			elif desired_method == 'GET': c = request.GET
			else:
				raise HttpResponseForbidden("request method not POST neither GET. is %s, instead." % request.method)
			
			for arg in desired_args:
				if not arg in c.keys():
					return HttpResponseForbidden("invalid request arguments.")
			return func(request, *args, **kwargs)
		return wrapper

	return decorator