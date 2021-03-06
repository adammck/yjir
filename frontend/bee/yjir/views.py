# django
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

# yjir
from bee.yjir.models import *
from bee.yjir.forms import *

# for test button
import bee.settings as settings
import urllib




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


def backend_test(req):
	if req.POST:
		# forward the message to kannel, and just
		# output the result as plain text (this is
		# just for development, should be hidden)
		msg = urllib.quote_plus(req.POST["msg"])
		url = "http://localhost:%d/?callerid=%s&message=%s"\
		      % (settings.KANNEL_PORT_RECEIVE, settings.TEST_NUMBER, msg)
		result = urllib.urlopen(url).read()
		return HttpResponse(result, mimetype="text/plain")
		
	else:
		# this view should only be called via post,
		# so throw an ugly error if we end up here
		from django.http import HttpResponseNotAllowed
		return HttpResponseNotAllowed(["POST"])


def api(req, scope_name, keyword_name):
	if req.POST:
		pass
	
	else:
		# the API is only available via POST, for now
		from django.http import HttpResponseNotAllowed
		return HttpResponseNotAllowed(["POST"])
	




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
	
	# fetch the destinations already attached to this
	# action, and pad the array up to ten items (to help
	# render the spare form fields without javascript)
	dests = list(ac.destination_set.all())
	show_others = True if len(dests) else False
	if len(dests) < 10: dests.extend(range(10-len(dests)))

	
	# actions are considerably more complicated
	# than the other classes, so do some post-
	# processing here	
	if req.POST:
	
		# arbitrary upper boundary
		# for other destinations
		for n in range(10):
			
			# pluck out all relevant fields with blank
			# defaults, to avoid raising KeyErrors
			pk   = req.POST.get("recip_%d_pk"   % (n), "")
			type = req.POST.get("recip_%d_type" % (n), "")
			dest = req.POST.get("recip_%d_dest" % (n), "")
			
			# if a primary key was provided, then we are
			# updating (or deleting!) an existing destination
			if pk:
				dest_obj = Destination.objects.get(pk=pk)
			
				if type and dest:
					dest_obj.type = type
					dest_obj.dest = dest
					dest_obj.save()
		
				# if the destination was cleared, then
				# destroy the object. just to keep the
				# database tidy, really
				else: dest_obj.delete()
		
			# no pk provided; if a type and destination
			# were entered here, it's brand new in the db
			elif type and dest:
				Destination.objects.create(
					action=ac,
					type=type,
					dest=dest)
	
		# if "save+test" were clicked, then simulate
		# a kannel callback (to the backend.py)
		if req.POST.has_key("submit") and req.POST["submit"] == "Submit + Test":
			url = "http://localhost:%d/?callerid=%s&message=action+%d"\
				  % (settings.KANNEL_PORT_RECEIVE, settings.TEST_NUMBER, int(action_id))
			urllib.urlopen(url).read()
	
	# finally, render the action form
	return any_form(req, ActionForm, inst=ac, tmpl_data = { "recipients": dests, "show_others": show_others })

