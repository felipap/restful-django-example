# -*- coding: utf8 -*-
# for github.com/f03lipe

# Python stuff
from functools import wraps
import logging
import pdb

# Django stuff
from django.shortcuts import redirect

# Project stuff
from worddb.app.models import User, List, Word, get_hash, UserForm, ListForm, WordForm
from worddb.app.doREST import RESTBasicHandler, RESTHandler
from worddb.app.helpers import RaisableRedirect, Json404 # Exceptions
from worddb.app.helpers import get_object_or_json404
from worddb.app.helpers import renderHTML, renderJSON, toJson

# TODOs:
# Get logging to work.
# Save through Ctrl+S.
# Rename css elements.
# Add search to words.
# Remove ugly toolbox.
# Yes, I did align'em.

# JSON data convention:
## succes: 	True|False	=> indicates wheter the action succeded
## messages:[msg, ]		=> general text information #! substitute by a list or smthg...
## errors: 	[msg, ]		=> shows errors associated with the call


def _setup_session(session, user):
	# That's all, by now.
	session['userid'] = user.id


class LoginHandler(RESTBasicHandler):
	""" Called when the user hits '/login' """

	def __call__(self, request, *args, **kwargs):
		"""
		Overrides parent's method to check if user is logged out. If it does,
		redirect to '/lists'. This approach could be derived by using a	class
		decorator, depending on the demand for this functionality among	the
		subclasses of RESTBasicHandler.
		"""
		if request.session.get('userid'):
			return redirect('/lists')
		return super(LoginHandler, self).__call__(request, *args, **kwargs)

	@renderHTML('login.html')
	def get(request, form):
		return dict()

	@renderJSON
	def put(request, form):
		email = form.get('email')
		password = form.get('password')
		if not all((email, password)):
			# Client-side error. Should not be possible by proper calls.
			raise Json404({'success': False, 'errors': ['Please fill all fields.']})
		try:
			user = User.objects.get(email=email, password=get_hash(password))
		except User.DoesNotExist:
			raise Json404() #! Should the response be more specific?
		print("Yes, been here")
		_setup_session(request.session, user)
		return {
			'success': True,
			'redirect': '/lists?welcome=1'
		}


class SignInHandler(RESTBasicHandler):
	""" Called when the user hits '/signin' """

	def __call__(self, request, *args, **kwargs):
		"""
		Overrides parent's method to check if user is logged out. If it does,
		redirect to '/lists'. This approach could be derived by using a	class
		decorator, depending on the demand for this functionality among	the
		subclasses of RESTBasicHandler.
		"""
		if request.session.get('userid'):
			return redirect('/lists')
		return super(SignInHandler, self).__call__(request, *args, **kwargs)

	@renderHTML('signin.html')
	def get(request, form):
		return dict()

	@renderJSON
	def post(request, form):
		name = form.get('first_name')
		email = form.get('email')
		password = form.get('password')

		print form

		if not all((name, email, password)):
			# Client-side error. Should not be possible by proper calls.
			raise Json404({'success': False, 'errors': ['Please fill all fields.']})

		form = UserForm(form)
		if not form.is_valid():
			return {'success': False, 'errors': sum(form.errors.values(),[])}
		if User.objects.filter(email=email):
			return {'success': False, 'errors': ['This email is already registered.']}

		user = User.objects.create(
			first_name=name,
			email=email,
			password=get_hash(password))
		_setup_session(request.session, user)
		return {'success': True, 'redirect': '/lists?welcome=0'}



def logout(request):
	try:
		del request.session['userid']
	except KeyError:
		pass # Fail silently
	return redirect('/login')



class ListHandler(RESTHandler):
	"""
	REST handler for models.Lists.
	"""

	objSpecifier = 'list_id'
	requireLogged = True

	@renderJSON
	def create(request, user, form):
		list_form = ListForm(form)
		if not list_form.is_valid():
			errors = sum(list_form.errors.values(), [])
			return dict(success=False, errors=errors)
		fields = dict()
		for arg in ('label', 'description'):
			fields[arg] = form[arg]
		list = List.objects.create(user=user, **fields)
		return {
			'success': 	True,
			'messages': ['list \'%s\' created' % list.label],
			'listid': 	list.id,
			'object':	toJson(list),
		}

	@renderHTML('listspanel.html')
	def getAll(request, user, form):
		lists = toJson(*user.list_set.order_by('date_modified'))
		return {'serialized_lists': lists}

	@renderJSON
	def update(request, user, form, list_id):
		list = get_object_or_json404(List, id=list_id)
		errors = []
		list_form = ListForm(form)
		for arg in ('label', 'description'):
			if arg in form:
				if list_form[arg].errors:
					errors += list_form[arg].errors
				else:
					setattr(list, arg, form[arg])
		if errors:
			return dict(success=False, errors=errors)

		list.save()
		return {
			'success': 	True,
			'messages': ["list \'%s\' updated" % list.label],
			'object': 	toJson(list),
		}

	@renderJSON
	def delete(request, user, form, list_id):
		list = get_object_or_json404(List, id=list_id)
		json = toJson(list)
		list.delete()
		return {
			'success': 	True,
			'messages': ['list \'%s\' removed' % list.label],
			'object': 	json,
		}

	@renderHTML('listpage.html')
	def get(request, user, form, list_id):
		list = get_object_or_json404(List, id=list_id)
		words = toJson(*list.word_set.order_by('date_modified'))
		return {'serialized_words': words, 'parentlist': list}


class WordHandler(RESTHandler):
	"""
	REST handler for models.Words.
	"""

	objSpecifier = 'word_id'
	requireLogged = True

	@renderJSON
	# @require_args('listid', 'word', 'meaning', 'origin')
	def create(request, user, form, list_id):
		list = get_object_or_json404(List, id=list_id)

		# test incoming data
		word_form = WordForm(form)
		if not word_form.is_valid():
			errors = sum(word_form.errors.values(), [])
			return dict(success=False, errors=errors)

		fields = dict()
		for arg in ('word', 'meaning', 'origin'):
			fields[arg] = form[arg]
		word = Word.objects.create(list=list, **fields)
		return {
			'success': 	True,
			'messages': ['word \'%s\' added to \'%s\'' % (word_form['word'].value(), list.label)],
			'wordid': 	word.id,
			'object': 	toJson(word),
		}

	@renderJSON
	def update(request, user, form, list_id, word_id):
		list = get_object_or_json404(List, id=list_id)
		word = get_object_or_json404(Word, id=word_id, list=list)

		errors = []
		word_form = WordForm(form)
		for arg in ('word', 'meaning', 'origin'):
			if arg in form:
				if word_form[arg].errors:
					errors += word_form[arg].errors
				else:
					setattr(word, arg, form[arg])
		if errors:
			return dict(success=False, errors=errors)

		word.save()
		return {
			'success': 	True,
			'messages': ["word '%s' updated" % word.word],
			'object': 	toJson(word),
		}

	@renderJSON
	def delete(request, user, form, list_id, word_id):
		list = get_object_or_json404(List, id=list_id)
		word = get_object_or_json404(Word, id=word_id, list=list)
		json = toJson(word)
		word.delete()

		return {
			'success': 	True,
			'messages': ['word \'%s\' removed from %s ' % (word.word, list.label)],
			'object': 	json,
		}

