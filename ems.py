# -*- coding: utf-8 -*-
#!/usr/bin/env python
#simplejw
import time
import simplejson
import requests
import MySQLdb
from MySQLdb.cursors import DictCursor

if __name__ == "__main__":

    headers = {
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'
    }

    conn = MySQLdb.connect(host="localhost",user="root",passwd="",db="express",charset="utf8", cursorclass=DictCursor)
    cursor = conn.cursor()
    sql = "select order_id, ems_sn, delivery_id from orders where shipping_status >= 5 and shipping_status < 8 and ems_sn=51106599"
    cursor.execute(sql)

    orders = cursor.fetchall()

    for row in orders:
        time.sleep( 6 )

        now = int(time.time())
        sql = "select * from order_ems where order_id = %s" % row['order_id']
        cursor.execute(sql)

        ems = cursor.fetchone()

        if not ems:
            sql = "insert into order_ems (order_id, ems_sn, shipping_ext, updated) values (%s, %s, '', %s)"
            cursor.execute(sql, (row['order_id'], row['ems_sn'], now))

        #elif int(ems['updated']) - now < 3600:
        #        continue

        #url = "http://www.kuaidi100.com/query?id=1&type=ems&postid=%s" % row['ems_sn']
        
        if row['delivery_id'] == 1:
            url = "http://www.kuaidi100.com/query?id=1&type=ems&postid=%s" % row['ems_sn']
        elif row['delivery_id'] == 2:
            url = "http://www.kuaidi100.com/query?id=1&type=zhongtong&postid=%s" % row['ems_sn']

        r = requests.get(url, headers=headers)
        print r.text
        content = simplejson.loads(r.text)

        if content['message'] == "ok":
            content = content['data']
            content = simplejson.dumps(content, ensure_ascii=False)

            sql = "update order_ems set ems_sn = %s, shipping_ext = %s where order_id = %s"
            cursor.execute(sql, (row['ems_sn'], content, row['order_id']))

            if content.find(u'签收人') != -1:
                sql = "update orders set shipping_status = 8 where order_id = %s"
                cursor.execute(sql, (row['order_id'], ))

    conn.commit()