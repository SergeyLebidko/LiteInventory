from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'main/index.html', context={})


@login_required
def inventory(request):
    return render(request, 'main/inventory.html', context={})
