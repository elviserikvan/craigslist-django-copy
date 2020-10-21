from django.shortcuts import render
from bs4 import BeautifulSoup
from requests.compat import quote_plus
from . import models
import requests

BASE_CRAIGLIST_URL = 'https://losangeles.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'

def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get('search')
    models.Search.objects.create(search=search) # Add search query to database history
    final_url = BASE_CRAIGLIST_URL.format(quote_plus(search)) # Format url with user parameters


    """ Make the request and get the html code """
    response = requests.get(final_url)
    data = response.text


    """ Start scrapping """
    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_postings = []
    for post in post_listings:

        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')

        """Trying to get the post price """
        if post_listings[0].find(class_='result-price'):
            post_price = post_listings[0].find(class_='result-price').text
        else:
            post_price = 'N/A'


        """Trying to get the post image """
        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image_url = 'https://craigslist.org/images/peace.jpg'


        final_postings.append((post_title, post_url, post_price, post_image_url))




    """Send it to the view and render it """
    stuff_for_frontend = {
            'search': search,
            'final_postings': final_postings
    }
    return render(request, 'my_app/new_search.html', stuff_for_frontend)
