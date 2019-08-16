#!/usr/bin/env python
# -*- mode: Python; tab-width: 4; indent-tabs-mode: nil; -*-
# ex: set tabstop=4
# Please do not change the two lines above. See PEP 8, PEP 263.


import os
import sys
import re

reload(sys)

sys.setdefaultencoding('utf8')

# folder = "/Users/penghuailiang/Desktop/hu'ailiang.github.io/"
folder = "/Users/penghuailiang/Documents/projects/huailiang.github.io/source/_posts/"


XML_1_0_VALID_HEX = [
    [0x0009],  # TAB
    [0x000A],  # LINEFEED
    [0x000D],  # CARRIAGE RETURN
    [0x0020, 0xD7FF],  # VALID CHARACTER RANGE 1
    [0xE000, 0xFFFD],  # VALID CHARACTER RANGE 2
]

XML_1_0_RESTRICTED_HEX = [
    [0x007F, 0x0084],  # one C0 control character and all but one C1 control
    [0x0086, 0x009F],  # one C0 control character and all but one C1 control
    [0xFDD0, 0xFDEF],  # control characters/permanently assigned to non-characters
]

if sys.maxunicode > 0x10000:
    XML_1_0_VALID_HEX.append((0x10000, min(sys.maxunicode, 0x10FFFF)))

# Add control characters and non-characters to the restricted range if this python
# build supports the applicable range
for i in [hex(i) for i in range(1, 17)]:
    if not sys.maxunicode >= int('{}FFFF'.format(i), 0):
        continue
    XML_1_0_RESTRICTED_HEX.append([
        int('{}FFFE'.format(i), 0),
        int('{}FFFF'.format(i), 0),
    ])

XML_1_0_VALID_UNI = ['-'.join([unichr(y) for y in x]) for x in XML_1_0_VALID_HEX]
INVALID_UNICODE_RAW_RE = ur'[^{}]'.format(''.join(XML_1_0_VALID_UNI))
"""The raw regex string to use when replacing invalid characters"""

INVALID_UNICODE_RE = re.compile(INVALID_UNICODE_RAW_RE, re.U)
"""The regex object to use when replacing invalid characters"""

XML_1_0_RESTRICTED_UNI = ['-'.join([unichr(y) for y in x]) for x in XML_1_0_RESTRICTED_HEX]
RESTRICTED_UNICODE_RAW_RE = ur'[{}]'.format(''.join(XML_1_0_RESTRICTED_UNI))
"""The raw regex string to use when replacing restricted characters"""

RESTRICTED_UNICODE_RE = re.compile(RESTRICTED_UNICODE_RAW_RE, re.U)
"""The regex object to use when replacing restricted characters"""

DEFAULT_REPLACEMENT = u'\uFFFD'
"""The default character to use when replacing characters"""


def replace_invalid_unicode(text, replacement=None):
    """Replaces invalid unicode characters with `replacement`
    Parameters
    ----------
    text : str
        * str to clean
    replacement : str, optional
        * default: None
        * if invalid characters found, they will be replaced with this
        * if not supplied, will default to DEFAULT_REPLACEMENT
    Returns
    -------
    str, cnt, RE : tuple
        * str : the cleaned version of `text`
        * cnt : the number of replacements that took place
        * RE : the regex object that was used to do the replacements
    """
    if replacement is None:
        replacement = DEFAULT_REPLACEMENT
    s, cnt = INVALID_UNICODE_RE.subn(replacement, text)
    return s, cnt, INVALID_UNICODE_RE

def rminvalid(file):
	if sys.maxunicode > 0x10000:
	    XML_1_0_VALID_HEX.append((0x10000, min(sys.maxunicode, 0x10FFFF)))
	txt = ""
	with open(file, 'r') as f:
		txt = f.read() 
		txt,c,re = replace_invalid_unicode(txt)
	with open(file, 'w') as f:
		f.write(txt)

def rm_all_invalid(folder):
	for d in os.listdir(folder):
		print("handle %s" % d)
		file =  os.path.join(folder,d)
		rminvalid(file)

def format_file(file):
	lines = []
	with open(file, 'r') as f:
		lines = f.readlines()
		for i in range(len(lines)):
			if "```" in lines[i]:
				line = lines[i]
				if "py" in line or "python" in line or "Python" in line:
					lines[i] = "{% highlight python %}\n"
					continue
				if "cs" in line or "csharp" in line or "c#" in line:
					lines[i] = "{% highlight csharp %}\n"
					continue
				if "bash" in line or "sh" in line or "shell" in line:
					lines[i] = "{% highlight bash %}\n"
					continue
				if "cpp" in line or "c" in line:
					lines[i] = "{% highlight cpp %}\n"
					continue
				if "groovy" in line:
					lines[i] = "{% highlight groovy %}\n"
					continue
				if "r" in line:
					lines[i] = "{% highlight r %}\n"
					continue
				if "lua" in line:
					lines[i] = "{% highlight lua %}\n"
					continue
				if "hlsl" in line:
					lines[i] = "{% highlight c %}\n"
					continue
				if "javascript" in line or "js" in line:
					lines[i] = "{% highlight javascript %}\n"
					continue
				if "html" in line or "json" in line:
					lines[i] = "{% highlight json %}\n"
					continue
				if line == "```\n" or line == "```` \n" or line == "``` \t\n" or line == ' ```\n' or line == "  ```\n":
					lines[i] = "{% endhighlight %}\n"
					continue

	with open(file, 'w') as f:
		f.writelines(lines)


def format_all_file(folder):
	for d in os.listdir(folder):
		file = os.path.join(folder,d)
		print("format %s" % file)
		format_file(file)


if __name__=='__main__':
	folder = "/Users/penghuailiang/Documents/projects/huailiang.github.io/source/_posts/"
	rm_all_invalid(folder)
