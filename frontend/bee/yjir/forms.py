from django.forms import ModelForm
from bee.yjir.models import *

class ScopeForm(ModelForm):
	class Meta:
		model = Scope

class KeywordForm(ModelForm):
	class Meta:
		model = Keyword

class ActionForm(ModelForm):
	class Meta:
		model = Action

