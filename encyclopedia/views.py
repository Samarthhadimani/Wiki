from django.http import HttpResponseNotFound,HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.shortcuts import render
import markdown2
from . import util
from django.contrib import messages
import random

class NewPageForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def page(request,title):
    content=util.get_entry(title)
    if content:
        return render(request,"encyclopedia/page.html",{
            "title": title.capitalize(),
            "content": markdown2.markdown(content)
        })
    else:
        return HttpResponseNotFound("Page not found")
    
class SearchView():
    # model = Products
    template_name = 'encyclopedia/page.html'
    context_object_name = 'all_search_results'

    def get_queryset(self):
        print('I am here')
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            postresult = util.get_entry.filter(title__contains=query)
            result = postresult
        else:
            result = None
        return result


def search(request):
    query = request.GET.get('q')
    result = []
    if query:
        result = util.search(query)
        if len(result) ==1 :
            return render(request,"encyclopedia/page.html",{
                "title": result[0],
                "content": markdown2.markdown(util.get_entry(result[0]))
            })
        else :
            return render(request,"encyclopedia/index.html",{
                "entries": result
            })
    else:
        return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
        })

def new(request):
    if request.method == "GET":
        return render(request,"encyclopedia/new.html",{
            "form": NewPageForm()
        })
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if(form.is_valid()):
            title=form.cleaned_data['title']
            title=title.lower()
            content=form.cleaned_data["content"]
            list=[entry.lower() for entry in util.list_entries()]
            if title in list:
                messages.add_message(
                    request,
                    messages.WARNING,
                    message=f'Entry "{title}" already exists',
                )
            else:
                with open(f"entries/{title}.md","w") as file:
                    file.write(content)
                    return render(request,"encyclopedia/page.html",{
                        "title": title,
                        "content": markdown2.markdown(content)
                    })
        else:
            messages.add_message(
                request, messages.WARNING, message="Invalid request form"
            )

    return render(
        request,
        "encyclopedia/new.html",
        {"form": form},
    )
   
            
def random_page(request):
    list=util.list_entries()
    return page(request,random.choice(list))