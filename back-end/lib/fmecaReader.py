import pandas as pd
import re
import json

CKPT = "test-node" ## 测点
RES = "fault-node" ## 故障节点
SUBSYS = "sub-system" ## 子系统

def _clean_text(text):
    #pattern = r'^[a-z]+\.' # 匹配以字母和点号（.）开头的字符串
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
    for itm in b_c_sign:
        b_c_value = b_c_value.replace(itm, "")
    return len(b_c_value.replace(" ", "")) > 0

def read_fmeca(df, check_invalid_col = ["单元名称、型号或图号（2）", "故障模式(4)"],
               c_col = "{单元名称、型号或图号（2）}",
               d_col = "{单元名称、型号或图号（2）}{故障模式(4)}",
               b_c_col = "{单元名称、型号或图号（2）}{故障模式(4)}@{故障检测方法（8）}",
               e_col = "{故障自身影响}",
               f_col = "{对上一级产品的影响}"):
    if check_invalid_col:
        df.dropna(subset=check_invalid_col, how="all", axis=0)
        df.loc[:, check_invalid_col] = df.loc[:, check_invalid_col].fillna(method="ffill")
    df = df.fillna("")
    _convert_col(df, c_col, 'c_value')
    _convert_col(df, d_col, 'd_value')
    _convert_col(df, b_c_col, 'b_c_value')
    _convert_col(df, e_col, 'e_value')
    _convert_col(df, f_col, 'f_value')

    result_list = {"nodes":[], "edges": []}
    node_registre = set()
    subsys = {}
    #print(df.loc[:, ['d_value', 'b_c_value', 'e_value', 'f_value']])
    if d_col in b_c_col:
        d_col_sign = [itm for itm in re.sub(r"\{[^}]*\}", "|<-EPC->|", "".join(b_c_col.split(d_col,1))).split("|<-EPC->|") if itm]
    else:
        d_col_sign = []
    for c_value, d_value, b_c_value, e_values, f_values in df.loc[:, ['c_value', 'd_value', 'b_c_value', 'e_value', 'f_value']].values:
        if not d_value.replace(" ", ""):
            continue
        if c_value.replace(" ", ""):
            subsys[c_value] = subsys.get(c_value, []) + [d_value]
        if d_value not in b_c_value or _check_repeat("".join(b_c_value.split(d_value, 1)), d_col_sign):
            result_list['nodes'].append({'text': b_c_value, 'type': CKPT})
            result_list['edges'].append({'from': d_value, 'to': b_c_value})
        if d_value not in node_registre:
            result_list['nodes'].append({'text': d_value, 'type': RES})
            node_registre.add(d_value)
        if e_values:
            for e_value in e_values.split(";"):
                if not e_value.replace(" ", ""):
                    continue
                result_list['edges'].append({'from': d_value, 'to': e_value})
                if e_value not in node_registre:
                    result_list['nodes'].append({'text': e_value, 'type': RES})
                    node_registre.add(e_value)
                if f_values:
                    for f_value in f_values.split(";"):
                        if not f_value.replace(" ", ""):
                            continue
                        result_list['edges'].append({'from': e_value, 'to': f_value})
                        if f_value not in node_registre:
                            result_list['nodes'].append({'text': f_value, 'type': RES})
                            node_registre.add(f_value)
        elif f_values:
            for f_value in f_values.split(";"):
                if not f_value.replace(" ", ""):
                    continue
                result_list['edges'].append({'from': d_value, 'to': f_value})
                if f_value not in node_registre:
                    result_list['nodes'].append({'text': f_value, 'type': RES})
                    node_registre.add(f_value)
    for subs, subsitms in subsys.items():
        result_list['nodes'].append({'text': subs, 'type': SUBSYS, "children": list(set(subsitms))})
    return result_list

if __name__ == '__main__':
    df = pd.read_excel(r'2example.xlsx', sheet_name="body")

    result_list = read_fmeca(df)

    print(result_list)

    with open("result.json", "w+", encoding="utf-8") as f:
        json.dump(result_list, f, indent=4, ensure_ascii=False)
