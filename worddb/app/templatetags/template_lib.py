
from django import template

register = template.Library()

@register.filter(name='automate')
def crazy(string): # Only one argument.
    s = []
    for i in range(string.__len__()):
    	if i % 2 == 0:
    		s.append(string[i].upper())
    	else:
    		s.append(string[i].lower())
    return ''.join(s)