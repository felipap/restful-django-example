#!/usr/bin/env python
# app/views.py

from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.utils import simplejson
from django import forms

from app.models import User, List, Word, get_hash
from app.decorators import require_logged, require_not_logged, require_args, require_method, render_to
from app.dbhelper import _get_user, _in_user_database, _get_list, _in_list_database, _get_word, _in_word_database

# import re
# import logging
# import pdb # import python debugger?



# TO DOs:
# implement log system



# JSON pattern for the application;
# succes: True | False => indicates wheter the action succeded
# text [text] => general text information // substitute by a messages list or smthg...
# errors: [list] => shows errors associated with the call

def JsonObject(**obj):
	return HttpResponse(simplejson.dumps(obj))


## user account related views
###############################################################

class UserForm(forms.Form):

	first_name = forms.CharField(min_length=3, max_length=21, error_messages={
		'required':'what should we call you?',
		'max_length':'name is too long. choose at most 21 characters.',
		'min_length':'name is too short. choose at least 3 characters.'
	})
	
	email = forms.EmailField(error_messages={
		'invalid':'please, enter a valid email address.',
		'required':'please, enter a valid email address.'
	})
	
	password = forms.RegexField(r'[A-Za-z0-9@#$%^&+= ]{4,50}$',
				error_messages={
		'invalid':'invalid password. choose at least 4 characters, at most 50.',
		'required':'enter a password.',
	})



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

	if _in_user_database(email=email):
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

	u = _get_user(email=email, password=password)	
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


@require_logged
@render_to('listspanel.html')
def listspanel(request):

	# if '?welcome=0', user has just signed in
	# elif '?welcome=1' used has just logged in
	# these arguments are passed by 'signin' and 'login' views, respectively

	try:
		user = User.objects.get(id=request.session['userid'])
	except User.DoesNotExist: # user not in db anymore (any db resets? :)
		logger.warning("user %s not found. redirecting ip %s to logout." % \
			(request.session['userid'], request.META['REMOTE_ADDR']))
		return redirect('/logout')
	
	messages = []
	if request.GET.has_key('welcome'): # user is back
		if request.GET['welcome'] == '0':
			messages = ['welcome, %s!' % user.first_name,]
		elif request.GET['welcome'] == '1':
			messages = ['welcome back, %s!' % user.first_name,]

	order = 'date_created'
	if 'order_by' in request.GET:
		value = request.GET['order_by']
		if value == 'created': order = 'date_created'
		elif value == 'modified': order = 'date_modified'
		elif value == 'listlabel': order = 'label'
		if 'reversed' in request.GET and request.GET['reversed'] == '1':
			order = '-'+order
	
	lists = user.list_set.all() if not order else user.list_set.order_by(order)
	return {'lists': lists, 'flash_messages': messages}


@require_logged
@render_to('listpage.html')
def listpage(request, listname):
	
	try:
		user = User.objects.get(id=request.session['userid'])
	except User.DoesNotExist: # user not in db anymore (any db resets? :)
		# user not found. redirect to logout.
		return redirect('/logout')
	
	try:
		l = user.list_set.get(label=listname)
	except List.DoesNotExist:
		raise Http404('list not found')
	
	order = 'date_created'
	if 'order_by' in request.GET:
		value = request.GET['order_by']
		if value == 'created': order = 'date_created'
		elif value == 'modified': order = 'date_modified'
		elif value == 'word': order = 'word'
		if 'reversed' in request.GET and request.GET['reversed'] == '1':
			order = '-'+order
	
	words = l.word_set.all() if not order else l.word_set.order_by(order)
	return {'words': words, 'parentlist': l}

###############################################################


# list and word API functions below (put in separate file?)

# API calls

class ListForm(forms.Form):
	label = forms.CharField(max_length=30, error_messages={
		'invalid':'invalid list name. choose at least 1 character.',
		'required':'enter a list name, at least 3 characters long.',
		'max_length':'list name is too long. choose at most 30 characters.'
	})
	
	description = forms.CharField(required=False, max_length=140, error_messages={
		'max_length':'description is too long. choose at most 140 characters'})
	
	def clean_label(self):
		if self.cleaned_data['label'].strip() == 'api':
			raise forms.ValidationError('list name invalid') # cannot be "api"



@require_logged
@require_method('POST')
@require_args('label', 'description')
def add_list(request):

	user = _get_user(userid=request.session['userid'])
	
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
@require_args('listid')
def change_list(request):
	# passing listid is obligatory, but description and label are optional

	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=request.POST['listid'])
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
	
	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=request.POST['listid'])

	if not l:
		return JsonObject(success=False, errors=['list not found',])

	l.delete()
	return JsonObject(success=True, text='list \'%s\' removed' % l.label)

## WORDS

class WordForm(forms.Form):
	word = forms.CharField(max_length=30, error_messages={
		'required':'invalid word. choose at least 1 character.',
		'max_length':'word is too long. choose at most 30 characters.' })
	
	meaning = forms.CharField(required=False, max_length=100, error_messages={
		'max_length':'meaning is too long. choose at most 100 characters.' })
	
	origin = forms.CharField(required=False, max_length=100, error_messages={
		'max_length':'origin is too long. choose at most 100 characters.' })



@require_logged
@require_method('POST')
@require_args('listid', 'word', 'meaning', 'origin')
def add_word(request):

	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=request.POST['listid'])
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
@require_args('listid')
def change_list(request):
	# passing listid is obligatory, but description and label are optional

	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=request.POST['listid'])
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
@require_args('wordid', 'listid')
def change_word(request):
	# passing listid and wordid is obligatory, but description and label are optional
	
	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=request.POST['listid'])
	if not l:
		return JsonObject(success=False, errors=['list not found',])
	w = _get_word(list=l, wordid=request.POST['wordid'])
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

	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=request.POST['listid'])

	if not l:
		return JsonObject(success=False, text='list not found')

	w = _get_word(list=l, wordid=request.POST['wordid'])
	
	if not w:
		return JsonObject(success=False, text='word doens\'t exist.')

	w.delete()
	return JsonObject(success=True, text='word removed from %s ' % l.label)