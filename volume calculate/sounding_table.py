import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from math import modf


class Sounding_Cal(object):
    """
    对传入的数据进行进行相关处理后在数据库中查询对应索引数据
    及根据查询值进行相关计算得到对应的油舱容积。
    """

    def __init__(self, database, draft='1', slope='1', oil_tank='NO.1P', sounding='2'):
        """

        :param draft: 吃水差
        :param slope: 左右倾
        :param oil_tank: 油舱名称
        :param sounding: 测量实高
        """

        self.draft = Decimal(draft)
        self.slope = Decimal(slope)
        self.tank_name = oil_tank
        self.sounding = Decimal(sounding)
        self.database = database
        intervals, table_names, draft_range, heel_range = self.get_database_inform()
        self.__table_names = table_names
        self.__interval = Decimal(intervals)
        self.__draft_range = draft_range
        self.__heel_range = heel_range
        self.touple = (Decimal(-3), Decimal(-2), Decimal(-1), Decimal(0)
                       , Decimal(1), Decimal(2), Decimal(3), Decimal(4), Decimal(5))

    @property
    def table_names(self):
        """
        获取私有属性
        :return: 返回私有属性table_names
        """
        return self.__table_names

    @property
    def interval(self):
        """
        获取属性
        :return: 私有属性interval
        """
        return self.__interval

    @property
    def draft_range(self):
        return self.__draft_range

    @property
    def heel_range(self):
        return self.__heel_range

    def handling_sounding(self, choose):
        """
        根据给出的choose，选择计算模式，tr为吃水修正计算，heel为倾斜修正计算。
        :param choose: 计算模式，tr或heel
        :return: 返回对应模式的查表计算结果。
        """
        if choose == 'tr':
            statu = self.draft
        else:
            statu = self.slope
        if (Decimal(self.sounding) % Decimal(self.interval)) == Decimal('0'):
            self.sounding = Decimal(int(self.sounding))  # int函数取出数值的整数部分，防止输入时添加小数.0
            if Decimal(statu) in self.touple:
                result = self.sql_lookup(choose, statu, self.tank_name, self.sounding)
                return result
            else:
                # 取整数部分
                if statu > Decimal('0'):
                    statu_min = Decimal(int(statu))
                    statu_max = statu_min + 1
                else:
                    x, mi = modf(float(statu))
                    # 使用int取整可以取负数
                    statu_max = int(mi)
                    statu_min = statu_max - 1
                result_min = self.sql_lookup(choose, statu_min, self.tank_name, self.sounding)
                result_max = self.sql_lookup(choose, statu_max, self.tank_name, self.sounding)
                result = self.cross_plus(statu, statu_min, 1,
                                         result_max, result_min)
                return result
        else:
            sounding_min = Decimal(int(Decimal(self.sounding) / Decimal(self.interval))) * self.interval
            sounding_max = sounding_min + int(self.interval)
            print(sounding_max, self.sounding, sounding_min)
            if statu in self.touple:
                result_min = self.sql_lookup(choose, statu, self.tank_name, sounding_min)
                result_max = self.sql_lookup(choose, statu, self.tank_name, sounding_max)
                result = self.cross_plus(self.sounding, sounding_min, self.interval,
                                         result_max, result_min)
                return result
            else:
                # 计算测量修正小值
                print('statu:', statu)
                if statu > Decimal('0'):
                    statu_min = Decimal(int(statu))
                    statu_max = statu_min + 1
                else:
                    x, mi = modf(float(statu))
                    print(mi)
                    statu_max = int(mi)
                    statu_min = statu_max - 1
                print(statu, statu_max, statu_min)
                # 计算测量修正小值
                result_min_min = self.sql_lookup(choose, statu_min, self.tank_name, sounding_min)
                result_min_max = self.sql_lookup(choose, statu_max, self.tank_name, sounding_min)
                result_sounding_min = self.cross_plus(statu, statu_min, 1,
                                                      result_min_max, result_min_min)

                # 计算测量修正大值
                result_max_min = self.sql_lookup(choose, statu_min, self.tank_name, sounding_max)
                result_max_max = self.sql_lookup(choose, statu_max, self.tank_name, sounding_max)
                result_sounding_max = self.cross_plus(statu, statu_min, 1, result_max_max, result_max_min)

                # 计算测量实际值l
                result = self.cross_plus(self.sounding, sounding_min, self.interval,
                                         result_sounding_max, result_sounding_min)
                print(result_sounding_min, result_sounding_max, result)

                return result

    @staticmethod
    def cross_plus(scale, scale_min, interval, result_max, result_min):
        result = result_min + (result_max - result_min) * (scale - scale_min) / Decimal(interval)
        return result

    @staticmethod
    def round_dec(n, d):
        """

        :param n: 需要进行四舍五入的数，可以是float，decimal
        :param d: 保留小数的位数
        :return: 返回四舍五入结果，Decimal类型
        """
        s = '0.' + '0' * d
        return Decimal(str(n)).quantize(Decimal(s), ROUND_HALF_UP)

    def sql_lookup(self, draft_slope, draft, tank_name, sounding):
        """
        根据提供的参数进行查表操作
        """
        sql = 'SELECT "{}={}" FROM "{}" WHERE SOUND={}'.format(draft_slope, draft, tank_name, sounding)
        mydb = sqlite3.connect(self.database)
        db = mydb.cursor()
        print(sql)
        db.execute(sql)
        a = db.fetchone()
        print(a[0])
        return Decimal(a[0])

    def check_param(self, sounding, slope, draft, tank_name):
        """

        :param sounding:实际测量高度
        :param slope:倾斜角度
        :param draft:前后吃水差值
        :param tank_name:str,用于查表找到对应舱柜的最大测深
        :return:(check_res,flag)check_res,不合规参数列表；flag，参数是否都合规。
        """
        max_sounding = self.get_max_sounding(tank_name, 'sound')
        check_res = []
        heel_min = self.heel_range[0]
        heel_max = self.heel_range[-1]
        draft_min = self.draft_range[0]
        draft_max = self.draft_range[-1]
        flag = True
        if sounding > Decimal(max_sounding):
            check_res.append('测高', )
            flag = False
        if not (Decimal(str(heel_min)) <= slope <= Decimal(str(heel_max))):
            check_res.append('左右倾', )
            flag = False
        if not (Decimal(str(draft_min)) <= draft <= Decimal(str(draft_max))):
            check_res.append('吃水差', )
            flag = False
        return check_res, flag

    def handling_result(self):
        """
        将两个模式的计算结果组合进行计算
        :return:(result/check_res, flag)返回最终舱容结果或不合规参数，计算状态
        """
        check_res, flag = self.check_param(self.sounding, self.slope, self.draft, self.tank_name)
        print(check_res, flag)
        if flag:
            result_draft = self.handling_sounding('tr')
            result_slop = self.handling_sounding('HEEL')
            result = result_draft + result_slop
            print('result', result_slop, result_draft)
            return result, True
        else:
            return check_res, False

    def get_max_sounding(self, table_name, column_name):
        """
        获取数据表的最大测量深度。
        :param table_name: 数据表名称
        :param column_name: 水平表头名称
        :return: 最大测量深度
        """
        mydb = sqlite3.connect(self.database)
        db = mydb.cursor()
        # sound在不同测深表中可能不一样，此处需要在导入表格时给予强调，防止导入错误名称
        sql = 'select "{}" from "{}"'.format(column_name, table_name)
        db.execute(sql)
        li = db.fetchall()
        sounding_list = []
        for i in li:
            try:
                int(i)
            except Exception:
                sounding_list.append(float(i[0]))
            else:
                sounding_list.append(int(i[0]))

        sounding_list.sort()
        maxsounding = sounding_list[-1]
        return maxsounding

    def get_database_inform(self):
        """
        获取数据信息
        :return: interval，table_names
        """
        mydb = sqlite3.connect(self.database)
        db = mydb.cursor()
        sql = 'select name from sqlite_master where type="table"'
        tab_name = db.execute(sql).fetchall()
        tab_names = [line[0] for line in tab_name]  # 列表推导式
        col_names = []
        for line in tab_names:
            col_name = db.execute('pragma table_info("{}")'.format(line)).fetchall()
            col_name = [x[1] for x in col_name]
            col_names.append(col_name)
        # print(col_names[0][0])
        col1 = db.execute('select "{}" from "{}"'.format(col_names[0][0], tab_names[0])).fetchall()
        # print(col1)
        # db.execute('UPDATE "NO.1S" SET "HEEL=0"=0')
        # db.execute('commit')
        col1_values = []
        for i in col1:
            col1_values.append(int(i[0]))
        col1_values.sort()
        # print(col1_values)
        line2_sounding = col1_values[1]
        line1_sounding = col1_values[0]
        interval = str(line2_sounding - line1_sounding)

        draft_range = []
        heel_range = []
        for i in col_names[0]:
            prifex_tr = 'tr='
            prifex_HEEL = 'HEEL='
            if prifex_tr in i:
                num = int(i.strip('tr='))
                draft_range.append(num)
            elif prifex_HEEL in i:
                num = int(i.strip('HEEL='))
                heel_range.append(num)
        draft_range.sort()
        heel_range.sort()
        return interval, tab_names, draft_range, heel_range


def main():
    while True:
        draft = input('吃水差：')
        while not (Decimal(draft) <= Decimal(5) and Decimal(draft) >= Decimal(-2)):
            print('吃水差超出范围，请重新输入！')
            draft = input('吃水差：')
        slope = input('左右倾：')
        while not (Decimal(slope) <= Decimal(3) and Decimal(slope) >= Decimal(-3)):
            print('左右倾超出范围，请重新输入！')
            slope = input('左右倾：')
        tank = input('油舱号：')
        oil_tank = 'NO.' + tank
        sounding = input('测深：')
        calculate = Sounding_Cal(draft, slope, oil_tank, sounding)
        result = calculate.handling_result()
        print(oil_tank + '存油：' + str(result) + 'm3')


if __name__ == '__main__':
    main()
