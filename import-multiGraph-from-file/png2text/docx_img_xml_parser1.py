from docx import Document
from lxml import etree
import re, xmltodict

def _convertTxml(txtStruct, conn=''):
    res = []
    if isinstance(txtStruct, dict):
        for k, v in txtStruct.items():
            if k == 'w:t':
                res.append(str(v))
                break
            elif isinstance(v, list) or isinstance(v, dict):
                res.extend(_convertTxml(v, conn=conn))
    elif isinstance(txtStruct, list):
        for v in txtStruct:
            res.extend(_convertTxml(v, conn=conn))
    return conn.join(res)

def _getFuzzyValue(nodeStruct, key_):
    for k, v in nodeStruct.items():
        if key_ in k.lower():
            return v
    return ""
        
def _convertNxml(nodeStruct, conn=''):
    res = []
    if isinstance(nodeStruct, list):
        for itm in nodeStruct:
            res.extend(_convertNxml(itm, conn=conn))
    elif isinstance(nodeStruct, dict):
        if "v:textbox" in nodeStruct.keys():
            res.append({
                'left': int(_getFuzzyValue(nodeStruct, "style").split(";left:",1)[1].split(";",1)[0]),
                'top': int(_getFuzzyValue(nodeStruct, "style").split(";top:",1)[1].split(";",1)[0]),
                'width': int(_getFuzzyValue(nodeStruct, "style").split(";width:",1)[1].split(";",1)[0]),
                'height': int(_getFuzzyValue(nodeStruct, "style").split(";height:",1)[1].split(";",1)[0]),
                'id': _getFuzzyValue(nodeStruct, "spid"),
                "text": _convertTxml(nodeStruct['v:textbox'], conn=conn)
                })
    return res

def _convertVxml(vStruct, conn=''):
    struct = {'nodes':[], 'edges':[]}
    if isinstance(vStruct, list):
        for v in vStruct:
            struct_ = _convertVxml(v)
            struct['nodes'].extend(struct_['nodes'])
            struct['edges'].extend(struct_['edges'])
    elif isinstance(vStruct, dict):
        for k, v in vStruct.items():
            if k in ['v:line','v:lines']:
                for itm in v:
                    struct['edges'].append({
                        'from': [int(i) for i in _getFuzzyValue(itm, "from").split(',')],
                        'to': [int(i) for i in _getFuzzyValue(itm, "to").split(',')],
                        'id': _getFuzzyValue(itm, "spid"),
                        })
            elif k in ['v:rect', 'v:shape']:
                struct['nodes'].extend(_convertNxml(v, conn=conn))
            elif isinstance(v, list) or isinstance(v, dict):
                struct_ = _convertVxml(v, conn=conn)
                struct['nodes'].extend(struct_['nodes'])
                struct['edges'].extend(struct_['edges'])
    return struct
    
def get_img(path):
    body_xml_str = Document(path)._body._element.xml # 获取body中的xml
    image_xml_str = [
        _convertVxml(xmltodict.parse(body_xml_slice)['w:pict'])
        for body_xml_slice in re.findall(
            r'(\<w\:pict[\w\W]+?\<\/w\:pict\>)',
            body_xml_str
            )]
    return image_xml_str

if __name__ == '__main__':
    from pprint import pprint
    path = r'飞控高升力LRU清单.doc'
    pprint(get_img(path))
