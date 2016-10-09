import sys
from smser import numberCompletion, readMsgs, MSG_DRAFT, buildFilteredTree

if(len(sys.argv) < 4):
    print('Specify filename')
    sys.exit(1)


srcnumber = sys.argv[2]
dstnumber = sys.argv[3]

print('Parsing message file...')
e = readMsgs(sys.argv[1])
print('Done parsing file')

result = []
nmsg=0
for i in e.getroot():

    if(i.get('type') in [None, MSG_DRAFT]):
        print('Warning: dropping draft: {0}'.format(i.items()))
        continue

    try:
        num=numberCompletion(i.get('address'))
    except ValueError as x:
        print('MSG IS {0}'.format(i.items()))
        raise x
    if num == srcnumber:
        print(u'{0} : {1}'.format(i.get('type'), i.get('body')))
        i.set('address', dstnumber)
        i.set('type', '1' if type=='2' else '2')
        result.append(i)
        nmsg+=1


newe=buildFilteredTree(e, result)
assert(len(newe.getroot().getchildren()) == nmsg)
print ('{0} messages processed, {1} messages extracted'.format(len(e.getroot().getchildren()),nmsg))

newe.write(sys.argv[1]+'.new')



