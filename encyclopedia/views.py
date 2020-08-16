from markdown2 import markdown
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render
from django.urls import reverse
from random import randrange

from . import util

class NewPage(forms.Form):
    title = forms.CharField(label='Title', min_length=1)
    content = forms.CharField(label='', widget=forms.Textarea)


def index(request):
    if request.method == "POST":
        search = request.POST["q"]
        entries = util.list_entries()
        results = []
        for entry in entries:
            key = entry.lower()
            n = key.find(search.lower())
            print(search, entry, n)
            if n != -1:
                results.append(entry)
        for result in results:
            if result.lower() == search.lower():
                return HttpResponseRedirect(result)
        return render(request, "encyclopedia/index.html", {
            "entries": results,
            "search": 1,
        })

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })

def edit(request, entry):
    if request.method == "POST":
        entry = request.POST['entry']
        content = request.POST['content']
        util.save_entry(entry, content)
        return HttpResponseRedirect(f"/wiki/{entry}")
    content = util.get_entry(entry)
    return render(request, "encyclopedia/edit.html", {
        "entry": entry,
        "content": content
    })
    

def entry(request, entry):
    content = util.get_entry(entry)
    if not content:
        return HttpResponse("Error: Entry not found")
    return render(request, "encyclopedia/entry.html", {
        "title": entry,
        "content": util.markdown(content)
    })

def new(request):
    if request.method == "POST":
        form = NewPage(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            entries = util.list_entries()

            for entry in entries:
                if entry.lower() == title.lower():
                    return render(request, "encyclopedia/new.html", {
                        "form": form,
                        "error": 1,
                        "error_message": "Error: Title already in use"
                    })
            
            util.save_entry(title, content)
            return HttpResponseRedirect(title)

        return HttpResponse("Error: TO DO")
    
    return render(request, "encyclopedia/new.html", {
        "form": NewPage
    })

def random(request):
    entries = util.list_entries()
    random = randrange(len(entries))
    entry = entries[random]
    return HttpResponseRedirect(entry)