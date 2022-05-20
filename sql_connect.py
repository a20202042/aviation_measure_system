import MySQLdb, base64, time, global_var as gvar


class sql_connect:

    def __init__(self):
        self.sql_host = '163.18.69.14'
        self.sqldb = 'pdal-measurement-2021'
        self.sql_user = 'root'
        self.sql_charset = 'utf8'
        self.sql_password = 'rsa+0414018'
        self.all_name = [
            'mysite_project', 'mysite_measure_items', 'mysite_measurement_work_order_create',
            'mysite_measuring_tool']
        self.project_item = ['project_name', 'project_create_time', 'founder_name', 'remake']
        self.project_work_order = ['project_name', 'sor_no', 'part_no', 'number_of_part', 'materials',
                                   'manufacturing_machine',
                                   'batch_number', 'class', 'inspector', 'remake']
        self.measur_tool = ['tool_name', 'tool_type', 'tool_precision', 'tool_test_date']
        self.measure_item = ['project_name', 'tool_name', 'measure_items', 'upper', 'lower', 'center', 'decimal_piaces']
        self.conn = MySQLdb.connect(host=(self.sql_host), user=(self.sql_user), passwd=(self.sql_password),
                                    db=(self.sqldb), charset=(self.sql_charset))
        self.cursor = self.conn.cursor()

    def sql_all_date(self, table_name):
        SQL = 'SELECT * FROM  %s' % table_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        list_data = []
        for item in data:
            all_data = list(item)
            all_data.pop(0)
            list_data.append(all_data)

        print('%s_all_date:%s' % (table_name, list_data))
        return list_data

    def sql_find_project(self, project_name):
        SQL = " SELECT *  From mysite_project WHERE mysite_project.project_name = '%s' " % project_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        list_data = []
        for i in data:
            list_data.append(i)

        print(data)
        return list_data

    def sql_find_work_order(self, project_name):
        SQL = "SELECT *  From  mysite_measurement_work_order_create  WHERE mysite_measurement_work_order_create.project_measure_id=(SELECT mysite_project.id FROM mysite_project WHERE mysite_project.project_name='%s')" % project_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        list_data = []
        for item in data:
            all_data = list(item)
            all_data.pop(0)
            all_data.pop(-1)
            all_data.insert(0, project_name)
            list_data.append(all_data)

        return list_data

    def sql_find_work_order_all(self, project_name):
        SQL = "SELECT mysite_measurement_work_order.sor_no, mysite_measurement_work_order.number_of_parts, mysite_measurement_work_order.create_time,mysite_measurement_work_order.remake, mysite_measurement_work_order.measure_state  From  mysite_measurement_work_order  WHERE mysite_measurement_work_order.project_measure_id=(SELECT mysite_project.id FROM mysite_project WHERE mysite_project.project_name='%s')" % project_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        list_data = []
        for item in data:
            if item[(-1)] == 'OK':
                pass
            else:
                all_data = list(item)
                list_data.append(all_data)

        return list_data

    def sql_find_measure_item(self, project_name):
        SQL = "SELECT mysite_measure_items.measurement_items,mysite_measure_items.upper_limit, mysite_measure_items.lower_limit, mysite_measure_items.specification_center, mysite_measure_items.decimal_piaces, mysite_measure_items.measure_unit, mysite_measure_items.measure_points, mysite_measure_items.measure_number, mysite_measure_items.too_name_id  From  mysite_measure_items  WHERE mysite_measure_items.project_measure_id=(SELECT mysite_project.id FROM mysite_project WHERE mysite_project.project_name='%s')" % project_name
        self.measure_item = ['量測專案名稱', '量測項目名稱', '量測數值上限', '量測數值下限', '量測數值中心',
                             '量測小數點位數', '量測單位', '量測點數', '量測次數', '量具名稱']
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        list_data = []
        for item in data:
            data = list(item)
            SQL = 'SELECT mysite_measuring_tool.toolname From  mysite_measuring_tool WHERE mysite_measuring_tool.id = %s' % \
                  data[(-1)]
            self.cursor.execute(SQL)
            tool_name = self.cursor.fetchall()[0][0]
            data.pop(-1)
            data.append(tool_name)
            data.insert(0, project_name)
            list_data.append(data)

        return list_data

    def sql_work_order_id(self, work_order_name):
        SQL = "SELECT mysite_measurement_work_order.id FROM mysite_measurement_work_order WHERE mysite_measurement_work_order.sor_no='%s'" % work_order_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        list_data = []
        for item in data:
            list_data = item[0]

        print(list_data)
        return list_data

    def sql_work_order_sor_no_data(self, id):
        SQL = "SELECT mysite_measurement_work_order.sor_no, mysite_measurement_work_order.number_of_parts, mysite_measurement_work_order.create_time,mysite_measurement_work_order.remake, mysite_measurement_work_order.measure_state  From  mysite_measurement_work_order  WHERE mysite_measurement_work_order.id='%s'" % id
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        list_data = []
        for item in data:
            list_data.append(item)

        print(list_data)
        return list_data

    def sql_work_order_measure_item(self, work_order_id):
        SQL = "SELECT mysite_work_order_measure_items.measurement_items,mysite_work_order_measure_items.upper_limit, mysite_work_order_measure_items.lower_limit, mysite_work_order_measure_items.specification_center,mysite_work_order_measure_items.measure_unit,  mysite_work_order_measure_items.measure_number, mysite_work_order_measure_items.tool_name_id  From  mysite_work_order_measure_items  WHERE mysite_work_order_measure_items.measurement_work_order_id='%s'" % work_order_id
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        list_data = []
        for item in data:
            item = list(item)
            tool_name = self.sql_tool_name(item[(-1)])
            item[-1] = tool_name
            list_data.append(item)

        return list_data

    def sql_tool_name(self, tool_id):
        SQL = "SELECT mysite_measuring_tool.toolname FROM mysite_measuring_tool WHERE mysite_measuring_tool.id='%s'" % tool_id
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        tool_name = data[0][0]
        return tool_name

    def sql_version(self):
        self.cursor.execute('SELECT VERSION()')
        return self.cursor.fetchone()

    def sql_insert_value(self, data):
        data_list = []
        time_now = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime())
        for value_data in data:
            # SQL = "SELECT mysite_work_order_measure_items.id  From  mysite_work_order_measure_items  WHERE mysite_work_order_measure_items.measurement_items = '%s'" % value_data[(-4)]
            # self.cursor.execute(SQL)
            # mysite_work_order_measure_items_id = list(self.cursor.fetchone())[0]
            # print(mysite_work_order_measure_items_id)
            SQL = "SELECT mysite_measurement_work_order.project_measure_id   From  mysite_measurement_work_order  WHERE mysite_measurement_work_order.sor_no = '%s'" % gvar.work_order
            self.cursor.execute(SQL)
            meaure_project_id = list(self.cursor.fetchone())[0]
            SQL = "SELECT mysite_measuring_tool.id   From  mysite_measuring_tool  WHERE mysite_measuring_tool.toolname = '%s'" % \
                  value_data[(-2)]
            self.cursor.execute(SQL)
            measure_tool_id = list(self.cursor.fetchone())[0]
            SQL = "SELECT mysite_measurement_work_order.id   From  mysite_measurement_work_order  WHERE mysite_measurement_work_order.sor_no = '%s'" % gvar.work_order
            self.cursor.execute(SQL)
            measure_work_order = list(self.cursor.fetchone())[0]
            print(value_data)
            # str()
            # ---------
            measure_item_data = []
            SQL = "SELECT mysite_work_order_measure_items.id, mysite_work_order_measure_items.measurement_items   From  mysite_work_order_measure_items  WHERE mysite_work_order_measure_items.measurement_work_order_id = '%s'" % measure_work_order
            self.cursor.execute(SQL)
            data = self.cursor.fetchall()
            for item in data:
                measure_item_data.append([item[0], item[1]])
            for item in measure_item_data:
                if item[1] == value_data[(-4)]:
                    # SQL = "SELECT mysite_work_order_measure_items.id From  mysite_measure_items WHERE mysite_measure_items.id ='%s'" % item[0]
                    # self.cursor.execute(SQL)
                    # data = self.cursor.fetchall()
                    mysite_work_order_measure_items_id = item[0]
            # ---------
            data_list.append((
                value_data[(-1)], value_data[0], value_data[1], value_data[2], time_now, meaure_project_id,
                measure_tool_id,
                measure_work_order, mysite_work_order_measure_items_id, value_data[7]))

        print(data_list)
        SQL = "INSERT INTO mysite_measure_values(measure_man,measure_value,measure_unit,measure_time, time_now,measure_project_id, measure_tool_id, measure_work_order_id, measure_work_order_measure_item_id,measure_number,remake ) VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'')"
        self.cursor.executemany(SQL, data_list)
        self.conn.commit()
        print('insert ok')

    def sql_update_work_order_state(self, work_order):
        SQL = "UPDATE mysite_measurement_work_order SET mysite_measurement_work_order.measure_state = 'OK' WHERE mysite_measurement_work_order.sor_no = '%s'" % work_order
        self.cursor.execute(SQL)
        self.conn.commit()

    def sql_delet_data(self):
        SQL = "DELETE FROM mainsite_project WHERE name ='123'"
        self.cursor.execute(SQL)
        self.conn.commit()

    def sql_find_work_order_part_number(self, work_order):
        SQL = "SELECT mysite_measurement_work_order.number_of_parts   From  mysite_measurement_work_order  WHERE mysite_measurement_work_order.sor_no = '%s'" % work_order
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        part_number = data[0][0]
        return part_number

    def sql_image_all_project_name(self):
        SQL = 'SELECT mysite_project.project_name  From  mysite_project'
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        new_data = []
        for item in data:
            item = list(item)
            new_data.append(item[0])

        return new_data

    def sql_image_base64data(self, item_name):
        SQL = "SELECT mysite_measure_items.image_base64_data  From  mysite_measure_items WHERE mysite_measure_items.measurement_items ='%s'" % item_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        data = data[0][0]
        return data

    def sql_image_base64data_project_id(self, project_id, measure_item):
        SQL = "SELECT mysite_measure_items.id ,mysite_measure_items.measurement_items From  mysite_measure_items WHERE mysite_measure_items.project_id ='%s'" % project_id
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        measure_item_data = []
        for item in data:
            measure_item_data.append([item[0], item[1]])
        for item in measure_item_data:
            if item[1] == measure_item:
                SQL = "SELECT mysite_measure_items.image_base64_data From  mysite_measure_items WHERE mysite_measure_items.id ='%s'" % item[0]
                self.cursor.execute(SQL)
                data = self.cursor.fetchall()
                data = data[0][0]
        return data

    def sql_project_name_to_project_id(self, project_name):
        SQL = " SELECT mysite_project.id  From mysite_project WHERE mysite_project.project_name = '%s' " % project_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        data = data[0][0]
        return data

    def sql_all_image_item(self, project_name):
        SQL = "SELECT mysite_measure_items.measurement_items  From  mysite_measure_items WHERE mysite_measure_items.project_id=(SELECT mysite_project.id FROM mysite_project WHERE mysite_project.project_name='%s')" % project_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        new_data = []
        for item in data:
            d = item[0]
            new_data.append(d)
        print(new_data)
        return new_data

    def sql_project_id_key_name(self, project_name):
        SQL = "SELECT mysite_measure_items.measurement_items, mysite_measure_items.id  From  mysite_measure_items WHERE mysite_measure_items.project_measure_id=ANY(SELECT mysite_project.id FROM mysite_project WHERE mysite_project.project_name='%s')" % project_name
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        new_data = []
        for item in data:
            d = item[0]
            new_data.append(d)

        print(new_data)
        return new_data

    def sql_work_order_get_project_id(self, work_order_id):
        SQL = " SELECT mysite_measurement_work_order.project_measure_id  From mysite_measurement_work_order WHERE mysite_measurement_work_order.id = '%s' " % work_order_id
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        data = data[0][0]
        return data

    def sql_project_name(self, project_id):
        SQL = " SELECT mysite_project.project_name  From mysite_project WHERE mysite_project.id = '%s' " % project_id
        self.cursor.execute(SQL)
        data = self.cursor.fetchall()
        data = data[0][0]
        print(data)
        return data

    def sql_work_order_appearance_defect(self, work_order, data):
        for item in data:
            work_id = self.sql_work_order_id(work_order)
            SQL = "INSERT INTO mysite_work_order_appearance_defect(base64_image, part_number, remake, work_order_id)VALUES ('%s', '%s', '%s', %s)" % (
                item['image_base64'], item['number'], item['remake'], work_id)
            self.cursor.execute(SQL)
            self.conn.commit()

        print('insert appearance defect ok')


def save(file_name, base64_data, pict_type):
    import os
    system_root = os.path.dirname(os.path.realpath(__file__))
    with open('%s/%s.%s' % (system_root, file_name, pict_type), 'wb') as (file):
        jiema = base64.b64decode(base64_data)
        file.write(jiema)


import tkinter.messagebox as msgbox
# okay decompiling sql_connect.pyc
