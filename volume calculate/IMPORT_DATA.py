from os import path

import pandas as pd
from sqlalchemy import create_engine


class ImportExceldata(object):
    """获取excel数据并写入数据库"""

    def __init__(self, path):
        self.path = path
        self.excel = pd.ExcelFile(path)
        self.sheet_names = self.excel.sheet_names
        self.excle2sqlite3()

    def excle2sqlite3(self):
        """
        Excel文件转化为数据库文件。
        """
        if not path.exists('sql.db'):
            for name in self.sheet_names:
                wb = pd.read_excel(self.excel, name, index_col=0)
                # 加载数据库引擎
                engine = create_engine('sqlite:///sql.db', echo=False)
                wb.to_sql('{}'.format(name), con=engine)


if __name__ == '__main__':
    # 测试用path
    x = ImportExceldata('C:/Users/zsw/Desktop/3S仓容表.xlsx')
    x.read_excle()
