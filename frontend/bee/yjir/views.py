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




def view_users(req):
	data = {"users": Destination.objects.all()}
	return render_to_response("users.html", data)

def add_user(req):
	if req.POST:
		
		# create the new user, and redirect to view
		# all of them. there is no way to "view" a
		# single user without editing it, right now
		u = Destination.objects.create(
			name          = req.POST["name"],
			phone_number  = req.POST["phone_number"],
			email_address = req.POST["email_address"])
		return HttpResponseRedirect("/yjir/users/")
		
	# not posting, just render the add/edit a user form
	data = { "form_action": req.META["PATH_INFO"] }
	return render_to_response("forms/user.html", data)

def edit_user(req, user_id):
	u = get_object_or_404(Destination, pk=user_id)
	data = { "form_action": req.META["PATH_INFO"], "user": u }
	return render_to_response("forms/user.html", data)




def msg(msg, link):
	data = { "msg": msg, "link": link }
	return render_to_response("msg.html", data)


def any_form(req, formClass, inst=None, init={}):
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
			
				# passed validation, socreate the new
				# instance and redirect to view it
				inst = form.save()
				url = inst.get_absolute_url()
				return msg("The %s (%s) was added." % (mdesc, inst), url)
		
		# "cancel" was clicked, so send the user back to
		# where they came from. this is crappy behavior,
		# but is overridden by JS where available
		else: return HttpResponseRedirect(req.META["HTTP_REFERER"])
	
	# render the form, whether this is the first
	# time (containing no data), or because the
	# submission FAILED the validation
	else: form = formClass(instance=inst, initial=init)
	return render_to_response(
		"forms/%s.html" % (mdesc),
		{ "form": form, "instance": inst })




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
	return any_form(req, ActionForm, init={"keyword": kw.pk})

def edit_action(req, scope_name, keyword_name, action_id):
	sc = get_object_or_404(Scope, name=scope_name)
	kw = get_object_or_404(Keyword, scope=sc, name=keyword_name)
	ac = get_object_or_404(Action, keyword=kw, pk=action_id)
	return any_form(req, ActionForm, inst=ac)




def add_actionx(req, scope_name, keyword_name):
	# ensure that we aren't creating an action in
	# a scope or keyword that doesn't already exist
	s  = get_object_or_404(Scope, name=scope_name)
	kw = get_object_or_404(Keyword, scope=s, name=keyword_name)
	
	if req.POST:
		# as above, create, and redirect to it
		# no checking for duplicates here
		ac = Action.objects.create(
			keyword=kw,
			bearer_type=req.POST["bearer_type"],
			reply_to_sender=(req.POST["reply_to_sender"]=="true"),
			destinations=req.POST["destinations"],
			payload=req.POST["payload"])
		
		# add all of the associated phone numbers
		#ac.set_destinations(req.POST["destinations"].splitlines())
		return HttpResponseRedirect("/yjir/" + scope_name + "/" + kw.name)
	
	# or render the add/edit an action form
	data = { "scope": s, "keyword": kw, "form_action": req.META["PATH_INFO"] }
	return render_to_response("forms/action.html", data)


def edit_actionx(req, scope_name, keyword_name, action_id):
	s  = get_object_or_404(Scope, name=scope_name)
	kw = get_object_or_404(Keyword, scope=s, name=keyword_name)
	ac = get_object_or_404(Action, keyword=kw, pk=action_id)
	
	if req.POST:
		if req.POST.has_key("delete"):
			ac.delete()
			
		if req.POST.has_key("submit"):
			ac.bearer_type     = req.POST["bearer_type"]
			ac.reply_to_sender = (req.POST["reply_to_sender"]=="true")
			#ac.set_destinations(req.POST["destinations"].splitlines())
			ac.destinations    = req.POST["destinations"]
			ac.payload         = req.POST["payload"]
			ac.save()
		
		# redirect to view the edited action (same destination for
		# all actions (submit, delete, cancel), because there is
		# no "view" for actions, only "edit"
		return HttpResponseRedirect("/yjir/" + s.name + "/" + kw.name)
	
	# the phone numbers are displayed in a textarea, one
	# per line, so fetch them all and flatten them to
	# be dumped into the template
	#numbers = ac.phonenumber_set.all().values_list("phone_number", flat=True)
	#flat_destinations = "\n".join(numbers)
	
	data = { "form_action": req.META["PATH_INFO"], "scope": s, "keyword": kw, "action": ac }#, "destinations": flat_destinations }
	return render_to_response("forms/action.html", data)

