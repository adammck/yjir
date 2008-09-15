from django.forms import ModelForm, fields, widgets
from bee.yjir.models import *
import re




# this field is for entering scopes and keywords which will
# be SMSed into the system, so must be kept short and simple
class LowerCaseLettersField(fields.RegexField):
	default_error_messages = {
		"invalid": "Enter a valid 'slug' containing only letters"}
	
	def __init__(self, *args, **kwargs):
		super(LowerCaseLettersField, self).__init__(
			re.compile(r'^[a-z]+$'), *args, **kwargs)

class ScopeForm(ModelForm):
	class Meta: model = Scope
	name = LowerCaseLettersField()

class KeywordForm(ModelForm):
	class Meta: model = Keyword
	name = LowerCaseLettersField()




# this field is especially for entering a list of
# destination phone numbers into the action form
class DestinationsField(fields.RegexField):
	widget = widgets.Textarea(attrs = {"cols": 24, "rows": 3})
	
	default_error_messages = {
		"invalid": "Destinations may only contain digits and newlines"}
	
	def __init__(self, *args, **kwargs):
		super(DestinationsField, self).__init__(
			re.compile(r'^[\d\r\n]+$'), *args, **kwargs)

class ActionForm(ModelForm):
	class Meta: model = Action
	#destinations = DestinationsField()
		

