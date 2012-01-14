
# dbhelper.py

from app.models import User, List, Word, get_hash

import hashlib

# API:
## _get_user([userid],[email],[password])
## _get_list(user, listlabel)
## _get_word(list, wordid)

## _in_user_database(email [, password])
## _in_list_database(user, listid)
## _in_word_database(list, worid)

def _in_user_database(email, password=None):
	return bool(email=email, password=password)
	
def _in_list_database(user, listlabel=None, listid=None):
	return bool(_get_list(user=user, listlabel=listlabel, listid=listid))

def _in_word_database(list, word=None, wordid=None):
	return bool(_get_word(list=list, word=word, wordid=wordid))

###

def _get_user(userid=None, email=None, password=None):
	
	try:
		args = dict()
		if userid != None: args['userid'] = userid
		if email != None: args['email'] = email
		if password != None: # THIS IS CRUCIAL, PASSWORD IS HASHED !HERE!
			args['password'] = get_hash(password)
		
		assert args, 'you ought to give me something :P'
		return User.objects.get(**args)
	except User.DoesNotExist:
		return None

def _get_list(user, listid):
	
	try:
		return user.list_set.get(id=listid)
	except List.DoesNotExist:
		return None

def _get_word(list, wordid):

	try:
		return list.word_set.get(id=wordid)
	except Word.DoesNotExist:
		return None

###