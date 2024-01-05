# coding:utf-8

import re, jieba
from sklearn import feature_extraction, feature_selection
import numpy as np
import pandas as pd

def _clean_text(text):
    return re.sub(r"^[\t\n\r ]+|$[\t\n\r ]+", '', re.sub("^[\t\n\r a-zA-Z0-9]+\.", "", text))

def _convert_col(df, col, key):
    df[key] = ["" for _ in df.index.values]
    for coltxt in col.split("}"):
        if "{" in coltxt:
            colSep, colName = coltxt.split("{", 1)
            df[key] = df[key].str.cat(df[colName].map(lambda itm: _clean_text(itm)), sep=colSep)
        else:
            df[key] += coltxt

def _check_repeat(detection_value, b_c_sign):
    for itm in sorted(b_c_sign, key=len, reverse=True):
        detection_value = detection_value.replace(itm, "")
    return len(detection_value.replace(" ", "")) > 0


def _dict_add(texts_, fr, value_):
    texts_add = fr.groupby(['component_value'])[value_].apply(list).to_dict()
    for key, value in texts_add.items():
        texts_[key] = texts_.get(key, []) +  value
    return texts_

def _getTfIdfModel(txts, ngrams=3, p_value_limit=0.95, max_features=10000, xstep=10):
    convert_txts = [" ".join(jieba.cut(txt)) for k, itm in txts.items() for txt in itm if txt.replace("-", "").replace(" ","")]
    labels = [k for k, itm in txts.items() for txt in itm if txt.replace("-", "").replace(" ","")]
    vectorizer = feature_extraction.text.TfidfVectorizer(max_features=max_features, ngram_range=(1, ngrams))
    vectorizer.fit(convert_txts)
    corpus = vectorizer.transform(convert_txts)
    try:
        key_names = vectorizer.get_feature_names_out()
    except:
        key_names = vectorizer.get_feature_names()
    p_all = np.zeros(len(key_names))
    for label in np.unique(labels):
        _, p = feature_selection.chi2(corpus, [label == label_ for label_ in labels])
        p_all = np.minimum(p_all, p)
    ind = np.argsort(p_all)
    ind = ind[p_all[ind] < 1 - p_value_limit]
    return [key_names[i].replace(" ", "") for i in ind], vectorizer, sorted(ind)

def dtw_distance(doc1, doc2):
    i = 0
    j = 0
    distance = 0
    while i < (len(doc1) - 1) or j < (len(doc2) - 1):
        cost = [np.inf, np.inf, np.inf]
        if i < (len(doc1) - 1):
            cost[0] = np.linalg.norm(doc1[i, :] - doc1[(i + 1), :])
        if j < (len(doc2) - 1):
            cost[1] = np.linalg.norm(doc2[j, :] - doc2[(j + 1), :])
        if i < (len(doc1) - 1) and j < (len(doc2) - 1):
            cost[2] = np.linalg.norm(doc1[(i + 1), :] - doc2[(j + 1), :])
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

def _col_match(words, vectorizer, mode, cause, self_effect, trans_effect, final_effect, index):
    words = sorted(set(words), key=len, reverse=True)
    num = len(mode)

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
    for itemInd, name in enumerate(self_effect):
        name_ = name
        for wordInd, word in enumerate(words):
            if word in name_:
                temp1[:, itemInd] = 0
                temp1[wordInd, itemInd] = 1
                name_ = name_.replace(word, "#")
                
    temp2 = np.zeros([(len(words) + 1), num])
    temp2[len(words), :] = 1
    for itemInd, name in enumerate(trans_effect):
        name_ = name
        for wordInd, word in enumerate(words):
            if word in name_:
                temp2[:, itemInd] = 0
                temp2[wordInd, itemInd] = 1
                name_ = name_.replace(word, "#")
                
    temp3 = np.zeros([(len(words) + 1), num])
    temp3[len(words), :] = 1
    for itemInd, name in enumerate(final_effect):
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
                x2 = vectorizer.transform(jieba.cut(self_effect[j]))[:, index].toarray()
                a = dtw_distance(x1, x2)
                co1[i][j] = a
                
        for j in range(num):
            if temp2[ind][j] == 1:
                x2 = vectorizer.transform(jieba.cut(trans_effect[j]))[:, index].toarray()
                a = dtw_distance(x1, x2)
                co2[i][j] = a
                
        for j in range(num):
            if temp3[ind][j] == 1:
                x2 = vectorizer.transform(jieba.cut(final_effect[j]))[:, index].toarray()
                a = dtw_distance(x1, x2)
                co3[i][j] = a
                
    co0 = _returnmin(co0, num)
    co1 = _returnmin(co1, num)
    co2 = _returnmin(co2, num)
    co3 = _returnmin(co3, num)
    return co0, co1, co2, co3


def read_fmeca(df, check_invalid_col=["单元名称、型号或图号（2）", "故障模式(4)"],
               component_col="{单元名称、型号或图号（2）}",
               faultcause_col="{故障原因(5)}",
               faultmode_col="{单元名称、型号或图号（2）}{故障模式(4)}",
               detection_col="{单元名称、型号或图号（2）}{故障模式(4)}@{故障检测方法（8）}",
               self_effect_col="{故障自身影响}",
               trans_effect_col="{对上一级产品的影响}",
               final_effect_col="{最终影响}",
               ckptnode="test-node", resnode="fault-node"):
    if check_invalid_col:
        df.dropna(subset=check_invalid_col, how="all", axis=0)
        df.loc[:, check_invalid_col] = df.loc[:, check_invalid_col].fillna(method="ffill")
    df = df.fillna("")
    _convert_col(df, component_col, 'component_value')
    _convert_col(df, faultcause_col, 'faultcause_value')
    _convert_col(df, faultmode_col, 'faultmode_value')
    _convert_col(df, detection_col, 'detection_value')
    _convert_col(df, self_effect_col, 'self_effect_value')
    _convert_col(df, trans_effect_col, 'trans_effect_value')
    _convert_col(df, final_effect_col, 'final_effect_value')
    subsystem = {subsys: [] for subsys in set(df.loc[:, 'component_value'].values.tolist())}

    ## Td-Idf Model Initialization
    fr = df.loc[:, ['component_value', 'faultcause_value', 'faultmode_value', 'self_effect_value', 'trans_effect_value', 'final_effect_value']]
    texts_ = fr.groupby(['component_value'])['faultcause_value'].apply(list).to_dict() ## { component_value: [b_value1, b_value2, ...], ... }
    texts_ = _dict_add(texts_, fr, 'faultmode_value')
    texts_ = _dict_add(texts_, fr, 'self_effect_value')
    texts_ = _dict_add(texts_, fr, 'trans_effect_value')
    texts_ = _dict_add(texts_, fr, 'final_effect_value')
    _, vectorizer, index = _getTfIdfModel(texts_)
    
    mode = df.loc[:, 'faultmode_value'].values.tolist()
    cause = df.loc[:, 'faultcause_value'].values.tolist()
    self_effect = df.loc[:, 'self_effect_value'].values.tolist()
    trans_effect = df.loc[:, 'trans_effect_value'].values.tolist()
    final_effect = df.loc[:, 'final_effect_value'].values.tolist()
    co0, co1, co2, co3 = _col_match(df.loc[:, 'component_value'].values.tolist(), vectorizer, mode, cause, self_effect, trans_effect, final_effect, index)
    
    indy, indx = np.where(co0 > 0.5)
    df.loc[indx, 'faultcause_value'] = [mode[i] if cause[tureId].replace(" ", "").replace("-", "") else "" for tureId, i in zip(indx, indy)]
    indy, indx = np.where(co1 > 0.5)
    df.loc[indx, 'self_effect_value'] = [mode[i] if self_effect[tureId].replace(" ", "").replace("-", "") else "" for tureId, i in zip(indx, indy)]
    indy, indx = np.where(co2 > 0.5)
    df.loc[indx, 'trans_effect_value'] = [mode[i] if trans_effect[tureId].replace(" ", "").replace("-", "") else "" for tureId, i in zip(indx, indy)]
    indy, indx = np.where(co3 > 0.5)
    df.loc[indx, 'final_effect_value'] = [mode[i] if final_effect[tureId].replace(" ", "").replace("-", "") else "" for tureId, i in zip(indx, indy)]
        
    if faultmode_col in detection_col:
        d_col_sign = [itm for itm in
                      re.sub(r"\{[^}]*\}", "|<-EPC->|", "".join(detection_col.split(faultmode_col, 1))).split("|<-EPC->|") if itm]
    else:
        d_col_sign = []

    result_list = {"nodes": [], "edges": []}
    node_registre = set()
    component_pre = None
    for component_value, faultmode_value, detection_value, \
        faultcause_values, self_effect_values, trans_effect_values, final_effect_values in \
            df.loc[:,['component_value', 'faultmode_value', 'detection_value', 
                      'faultcause_value', 'self_effect_value', 'trans_effect_value', 
                      'final_effect_value']].values:
        if not faultmode_value.replace(" ", "").replace("-", ""):
            continue
        if faultmode_value not in detection_value or _check_repeat("".join(detection_value.split(faultmode_value, 1)), d_col_sign):
            result_list['nodes'].append({'text': detection_value, 'type': ckptnode})
            result_list['edges'].append({'from': faultmode_value, 'to': detection_value})
        if faultmode_value not in node_registre:
            result_list['nodes'].append({'text': faultmode_value, 'type': resnode})
            node_registre.add(faultmode_value)
        if (component_value and component_value.replace(" ","")).replace("-", ""):
            if faultmode_value not in subsystem[component_value]:
                subsystem[component_value].append(faultmode_value)
            component_pre = component_value
        elif component_pre:
            if faultmode_value not in subsystem[component_pre]:
                subsystem[component_pre].append(faultmode_value)
        if faultcause_values:
            for faultcause_value in faultcause_values.split(";"):
                if not faultcause_value.replace(" ", "").replace("-", ""):
                    continue
                if faultcause_value is not faultmode_value:  #
                    result_list['edges'].append({'from': faultcause_value, 'to': faultmode_value})
                if faultcause_value not in node_registre:
                    result_list['nodes'].append({'text': faultcause_value, 'type': resnode})
                    node_registre.add(faultcause_value)
        if self_effect_values:
            for self_effect_value in self_effect_values.split(";"):
                if not self_effect_value.replace(" ", "").replace("-", ""):
                    continue
                if faultmode_value is not self_effect_value:
                    result_list['edges'].append({'from': faultmode_value, 'to': self_effect_value})
                if self_effect_value not in node_registre:
                    result_list['nodes'].append({'text': self_effect_value, 'type': resnode})
                    node_registre.add(self_effect_value)
                if trans_effect_values:
                    for trans_effect_value in trans_effect_values.split(";"):
                        if not trans_effect_value.replace(" ", ""):
                            continue
                        if self_effect_value is not trans_effect_value:
                            result_list['edges'].append({'from': self_effect_value, 'to': trans_effect_value})
                        if trans_effect_value not in node_registre:
                            result_list['nodes'].append({'text': trans_effect_value, 'type': resnode})
                            node_registre.add(trans_effect_value)
                        if final_effect_values:
                            for final_effect_value in final_effect_values.split(";"):
                                if not final_effect_value.replace(" ", ""):
                                    continue
                                if trans_effect_value is not final_effect_value:
                                    result_list['edges'].append({'from': trans_effect_value, 'to': final_effect_value})
                                if final_effect_value not in node_registre:
                                    result_list['nodes'].append({'text': final_effect_value, 'type': resnode})
                                    node_registre.add(final_effect_value)
                elif final_effect_values:
                    for final_effect_value in final_effect_values.split(";"):
                        if not final_effect_value.replace(" ", "").replace("-", ""):
                            continue
                        if self_effect_value is not final_effect_value:
                            result_list['edges'].append({'from': self_effect_value, 'to': final_effect_value})
                        if final_effect_value not in node_registre:
                            result_list['nodes'].append({'text': final_effect_value, 'type': resnode})
                            node_registre.add(final_effect_value)

        elif trans_effect_values:
            for trans_effect_value in trans_effect_values.split(";"):
                if not trans_effect_value.replace(" ", "").replace("-", ""):
                    continue
                if faultmode_value is not trans_effect_value:
                    result_list['edges'].append({'from': faultmode_value, 'to': trans_effect_value})
                if trans_effect_value not in node_registre:
                    result_list['nodes'].append({'text': trans_effect_value, 'type': resnode})
                    node_registre.add(trans_effect_value)
                if final_effect_values:
                    for final_effect_value in final_effect_values.split(";"):
                        if not final_effect_value.replace(" ", ""):
                            continue
                        if trans_effect_value is not final_effect_value:
                            result_list['edges'].append({'from': trans_effect_value, 'to': final_effect_value})
                        if final_effect_value not in node_registre:
                            result_list['nodes'].append({'text': final_effect_value, 'type': resnode})
                            node_registre.add(final_effect_value)
        elif final_effect_values:
            for final_effect_value in final_effect_values.split(";"):
                if not final_effect_value.replace(" ", "").replace("-", ""):
                    continue
                if faultmode_value is not final_effect_value:
                    result_list['edges'].append({'from': faultmode_value, 'to': final_effect_value})
                if final_effect_value not in node_registre:
                    result_list['nodes'].append({'text': final_effect_value, 'type': resnode})
                    node_registre.add(final_effect_value)
    nodeNames = [node["text"] for node in result_list['nodes']]
    edges = [[] for node in result_list['nodes']]
    for edge in result_list['edges']:
        edges[nodeNames.index(edge["from"])].append(nodeNames.index(edge["to"]))
    subsystems = {subsysid: {"name": subsysInfo[0], "nodesId": sorted(subsysInfo[1])} for subsysid, subsysInfo in enumerate(subsystem.items())} 
##    for subsys, faults in subsystem.items():
##        result_list['nodes'].append({'text': subsys, 'type': SUBSYS, 'children': sorted(faults)})
    return result_list['nodes'], edges, subsystems
