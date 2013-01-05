# -*- coding: utf8 -*-
# for github.com/f03lipe

# Python stuff
from datetime import datetime
from functools import wraps
import hashlib

# Django stuff
from django.db import models
from django import forms


# In real life, use salts, plz
get_hash = lambda password: hashlib.sha224(password).hexdigest()

## FORMS

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
	password = forms.RegexField(r'^[A-Za-z0-9@#$%^&+= ]{4,50}$',
				error_messages={
		'invalid':'invalid password. choose at least 4 characters, at most 50.',
		'required':'enter a password.',
	})


class ListForm(forms.Form):
	label = forms.RegexField(r'^[A-Za-z0-9#\'"%^+ ]{1,30}$',
				error_messages={
		'invalid':'invalid list name. choose from 1 up to 30 characters.', 
		'required':'enter a list name.',
	})
	description = forms.CharField(required=False, max_length=140, error_messages={
		'max_length':'description is too long. choose at most 140 characters'
	})


class WordForm(forms.Form):
	word = forms.CharField(max_length=60, error_messages={
		'required':'invalid word. choose at least 1 character.',
		'max_length':'word is too long. choose at most 60 characters.'
	})
	meaning = forms.CharField(required=False, max_length=100, error_messages={
		'max_length':'meaning is too long. choose at most 100 characters.'
	})
	origin = forms.CharField(required=False, max_length=100, error_messages={
		'max_length':'origin is too long. choose at most 100 characters.'
	})

## MODELS

class User(models.Model):

	first_name = models.CharField(max_length=20)
	email = models.EmailField(unique=True)
	password = models.CharField(max_length=56)

	def __unicode__(self):
		return "%s: %s" % (self.first_name, self.email)

class List(models.Model):

	label = models.CharField(max_length=30)
	user = models.ForeignKey(User)
	description = models.CharField(max_length=140)
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.label
	
	def save(self, *args, **kwargs):
		assert self.label != 'api', 'listname can\'t be \'api\''
		super(List, self).save(*args, **kwargs)


class Word(models.Model):

	word = models.CharField(max_length=30)
	date_created = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(auto_now=True)
	origin = models.CharField(max_length=100, blank=True)
	meaning = models.CharField(max_length=100, blank=True)
	list = models.ForeignKey(List)

	def save(self, *args, **kwargs):
		self.list.date_modified = datetime.now()
		self.list.save() # Change 'date_modified' of list when its words are modified.
		super(Word, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.word
