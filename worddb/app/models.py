#!/usr/bin/env python
# app/models.py 

from django.db import models

from datetime import datetime
import hashlib

get_hash = lambda password: hashlib.sha224(password).hexdigest()

class User(models.Model):

	# fields:
	# first_name[20] // user's first name
	# email
	# password[56] (sha224 hash)

	first_name = models.CharField(max_length=20)
	email = models.EmailField(unique=True)
	password = models.CharField(max_length=56)

	def save(self, *args, **kwargs):
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

	def save(self, *args, **kwargs):
		self.list.date_modified = datetime.now()
		self.list.save() # change 'date_modified' of list when words are modified
		super(Word, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.word
