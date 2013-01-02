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
from app.helpers import renderHTML, renderJSON


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

#! remove
def JsonObject(**obj):
	return HttpResponse(simplejson.dumps(obj))


## user account related views
###############################################################


@require_not_logged
@renderHTML('signin.html')
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
		return JsonObject(success=False,
			errors=["this email is already registered. haven't you signed up before?"])
	
	u = User.objects.create(first_name=first_name, email=email, password=get_hash(password))
	request.session['userid'] = u.id
	return JsonObject(success=True,
			text='you\'re being signed in <img src="/static/images/loading.gif" />', 
			redirect='/lists?welcome=0')


@renderHTML('login.html')
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
	return JsonObject(success=True,
		text='you\'re being logged in <img src="/static/images/loading.gif" />',
		redirect='/lists?welcome=1')


def logout(request):
	try:
		del request.session['userid']
	except KeyError:
		pass # Fail silently
	return redirect('/login')


###############################################################


# list and word API functions below (put in separate file?)

# Python stuff
from functools import wraps
import logging

# Django stuff
from django.shortcuts import get_object_or_404

# Project stuff
from app.models import User, List, Word, get_hash, UserForm, ListForm, WordForm
from app.doREST import RESTHandler
from app.helpers import RaisableRedirect, Json404 # Exceptions
from app.helpers import get_user_or_404, get_object_or_json404
from app.helpers import renderHTML, renderJSON


logging.info("oi")


class ListHandler(RESTHandler):
	"""
	REST handler for models.Lists.
	The methods defined below and their respective mime-types are:
		- create (JSON)
		- getAll (HTML)
		- update (JSON)
		- get (HTML)
		- delete (JSON)
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
		l = List.objects.create(user=user, **fields)
		return dict(success=True, text='list \'%s\' created' % l.label, listid=l.id)

	@renderHTML('listspanel.html')
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

	@renderJSON
	def update(request, user, form, list):
		list = get_object_or_json404(List, id=list_id)

		errors = []
		list_form = ListForm(request.POST)
		for arg in ('label', 'description'):
			if arg in request.POST:
				if list_form[arg].errors:
					errors += list_form[arg].errors
				else: 
					setattr(list, arg, request.POST[arg])
		if errors:
			return dict(success=False, errors=errors)
		
		list.save()
		return dict(success=True, text="list \'%s\' updated" % list.label)

	@renderJSON
	def delete(request, user, form, list_id):
		list = get_object_or_json404(List, id=list_id)
		list.delete()
		return dict(success=True, text='list \'%s\' removed' % list.label)

	@renderHTML('listpage.html')
	def get(request, user, form, list_id):
		list = get_object_or_json404(List, id=list_id)
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




class WordHandler(RESTHandler):
	"""
	REST handler for models.Words.
	The methods defined below and their respective mime-types are:
		- create (JSON)
		- getAll (HTML)
		- update (JSON)
		- get (HTML)
		- delete (JSON)
	"""

	# @renderHTML('listpage.html')
	# def getAll(request, user, form):
	# 	pass
	# def get(request, user, form, list_id, word_id):
	# 	pass


	objSpecifier = 'word_id'
	requireLogged = True

	@renderJSON
	# @require_args('listid', 'word', 'meaning', 'origin')
	def create(request, user, form, list_id):
		list = get_object_or_json404(List, id=list_id)
		
		# test incoming data
		word_form = WordForm(request.POST)
		if not word_form.is_valid():
			errors = sum(word_form.errors.values(), [])
			return dict(success=False, errors=errors)
		
		fields = dict()
		for arg in ('word', 'meaning', 'origin'):
			fields[arg] = request.POST[arg]
		w = Word.objects.create(list=list, **fields)

		return {
			'success': True,
			'text': 'word \'%s\' added to \'%s\'' % (word_form['word'].value(), list.label),
			'wordid': w.id
		}

	@renderJSON
	def update(request, user, form, list_id, word_id):
		# passing listid and wordid is obligatory, but description and label are optional
		list = get_object_or_json404(List, id=list_id)	
		word = get_object_or_json404(Word, id=word_id, list=list)

		errors = []
		word_form = WordForm(request.POST)
		for arg in ('word', 'meaning', 'origin'):
			if arg in request.POST:
				if word_form[arg].errors:
					errors += word_form[arg].errors
				else:
					setattr(word, arg, request.POST[arg])
		if errors:
			return dict(success=False, errors=errors)
		
		word.save()
		return {
			'success': True,
			'text': "word '%s' updated" % word.word
		}

	@renderJSON
	def delete(request, user, form, list_id, word_id):
		list = get_object_or_json404(List, id=list_id)	
		word = get_object_or_json404(Word, id=word_id, list=list)
		word.delete()
		
		return {
			'success': True,
			'text': 'word \'%s\' removed from %s ' % (word.word, list.label)
		}

