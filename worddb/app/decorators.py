
# decorators.py
# the decorators used by the views of the app

from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from functools import wraps

def require_login(want_logged=True):

	# if want_logged is True
	## rederer is executed if user is logged, redirect to '/login' otherwise
	# elif want_logged is False
	## rederer is executed if user is not logged, redirect to '/lists' otherwise
	
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
			request_method = request.META['REQUEST_METHOD']
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