import os
import re
import collections

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pinyin.pinyin import han2bopomofo

plt.rcParams['font.sans-serif'] = ['SimHei']

p = han2bopomofo()

ROOT = os.getcwd()
FILES = ["留言1-1_op_已加密_转写"]


def get_spell(data):
    '''将文本文件转拼音
    '''
    with open(data, "r", encoding="utf-8") as fp:
        pinyin_lists = fp.readlines()
    pinyins = ""
    '''以下7行用于清除《读者十年精华》的无用行
    '''
    # for pinyin in pinyin_lists:
    # rs = re.match('^(.+?):(.+)?$', pinyin)
    # if rs is not None:
    #     if rs.groups()[0] == "Title":
    #         pinyin = re.sub(r'^(.+?):(.+)?$', r'\2', pinyin)
    #     else:
    #         pinyin = re.sub(r'^(.+?):(.+)?$', '', pinyin)
    for pinyin in pinyin_lists:
        for char in pinyin:
            if char in "\n".join(re.findall(u'[\u4e00-\u9fa5]+', pinyin)):
                pinyins += "".join(p.convert(char))
            else:
                pinyins += char
            pinyins += " "
        pinyins += "\n"
    # print(pinyins)
    # pinyins = re.sub(r'( ?\r?\n)+', r'\n', pinyins)
    # pinyins = re.sub(r'\n ', r'\n', pinyins)
    # pinyins = re.sub(r'　', r' ', pinyins)
    with open("{}_op.txt".format(data[:-4]), "w", encoding="utf-8") as fp:
        fp.write(pinyins)
    return pinyins


def uniform_pinyin(pinyins):
    '''将拼音字符替换成标准化字母
    '''
    pinyins = re.sub("[{}]".format("āáǎàɑ"), "a", pinyins)
    pinyins = re.sub("[{}]".format("ōóǒòó̀"), "o", pinyins)
    pinyins = re.sub("[{}]".format("ūúǔù"), "u", pinyins)
    pinyins = re.sub("(?<=[ln])[{}](?=[e\s])".format("üǖǘǚǜ"), "v", pinyins)
    pinyins = re.sub("[{}]".format("üǖǘǚǜ"), "u", pinyins)
    pinyins = re.sub("[{}]".format("īíǐì"), "i", pinyins)
    pinyins = re.sub("[{}]".format("ēéěè"), "e", pinyins)
    pinyins = re.sub("[{}]".format("ńňǹ"), "n", pinyins)
    pinyins = re.sub("[{}]".format(",ḿ"), "", pinyins)
    pinyins = re.sub("[{}]".format("ɡ"), "g", pinyins)
    return pinyins


def purify_pinyin(pinyins, preserve_space=1, lower_case=1):
    '''去除标点符号和多余空白
    '''
    pinyins = uniform_pinyin(pinyins)
    if lower_case == 1:
        pinyins = pinyins.lower()
        pinyins = re.sub(r'[^a-z]', " ", pinyins)
    else:
        pinyins = pinyins.upper()
        pinyins = re.sub(r'[^A-Z]', " ", pinyins)
    if preserve_space == 1:
        pinyins = re.sub(r'\s+', " ", pinyins)
    else:
        pinyins = re.sub(r'\s+', "", pinyins)
    return pinyins


def freq_ana(f):
    '''统计各个字母的出现频率
    '''
    if not os.path.exists(os.path.join(ROOT, f + "_op.txt")):
        get_spell(f + ".txt")
    with open(f + "_op.txt", "r", encoding="utf-8") as fp:
        amount = 0
        if re.search("_已加密", f):
            pinyin = purify_pinyin(fp.read(), preserve_space=0, lower_case=0)
            rel = 0
        else:
            pinyin = purify_pinyin(fp.read(), preserve_space=0)
            rel = 1
        alpha_dict = collections.Counter(pinyin)
        data = pd.DataFrame()
        data["letter"] = list(alpha_dict.keys())
        data["frequency"] = list(alpha_dict.values())
        for i in list(alpha_dict.values()):
            amount += int(i)
        data["relative_frequency"] = list(
            map(lambda i: i / amount * 100, alpha_dict.values()))
        sorted_data = data.sort_values(by="frequency", ascending=False)
        print("{}\n{}\n{}".format("-" * 40, f, "-" * 40))
        print(sorted_data)
        sorted_data.to_csv(f + r'.csv', sep='\t', encoding='utf-8')
        plot_freq(sorted_data, amount, rel)


def plot_freq(sorted_data, amount, rel):
    fig, ax = plt.subplots(figsize=(13, 6))
    # 调整边距
    # fig.tight_layout()  # 调整整体空白
    plt.subplots_adjust(left=0.07, right=0.99, top=0.95,
                        bottom=0.09, wspace=0.5, hspace=0.5)  # 调整子图间距

    g = sns.barplot(x="letter", y="frequency", data=sorted_data)
    # 在柱状图上绘制该字符的频率数值
    col = "relative_frequency" if rel else "frequency"
    fmt_label = "{:.2%}" if rel else "{:d}"
    rects = g.patches
    for rect, label in zip(rects, sorted_data[col]):
        g.text(rect.get_x() + rect.get_width() / 2,
               rect.get_height() + amount * 0.001,
               # '%.2f%%' % (label), color="black", ha="center", fontsize=9)
               fmt_label.format(label / 100 if rel else label),
               color="black", ha="center", fontsize=9)
    g.set_title(f)
    g.set_ylabel("出现次数" + " (总共{}字母)".format(str(amount)))
    g.set_xlabel("拼音字母")
    plt.savefig(f + r'.pdf', format='pdf')
    plt.savefig(f + r'.svg', format='svg')
    plt.savefig(f + r'.png', format='png')
    plt.show()

for f in FILES:
    # if not re.search("_已加密", f):
    #     get_spell(f + ".txt")
    freq_ana(f)
