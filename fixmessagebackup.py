import sys
from smser import fixAndDeleteDuplicates, readMsgs

if(len(sys.argv) < 2):
    print('Specify filename')
    sys.exit(1)

e = readMsgs(sys.argv[1])

print('Done parsing file')

newe = fixAndDeleteDuplicates(e)


print('FINISHED')

newe.write(sys.argv[1]+'.new')

