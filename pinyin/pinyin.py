# -*- coding: utf-8 -*-

from os import path
import codecs

table = {}
def load_data():

    try:
        fp = codecs.open(path.join(path.dirname(
            __file__), 'pinyin.txt'), 'r', 'utf-8')
    except IOError:
        raise Exception("Can't load data from pinyin.txt")
    except UnicodeDecodeError:
        raise Exception("Can't decode data from pinyin.txt")
    else:
        for l in fp.readlines():
            table[l[0]] = l[1:-1]
        fp.close()


class han2bopomofo(object):

    def __init__(self):
        load_data()

    def convert(self, hanzi):
        pinyin = []
        tASCII = ''
        # 字符检查
        for c in hanzi.lower() + ' ':  # 加个空格多一次循环 修正尾部字符丢失问题
            i = ord(c)
            # 48-57[0-9]   97-122[a-z]
            if (i >= 48 and i <= 57) or (i >= 97 and i <= 122):
                tASCII += c
                continue

            tASCII and pinyin.append(tASCII)
            tASCII = ''

            if table.get(c):
                pinyin.append(table[c])

        return pinyin


# if __name__ == '__main__':
#     import time
#     t = u'听说你们密码小组小有所成'
#     s = time.time()
#     p = han2bopomofo() # you class
#     print('init:', time.time() - s)
#     print('-'.join(p.convert(t))) # you convert
#     s = time.time()
#     for i in range(10000):
#         p.convert(t) # you convert
#     print('convert:', time.time() - s)
