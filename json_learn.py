import json
import pymysql

hostname = ''
username = ''
password = ''
database = ''


def do_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.close()
    conn.close()
    return list(cursor.fetchall())


def get_sourceid_and_compare_result():
    conn = pymysql.connect(host=hostname, user=username, passwd=password,
                           db=database, charset="utf8")
    source_query = '''
                SELECT
                    source_id, compare_result
                FROM
                    subcrawl.source
                WHERE
                    last_process > DATE_SUB(NOW(), INTERVAL 168 HOUR)
                AND
                    status = 'COMPARED'
                ;
                '''
    source_list = do_query(conn, source_query)
    return source_list


for query_item in get_sourceid_and_compare_result():
    compare_result = query_item[1]
    data = json.loads(compare_result)
    countAddNum = 0
    countReopenNum = 0

    for subsourceKind in data:
        for key_subsourceKind, value_subsourceKind in subsourceKind.items():
            if (key_subsourceKind == 'addsubsource'):
                countAddNum = countAddNum + len(value_subsourceKind)

            # elif (key_subsourceKind == 'updatesubsource'):
            #     for updateSubsource in value_subsourceKind:
            #         for key_updateSubsource, value_updateSubsource in \
            #                 updateSubsource.items():
            #             if (value_updateSubsource == 'UPDATE: reopen'):
            #                 countReopenNum = countReopenNum + 1

            elif (key_subsourceKind in ['updatesubsource', 'othersource']):
                for updateSubsource in value_subsourceKind:
                    for key_updateSubsource, value_updateSubsource in \
                            updateSubsource.items():
                        if ('reopen' in str(value_updateSubsource)):
                            countReopenNum = countReopenNum + 1
                        elif ('add' in str(value_updateSubsource)):
                            countAddNum = countAddNum + 1
    print(query_item[0], countAddNum, countReopenNum)
