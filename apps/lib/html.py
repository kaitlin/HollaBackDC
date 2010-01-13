import htmlentitydefs
import re

pattern = re.compile("&(\w+?);")

def descape_entity(m, defs=htmlentitydefs.name2codepoint):
    # callback: translate one entity to its ISO Latin value
    try:
        return unichr(defs[m.group(1)])
    except KeyError:
        return m.group(0) # use as is

def descape(string):
    return pattern.sub(descape_entity, string)

