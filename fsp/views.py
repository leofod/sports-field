from django.shortcuts import render

def handler404(request, *args, **kwargs):
    if(request.session.get('user_id')):
        url = 'log.html'
    else:
        url = 'nolog.html'

    return render(request, 'errs/404.html', {"url": url}, status=404)

def handler403(request, *args, **argv):
    if(request.session.get('user_id')):
        url = 'log.html'
    else:
        url = 'nolog.html'
    return render(request, 'errs/403.html', {"url": url}, status=403)

def handler500(request, *args, **argv):
    if(request.session.get('user_id')):
        url = 'log.html'
    else:
        url = 'nolog.html'
    return render(request, 'errs/500.html', {"url": url}, status=500)
