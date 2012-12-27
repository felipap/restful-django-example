
from django import template

import datetime, re

# this module was created while learning about tags and filters creating (django book chapter 9, a though one...)

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

@register.tag(name="get_current_time")
def do_current_time(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, arg = token.contents.split(' ', 1) 
    except ValueError: 
        msg = '%r tag requires a single argument' % token.split_contents()[0]
        raise template.TemplateSyntaxError(msg)
    
    m = re.search(r'(.*?) as (\w+)', arg)
    if m:
    	fmt, var_name = m.groups()
    else:
    	msg = '%r tag had invalid arguments' % tag_name
    	raise template.TemplateSyntaxError(msg)

    if not (fmt[0] == fmt[-1] and fmt[0] in ('"', "'")):
    	msg = "%r tag's agument should be in quotes" % tag_name
    	raise template.TemplateSyntaxError(msg)
    
    return CurrentTimeNode(fmt[1:-1], var_name)


class CurrentTimeNode(template.Node):
    def __init__(self, format_string, var_name):
	 	self.format_string = str(format_string)
	 	self.var_name = var_name

    def render(self, context):
        now = datetime.datetime.now()
        context[self.var_name] = now.strftime(self.format_string)
        return ''
