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

def _convertNxml(nodeStruct, conn=''):
    res = []
    if isinstance(nodeStruct, list):
        for itm in nodeStruct:
            res.extend(_convertNxml(itm, conn=conn))
    elif isinstance(nodeStruct, dict):
        if "v:textbox" in nodeStruct.keys():
            res.append({
                'type': "textbox",
                'left': int(nodeStruct['@style'].split(";left:",1)[1].split(";",1)[0]),
                'top': int(nodeStruct['@style'].split(";top:",1)[1].split(";",1)[0]),
                'width': int(nodeStruct['@style'].split(";width:",1)[1].split(";",1)[0]),
                'height': int(nodeStruct['@style'].split(";height:",1)[1].split(";",1)[0]),
                'id': nodeStruct['@o:spid'],
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
            if k in ['v:line']:
                for itm in v:
                    struct['edges'].append({
                        'type': "line",
                        'from': [int(i) for i in itm['@from'].split(',')],
                        'to': [int(i) for i in itm['@to'].split(',')],
                        'id': itm['@o:spid'],
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


def get_hierarchy(path, error=10):
    result = get_img(path)
    for pic in range(len(result)):
        containers = result[pic]['nodes']
        arrows = result[pic]['edges']
        for i in range(len(containers)):
            result[pic]['nodes'][i]['children'] = []
            for j in range(i, len(containers)):  # 第i个框上下左右都包含第j个框
                if containers[i]['left']<containers[j]['left'] and containers[i]['top']<containers[j]['top'] and\
                        (containers[i]['left']+containers[i]['width'])<(containers[j]['left']+containers[j]['width']) and\
                        (containers[i]['top']+containers[i]['height'])<(containers[j]['top']+containers[j]['height']):
                    result[pic]['nodes'][i]['children'].append(result[pic]['nodes'][j]['id'])
        for i in range(len(arrows)):
            result[pic]['edges'][i]['from_id'] = ''
            result[pic]['edges'][i]['to_id'] = ''
            current_width = float('inf')
            for j in range(len(containers)):  # 第i条线的起点横纵都被第j个框包含
                if containers[j]['left'] - error < result[pic]['edges'][i]['from'][0] < containers[j]['left']+containers[j]['width']+error and\
                        containers[j]['top']-error < result[pic]['edges'][i]['from'][1] < containers[j]['top']+containers[j]['height']+error:
                    if int(result[pic]['nodes'][j]['width']) < current_width:
                        result[pic]['edges'][i]['from_id'] = result[pic]['nodes'][j]['id']
                        current_width = int(result[pic]['nodes'][j]['width'])
            current_width = float('inf')
            for j in range(len(containers)):  # 第i条线的终点横纵都被第j个框包含
                if containers[j]['left'] - error < result[pic]['edges'][i]['to'][0] < containers[j]['left'] + containers[j]['width'] + error and\
                        containers[j]['top'] - error < result[pic]['edges'][i]['to'][1] < containers[j]['top'] + containers[j]['height'] + error:
                    if int(result[pic]['nodes'][j]['width']) < current_width:
                        result[pic]['edges'][i]['to_id'] = result[pic]['nodes'][j]['id']
                        current_width = int(result[pic]['nodes'][j]['width'])
    return result


if __name__ == '__main__':
    from pprint import pprint
    path = r'飞控高升力LRU清单.docx'

    pprint(get_hierarchy(path), indent=2)
