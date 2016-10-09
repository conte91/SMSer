import sys
from smser import numberCompletion, readMsgs, MSG_DRAFT, buildFilteredTree

if(len(sys.argv) < 2):
    print('Specify filenames')
    sys.exit(1)


filenames=sys.argv[1:]

es=[]
for x in filenames:
    print('Parsing message file: {0}...'.format(x))
    e = readMsgs(x)
    print('Done parsing file')
    es.append(e)

result = []
for i in es:
    result+=i.getroot().getchildren()

newe=buildFilteredTree(es[0], result)
sums=sum([len(e.getroot().getchildren()) for e in es])
assert(len(newe.getroot().getchildren()) == sums)
print ('{0} messages processed'.format(sums))

newe.write(sys.argv[1]+'.new')



