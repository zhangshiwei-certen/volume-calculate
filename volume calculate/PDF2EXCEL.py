import pdfplumber  # 为了操作PDF
from openpyxl import Workbook


def pdf2excel(path):
    wb = Workbook()  # 创建文件对象
    ws = wb.active  # 获取第一个sheet
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            if page.extract_text() is not None:
                text = page.extract_text().splitlines()
                for chars in text:
                    line = chars.split()
                    print(line)
                    ws.append(line)
    pdf.close()
    # 保存Excel表
    wb.save('舱容表.xlsx')
