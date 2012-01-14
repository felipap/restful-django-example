# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.utils import simplejson

from app.models import User, List, Word, get_hash
from app.decorators import require_logged, require_not_logged, require_args, require_method, render_to
from app.dbhelper import _get_user, _in_user_database, _get_list, _in_list_database, _get_word, _in_word_database

from urllib import quote
import hashlib
import re
import logging

# TO DOs:
# recycle db access functions
# document general JSON response pattern
# implement log system and substitute print

# JsonObject = lambda **obj: HttpResponse(simplejson.dumps(obj))
# JsonError = lambda text: HttpResponseForbidden(simplejson.dumps({'error': True, 'text': text}))

def JsonObject(**obj):
	print "object being returned:", obj
	return HttpResponse(simplejson.dumps(obj))

def JsonError(**obj):
	print "error being returned:", obj
	return HttpResponseForbidden(simplejson.dumps({'error': True, 'text': text}))


## user account related views
###############################################################

IS_VALID_FIRST_NAME = lambda fn: re.match(r'^[_a-zA-Z][a-zA-Z0-9_]{4,20}$', fn)
IS_VALID_EMAIL = lambda email: re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$', email)
IS_VALID_PASSWORD = lambda password: re.match(r'[A-Za-z0-9@#$%^&+=]{6,70}', password)

@require_not_logged
@render_to('login.html')
def login(request):

	for arg in ('email', 'password'):
		if arg not in request.POST: # argument not found, return login page
			return dict()
	
	email = request.POST.get('email').strip()
	password = request.POST.get('password').strip()

	u = _get_user(email=email, password=password)	
	if not u: # if user not found
		return dict(flash_msg={
				'text': 'invalid email/password combination',
				'css': 'background: \'#FB3F51\''})
	
	request.session['userid'] = u.id
	return redirect('/lists?new=1')

@require_not_logged
@render_to('signin.html')
def signin(request):

	for arg in ('first_name', 'email', 'password'):
		if not arg in request.POST: # argument not found, return signin page
			return dict()
	
	first_name = request.POST.get('first_name').strip()
	email = request.POST.get('email').strip()
	password = request.POST.get('password').strip()

	args_tests_pack = [
		(IS_VALID_FIRST_NAME, first_name,
			"invalid first name. use only letters, digits and underscores. from 6 up to 21 characters"),
		(IS_VALID_EMAIL, email,
			"please enter a valid email"),
		(IS_VALID_PASSWORD, password,
			"invalid password. choose at least 6 characters") ]
	for test in args_tests_pack:
		if not test[0](test[1]):
			return dict(flash_msg={'text': test[2], 'css': 'background: \'#FB3F51\''})

	if _in_user_database(email=email):
		return dict(flash_msg={
				'text': "your email is already registered. haven't you signed up before?",
				'css': 'background: \'#FB3F51\''})
	
	u = User(first_name=first_name, email=email, password=get_hash(password))
	u.save()
	request.session['userid'] = u.id
	return redirect('/lists?new=1')


@require_logged
def logout(request):
	del request.session['userid']
	return redirect('/login')

###############################################################


@require_logged
@render_to('listspanel.html')
def listspanel(request):

	# if 'new' passed as get arg, user has just signed in
	# elif 'welcome' passed as get arg. user has just logged in
	# these arguments are passed by 'signin' and 'login' views

	try:
		user = User.objects.get(id=request.session['userid'])
	except User.DoesNotExist: # user not in db anymore (any db resets? :)
		print "user %s not found. redirecting ip %s to logout." % \
			(request.session['userid'], request.META['REMOTE_ADDR'])
		return redirect('/logout')
	
	flash_message = ''
	if request.GET.has_key('welcome'): # user is back
		flash_message = 'welcome back, %s!' % user.first_name
	elif request.GET.has_key('new'): # new user
		flash_message = 'welcome, %s!' % user.first_name

	return {'lists': user.list_set.all(), 'flash_msg': {'text': flash_message}}


@require_logged
@render_to('listpage.html')
def listpage(request, listname):
	
	try:
		user = User.objects.get(id=request.session['userid'])
	except User.DoesNotExist: # user not in db anymore (any db resets? :)
		print "user %s not found. redirecting ip %s to logout." % \
			(request.session['userid'], request.META['REMOTE_ADDR'])
		return redirect('/logout')
	
	try:
		l = user.list_set.get(label=listname)
	except List.DoesNotExist:
		raise Http404('list not found')

	return {'words': l.word_set.all(), 'parentlist': l}

###############################################################


# list and word API functions below (put in separate file?)

# API calls



IS_VALID_LIST_DESC = lambda desc: len(desc)<=140
IS_VALID_LIST_LABEL = lambda label: re.match(r'^[A-Za-z0-9@#$%^&+= ]{2,30}$(?<!^api)', label)
IS_VALID_WORD = lambda word: re.match("[A-Za-z0-9@#$%^&+=]{1,70}", word)
IS_VALID_WORD_MEANING = lambda meaning: len(meaning) < 100
IS_VALID_WORD_ORIGIN = lambda origin: len(origin) < 100

@require_logged
@require_method('POST')
@require_args('label', 'description')
def add_list(request):
	request.POST = request.GET or request.POST

	label = request.POST['label'].strip()
	description = request.POST['description'].strip()

	user = _get_user(userid=request.session['userid'])
	
	if not IS_VALID_LIST_LABEL(label):
		return JsonObject(success=False, text='invalid list name. up to 30 characters, only.')
	if not IS_VALID_LIST_DESC(description):
		return JsonObject(success=False, text='invalid description. up to 140 characters, only.')
	
	l = List(label=label, user=user, description=description)
	l.save()
	
	return JsonObject(success=True, text='list created', listid=l.id)


@require_logged
@require_method('POST')
@require_args('listid')
def change_list(request):
	# passing listid is obligatory, but description and label are optional

	listid = request.POST['listid'].strip()

	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=listid)
	if not l:
		return JsonObject(success=False, text='list not found')
	
	label = request.POST.get('label', None)
	desc = request.POST.get('description', None)
	
	if label is not None:
		if IS_VALID_LIST_LABEL(label.strip()): l.label = label.strip()
		else: return JsonObject(success=False, text='invalid list label')
	if desc is not None:
		if IS_VALID_LIST_DESC(desc.strip()): l.description = desc.strip()
		else: return JsonObject(success=False, text='invalid list description')
	
	l.save()
	return JsonObject(success=True, text="list \'%s\' updated" % l.label)


@require_logged
@require_method('POST')
@require_args('listid')
def remove_list(request):
	
	listid = request.POST['listid']
	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=listid)

	if not l:
		return JsonObject(success=False, text='list not found')
	l.delete()
	return JsonObject(success=True, text='list removed')


@require_logged
@require_method('POST')
@require_args('listid', 'word', 'meaning', 'origin')
def add_word(request):

	word = request.POST['word'].strip()
	meaning = request.POST['meaning'].strip()
	listid = request.POST['listid'].strip()
	origin = request.POST['origin'].strip()

	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=listid)
	

	if not l:
		return JsonObject(success=False, text='list not found')

	if not IS_VALID_WORD(word):
		return JsonObject(success=False, text='invalid word %s' % word)
	if not IS_VALID_WORD_MEANING(meaning):
		return JsonObject(success=False, text='invalid word meaning')
	if not IS_VALID_WORD_ORIGIN(origin):
		return JsonObject(success=False, text='invalid word origin')
	
	w = Word(word=word, meaning=meaning, origin=origin, list=l)
	w.save()

	return JsonObject(success=True, text='word added to \'%s\'' % l.label, wordid=w.id)


@require_logged
@require_method('POST')
@require_args('wordid', 'listid')
def change_word(request):

	wordid = request.POST['wordid'].strip()
	listid = request.POST['listid'].strip()

	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=listid)
	if not l:
		return JsonObject(success=False, text='list not found')
	w = _get_word(list=l, wordid=wordid)
	if not w:
		return JsonObject(success=False, text='word doesn\'t exist')
	
	word = request.POST.get('word', None)
	origin = request.POST.get('origin', None)
	meaning = request.POST.get('meaning', None)

	if word is not None:
		if IS_VALID_WORD(word.strip()): w.word = word.strip()
		else: return JsonObject(success=False, text='invalid word')
	if meaning is not None:
		if IS_VALID_WORD_MEANING(meaning.strip()): w.meaning = meaning.strip()
		else: return JsonObject(success=False, text='invalid word meaning field')
	if origin is not None:
		if IS_VALID_WORD_ORIGIN(origin.strip()): w.origin = origin.strip()
		else: return JsonObject(success=False, text='invalid word origin field')
	
	w.save()
	return JsonObject(success=True, text='word updated')


@require_logged
@require_method('POST')
@require_args('wordid', 'listid')
def remove_word(request):

	wordid = request.POST['wordid'].strip()
	listid = request.POST['listid'].strip()

	user = _get_user(userid=request.session['userid'])
	l = _get_list(user=user, listid=listid)

	if not l:
		return JsonObject(success=False, text='list not found')
	w = _get_word(list=l, wordid=wordid)
	if not w:
		return JsonObject(success=False, text='word doens\'t exist.')
	w.delete()
	return JsonObject(success=True, text='word removed from %s ' % l.label)