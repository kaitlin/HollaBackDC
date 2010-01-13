# -*- mode: python; coding: utf-8; -*-

import os.path
import random
try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1

from django.db import settings
try:
    import Image
    import ImageFont
    import ImageDraw
except ImportError:
    if settings.CAPTCHA == 'simple':
        raise
    else:
        pass

from lib.threadlocals import get_request

def random_word(size=6):
    chars = "abcdefghijklmnopqrstuvwzyz0123456789"
    return ''.join(random.choice(chars) for x in xrange(size))

def solutions():
    session = get_request().session
    if not 'captcha_solutions' in session:
        session['captcha_solutions'] = {}
    return session['captcha_solutions']

def generate():
    solution = random_word()
    captcha_id =  sha1(solution).hexdigest()
    solutions()[captcha_id] = solution
    return captcha_id

def test_solution(captcha_id, solution):
    return solution == solutions().get(captcha_id, None)

def render(captcha_id, output):
    solution = solutions().get(captcha_id, 'foobar')
    fgcolor = 0xffffff
    bgcolor = 0x000000
    font = ImageFont.truetype(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data/Vera.ttf'), 25)
    dim = font.getsize(solution)
    im = Image.new('RGB', (dim[0] + 20, dim[1] + 10), bgcolor)
    d = ImageDraw.Draw(im)
    x, y = im.size
    #r = random.randint
    # draw 100 random colored boxes on the background
    #for num in range(100):
        #d.rectangle((r(0,x),r(0,y),r(0,x),r(0,y)),fill=r(0,0xffffff))
    # add the text to the image
    d.text((10, 5), solution, font=font, fill=fgcolor)
    #im = im.filter(ImageFilter.EDGE_ENHANCE_MORE)
    # save the image to a file
    im.save(output, format='JPEG')
