# Pad a rom out to 16kB with &FF bytes

import sys

fn, = sys.argv[1:]

out_fn = "%s.padded" % fn

print "padding %s to %s" % (fn, out_fn)

data = open(fn).read()
of = open(out_fn, 'w')
of.write(data)
of.write('\xff' * (16384 - len(data)))
