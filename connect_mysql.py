import mysql.connector

# try:
#     conn = mysql.connector.connect(host='127.0.0.1', user='root', password='admin123', database='forums_shard111')
# except mysql.connector.Error as err:
#     print(err)
# else:
#     cursor = conn.cursor()
#     cursor.execute("select * from forums_shard111.user;")
#     values = cursor.fetchall()
#     print(values)
#     print("___")
#     conn.close()
import time


def main():
    for idForDatashard in range(109, 116):
        shardName = "forums_shard" + str(idForDatashard)
        try:
            conn = mysql.connector.connect(host='127.0.0.1', user='root', password='admin123',
                                           database=shardName, charset="utf8")
        except mysql.connector.Error as err:
            print(err)
        else:
            cursor = conn.cursor()
            query = "select * from " + shardName + ".user;"
            try:
                cursor.execute(query)
                values = cursor.fetchall()
                print(values)
                print("___")
                conn.close()
            except mysql.connector.Error as err:
                print(err)
        print(shardName)
        time.sleep(1)

main()