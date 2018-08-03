from __future__ import print_function
from bs4 import BeautifulSoup
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute
from time import sleep
import requests
import random
import json

class PaintingModel(Model):
    class Meta:
        table_name = "painting"
    
    episode = UnicodeAttribute(hash_key=True)
    title = UnicodeAttribute()
    colors = ListAttribute()

paintings = json.loads(PaintingModel.dumps())
table_len = len(paintings)
random_index = random.randint(0, table_len-1)
painting = paintings[random_index]

episode = painting[0]
title = painting[1]['attributes']['title']['S']
colors = [x['S'] for x in painting[1]['attributes']['colors']['L']]
