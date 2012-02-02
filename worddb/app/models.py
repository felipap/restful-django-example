#!/usr/bin/env python
# app/models.py 

from django.db import models

from datetime import datetime
import hashlib
import pdb
from functools import wraps

get_hash = lambda password: hashlib.sha224(password).hexdigest()

def check_arguments(*valid_kwargs):
	"""
	checks if the keyword arguments of a manager method call are
	within the valid arguments established
	"""
	
	def decorator(method):
		@wraps(method)
		def wrapper(self, *args, **kwargs):
			if not set(kwargs).issubset(valid_kwargs):
				raise Exception("bad arguments entered")
			return method(self, *args, **kwargs)
		return wrapper
	return decorator


class UserManager(models.Manager):
	""" custom manager for Users. adds 'in_user_database' and 'get_user' methods. """

	@check_arguments('id', 'email', 'password')
	def in_user_database(self, **kwargs):
		return bool(self.get_user(**kwargs))
	
	@check_arguments('id', 'email', 'password')
	def get_user(self, **kwargs):
		
		if 'password' in kwargs.keys():
			kwargs['password'] = get_hash(kwargs['password'])
		
		try: return self.get(**kwargs)
		except User.DoesNotExist: # let it raise MultipleObjectsReturned
			return None


class ListManager(models.Manager):
	""" custom manager for List. adds 'in_list_database' and 'get_list' methods. """

	@check_arguments('listlabel', 'id')
	def in_list_database(self, user, **kwargs):
		return bool(self.get_list(user, **kwargs))
	
	@check_arguments('listlabel', 'id')
	def get_list(self, user, **kwargs):
		try: return user.list_set.get(**kwargs)
		except List.DoesNotExist: # let it raise MultipleObjectsReturned
			return None


class WordManager(models.Manager):
	""" custom manager for Word. adds 'in_word_database' and 'get_word' methods. """

	@check_arguments('id', 'word', 'origin', 'description')
	def in_word_database(self, list, **kwargs):
		return bool(self.get_word(user, **kwargs))
	
	@check_arguments('id', 'word', 'origin', 'description')
	def get_word(self, list, **kwargs):
		try: return list.word_set.get(**kwargs)
		except Word.DoesNotExist: # let it raise MultipleObjectsReturned
			return None
			

class User(models.Model):

	# fields:
	# first_name[20] // user's first name
	# email
	# password[56] (sha224 hash)

	first_name = models.CharField(max_length=20)
	email = models.EmailField(unique=True)
	password = models.CharField(max_length=56)

	objects = UserManager() # custom manager

	def save(self, *args, **kwargs): # !useless
		super(User, self).save(*args, **kwargs)

	def __unicode__(self):
		return "%s: %s" % (self.first_name, self.email)

class List(models.Model):

	# fields
	# name[20]
	# user (ForeignKey)

	label = models.CharField(max_length=30)
	user = models.ForeignKey(User)
	description = models.CharField(max_length=140)

	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)

	objects = ListManager() # custom manager

	def __unicode__(self):
		return self.label
	
	def save(self, *args, **kwargs):
		assert self.label != 'api', 'listname can\'t be \'api\''
		super(List, self).save(*args, **kwargs)


class Word(models.Model):

	word = models.CharField(max_length=30)

	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)

	origin = models.CharField(max_length=100, blank=True, null=True)
	meaning = models.CharField(max_length=100, blank=True, null=True)
	
	list = models.ForeignKey(List)

	objects = WordManager() # custom manager

	def save(self, *args, **kwargs):
		self.list.date_modified = datetime.now()
		self.list.save() # change 'date_modified' of list when words are modified
		super(Word, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.word
