# coding:utf-8

import os, jieba
import re
import itertools
import json
from sklearn import feature_extraction, feature_selection
import numpy as np
import pandas as pd
#import seaborn as sns
#import matplotlib.pyplot as plt
#from matplotlib.font_manager import FontProperties
#from matplotlib import colors

CKPT = "test-node"  ## 测点
RES = "fault-node"  ## 故障节点
SUBSYS = "sub-system"  ## 子系统

#plt.rc("font", family="Times New Roman", size=12)
#plt.rcParams["axes.unicode_minus"] = False
#FONT = FontProperties(fname=os.path.join(r".", "simhei.ttf"), size=12)


def _clean_text(text):
    # pattern = r'^[a-z]+\.' # 匹配以字母和点号（.）开头的字符串
    return re.sub(r"^[\t\n\r ]+|$[\t\n\r ]+", '', re.sub("^[\t\n\r a-zA-Z0-9]+\.", "", text))


def _convert_col(df, col, key):
    df[key] = ["" for _ in df.index.values]
    for coltxt in col.split("}"):
        if "{" in coltxt:
            colSep, colName = coltxt.split("{", 1)
            df[key] = df[key].str.cat(df[colName].map(lambda itm: _clean_text(itm)), sep=colSep)
        else:
            df[key] += coltxt


def _check_repeat(b_c_value, b_c_sign):
    for itm in sorted(b_c_sign, key=len, reverse=True):
        b_c_value = b_c_value.replace(itm, "")
    return len(b_c_value.replace(" ", "")) > 0


def _dict_add(texts_, fr, value_):
    texts_add = fr.groupby(['a_value'])[value_].apply(list).to_dict()
    for key, value in texts_add.items():
        texts_[key] = texts_.get(key, []) +  value
    return texts_

def _getTfIdfModel(txts, ngrams=3, p_value_limit=0.95, max_features=10000, showRes=False, xstep=10):
    convert_txts = [" ".join(jieba.cut(txt)) for k, itm in txts.items() for txt in itm]
    labels = [k for k, itm in txts.items() for _ in itm]
    vectorizer = feature_extraction.text.TfidfVectorizer(max_features=max_features, ngram_range=(1, ngrams))
    vectorizer.fit(convert_txts)
    corpus = vectorizer.transform(convert_txts)
    key_names = vectorizer.get_feature_names_out()
    p_all = np.zeros(len(key_names))
    for label in np.unique(labels):
        _, p = feature_selection.chi2(corpus, [label == label_ for label_ in labels])
        p_all = np.minimum(p_all, p)
    ind = np.argsort(p_all)
    ind = ind[p_all[ind] < 1 - p_value_limit]
    if showRes:
        ## to draw texts's vectors with a step `row_step`
        corpus = vectorizer.transform([txt for txt in convert_txts])[:, sorted(ind)].todense()
        X_names = vectorizer.get_feature_names_out()
        X_names = [X_names[i] for i in sorted(ind)]
        xticks = X_names
        yticks = [f"{txtKey}[{txtId}]" for txtKey, txt in txts.items() for txtId, _ in enumerate(txt)]
        data = pd.DataFrame(corpus, index=yticks, columns=xticks)
    return [key_names[i].replace(" ", "") for i in ind], vectorizer, sorted(ind)


def dtw_distance(doc1, doc2):
    i = 0
    j = 0
    distance = 0
    while i < (len(doc1) - 1) or j < (len(doc2) - 1):
        cost = [np.inf, np.inf, np.inf]
        if i < (len(doc1) - 1):
            cost[0] = np.linalg.norm(doc1[i, :] - doc1[(i + 1), :])
            # cost[0]=min(np.linalg.norm(doc1[i,:]-doc1[(i+1),:]),sum(doc1[(i+1),:]))
        if j < (len(doc2) - 1):
            cost[1] = np.linalg.norm(doc2[j, :] - doc2[(j + 1), :])
            # cost[1]=min(np.linalg.norm(doc2[j,:]-doc2[(j+1),:]),sum(doc2[(j+1),:]))
        if i < (len(doc1) - 1) and j < (len(doc2) - 1):
            cost[2] = np.linalg.norm(doc1[(i + 1), :] - doc2[(j + 1), :])
            # cost[2] = min(np.linalg.norm(doc1[(i+1), :] - doc2[(j + 1), :]), (sum(doc2[(j + 1), :])+sum(doc1[(i + 1), :]))/2)
        distance = distance + np.min(cost)
        a = np.argmin(cost) + 1
        if a == 1:
            i = i + 1
        if a == 2:
            j = j + 1
        if a == 3:
            i = i + 1
            j = j + 1
    return distance

def _returnmin(co, num, thres=1.5):
    co = np.where(co < co.T, co, np.inf)
    for j in range(num):
        indx = np.argmin(co[:, j])
        x = co[indx, j]
        co[:, j] = np.inf
        co[indx, j] = x
    return (co <= thres).astype("int8")

def _col_match(words, vectorizer, mode, cause, result1, result2, result3, index):
    words = sorted(set(words), key=len, reverse=True)
    num = len(mode)

    # 标记关键实体
    temp0 = np.zeros([(len(words) + 1), num])
    temp0[len(words), :] = 1
    for itemInd, name in enumerate(cause):
        name_ = name
        for wordInd, word in enumerate(words):
            if word in name_:
                temp0[:, itemInd] = 0
                temp0[wordInd, itemInd] = 1
                name_ = name_.replace(word, "#")
                        
    temp1 = np.zeros([(len(words) + 1), num])
    temp1[len(words), :] = 1
    for itemInd, name in enumerate(result1):
        name_ = name
        for wordInd, word in enumerate(words):
            if word in name_:
                temp1[:, itemInd] = 0
                temp1[wordInd, itemInd] = 1
                name_ = name_.replace(word, "#")
                
    temp2 = np.zeros([(len(words) + 1), num])
    temp2[len(words), :] = 1
    for itemInd, name in enumerate(result2):
        name_ = name
        for wordInd, word in enumerate(words):
            if word in name_:
                temp2[:, itemInd] = 0
                temp2[wordInd, itemInd] = 1
                name_ = name_.replace(word, "#")
                
    temp3 = np.zeros([(len(words) + 1), num])
    temp3[len(words), :] = 1
    for itemInd, name in enumerate(result3):
        name_ = name
        for wordInd, word in enumerate(words):
            if word in name_:
                temp3[:, itemInd] = 0
                temp3[wordInd, itemInd] = 1
                name_ = name_.replace(word, "#")

    co0 = np.ones([num, num]) * np.inf
    co1 = np.ones([num, num]) * np.inf
    co2 = np.ones([num, num]) * np.inf
    co3 = np.ones([num, num]) * np.inf
    for i in range(num):
        for wordInd, word in enumerate(words):
            if word in mode[i]:
                ind = wordInd
                break
        x1 = vectorizer.transform(jieba.cut(mode[i]))[:, index].toarray()
        
        for j in range(num):
            if temp0[ind][j] == 1:
                x2 = vectorizer.transform(jieba.cut(cause[j]))[:, index].toarray()
                a = dtw_distance(x1, x2)
                co0[i][j] = a
                
        for j in range(num):
            if temp1[ind][j] == 1:
                x2 = vectorizer.transform(jieba.cut(result1[j]))[:, index].toarray()
                a = dtw_distance(x1, x2)
                co1[i][j] = a
                
        for j in range(num):
            if temp2[ind][j] == 1:
                x2 = vectorizer.transform(jieba.cut(result2[j]))[:, index].toarray()
                a = dtw_distance(x1, x2)
                co2[i][j] = a
                
        for j in range(num):
            if temp3[ind][j] == 1:
                x2 = vectorizer.transform(jieba.cut(result3[j]))[:, index].toarray()
                a = dtw_distance(x1, x2)
                co3[i][j] = a
                
    co0 = _returnmin(co0, num)
    co1 = _returnmin(co1, num)
    co2 = _returnmin(co2, num)
    co3 = _returnmin(co3, num)
    return co0, co1, co2, co3


def read_fmeca(df, check_invalid_col=["单元名称、型号或图号（2）", "故障模式(4)"],
               a_col="{单元名称、型号或图号（2）}",
               b_col="{故障原因(5)}",
               d_col="{单元名称、型号或图号（2）}{故障模式(4)}",
               b_c_col="{单元名称、型号或图号（2）}{故障模式(4)}@{故障检测方法（8）}",
               e_col="{故障自身影响}",
               f_col="{对上一级产品的影响}",
               g_col="{最终影响}"):
    if check_invalid_col:
        df.dropna(subset=check_invalid_col, how="all", axis=0)
        df.loc[:, check_invalid_col] = df.loc[:, check_invalid_col].fillna(method="ffill")
    df = df.fillna("")
    _convert_col(df, a_col, 'a_value')
    _convert_col(df, b_col, 'b_value')
    _convert_col(df, d_col, 'd_value')
    _convert_col(df, b_c_col, 'b_c_value')
    _convert_col(df, e_col, 'e_value')
    _convert_col(df, f_col, 'f_value')
    _convert_col(df, g_col, 'g_value')

    ## Td-Idf Model Initialization
    fr = df.loc[:, ['a_value', 'b_value', 'd_value', 'e_value', 'f_value', 'g_value']]
    texts_ = fr.groupby(['a_value'])['b_value'].apply(list).to_dict() ## { a_value: [b_value1, b_value2, ...], ... }
    texts_ = _dict_add(texts_, fr, 'd_value')
    texts_ = _dict_add(texts_, fr, 'e_value')
    texts_ = _dict_add(texts_, fr, 'f_value')
    texts_ = _dict_add(texts_, fr, 'g_value')
    key_names, vectorizer, index = _getTfIdfModel(texts_)
    
    mode = df.loc[:, 'd_value'].values.tolist()
    cause = df.loc[:, 'b_value'].values.tolist()
    result1 = df.loc[:, 'e_value'].values.tolist()
    result2 = df.loc[:, 'f_value'].values.tolist()
    result3 = df.loc[:, 'g_value'].values.tolist()
    co0, co1, co2, co3 = _col_match(df.loc[:, 'a_value'].values.tolist(), vectorizer, mode, cause, result1, result2, result3, index)
    
    indx, indy = np.where(co0 > 0.5)
    df.loc[indx, 'b_value'] = [mode[i] for i in indy]
    indx, indy = np.where(co1 > 0.5)
    df.loc[indx, 'e_value'] = [mode[i] for i in indy]
    indx, indy = np.where(co2 > 0.5)
    df.loc[indx, 'f_value'] = [mode[i] for i in indy]
    indx, indy = np.where(co3 > 0.5)
    df.loc[indx, 'g_value'] = [mode[i] for i in indy]
        
    if d_col in b_c_col:
        d_col_sign = [itm for itm in
                      re.sub(r"\{[^}]*\}", "|<-EPC->|", "".join(b_c_col.split(d_col, 1))).split("|<-EPC->|") if itm]
    else:
        d_col_sign = []

    result_list = {"nodes": [], "edges": []}
    node_registre = set()
    for d_value, b_c_value, b_values, e_values, f_values, g_values in df.loc[:,
                                                                      ['d_value', 'b_c_value', 'b_value', 'e_value',
                                                                       'f_value', 'g_value']].values:
        if not d_value.replace(" ", ""):
            continue
        if d_value not in b_c_value or _check_repeat("".join(b_c_value.split(d_value, 1)), d_col_sign):
            result_list['nodes'].append({'text': b_c_value, 'type': CKPT})
            result_list['edges'].append({'from': d_value, 'to': b_c_value})
        if d_value not in node_registre:
            result_list['nodes'].append({'text': d_value, 'type': RES})
            node_registre.add(d_value)
        if b_values:
            for b_value in b_values.split(";"):
                if not b_value.replace(" ", ""):
                    continue
                if b_value is not d_value:  #
                    result_list['edges'].append({'from': b_value, 'to': d_value})
                if b_value not in node_registre:
                    result_list['nodes'].append({'text': b_value, 'type': RES})
                    node_registre.add(b_value)
        if e_values:
            for e_value in e_values.split(";"):
                if not e_value.replace(" ", ""):
                    continue
                if d_value is not e_value:
                    result_list['edges'].append({'from': d_value, 'to': e_value})
                if e_value not in node_registre:
                    result_list['nodes'].append({'text': e_value, 'type': RES})
                    node_registre.add(e_value)
                if f_values:
                    for f_value in f_values.split(";"):
                        if not f_value.replace(" ", ""):
                            continue
                        if e_value is not f_value:
                            result_list['edges'].append({'from': e_value, 'to': f_value})
                        if f_value not in node_registre:
                            result_list['nodes'].append({'text': f_value, 'type': RES})
                            node_registre.add(f_value)
                        if g_values:
                            for g_value in g_values.split(";"):
                                if not g_value.replace(" ", ""):
                                    continue
                                if f_value is not g_value:
                                    result_list['edges'].append({'from': f_value, 'to': g_value})
                                if g_value not in node_registre:
                                    result_list['nodes'].append({'text': g_value, 'type': RES})
                                    node_registre.add(g_value)
                elif g_values:
                    for g_value in g_values.split(";"):
                        if not g_value.replace(" ", ""):
                            continue
                        if e_value is not g_value:
                            result_list['edges'].append({'from': e_value, 'to': g_value})
                        if g_value not in node_registre:
                            result_list['nodes'].append({'text': g_value, 'type': RES})
                            node_registre.add(g_value)

        elif f_values:
            for f_value in f_values.split(";"):
                if not f_value.replace(" ", ""):
                    continue
                if d_value is not f_value:
                    result_list['edges'].append({'from': d_value, 'to': f_value})
                if f_value not in node_registre:
                    result_list['nodes'].append({'text': f_value, 'type': RES})
                    node_registre.add(f_value)
                if g_values:
                    for g_value in g_values.split(";"):
                        if not g_value.replace(" ", ""):
                            continue
                        if f_value is not g_value:
                            result_list['edges'].append({'from': f_value, 'to': g_value})
                        if g_value not in node_registre:
                            result_list['nodes'].append({'text': g_value, 'type': RES})
                            node_registre.add(g_value)
        elif g_values:
            for g_value in g_values.split(";"):
                if not g_value.replace(" ", ""):
                    continue
                if d_value is not g_value:
                    result_list['edges'].append({'from': d_value, 'to': g_value})
                if g_value not in node_registre:
                    result_list['nodes'].append({'text': g_value, 'type': RES})
                    node_registre.add(g_value)
    return result_list


if __name__ == '__main__':
    df = pd.read_excel(r'example.xlsx', sheet_name="body")

    result_list = read_fmeca(df)

    print(result_list)

    with open("result.json", "w+", encoding="utf-8") as f:
        json.dump(result_list, f, indent=4, ensure_ascii=False)
