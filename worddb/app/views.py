#!/usr/bin/env python
# app/views.py

from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.utils import simplejson
from django import forms

from app.models import User, List, Word, get_hash, UserForm, ListForm, WordForm
from app.decorators import require_logged, require_not_logged, require_args, require_method, render_to

# import re
# import logging
# import pdb


# TODOs:
# implement log system
# implementar salvar pelo comando Ctrl+S no browser
# mudar nome do elemento '.list' em listspanel.html
# add search to words
# organize a tool box
## organize 'search this word here' when meaning is empty

# JSON pattern for the application;
# succes: True | False => indicates wheter the action succeded
# text [text] => general text information // substitute by a messages list or smthg...
# errors: [list] => shows errors associated with the call

def JsonObject(**obj):
	return HttpResponse(simplejson.dumps(obj))


## user account related views
###############################################################


@require_not_logged
@render_to('signin.html')
def signin(request):

	if request.method == 'GET':
		return dict()

	for arg in ('first_name', 'email', 'password'):
		if not arg in request.POST: # method is post, but argument not found
			return JsonObject(success=False, errors=['invalid access'])
	
	sign_form = UserForm(request.POST) 
	if not sign_form.is_valid():
		return JsonObject(success=False, errors=sum(sign_form.errors.values(),[]))

	first_name = request.POST['first_name']
	email = request.POST['email']
	password = request.POST['password']

	if User.objects.in_user_database(email=email):
		return JsonObject(success=False, errors=["this email is already registered. haven't you signed up before?"])
	
	u = User.objects.create(first_name=first_name, email=email, password=get_hash(password))
	request.session['userid'] = u.id
	return JsonObject(success=True, text='you\'re being signed in <img src="/static/images/loading.gif" />',
			redirect='/lists?welcome=0')


@require_not_logged
@render_to('login.html')
def login(request):

	if request.method == 'GET':
		return dict()
	
	for arg in ('email', 'password'):
		if arg not in request.POST: # method is post, but argument not found
			return JsonObject(success=False, errors=['invalid access'])
	
	email = request.POST['email']
	password = request.POST['password']

	u = User.objects.get_user(email=email, password=password)	
	if not u: # if user not found
		return JsonObject(success=False, errors=['invalid email/password combination'])
	
	request.session['userid'] = u.id
	return JsonObject(success=True, text='you\'re being logged in <img src="/static/images/loading.gif" />',
			redirect='/lists?welcome=1')


@require_logged
def logout(request):
	del request.session['userid']
	return redirect('/login')


###############################################################


# list and word API functions below (put in separate file?)

# API calls

# import logging
# logger = logging.getLogger(__name__)

# class BadProgramming (Exception):
#	""" Raise it at will. """



from functools import wraps
from django.shortcuts import get_object_or_404
from app.models import User, List, Word, get_hash, UserForm, ListForm, WordForm

from doREST import RESTHandler
from doREST import Json404, RaisableRedirect

from app.helpers import get_user_or_404
from app.helpers import get_object_or_json404

class WordHandler(RESTHandler):
	""" REST handler for Words.
	The methods defined below and their respective mime-types are:
		- create (JSON)
		- getAll (HTML)
		- update (JSON)
		- get (HTML)
		- delete (JSON)
	"""

	objSpecifier = 'word_id'
	requireLogged = True

	# JSON
	# @require_args('listid', 'word', 'meaning', 'origin')
	def create(request, user, form, list_id):
		list = get_object_or_json404(List, id=list_id)

		user = User.objects.get(id=request.session['userid'])
		l = List.objects.get_list(user, id=request.POST['listid'])
		if not l:
			return JsonObject(success=False, text='list not found')
		
		# test incoming data
		word_form = WordForm(request.POST)
		if not word_form.is_valid():
			errors = sum(word_form.errors.values(), [])
			return JsonObject(success=False, errors=errors)
		
		fields = dict()
		for arg in ('word', 'meaning', 'origin'):
			fields[arg] = request.POST[arg]
		w = Word.objects.create(list=l, **fields)

		return JsonObject(success=True, text='word \'%s\' added to \'%s\'' % (word_form['word'].value(), l.label), wordid=w.id)
		pass

	# HTML
	# @render_to('listpage.html')
	# def getAll(request, user, form):
	# 	pass

	# JSON
	def update(request, user, form, list_id, word_id):
		print "called"

	# JSON
	def delete(request, user, form, list_id, word_id):
		pass

	# HTML
	# def get(request, user, form, list_id, word_id):
	# 	pass


class ListHandler(RESTHandler):
	""" REST handler for Lists.
	The methods defined below and their respective mime-types are:
		- create (JSON)
		- getAll (HTML)
		- update (JSON)
		- get (HTML)
		- delete (JSON)
	"""

	objSpecifier = 'list_id'
	requireLogged = True

	# JSON
	def create(request, user, form):
		list_form = ListForm(form)
		if not list_form.is_valid():
			errors = sum(list_form.errors.values(), [])
			return JsonObject(success=False, errors=errors)

		fields = dict()
		for arg in ('label', 'description'):
			fields[arg] = form[arg]
		l = List.objects.create(user=user, **fields)
		return JsonObject(success=True, text='list \'%s\' created' % l.label, listid=l.id)

	# HTML
	@render_to('listspanel.html')
	def getAll(request, user, form):
		fields = {'created': 'date_created', 'modified': 'date_modified', 'listlabel': 'label'}

		if 'order_by' in request.GET:
			value = request.GET['order_by']
			if value in fields:
				order = fields[value]
			elif value[0] == '-' and value[1:] in fields:
				order = '-'+fields[value[1:]]
			# fail silently
		else:
			order = None
			value = None
		
		lists = user.list_set.order_by('date_created') if not order else user.list_set.order_by(order)
		return {'lists': lists, 'order_by': value}

	# JSON
	def update(request, user, form, list_id):
		return change_list(request)

	# JSON
	def delete(request, user, form, list_id):
		pass

	# HTML
	@render_to('listpage.html')
	def get(request, user, form, list_id):
		
		list = get_object_or_404(List, id=list_id)
		fields = {'created': 'date_created', 'modified': 'date_modified', 'word': 'word'}
		if 'order_by' in request.GET:
			value = request.GET['order_by']
			if value in fields:
				order = fields[value]
			elif value[0] == '-' and value[1:] in fields:
				order = '-'+fields[value[1:]]
			# fail silently
		else:
			order = None
			value = None
		
		words = list.word_set.order_by('date_created') if not order else list.word_set.order_by(order)
		return {'words': words, 'parentlist': list, 'order_by': value}
 

################################

@require_logged
@require_args('label', 'description')
@require_method('POST')
def add_list(request):

	user = User.objects.get(id=request.session['userid'])
	
	list_form = ListForm(request.POST)
	if not list_form.is_valid():
		errors = sum(list_form.errors.values(), [])
		return JsonObject(success=False, errors=errors)

	fields = dict()
	for arg in ('label', 'description'):
		fields[arg] = request.POST[arg]

	l = List.objects.create(user=user, **fields)

	return JsonObject(success=True, text='list \'%s\' created' % l.label, listid=l.id)


@require_logged
@require_method('POST')
@require_args('listid', 'label', 'description')
def change_list(request):

	user = User.objects.get(id=request.session['userid'])
	l = List.objects.get_list(user, id=request.POST['listid'])
	if not l:
		return JsonObject(success=False, errors=['list not found',])

	errors = []
	list_form = ListForm(request.POST)
	for arg in ('label', 'description'):
		if arg in request.POST:
			if list_form[arg].errors:
				errors += list_form[arg].errors
			else: 
				setattr(l, arg, request.POST[arg])
	if errors:
		return JsonObject(success=False, errors=errors)
	
	l.save()
	return JsonObject(success=True, text="list \'%s\' updated" % l.label)


@require_logged
@require_method('POST')
@require_args('listid')
def remove_list(request):
	
	user = User.objects.get(id=request.session['userid'])
	l = List.objects.get_list(user, id=request.POST['listid'])

	if not l:
		return JsonObject(success=False, errors=['list not found',])

	l.delete()
	return JsonObject(success=True, text='list \'%s\' removed' % l.label)


## WORDS

@require_logged
@require_method('POST')
@require_args('listid', 'word', 'meaning', 'origin')
def add_word(request, list_id):

	user = User.objects.get(id=request.session['userid'])
	l = List.objects.get_list(user, id=request.POST['listid'])
	if not l:
		return JsonObject(success=False, text='list not found')
	
	# test incoming data
	word_form = WordForm(request.POST)
	if not word_form.is_valid():
		errors = sum(word_form.errors.values(), [])
		return JsonObject(success=False, errors=errors)
	
	fields = dict()
	for arg in ('word', 'meaning', 'origin'):
		fields[arg] = request.POST[arg]
	w = Word.objects.create(list=l, **fields)

	return JsonObject(success=True, text='word \'%s\' added to \'%s\'' % (word_form['word'].value(), l.label), wordid=w.id)




@require_logged
@require_method('POST')
@require_args('wordid', 'listid')
def change_word(request, list_id, word_id):
	# passing listid and wordid is obligatory, but description and label are optional
	
	user = User.objects.get(id=request.session['userid'])
	l = List.objects.get_list(user, id=request.POST['listid'])
	if not l:
		return JsonObject(success=False, errors=['list not found',])
	w = Word.objects.get_word(l, id=request.POST['wordid'])
	if not w:
		return JsonObject(success=False, text='word doesn\'t exist')

	errors = []
	word_form = WordForm(request.POST)
	for arg in ('word', 'meaning', 'origin'):
		if arg in request.POST:
			if word_form[arg].errors:
				errors += word_form[arg].errors
			else:
				setattr(w, arg, request.POST[arg])
	if errors:
		return JsonObject(success=False, errors=errors)
	
	w.save()
	return JsonObject(success=True, text="word '%s' updated" % w.word)


@require_logged
@require_method('POST')
@require_args('wordid', 'listid')
def remove_word(request):

	user = User.objects.get(id=request.session['userid'])
	l = List.objects.get_list(user, id=request.POST['listid'])

	if not l:
		return JsonObject(success=False, text='list not found')

	w = Word.objects.get_word(l, id=request.POST['wordid'])
	
	if not w:
		return JsonObject(success=False, text='word doens\'t exist.')

	w.delete()
	return JsonObject(success=True, text='word \'%s\' removed from %s ' % (w.word, l.label))
