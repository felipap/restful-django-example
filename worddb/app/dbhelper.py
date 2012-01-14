
# dbhelper.py

from app.models import User, List, Word

import hashlib

get_hash = lambda password: hashlib.sha224(password).hexdigest()

# API doc
# _get_user([userid]|[email] [, password])
# in_user_database(email [, password])

# _get_list(user, listlabel)
# _in_list_database(user, listlabel|listid)
# _get_word(list, word|wordid)
# _in_word_database(list, word|worid)

def _get_user(userid=None, email=None, password=None):
	# returns user if found
	# return None otherwise

	assert userid or email, 'gimme something, for god\'s sake!'
	try:
		if userid: u = User.objects.get(id=userid)
		else: u = User.objects.get(email=email)
		if password:
			if not u.password == get_hash(password):
				raise User.DoesNotExist
		return u
	except User.DoesNotExist:
		return None

def _in_user_database(email, password=None):
	# return True if user found
	# return None otherwise
	u = _get_user(email=email)
	if password is None:
		return bool(u)
	if u and u.password == get_hash(password):
		return True
	return False

###
###

def _get_list(user, listlabel=None, listid=None):
	# returns the list if list found
	# returns None otherwise
	try:
		if listlabel:
			return user.list_set.get(label=listlabel)
		else: return user.list_set.get(id=listid)
	except List.DoesNotExist:
		return None

def _in_list_database(user, listlabel=None, listid=None):
	# returns True if word found
	# returns False otherwise
	return bool(_get_list(user=user, listlabel=listlabel, listid=listid))

###
###

def _get_word(list, word=None, wordid=None):
	# returns word if word found
	# return None otherwise
	try:
		if word:
			return list.word_set.get(word=word)
		else: return list.word_set.get(id=wordid)
	except Word.DoesNotExist:
		return None

def _in_word_database(list, word=None, wordid=None):
	# return True if word found
	# returns False otherwise
	return bool(_get_word(list=list, word=word, wordid=wordid))

###
###