from django.shortcuts import render, redirect, reverse, get_object_or_404
from .models import Place
from .forms import NewPlaceForm, TripReviewForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

@login_required
def place_list(request):

    """If this is a POST request, the user clicked the Add button
    in the form. Check if the new place is valid, if so, save a 
    new Place to the database, and redirect to tis same page.
    This creats a GET request to this same route.
    
    If not a POST route, or Place is not valid, display a page with 
    a list of places and a form to add a new place.
    """

    if request.method == 'POST':
        #create new place
        form = NewPlaceForm(request.POST) #creating  a form from data in the request
        place = form.save(commit=False) #creating a model object from form
        place.user = request.user# associate the place with the logged-in user
        if form.is_valid(): #validation aganists database constraints
            place.save() #saves place to db 
            return redirect('place_list')#reloads home page
    
    #If not a POST, or the form is not valid, render the page
    #with the form to add a new place, and list of places
    places = Place.objects.filter(user=request.user).filter(visited=False).order_by('name')
    new_place_form = NewPlaceForm()#used to create HTML
    return render(request, 'travel_wishlist/wishlist.html', {'places': places, 'new_place_form': new_place_form})

@login_required
def places_visited(request):
    visited = Place.objects.filter(user=request.user).filter(visited=True).order_by('name')
    return render(request,'travel_wishlist/visited.html', {'visited': visited })

@login_required
def place_was_visited(request, place_pk):
    if request.method == 'POST':
        #pk = request.POST.get('pk')
        # place = Place.objects.get(pk=place_pk)
        place = get_object_or_404(Place, pk=place_pk)
        print(place.user, request.user)
        if place.user == request.user: # only let a user visit their own places
            place.visited = True
            place.save()
        else:
           return HttpResponseForbidden() 

    return redirect('place_list')   

@login_required
def about(request):
    author = 'Alicia'
    about = 'A website to create a list of places to visit'
    return render(request, 'travel_wishlist/about.html', {'author': author, 'about': about})


@login_required
def place_details(request, place_pk):
    
    place = get_object_or_404(Place, pk=place_pk)
    #return render(request, 'travel_wishlist/place_detail.html', {'place': place})

    # Does this place belong to the current user?
    if place.user != request.user:
        return HttpResponseForbidden()

    # is this a GET request (showdata + form), or a POST request (update Place object)?

    # if POST request, validate form data and update.
    if request.method == 'POST':
        form = TripReviewForm(request.POST, request.FILES, instance=place)
        # instance is the model object to update with the form data
        
        if form.is_valid():
            form.save()
            messages.info(request, 'Trip information updated!')
        else:
            messages.error(request, form.errors)

        return redirect('place_details', place_pk=place_pk)
    
    else:           
    # if GET request, show Place info and optional form.
    # If place is visited, show form; if place is not visited, no form.
        if place.visited:
            review_form = TripReviewForm(instance=place) #Pre-populate with data from this Place instance
            return render(request, 'travel_wishlist/place_detail.html', {'place': place, 'review_form': review_form})
        
        else:
            return render(request, 'travel_wishlist/place_detail.html', {'place': place})


@login_required
def delete_place(request, place_pk):
    place = get_object_or_404(Place, pk=place_pk) 
    if place.user == request.user:
        place.delete()
        return redirect('place_list')
    else:
        return HttpResponseForbidden()




    