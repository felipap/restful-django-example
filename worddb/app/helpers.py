# -*- coding: utf8 -*-

from django.http import Http404

from .models import User

class BadProgramming (Exception):
	""" Raise at will. """


def get_user_or_404(request):
	""" Attempt to get the user object or redirect to logout. """
	try:
		return User.objects.get(id=request.session['userid'])
	except (User.DoesNotExist, KeyError):
		# logger.warning("User %s not found. Redirecting ip %s to logout." % (request.session.get('userid'), request.META['REMOTE_ADDR']))
		raise Http404, "User not found"


def get_object_or_json404(request):
	""" Attempt to get the user object or return Json 404. """
	try:
		return User.objects.get(id=request.session['userid'])
	except (User.DoesNotExist, KeyError):
		# logger.warning("User %s not found. Redirecting ip %s to logout." % (request.session.get('userid'), request.META['REMOTE_ADDR']))
		from .doREST import Json404
		raise Json404, "User not found"