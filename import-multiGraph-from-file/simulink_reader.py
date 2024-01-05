""" Module 提供对于simulink文件的读取"""
import os
import re
import xml.etree.ElementTree as ET
from copy import deepcopy
from typing import List, Dict, Tuple
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
SIMULINK_FILE = r"test2.mdl"

# 画布缩放比例
WIDTH_RATE = 3
HEIGHT_RATE = 3


def _get_system(
    xml: ET.Element
) -> Dict:
    ''' 从单个system的XML提取system_data数据

    args:
        xml: system的xml对象
            <Element 'System' at 0x000001D8EDDA6D10>
    return:
        system_data: system的数据
            {'nodes': [{...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, ...], 'edges': [{...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, ...]}
    '''
    system_data = {"nodes": [], "edges": []}
    input_index = 1
    output_index = 1
    # 处理节点
    for node_xml in xml.findall("Block"):

        if (node_xml.attrib["BlockType"] == "SubSystem"):

            # 1.提取关键信息
            node_id = node_xml.attrib["SID"]
            node_text = node_xml.attrib["Name"]
            subsystem_id = node_xml.findall("System")[0].attrib["Ref"]

            for ele in node_xml.findall("P"):
                if ele.attrib["Name"] == "Position":
                    Position = eval(ele.text)
                    node_x = Position[0]*WIDTH_RATE
                    node_y = Position[1]*HEIGHT_RATE

                if ele.attrib["Name"] == "Ports":
                    ports = eval(ele.text)
                    if len(ports) == 2:
                        node_input = ports[0]
                        node_output = ports[1]
                    elif len(ports) == 1:
                        node_input = ports[0]
                        node_output = 0
                    else:
                        node_input = 0
                        node_output = 0

            node_width = 200
            node_height = 60 + max(node_input, node_output)*24

            # 2.构造subsystem Data
            node_data = {
                "id": node_id,
                "type": "subsystem-node",
                "x": node_x,
                "y": node_y,
                "properties": {
                    "tableName": "",
                    "SubsystemId": subsystem_id,
                    "fields": {
                        "input": node_input,
                        "output": node_output
                    }

                },
                "text": {
                    "x": node_x,
                    "y": node_y,
                    "value": node_text
                },
                "anchors": []
            }

            # 3 构造subsystem Data 中的anchors信息

            # 3.1 构造输入anchors
            for i in range(0, node_input):
                node_data["anchors"].append({
                    "x": node_x - node_width/2+10,
                    "y": node_y - node_height/2 + 60+i * 24,
                    "id": node_data['id']+'_'+str(i)+'_left',
                    "edgeAddable": False,
                    "type": "left"
                })

            # 3.2 构造输出anchors
            for i in range(0, node_output):
                node_data["anchors"].append({
                    "x": node_x - node_width/2+190,
                    "y": node_y - node_height/2 + 60+i * 24,
                    "id": node_data['id']+'_'+str(i)+'_right',
                    "edgeAddable": False,
                    "type": "right"
                })
        else:
            # 共用的属性信息
            properties = {
                "showType": "edit",
                "collision": False,
                "detectable": True,
                "fuzzible": False,
                "fuzzy_state": 0,
                "state": 0,
                "icon": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAsIDAsIDQwLCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBjb2xvcj0iIzAwMCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTU0MCAtOTg3LjM2KSI+PHBhdGggZD0iTTU2NS40MyAxMDAxLjljNi41NjIgMi4wODkgMTEuMzE2IDguMjMzIDExLjMxNiAxNS40ODggMCA4Ljk3NS03LjI3NSAxNi4yNS0xNi4yNSAxNi4yNXMtMTYuMjUtNy4yNzUtMTYuMjUtMTYuMjVjMC0yLjgwMi43MS01LjQzOCAxLjk1OC03Ljc0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHlsZT0iaXNvbGF0aW9uOmF1dG87bWl4LWJsZW5kLW1vZGU6bm9ybWFsIi8+PGNpcmNsZSBjeD0iNTYwIiBjeT0iMTAwMS40IiByPSIxLjUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjMiIHN0eWxlPSJpc29sYXRpb246YXV0bzttaXgtYmxlbmQtbW9kZTpub3JtYWwiLz48cGF0aCBkPSJNNTYwIDEwMTQuNGMtMS4yMDYgMC0xMS0xMC45OTktMTIuMzU0LTkuOTc1UzU1NyAxMDE2LjE0OCA1NTcgMTAxNy40czEuMzYgMyAzIDMgMy0xLjM2MSAzLTMtMS43OTQtMy0zLTN6IiBmaWxsPSIjZmZmIi8+PC9nPjwvc3ZnPg0K",
                "typeColor": "#85C1E9",
                "ui": "node-red"
            }

            # 1. 提取信息
            node_id = node_xml.attrib["SID"]
            node_text = node_xml.attrib["Name"]

            for ele in node_xml.findall("P"):
                if ele.attrib["Name"] == "Position":
                    Position = eval(ele.text)
                    node_x = Position[0]*WIDTH_RATE
                    node_y = Position[1]*HEIGHT_RATE

            node_data = {
                "id": node_id,
                "type": "",
                "x": node_x,
                "y": node_y,
                "properties": properties,
                "text": {
                    "x": node_x,
                    "y": node_y,
                    "value": node_text
                },
                "anchors": []
            }
            # 不同节点定制化策略
            if node_xml.attrib["BlockType"] == "Inport":
                node_data["type"] = "input-node"
                node_data["properties"]["index"] = input_index
                node_data["properties"]["typeColor"] = "#85C1E9"
                node_data["text"]["value"] = "输入"+str(input_index)
                node_data["anchors"].append({
                    "x": node_x + 50,
                    "y": node_y,
                    "id": node_id+"_right",
                    "edgeAddable": False,
                    "type": "right"
                })
                input_index += 1
            elif node_xml.attrib["BlockType"] == "Outport":
                node_data["type"] = "output-node"
                node_data["properties"]["index"] = output_index
                node_data["properties"]["typeColor"] = "#85C1E9"
                node_data["text"]["value"] = "输出"+str(output_index)
                node_data["anchors"].append({
                    "x": node_x - 50,
                    "y": node_y,
                    "id": node_id+"_left",
                    "edgeAddable": False,
                    "type": "left"
                })
                output_index += 1
            else:
                node_data["type"] = "fault-node"
                node_data["anchors"].append({
                    "x": node_x + 50,
                    "y": node_y,
                    "id": node_id+"_right",
                    "edgeAddable": False,
                    "type": "right"
                })
                node_data["anchors"].append({
                    "x": node_x - 50,
                    "y": node_y,
                    "id": node_id+"_left",
                    "edgeAddable": False,
                    "type": "left"
                })
        system_data["nodes"].append(node_data)

    # 处理连线
    for index, edge_xml in enumerate(xml.findall("Line")):
        # 1. 初始化edge
        edge_data = {
            "id": str(index),
            "type": "custom-edge",
            "properties": {},
            "pointsList": []
        }
        # 2. 处理起点
        for ele in edge_xml.findall("P"):
            if ele.attrib["Name"] == "Src":
                Source_ID = ele.text.split("#")[0]
                Source_Port = int(ele.text.split(":")[-1])

        edge_data["sourceNodeId"] = Source_ID

        for node in system_data["nodes"]:
            if node["id"] == Source_ID:
                if node["type"] == "subsystem-node":
                    edge_data["sourceAnchorId"] = node["id"] + \
                        "_"+str(Source_Port-1)+"_right"
                    for anchor in node["anchors"]:
                        if anchor["id"] == edge_data["sourceAnchorId"]:
                            edge_data["startPoint"] = {
                                "x": anchor["x"],
                                "y": anchor["y"]
                            }
                else:
                    edge_data["sourceAnchorId"] = node["id"]+"_right"
                    for anchor in node["anchors"]:
                        if anchor["id"] == edge_data["sourceAnchorId"]:
                            edge_data["startPoint"] = {
                                "x": anchor["x"],
                                "y": anchor["y"]
                            }
        # 3. 处理终点
        # 多分支
        Target_ID = None
        Target_Port = None
        stack_branch = []
        stack_branch.append(edge_xml)

        # 深度优先搜索 终止节点

        while (len(stack_branch) > 0):
            ele = stack_branch.pop()
            if ele.findall("Branch"):
                for ele2 in ele.findall("Branch"):
                    stack_branch.append(ele2)
            else:
                edge_data_copy = deepcopy(edge_data)
                for ele2 in ele.findall("P"):
                    if ele2.attrib["Name"] == "Dst":
                        Target_ID = ele2.text.split("#")[0]
                        Target_Port = int(ele2.text.split(":")[-1])
                        edge_data_copy["id"] = edge_data_copy["id"] + \
                            "_"+ele2.text

                edge_data_copy["targetNodeId"] = Target_ID
                for node in system_data["nodes"]:
                    if node["id"] == Target_ID:
                        if node["type"] == "subsystem-node":
                            edge_data_copy["targetAnchorId"] = node["id"] + \
                                "_"+str(Target_Port-1)+"_left"
                            for anchor in node["anchors"]:
                                if anchor["id"] == edge_data_copy["targetAnchorId"]:
                                    edge_data_copy["endPoint"] = {
                                        "x": anchor["x"],
                                        "y": anchor["y"]
                                    }
                        else:
                            edge_data_copy["targetAnchorId"] = node["id"]+"_left"
                            for anchor in node["anchors"]:
                                if anchor["id"] == edge_data_copy["targetAnchorId"]:
                                    edge_data_copy["endPoint"] = {
                                        "x": anchor["x"],
                                        "y": anchor["y"]
                                    }

                system_data["edges"].append(edge_data_copy)

    return system_data


def get_system(
    name: str, 
    xml: ET.Element, 
    parent_map: Dict
)->Dict:
    '''
    从xml中提取system信息

    Args:
        name: system的名称 
            例如: system_root.xml
        xml: xml对象
            <Element 'System' at 0x000001F39C775D10>
        parent_map: 父节点信息 {child:parent,child:parent...}
            {'system_2939': 'system_2927', 'system_3750': 'system_2927', 'system_3753': 'system_2927', 'system_3757': 'system_2927', 'system_3761': 'system_2927', 'system_3773': 'system_2927', 'system_3396': 'system_3388', 'system_3412': 'system_3388', 'system_3430': 'system_3388', 'system_3451': 'system_3388', 'system_3469': 'system_3388', 'system_3484': 'system_3388', 'system_3490': 'system_3388', 'system_3496': 'system_3388', ...}
    
    Return:system_data
        {
        "system_id": system_id,
        "name": system_id,
        "parent_id": parent_id,
        "data": _get_system(xml)
        }
    '''

    system_id = name.split(".")[0]

    if (system_id == "system_root"):
        parent_id = None
    else:
        parent_id = parent_map[system_id]

    return {
        "system_id": system_id,
        "name": system_id,
        "parent_id": parent_id,
        "data": _get_system(xml)
    }


def get_parent_map(
    xml_system_dict: Dict
):
    '''
    从xml中提取父节点信息

    Args:
        xml: xml对象
    '''
    parent_map = {}
    for name, xml in xml_system_dict.items():

        if name.split(".")[-1] == "rels":
            parent_id = name.split(".")[0]

            for ele in xml:
                parent_map[ele.attrib["Id"]] = parent_id

    return parent_map

def simulink_reader(
    file_path: str
)->Dict:
    '''
    从simulink文件中提取数据

    Args:
        file_path: simulink文件绝对路径 仅支持读取.mdl格式的simulink文件 且无法处理GOTO等特殊情况
    Return:
        G_data: 能够被前端渲染的数据
            {'currentSystemId': 'system_root', 'SystemData': [{...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, ...]}
    '''
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()

    xml_dict = {}
    FLAG = False
    for index, text in enumerate(content):
        # 正则表达式匹配__MWOPC_PART_BEGIN__
        if re.search("__MWOPC_PART_BEGIN__", text):

            # 哈希值跳过
            if re.search("BASE64", text):
                continue
            name = text.split(' ')[-1]
            start_index = index+2
            if re.search("Version information", content[start_index]):
                start_index += 1
            start = re.search(r"<[A-Z|a-z|:]+", content[start_index]).group()
            start = start[1:]
            FLAG = True
            continue

        if FLAG:
            if re.search("/"+start, text):
                FLAG = False
                end_index = index
                xml_dict[name] = "".join(content[start_index:end_index+1])

    xml_system_dict = {}

    for name, xml in xml_dict.items():
        if re.search("systems", name):

            if name.split("/")[2] == "systems":
                name = name.split("/")[-1].replace("\n", "")
                xml_system_dict[name] = ET.fromstring(xml)

    parent_map = get_parent_map(xml_system_dict)
    G_data = {
        "currentSystemId": "system_root",
        "SystemData": []
    }
    for name, xml in xml_system_dict.items():
        if name.split(".")[-1] == "xml":
            G_data["SystemData"].append(get_system(name, xml, parent_map))

    return G_data


if __name__ == "__main__":
    with open(os.path.join(DIR_PATH, SIMULINK_FILE), 'r', encoding='utf-8') as f:
        content = f.readlines()

    G_data = simulink_reader(os.path.join(DIR_PATH, SIMULINK_FILE))

    with open(os.path.join(DIR_PATH, "data.json"), "w+", encoding='utf-8') as f:
        import json
        json.dump(G_data, f, ensure_ascii=False, indent=4)

    
