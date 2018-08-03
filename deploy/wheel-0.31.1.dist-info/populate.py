from __future__ import print_function
from bs4 import BeautifulSoup
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute
from time import sleep
import requests

class PaintingModel(Model):
    class Meta:
        table_name = "painting"
    
    episode = UnicodeAttribute(hash_key=True)
    title = UnicodeAttribute()
    colors = ListAttribute()

PaintingModel.create_table(read_capacity_units=1, write_capacity_units=1)

with requests.session() as session:
    response = session.get('https://www.twoinchbrush.com/colorsearch')

    soup = BeautifulSoup(response.text, features="html.parser")
    token = soup.find("input", {"name":"_token"})['value']
    
    response = session.post('https://www.twoinchbrush.com/colorsearch', data={'diff': '0', '_token': token, 
    'color2': 'on',
    'color15': 'on',
    'color12': 'on',
    'color18': 'on',
    'color9': 'on',
    'color4': 'on',
    'color14': 'on',
    'color11': 'on',
    'color17': 'on',
    'color16': 'on',
    'color5': 'on',
    'color7': 'on',
    'color8': 'on',
    'color6': 'on',
    'color1': 'on',
    'color13': 'on',
    'color3': 'on',
    'color10': 'on'})

    soup = BeautifulSoup(response.text, features="html.parser")

    paintings = soup.findAll('div', {'class': 'painting-holder'})
    for painting in paintings:
        title = painting.find('p').text
        episode = painting.find('p', {'class': 'details'}).text.split('\n')[1].strip()
        id = painting.find('img')['id'].split('painting')[1]
        
        painting_response = session.get('https://www.twoinchbrush.com/painting/{}'.format(id))
        paint_soup = BeautifulSoup(painting_response.text, features='html.parser')
        colors = [x for x in paint_soup.findAll('ul')[-2].text.strip().split('\n') if x != '']
        colors = [x.strip() for x in colors if x != '\r']
        
        painting_entry = PaintingModel()
        
        painting_entry.title = title
        painting_entry.episode = episode
        painting_entry.colors = colors

        painting_entry.save()
        print('Finished {} {} painting{}'.format(title, episode, id))
        sleep(1)