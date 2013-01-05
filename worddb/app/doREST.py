# -*- coding: utf8 -*-
# for github.com/f03lipe
"""
REST wrapper for the application.
The basic usage of the classes defined in this file can be seen in app.views.
"""

# Django sutff
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.core.urlresolvers import reverse, NoReverseMatch

# Project stuff
from helpers import get_user_or_404, get_object_or_404
from helpers import BadProgramming
import models


class RESTBasicHandler(object):

	actions = {
		'GET': 'get',
		'PUT': 'put',
		'POST': 'post',
		'DELETE': 'delete',
	}

	def __call__(self, request, **urlFillers):
		""" Called each time a request is fired to the url.
			Obs: urlFillers are the variables set by the regex configuration
			in the urls.py file.
		"""

		try:
			view = getattr(self, self.actions[request.method])
		except KeyError:
			# Handler for such method was not defined.
			raise Http404, "Invalid call."
		except AttributeError:
			# Handlers misconfigured/not coded.
			raise BadProgramming, "My mama codes better than you!"
		form = self._get_form_data(request, request.method)
		return view.im_func(request, form, **urlFillers)


	@staticmethod
	def _get_form_data(request, method):
		""" Get data sent through the request. One way or another.
			
			The RESTful philosophy was not fully applied to django yet: data
			sent through PUT requests isn't stored as in POST or GET ones. The
			solution I found was implemented in django-piston, a wrapper for
			RESTful apps using django. It basically fakes a POST request and
			then calls request._load_post_and_files to fill up request.POST with
			the sent data.

			Please check out their documented code.
			https://bitbucket.org/jespern/django-piston/src/c4b2d21db51a/piston/utils.py#cl-154
		"""

		try:
			return getattr(request, method)
		except AttributeError:
			if hasattr(request, '_post'):
				del request._post
				del request._files
			try:
				request.method = "POST"
				request._load_post_and_files()
				request.method = method # "PUT"
			except AttributeError:
				request.META['REQUEST_METHOD'] = 'POST'
				request._load_post_and_files()
				request.META['REQUEST_METHOD'] = method # 'PUT'
	
			setattr(request, method, request.POST)
			return request.POST



class RESTHandler(RESTBasicHandler):
	"""
	Obs: The methods of the subclasses to handle the requests are all static.

	#! document idea for automatic fetcher
	# thought approaches

		objectMap = {
			'word': ('list', 'word_id'), # => Word.objects.get(id=word_id, list=list)
			'list': ('list_id')
		}

		decorator proposal
		@fetch(list=(List, {'id': 'list_id'}), word=(Word, {'id': 'word_id', 'list': 'list'}))

		def MM(cls_name, cls_parents, cls_attr):
			print "MMM"*20, cls_attr
			return type(cls_name, cls_parents, cls_attr)

		__metaclass__ = MM

	"""

	# These don't act on an object in particular.	
	objActions = {
		'GET': 'get',
		'POST': 'update',
		'DELETE': 'delete',
	}

	# These do.
	setActions = {
		'PUT': 'create',
		'GET': 'getAll',
	}

	# objSpecifier is present in the url regex and, when it's not null, specifies
	# an object to work with (usually passing the object's id). When a GET request
	# is made, if an object is specified the app must return information about that
	# object, otherwise, return all of them.
	objSpecifier = None

	# If requireLogged is set to True, redirection will occur to all non-logged 
	# requests (those without the 'userid' key in the sesssion).
	requireLogged = True

	def __call__(self, request, **urlFillers):
		""" Called each time a request is fired to the url.
			Obs: urlFillers are the variables set by the regex configuration
			in the urls.py file.
		"""
		args = dict()
		args['request'] = request
		args['form'] = self._get_form_data(request, request.method)
		print args['form']
		if self.requireLogged:
			args['user'] = get_user_or_404(request)
		
		if urlFillers.get(self.objSpecifier):
			# The request is object-specific: the action will take place on a 
			# defined object of the set, specified by urlFillers[self.objSpecifier]
			view_set = self.objActions
		else:
			view_set = self.setActions
			del urlFillers[self.objSpecifier]
		
		args.update(urlFillers)
		try:
			view = getattr(self, view_set[request.method])
		except KeyError:
			# Handler for such method was not defined.
			raise Http404, "Invalid call."
		except AttributeError:
			# Handlers misconfigured/not coded.
			raise BadProgramming, "I'd could do a better job blindfolded!"
		return view.im_func(**args)
