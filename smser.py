import re
import sys
from xml.etree import ElementTree
from xml.dom import minidom

MSG_DRAFT='3'
MSG_SENT='2'
MSG_RCVD='1'

valid_msgs_types=[MSG_DRAFT, MSG_SENT, MSG_RCVD, None]

def readMsgs(f):
    result = ElementTree.parse(f)
    if(result.getroot().tag not in ['smses', 'allsms']):
        raise ValueError('Invalid root tag: {0}'.format(result.getroot().tag))
    if(int(result.getroot().get('count'))!=len(result.getroot().getchildren())):
        raise ValueError('Message count mismatch: expecting {0} messages, but there are {1} nodes'.format(resulttree.getroot().get('count'), len(result.getroot().getchildren())))
    for i in result.getroot():
        if i.tag not in ['sms', 'mms']:
            raise ValueError('Invalid message tag: {0}\n\tMessage is: {1}'.format(i.tag, i.items()))
        if(i.get('type') not in valid_msgs_types):
            raise ValueError('Not a valid msg type: {0}\n\tMessage is: {1}\n\tValid msg types are: {2}'.format(i.get('type'), i.items(), valid_msgs_types))
    return result


### NUMBER COMPLETION, e.g. 3452929414 -> +392929414

special_numbers=['4074800', '4890895', '4071160', '40333001', '4860000']
def numberCompletion(number):

    num = re.sub(r'\s', '', number)
    try:
        n=int(num)
    except ValueError:
        print('Warning: assuming that {0} is a valid number'.format(num))
        return num

#Trivial case
    if(num[0]=='+'):
        return num
#Italian/eu mobiles
    elif(num[0]=='3'):
        return '+39'+num
#Italian/eu with +39 - +35 and similars can be 0039/003x
    elif(num[0:3]=='003' and len(num)==14):
        return '+3'+num[3:]
#British mobiles
    elif(len(num)==11 and num[0:2]=='07'):
        return '+447'+num[2:]
#Italian landlines
    elif(len(num)==10 and num[0]=='0'):
        return '+39'+num
#Special
    elif(len(num)<7 or num in special_numbers):
        return num
    elif(len(num)<10 and num[0:3] in ['400', '407']):
        return num
    else:
        raise ValueError('No valid number: {0}'.format(num))

def buildFilteredTree(original, nodes):
#Rebuild new tree
    r = ElementTree.Element(original.getroot().tag)
#Set root attributes
    attribs=original.getroot().items()
    for i in attribs:
        r.set(i[0], i[1])
    r.set('count', str(len(nodes)))
    for x in nodes:
        r.append(x)
    resulttree = ElementTree.ElementTree(r)
    return resulttree

# Delete duplicates of a message based on address, body, and date
def fixAndDeleteDuplicates(messages):
    def getKey(m):
        return (m.get('address'), m.get('date'), m.get('body'))

    result={}
    ndups=0
    nmsgs=0
    ndropped=0
    dups={}
    for i in messages.getroot():
        nmsgs+=1

        if(i.get('type') in [None,MSG_DRAFT]):
            print(u'Warning: dropping draft: {0}'.format(i.items()))
            ndropped+=1
            continue

        i.set('address', numberCompletion(i.get('address')))
        key=getKey(i)
        if key in result:
            print(u'Duplicate found!\n\tOriginal: {0}\n\tDuplicate: {1}\n'.format(result[key].items(), i.items()))
            if(key not in dups):
                dups[key]=[]
            dups[key].append(i)
            ndups+=1
        else:
            result[key]=i

    ## Do some statistics
    sumdups = sum([len(dups[x]) for x in dups])
    assert(sumdups==ndups)

    assert(nmsgs == len(messages.getroot().getchildren()))

    print ("**********SUMMARY**********")
    for x in dups:
        print(u'Original message: {0} {1} at {2}:\n\t{3}'.format('To' if result[x].get('type') == MSG_SENT else 'From', result[x].get('address'), result[x].get('readable_date'), result[x].get('body')))
        for i in dups[x]:
            print(u'\t -> Duplicate: {0} {1} at {2}:\n\t{3}'.format('To' if i.get('type') == MSG_SENT else 'From', i.get('address'), i.get('readable_date'), i.get('body')))

    print ('{0} messages processed, {1} duplicated removed, {2} dropped'.format(nmsgs, ndups, ndropped))
    print ("************END************")
    resulttree = buildFilteredTree(messages, result.values())

    assert(len(resulttree.getroot().getchildren()) == nmsgs-ndups-ndropped)
    return resulttree
