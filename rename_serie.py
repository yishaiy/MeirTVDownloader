import os
import sys


def rename(line):
    idx, url, filename, title, ref = line.split('||')
    if os.path.exists(filename):
    	# ref = ref.translate(None, '!?"')
    	title = title.translate(None, ':*<>|!?"\'')
    	newfilename = '{idx}_{name}.mp3'.format(idx=idx, name=title).decode('utf8')
    	print '{0} => {1}'.format(filename, repr(newfilename))
        os.rename(filename, newfilename)


if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
	print 'Usage: {0} <lessons.info>'
	exit(0)

content = open(sys.argv[1], 'rb').read()
lines = filter(lambda l: l != '', content.split('\n'))

for l in lines:
	rename(l)
