# django
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

# yjir
from bee.yjir.models import *
from bee.yjir.forms import *




def dashboard(req, scope_name=None, keyword_name=None, action_id=None):

	# all scopes are displayed
	# in the first column
	data = {"scopes": Scope.objects.all()}
	
	# once a scope has been selected,
	# a list of keywords belonging to
	# it is displayed in the middle
	if scope_name:
		scope = get_object_or_404(Scope, name=scope_name)
		data["keywords"] = scope.keyword_set.all()
		data["this_scope"] = scope
		
		# same for actions, once a
		# keyword has been selected
		if keyword_name:
			keyword = get_object_or_404(Keyword, scope=scope, name=keyword_name)
			data["actions"] = keyword.action_set.all()
			data["this_keyword"] = keyword
			
			# there is nothing iterable in an
			# action, so just add the object
			if action_id:
				action = get_object_or_404(Action, keyword=keyword, pk=action_id)
				data["this_action"] = action
	
	return render_to_response("index.html", data)




def msg(msg, link):
	data = { "msg": msg, "link": link }
	return render_to_response("msg.html", data)


def any_form(req, formClass, inst=None, init={}, tmpl_data={}):
	model = formClass.Meta.model
	mdesc = model.__name__.lower()
	
	if req.POST:
		
		# if the "delete" button was clicked,
		# destroy the instance, and inform the
		# user. the template also contains JS
		# to close the lightbox, if necessary
		if inst and req.POST.has_key("delete"):
			inst.delete()
			return msg("The %s was deleted." % (mdesc), "/yjir/")
		
		# only proceed if the "submit" button was
		# clicked, to allow "cancel" to pass through
		elif req.POST.has_key("submit"):
			
			# parse and validate the submission
			form = formClass(req.POST, instance=inst)
			if form.is_valid():
				
				# passed validation, so create/update
				# the instance and redirect to view it
				inst = form.save()
				url = inst.get_absolute_url()
				return msg("The %s (%s) was saved" % (mdesc, inst), url)
		
		# "cancel" was clicked, so send the user back to
		# where they came from. this is crappy behavior,
		# but is overridden by JS where available
		else: return HttpResponseRedirect(req.META["HTTP_REFERER"])
	
	# render the form, whether this is the first
	# time (containing no data), or because the
	# submission FAILED the validation
	else: form = formClass(instance=inst, initial=init)
	
	tmpl_data.update({
		"instance": inst,
		"form": form
	})
	
	return render_to_response(
		"forms/%s.html" % (mdesc),
		tmpl_data)




# ==== SCOPES ====

def add_scope(req):
	return any_form(req, ScopeForm)

def edit_scope(req, scope_name):
	sc = get_object_or_404(Scope, name=scope_name)
	return any_form(req, ScopeForm, inst=sc)


# ==== KEYWORDS ====

def add_keyword(req, scope_name):
	sc = get_object_or_404(Scope, name=scope_name)
	return any_form(req, KeywordForm, init={"scope": sc.pk})

def edit_keyword(req, scope_name, keyword_name):
	sc = get_object_or_404(Scope, name=scope_name)
	kw = get_object_or_404(Keyword, scope=sc, name=keyword_name)
	return any_form(req, KeywordForm, inst=kw)


# ==== ACTIONS ====

def add_action(req, scope_name, keyword_name):
	sc = get_object_or_404(Scope, name=scope_name)
	kw = get_object_or_404(Keyword, scope=sc, name=keyword_name)
	return any_form(req, ActionForm, init={"keyword": kw.pk}, tmpl_data = { "recipients": range(10) })

def edit_action(req, scope_name, keyword_name, action_id):
	sc = get_object_or_404(Scope, name=scope_name)
	kw = get_object_or_404(Keyword, scope=sc, name=keyword_name)
	ac = get_object_or_404(Action, keyword=kw, pk=action_id)
	return any_form(req, ActionForm, inst=ac, tmpl_data = { "recipients": range(10) })

