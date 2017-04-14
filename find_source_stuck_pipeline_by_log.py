import re


# def get_the_list_of_links():
#     file = open('/home/fanq/Workspace/learn_mysql/forums_p7.log', 'r')
#     lineNum = 0
#     listOfLinks = []
#     for line in file:
#         lineNum = lineNum + 1
#         lineContainLink = re.findall(
#             r'https?://[a-z-A-Z0-9]+\.[0-9a-z-A-Z_.%]+\.[a-z.]+/['
#             r'a-z-0-9%A-Z.?/&=]+',
#             line)
#         if (len(lineContainLink) > 0):
#             lineContainSubsource = re.findall(r'SubSourceLink', line)
#             if (len(lineContainSubsource) > 0):
#                 pass
#             elif(re.search(r'http\sstatuscode\sreturned\sby\sthe\sserver',
#                            line)):
#                 pass
#             else:
#                 listOfLinks.append(lineContainLink[0])
#         listOfLinks.sort()
#     return listOfLinks

def get_the_list_of_links():
    file = open('/home/fanq/Workspace/learn_mysql/forums_p7.log', 'r')
    lineNum, beginNum= 0
    listOfLinks = []
    for line in file:
        lineNum = lineNum + 1
        if
        listOfLinks.sort()
    return listOfLinks


listOfLinks = get_the_list_of_links()

print(len(listOfLinks))
for i in range(0, len(listOfLinks) - 1):
    try:
        itemOfLink = listOfLinks.pop(0)
        if (itemOfLink in listOfLinks):
            listOfLinks.remove(itemOfLink)
        else:
            print(itemOfLink)
    except:
        pass
