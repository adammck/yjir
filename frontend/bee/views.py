from django.http import HttpResponseRedirect

# there are no global views yet, so
# just redirect the index to YJIR

def index(request):
    return HttpResponseRedirect("/yjir/")

