# -*- coding: utf8 -*-
"""

"""

# Django sutff
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse, NoReverseMatch

# Project stuff
from helpers import get_user_or_404, get_object_or_404
from helpers import BadProgramming

##

class RESTHandler(object):
	"""
	Obs: The methods of the subclasses to handle the requests are all static.

	#! document
	objectMap:
		objectMap = {
			'modelA_id': ModelA
		}
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
			Obs: urlFillers are those variables set by the regex configuration
			in the urls.py file.
		"""
		args = dict()
		args['request'] = request
		args['form'] = self._get_form_data(request, request.method)
		if self.requireLogged:
			args['user'] = get_user_or_404(request)
		
		if urlFillers.get(self.objSpecifier):
			# The request is object-specific: the action will take place on a 
			# defined object of the set, specified by urlFillers[self.objSpecifier]
			method_set = self.objActions
		else:
			method_set = self.setActions
			del urlFillers[self.objSpecifier]
		
		args.update(_process_fillers(urlFillers))
		method = getattr(self, method_set[request.method])
		return method.im_func(**args)

	def _process_fillers(urlFillers):
		objs = []
		for specifier in urlFillers:
			model = objectMap.get(specifier)
			if model:
				name, attr = obj.rsplit('_', 1)
				obj[name] = get_object_or_404(model, **{name:attr})
		return objs

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


##



# from django.template import RequestContext, loader
# from django.conf import settings
# from django.core.exceptions import PermissionDenied
# from django.http import HttpResponseForbidden  

# def render_to_Json404(*args, **kwargs):     
# 	"""     
# 		Returns a HttpResponseForbidden whose content is filled with the result of calling     
# 		django.template.loader.render_to_string() with the passed arguments.     
# 	"""     
# 	if not isinstance(args,list):         
# 		args = []         
# 		args.append('403.html')              

# 	httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}          
# 	response = HttpResponseForbidden(loader.render_to_string(*args, **kwargs), **httpresponse_kwargs)              

# 	return response

# class Json404Middleware(object):     
# 	def process_exception(self,request,exception):         
# 		if isinstance(exception,Http403):             
# 			if settings.DEBUG:                 
# 				raise PermissionDenied             
# 			return render_to_Json404(context_instance=RequestContext(request))