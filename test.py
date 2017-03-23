import MySQLdb
import csv
import time

# hostname = 'source.integrasco.com'
hostname = ''
username = ''
password = ''
database = ''


def do_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return list(cursor.fetchall())

def main():
    conn = MySQLdb.connect(host=hostname, user=username, passwd=password,
                           db=database, charset="utf8")
    source_query = '''SELECT  a.type,ms.name,ms.sourceid,a.type
                 FROM 	 source.mainsource as ms
                         join source.collectionconfig as cc
                             on ms.collectionId = cc.collectionid
                         join source.agentservice as a
                             on cc.agentserviceid = a.agentserviceid
                 where	cc.status = 1 and not(a.agentserviceid = 2 or a.type = 'MEDIA')
                 order by a.type asc;'''
    source_list = do_query(conn, source_query)
    source_list = add_source_to_list(source_list)
    file_name = "export_" + time.strftime("%Y_%m_%d") + ".csv"
    with open(file_name, 'w') as csvfile:
        fieldnames = ['Social Media', 'Source (s)', 'Code', 'Parent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        type_name_before = ""
        for rowTuple in source_list:
            # typeNameBefore = getType(sourceList, sourceList.index(rowTuple))
            row = transfor(rowTuple)
            if row[0] == type_name_before:
                pass
            else:
                writer.writerow(
                    {'Social Media': row[0], 'Source (s)': row[0],
                     'Code': row[3],
                     'Parent': None})
                type_name_before = row[0]
            writer.writerow(
                {'Social Media': row[0], 'Source (s)': row[1], 'Code': row[2],
                 'Parent': row[3]})
            print(row)
    conn.close()


main()
