# views.py
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import googlemaps
import pandas as pd
import os

API_KEY = 'AIzaSyDIes_GnJsg7McupweHTwFPcTTXbh7Ei3g'
gmaps = googlemaps.Client(key=API_KEY)

def home(request):
    return render(request, 'home.html')

def index(request):
    if request.method == 'POST':
        city = request.POST['city']
        radius = int(request.POST['radius'])
        segment = request.POST['segment']
        file_name = request.POST['file_name']

        df = search_places(city, radius, segment)
        if df is None:
          
            return render(request, 'home.html', {'error': 'Error in geocoding'})

       
        response = save_csv(df, file_name)

        if response is None:
            
            return render(request, 'home.html', {'error': 'Error saving CSV file'})

        return response

    return render(request, 'home.html')

def search_places(city, radius, segment):
    try:
        geocode_result = gmaps.geocode(city)
        latitude = geocode_result[0]['geometry']['location']['lat']
        longitude = geocode_result[0]['geometry']['location']['lng']
    except:
        return None

    df = pd.DataFrame(columns=['codigo', 'razao_social', 'telefone_1', 'telefone_2'])

    page_token = None
    while True:
        places = gmaps.places_nearby(location=(latitude, longitude), radius=radius, keyword=segment, page_token=page_token)

        

        for place in places['results']:
            place_details = gmaps.place(place['place_id'])['result']
            codigo = place_details.get('formatted_phone_number', None)
            razao_social = place_details['name']
            telefone_1 = place_details.get('formatted_phone_number', None)
            telefone_2 = ""
            df.loc[len(df)] = [codigo, razao_social, telefone_1, telefone_2]

        page_token = places.get('next_page_token')
        if not page_token:
            break

    return df

def save_csv(df, file_name):
    if not df.empty:
    
        csv_content = df.to_csv(index=False)

        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={file_name}.csv'

        return response

    return None
