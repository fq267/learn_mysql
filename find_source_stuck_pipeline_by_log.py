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
    file = open('/Users/fanq/Workspace/learn_mysql/forums_p7_1.log', 'r')
    lineNum = 0
    beginNum = get_the_first_visiting_line(file)
    visitLinks, cleanLinks, failedLinks = [], [], []
    for line in file:
        lineNum += 1
        if lineNum > beginNum - 1:
            if line.startswith('INFO: [SiteLevel:0]Visiting'):
                visitlink = line.split('Visiting ')[1]
                visitLinks.append(visitlink[:-1])
            elif line.startswith('INFO: Cleaning'):
                resultlink = line.split('retrieved from ')[1]
                try:
                    link = resultlink.split('replies')[0]
                    cleanLinks.append(link[ :-1])
                except:
                    cleanLinks.append(resultlink)
            elif line.startswith('The url that failed: '):
                failedlink = line.split('The url that failed: ')[1]
                try:
                    link = failedlink.split('replies')[0]
                    failedLinks.append(link[ :-1])
                except:
                    failedLinks.append(failedlink)

    file.close()
    return {'visit':visitLinks,'clean':cleanLinks,'failed':failedLinks}

def get_the_first_visiting_line(file):
    lineNum = 0
    for line in file:
        lineNum += 1
        if line.startswith('INFO: [SiteLevel:0]Visiting'):
            return lineNum


linksInDict = get_the_list_of_links()
vlinks = linksInDict.get('visit')
clinks = linksInDict.get('clean')
flinks = linksInDict.get('failed')
for link in vlinks + flinks:
    if link in clinks:
        pass
    else:
        print(link)