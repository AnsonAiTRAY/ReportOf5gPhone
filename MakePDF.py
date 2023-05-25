import numpy as np
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, Circle
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Spacer, SimpleDocTemplate, PageBreak
from DataClass import PDFClass
from concurrent.futures import ThreadPoolExecutor
import time
import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
# Fonts register
msyh = "msyh"  # 微软雅黑
msyhbd = "msyhbd"  # 微软雅黑加粗
song = "simsun"  # 宋体
pdfmetrics.registerFont(TTFont(song, "simsun.ttc"))
pdfmetrics.registerFont(TTFont(msyh, "msyh.ttc"))
pdfmetrics.registerFont(TTFont(msyhbd, "msyhbd.ttc"))
# 页面设置大小为A4标准尺寸
PAGE_HEIGHT = A4[1]
PAGE_WIDTH = A4[0]
Data = PDFClass('', '', 0, [], [], [], 0.0, [], '', '', '', '', '', '', [], [])
LastData = PDFClass('', '', 0, [], [], [], 0.0, [], '', '', '', '', '', '', [], [])
page = 1


def FirstPage(c: Canvas, doc):
    global Data, LastData
    c.saveState()
    # 设置填充色
    c.setFillColor(colors.red)
    # 设置字体大小
    c.setFont(msyhbd, 36)
    # 绘制居中标题文本
    c.drawCentredString(300, PAGE_HEIGHT - 80, f"{Data.Name}评论数据分析报告")
    c.setFont(song, 12)
    c.setFillColor(colors.black)
    c.drawCentredString(300, PAGE_HEIGHT - 110, f"生成日期：{Data.CurrentTime}")
    c.line(30, PAGE_HEIGHT - 120, 570, PAGE_HEIGHT - 120)
    # 绘制商品图片
    c.setFont(song, 16)
    c.drawString(120, PAGE_HEIGHT - 140, "产品图片")
    c.drawImage(Data.Image, 75, PAGE_HEIGHT - 300, 150, 150)
    c.line(300, PAGE_HEIGHT - 130, 300, PAGE_HEIGHT - 290)
    # 绘制饼图
    c.drawCentredString(440, PAGE_HEIGHT - 140, f"{Data.Name}总体好评率：{Data.PositiveRate * 100}%")
    c.setFont(song, 10)
    if LastData.PositiveRate:
        if Data.PositiveRate > LastData.PositiveRate:
            c.setFillColor(colors.green)
            c.drawCentredString(440, PAGE_HEIGHT - 160,
                                f"环比增长：{(Data.PositiveRate - LastData.PositiveRate) * 100}%")
        if Data.PositiveRate < LastData.PositiveRate:
            c.setFillColor(colors.red)
            c.drawCentredString(440, PAGE_HEIGHT - 160,
                                f"环比降低：{(LastData.PositiveRate - Data.PositiveRate) * 100}%")
    c.setFont(song, 16)
    drawScorePie(c, 400, PAGE_HEIGHT - 280, Data.PositiveRate * 100)
    c.line(30, PAGE_HEIGHT - 300, 570, PAGE_HEIGHT - 300)
    # 绘制子商品数据
    row = Data.SubNum / 4
    # 多线程
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(int(row) + 1):
            for j in range(4):
                tmp = i * 4 + j
                if tmp < Data.SubNum:
                    t.submit(drawSubScorePie, c, 25 + j * 150, PAGE_HEIGHT - 320 - i * 230, Data.SubName[tmp],
                             Data.SubPositiveRate[tmp], LastData.SubPositiveRate[tmp], Data.SubPrice[tmp],
                             LastData.SubPrice[tmp], Data.SubImage[tmp])
            if i * 4 + 3 < Data.SubNum:
                c.line(30, PAGE_HEIGHT - 325 - (i + 1) * 200, 570, PAGE_HEIGHT - 325 - (i + 1) * 200)
    # 绘制页脚
    DrawPageInfo(c)

    # 绘制第二页，情感分析
    DrawPageHead(c)
    c.setFont(song, 24)
    drawRealPositiveBar(c, 100, PAGE_HEIGHT - 450, Data.SubName, Data.SubPositiveRate, Data.SubPositiveNum,
                        Data.SubRealPositiveNum)
    # 绘制页脚
    DrawPageInfo(c)

    # 绘制第三页，追评分析
    DrawPageHead(c)
    c.setFont(song, 24)
    c.drawCentredString(300, PAGE_HEIGHT - 150, f"{Data.Name}产品追加评论分析")
    # 绘制页脚
    DrawPageInfo(c)

    # 绘制第三页，好评关键词词云
    DrawPageHead(c)
    c.setFont(song, 24)
    c.drawCentredString(300, PAGE_HEIGHT - 150, f"{Data.Name}好评关键词词云")
    row = Data.SubNum / 3
    # 多线程
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(int(row) + 1):
            for j in range(3):
                tmp = i * 3 + j
                if tmp < Data.SubNum:
                    t.submit(drawSubCloudImage, c, 25 + j * 180, PAGE_HEIGHT - 190 - i * 200, Data.SubName[tmp],
                             Data.SubPositivePhraseCloud, 1)
            if i * 3 + 2 < Data.SubNum:
                c.line(30, PAGE_HEIGHT - 160 - (i + 1) * 200, 570, PAGE_HEIGHT - 160 - (i + 1) * 200)
    # 绘制页脚
    DrawPageInfo(c)

    # 绘制第三页，好评关键句词云
    DrawPageHead(c)
    c.setFont(song, 24)
    c.drawCentredString(300, PAGE_HEIGHT - 150, f"{Data.Name}好评关键句词词云")
    row = Data.SubNum / 3
    # 多线程
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(int(row) + 1):
            for j in range(3):
                tmp = i * 3 + j
                if tmp < Data.SubNum:
                    t.submit(drawSubCloudImage, c, 25 + j * 180, PAGE_HEIGHT - 190 - i * 200, Data.SubName[tmp],
                             Data.SubPositiveSentenceCloud, 1)
            if i * 3 + 2 < Data.SubNum:
                c.line(30, PAGE_HEIGHT - 160 - (i + 1) * 200, 570, PAGE_HEIGHT - 160 - (i + 1) * 200)
    # 绘制页脚
    DrawPageInfo(c)

    # 绘制第四页，中评关键词词云
    DrawPageHead(c)
    c.setFont(song, 24)
    c.drawCentredString(300, PAGE_HEIGHT - 150, f"{Data.Name}中评关键词词云")
    row = Data.SubNum / 3
    # 多线程
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(int(row) + 1):
            for j in range(3):
                tmp = i * 3 + j
                if tmp < Data.SubNum:
                    t.submit(drawSubCloudImage, c, 25 + j * 180, PAGE_HEIGHT - 190 - i * 200, Data.SubName[tmp],
                             Data.SubMidPhraseCloud, 2)
            if i * 3 + 2 < Data.SubNum:
                c.line(30, PAGE_HEIGHT - 160 - (i + 1) * 200, 570, PAGE_HEIGHT - 160 - (i + 1) * 200)
    # 绘制页脚
    DrawPageInfo(c)

    # 绘制第五页，中评关键句词云
    DrawPageHead(c)
    c.setFont(song, 24)
    c.drawCentredString(300, PAGE_HEIGHT - 150, f"{Data.Name}中评关键句词云")
    row = Data.SubNum / 3
    # 多线程
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(int(row) + 1):
            for j in range(3):
                tmp = i * 3 + j
                if tmp < Data.SubNum:
                    t.submit(drawSubCloudImage, c, 25 + j * 180, PAGE_HEIGHT - 190 - i * 200, Data.SubName[tmp],
                             Data.SubMidSentenceCloud, 2)
            if i * 3 + 2 < Data.SubNum:
                c.line(30, PAGE_HEIGHT - 160 - (i + 1) * 200, 570, PAGE_HEIGHT - 160 - (i + 1) * 200)
    # 绘制页脚
    DrawPageInfo(c)

    # 绘制第六页，差评关键词词云
    DrawPageHead(c)
    c.setFont(song, 24)
    c.drawCentredString(300, PAGE_HEIGHT - 150, f"{Data.Name}差评关键词词云")
    row = Data.SubNum / 3
    # 多线程
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(int(row) + 1):
            for j in range(3):
                tmp = i * 3 + j
                if tmp < Data.SubNum:
                    t.submit(drawSubCloudImage, c, 25 + j * 180, PAGE_HEIGHT - 190 - i * 200, Data.SubName[tmp],
                             Data.SubNegativePhraseCloud, 3)
            if i * 3 + 2 < Data.SubNum:
                c.line(30, PAGE_HEIGHT - 160 - (i + 1) * 200, 570, PAGE_HEIGHT - 160 - (i + 1) * 200)
    # 绘制页脚
    DrawPageInfo(c)

    # 绘制第七页，差评关键句词云
    DrawPageHead(c)
    c.setFont(song, 24)
    c.drawCentredString(300, PAGE_HEIGHT - 150, f"{Data.Name}差评关键词词云")
    row = Data.SubNum / 3
    # 多线程
    with ThreadPoolExecutor(max_workers=8) as t:
        for i in range(int(row) + 1):
            for j in range(3):
                tmp = i * 3 + j
                if tmp < Data.SubNum:
                    t.submit(drawSubCloudImage, c, 25 + j * 180, PAGE_HEIGHT - 190 - i * 200, Data.SubName[tmp],
                             Data.SubNegativeSentenceCloud, 3)
            if i * 3 + 2 < Data.SubNum:
                c.line(30, PAGE_HEIGHT - 160 - (i + 1) * 200, 570, PAGE_HEIGHT - 160 - (i + 1) * 200)
    # 绘制页脚
    DrawPageInfo(c)

    c.restoreState()


def DrawPageHead(c: Canvas):
    global Data
    c.showPage()
    c.saveState()
    # 设置填充色
    c.setFillColor(colors.red)
    # 设置字体大小
    c.setFont(msyhbd, 36)
    # 绘制居中标题文本
    c.drawCentredString(300, PAGE_HEIGHT - 80, f"{Data.Name}评论数据分析报告")
    c.setFont(song, 12)
    c.setFillColor(colors.black)
    c.drawCentredString(300, PAGE_HEIGHT - 110, f"生成日期：{Data.CurrentTime}")
    c.line(30, PAGE_HEIGHT - 120, 570, PAGE_HEIGHT - 120)


def LaterPages(c: Canvas, doc):
    c.saveState()
    c.restoreState()


def GeneratePDF(data, lastdata):
    # 创建文档
    global Data, LastData
    Data = data
    LastData = lastdata
    filename = f"{Data.Name}_{time.strftime('%Y%m%d%H%M%S', time.localtime())}.pdf"
    doc = SimpleDocTemplate(filename)
    Story = [Spacer(1, 2 * inch)]
    # 保存文档
    doc.build(Story, onFirstPage=FirstPage, onLaterPages=LaterPages)


def DrawPageInfo(c: Canvas):
    global page
    # 设置边框颜色
    c.setStrokeColor(colors.dimgrey)
    # 绘制线条
    c.line(30, PAGE_HEIGHT - 790, 570, PAGE_HEIGHT - 790)
    # 绘制页脚文字
    c.setFont(song, 8)
    c.setFillColor(colors.black)
    global Data
    c.drawString(30, PAGE_HEIGHT - 810, f"生成日期：{Data.CurrentTime}")
    c.drawString(560, PAGE_HEIGHT - 810, f"{page}")
    page = page + 1


def drawRealPositiveBar(canvas: Canvas, x, y, subname, subpositiverate, subpositivenum, subrealpositivenum):
    x_axis = subname
    y_bottom = subrealpositivenum
    y_up = [subpositivenum[i] - subrealpositivenum[i] for i in range(0, len(subname))]
    temp1 = [round((subrealpositivenum[i] * 100 / subpositivenum[i]), 2) for i in range(0, len(subname))]
    percentage1 = [f"{temp1[i]}%" for i in range(0, len(temp1))]
    plt.bar(x_axis, y_bottom, label='情感分析积极评论', color=['deeppink'])
    plt.bar(x_axis, y_up, bottom=y_bottom, label='好评评论', color=['dodgerblue'])
    for a, b, c in zip(x_axis, y_bottom, percentage1):
        plt.text(a, b + 0.1, c, ha='center', va='bottom')
    plt.title('积极情感在好评中的占比图')
    plt.xlabel('产品子项')
    plt.ylabel('评论数量')
    plt.legend()
    plt.savefig('bar1.png', dpi=300)
    canvas.drawImage('bar1.png', x, y, 400, 300)
    plt.cla()
    canvas.drawCentredString(300, PAGE_HEIGHT - 150, "产品评论情感分析")

    temp2 = [round((subpositiverate[i] * temp1[i]), 2) for i in range(0, len(subname))]
    percentage2 = [f"{temp2[i]}%" for i in range(0, len(temp2))]
    y_full = []
    for i in range(len(subname)):
        y_full.append(100)
    plt.bar(x_axis, temp2, label='真实好评率', color=['deeppink'])
    for a, b, c in zip(x_axis, temp2, percentage2):
        plt.text(a, b + 0.1, c, ha='center', va='bottom')
    plt.ylim((0, 100))
    plt.title('产品真实好评率')
    plt.xlabel('产品子项')
    plt.ylabel('好评率(%)')
    plt.legend()
    plt.savefig('bar2.png', dpi=300)
    canvas.drawImage('bar2.png', x, y-320, 400, 300)
    canvas.drawCentredString(x + 200, PAGE_HEIGHT - 470, "产品真实好评率")


def drawSubCloudImage(canvas: Canvas, x, y, subname, cloudimage, Positive):
    canvas.setFont(song, 16)
    if Positive == 1:
        canvas.drawCentredString(x + 100, y, f"{subname}好评关键词词云")
    if Positive == 2:
        canvas.drawCentredString(x + 100, y, f"{subname}中评关键词词云")
    if Positive == 3:
        canvas.drawCentredString(x + 100, y, f"{subname}差评关键词词云")
    canvas.drawInlineImage(cloudimage, x, y - 150, 180, 130)


def drawSubScorePie(canvas: Canvas, x, y, subname, score, lastscore, price, lastprice, image):
    """绘制评分饼图"""
    canvas.setFont(song, 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(x, y, f"{subname}好评率：{score * 100}%")
    canvas.setFont(song, 6)
    if lastscore:
        if score > lastscore:
            canvas.setFillColor(colors.green)
            canvas.drawCentredString(x + 50, y - 10, f"环比增长：{(score - lastscore) * 100}%")
        if score < lastscore:
            canvas.setFillColor(colors.red)
            canvas.drawCentredString(x + 50, y - 10, f"环比降低：{(lastscore - score) * 100}%")
    d = Drawing(50, 50)
    # 画大饼图
    pc = Pie()
    pc.width = 50
    pc.height = 50
    # 设置数据
    score = score * 100
    pc.data = [score, 100 - score]
    pc.slices.strokeWidth = 0.1
    # 设置颜色
    color = colors.seagreen
    if score < 60:
        color = colors.red
    elif score < 85:
        color = colors.orange
    pc.slices.strokeColor = colors.transparent
    pc.slices[0].fillColor = color
    pc.slices[1].fillColor = colors.transparent
    d.add(pc)
    # 画内圈
    circle = Circle(25, 25, 20)
    circle.fillColor = colors.white
    circle.strokeColor = colors.transparent
    d.add(circle)
    # 把饼图画到Canvas上
    d.drawOn(canvas, x + 25, y - 70)
    # 写字
    canvas.setFont(msyh, 12)
    canvas.setFillColor(color)
    global Data
    canvas.drawCentredString(x + 50, y - 45, f"{Data.PositiveRate * 100}%")
    canvas.setFont(msyh, 6)
    canvas.drawCentredString(x + 50, y - 55, getCommend(score))

    canvas.setFont(song, 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(x, y - 85, f"{subname}当前售价：{price}元")
    canvas.setFont(song, 6)
    if lastprice:
        if price > lastprice:
            canvas.setFillColor(colors.green)
            canvas.drawCentredString(x + 50, y - 95, f"环比增长：{((price - lastprice) / lastprice) * 100}%")
        else:
            canvas.setFillColor(colors.red)
            canvas.drawCentredString(x + 50, y - 95, f"环比降低：{((lastprice - price) / lastprice) * 100}%")
    canvas.drawImage(image, x, y - 200, 100, 100)


def drawScorePie(canvas: Canvas, x, y, score):
    """绘制评分饼图"""
    d = Drawing(100, 100)
    # 画大饼图
    pc = Pie()
    pc.width = 100
    pc.height = 100
    # 设置数据
    pc.data = [score, 100 - score]
    pc.slices.strokeWidth = 0.1
    # 设置颜色
    color = colors.seagreen
    if score < 60:
        color = colors.red
    elif score < 85:
        color = colors.orange
    pc.slices.strokeColor = colors.transparent
    pc.slices[0].fillColor = color
    pc.slices[1].fillColor = colors.transparent
    d.add(pc)
    # 画内圈
    circle = Circle(50, 50, 40)
    circle.fillColor = colors.white
    circle.strokeColor = colors.transparent
    d.add(circle)
    # 把饼图画到Canvas上
    d.drawOn(canvas, x, y)
    # 写字
    canvas.setFont(msyh, 24)
    canvas.setFillColor(color)
    global Data
    canvas.drawCentredString(x + 50, y + 45, f"{Data.PositiveRate * 100}%")
    canvas.setFont(msyh, 12)
    canvas.drawCentredString(x + 50, y + 25, getCommend(score))


def getCommend(score):
    if score > 95:
        return '好评如潮'
    elif score > 90:
        return '特别好评'
    elif score > 80:
        return '多半好评'
    elif score > 60:
        return '褒贬不一'
    elif score > 30:
        return '多半差评'
    else:
        return '差评如潮'


if __name__ == "__main__":
    subname = ['8+128', '8+256', '12+256', '12+512', '16+512']
    image = 'https://img10.360buyimg.com/n1/s450x450_jfs/t1/197012/39/33443/329748/646bac4bF223fdedb/d63e5a29f211efa2.png'
    subimage = [image, image, image, image, image]
    subprice = [3999, 4299, 4599, 4999, 5299]
    subprice1 = [3899, 4399, 4699, 5099, 5399]
    subpositiverate1 = [0.97, 0.98, 0.98, 0.98, 0.97]
    subpositiverate2 = [0.97, 0.97, 0.98, 0.97, 0.97]
    PN = [1000, 900, 1000, 800, 1100]
    RPN = [900, 850, 700, 700, 900]
    image2 = 'image2.png'
    image3 = 'image3.png'
    image4 = 'image4.png'
    tmp1 = PDFClass('小米13', image, 5, subname, subimage, subprice, 0.98, subpositiverate1, image2, image3, image4,
                    image2, image3, image4, PN, RPN)
    tmp2 = PDFClass('小米13', image, 5, subname, subimage, subprice1, 0.97, subpositiverate2, image2, image3, image4,
                    image2, image3, image4, PN, RPN)
    GeneratePDF(tmp1, tmp2)
