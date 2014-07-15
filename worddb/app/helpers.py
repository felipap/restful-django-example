# -*- coding: utf8 -*-
# for github.com/f03lipe

# Python stuff
from functools import wraps

# Django stuff
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
import json
from django.core.serializers import serialize 

# Project stuff
from worddb.app.models import User


## HELPERS

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
		raise Json404({'successs': False, 'errors': ['This object was not found.']})


def toJson(*set):
	_data = json.loads(serialize('json', set))
	print set, _data
	data = []
	for obj in _data:
		obj['fields'].update({'id': obj['pk']})
		data.append(obj['fields'])
	return json.dumps(data)


## CUSTOM EXCEPTIONS

class BadProgramming (Exception):
	""" Do use it. """


class Json404(Exception):
	"""
	Returns 404 as Json data.
	This is catched by the CustomMiddleware.
	"""

	def __init__(self, object):
		if object is None:
			object = {'success': False, 'status': 404}
		self.object = object
		# super(self, Json404).__init__(message)

	def __str__(self):
		return "<Json404 %s>" % self.object


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

#! redirection occuring?
class CustomMiddleware(object):
	""" Custom middleware to catch custom exceptions by the application. """

	def process_exception(self, request, exception):
		import worddb.app.helpers
		print exception, type(exception)
		if isinstance(exception, worddb.app.helpers.Json404):
			print exception.object
			return HttpResponse(json.dumps(exception.object), content_type='application/json', status=404)
		elif isinstance(exception, RaisableRedirect):
			return redirect(exception.url)


### Decorators for rendering

def renderJSON(func):
	"""
	Decorator to a view. Renders an object as json as returns as HttpResponse.
	"""
	def wrapper(*args, **kwargs):
		return HttpResponse(
			json.dumps(func(*args, **kwargs)),
			content_type="application/json")
	return wrapper


def renderHTML(template=None, content_type=None):
	# source: https://bitbucket.org/offline/django-annoying/src/tip/annoying/decorators.py
	"""
	Decorator for Django views that sends returned dict to render_to_response 
	function.

	Template name can be decorator parameter or TEMPLATE item in returned 
	dictionary.  RequestContext always added as context instance.
	If view doesn't return dict then decorator simply returns output.

	Parameters:
	 - template: template name to use
	 - content_type: content type to send in response headers

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
						context_instance=RequestContext(request), content_type=content_type)
		return wrapper
	return renderer