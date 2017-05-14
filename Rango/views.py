from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    context_dic = {'boldmessage': "Rango says: When concatenating system paths together,"
                                  " always use os.path.join()."}
    return render(request, 'rango/index.html', context=context_dic)

def about(request):
    return HttpResponse('Rango says it is about page. | <a href="/rango">Rango</a> |')
