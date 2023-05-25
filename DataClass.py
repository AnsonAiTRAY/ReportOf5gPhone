import time


class PDFClass:
    # 当前时间（自动生成）
    CurrentTime = ''
    # 产品名称
    Name = ''
    # 产品大图
    Image = ''
    # 产品子项数量
    SubNum = 0
    # 产品子项图片
    SubImage = []
    # 产品子项价格
    SubPrice = []
    # 产品子项名称
    SubName = []
    # 产品总好评率
    PositiveRate = 0
    # 产品子项好评率
    SubPositiveRate = []
    # 产品子项好评词组词云图
    SubPositivePhraseCloud = ''
    # 产品子项中评词组词云图
    SubMidPhraseCloud = ''
    # 产品子项差评词组词云图
    SubNegativePhraseCloud = ''
    # 产品子项好评句子词云图
    SubPositiveSentenceCloud = ''
    # 产品子项中评句子词云图
    SubMidSentenceCloud = ''
    # 产品子项差评句子词云图
    SubNegativeSentenceCloud = ''
    # 产品子项好评数量
    SubPositiveNum = []
    # 产品子项情感好评数量
    SubRealPositiveNum = []

    def __init__(self, name: str, image: str, subnum: int, subname: list, subimage: list, subprice: list,
                 positiverate: float, subpositiverate: list, subpositivephrasecloud: str, submidphrasecloud: str,
                 subnegativephrasecloud: str, subpositivesentencecloud: str, submidsentencecloud: str,
                 subnegativesentencecloud: str, subpositivenum: list, subrealpositivenum=list):
        self.CurrentTime = time.strftime('%Y-%m-%d', time.localtime())
        self.Name = name
        self.Image = image
        self.SubNum = subnum
        self.SubImage = subimage
        self.SubPrice = subprice
        self.SubName = subname
        self.PositiveRate = positiverate
        self.SubPositiveRate = subpositiverate
        self.SubPositivePhraseCloud = subpositivephrasecloud
        self.SubMidPhraseCloud = submidphrasecloud
        self.SubNegativePhraseCloud = subnegativephrasecloud
        self.SubPositiveSentenceCloud = subpositivesentencecloud
        self.SubMidSentenceCloud = submidsentencecloud
        self.SubNegativeSentenceCloud = subnegativesentencecloud
        self.SubPositiveNum = subpositivenum
        self.SubRealPositiveNum = subrealpositivenum
