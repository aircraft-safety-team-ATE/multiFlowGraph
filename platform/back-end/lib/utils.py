# 前端基本配置
import uuid
import copy
import json

from typing import Iterable
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
import os
from typing import List, Tuple, Dict, Union
import pandas as pd
DIR_PATH = os.path.dirname(os.path.abspath(__file__))

SYS = "subsystem-node"
INPUT_NODE = "input-node"
OUTPUT_NODE = "output-node"
RES = "fault-node"  # 故障节点
SW = "switch-node"  # 开关节点
CKPT = "test-node"  # 测点
EDGE = "flow-bazier-edge"
TESTTYPE = [CKPT]
FAULTTYPE = [INPUT_NODE, OUTPUT_NODE, RES, SW]

CHECK_INVALID_COL = ["单元名称、型号或图号（2）", "故障模式(4)"]
COMPONENT_COL = "{单元名称、型号或图号（2）}"
FAULTCAUSE_COL = "{故障原因(5)}"
FAULTMODE_COL = "{单元名称、型号或图号（2）}{故障模式(4)}"
DETECTION_COL = "{单元名称、型号或图号（2）}{故障模式(4)}@{故障检测方法（8）}"
SELF_EFFECT_COL = "{故障自身影响}"
TRANS_EFFECT_COL = "{对上一级产品的影响}"
FINAL_EFFECT_COL = "{最终影响}"

WIDTH = 180
NODEWIDTH = 100
HEIGHT = 24
PADDING = 50

DEBUG_MODE = False

if DEBUG_MODE:
    from gui_utils import render_node_pos, wash_node_pos
    from fmecaReader import read_fmeca
else:
    from .gui_utils import render_node_pos, wash_node_pos
    from .fmecaReader import read_fmeca
# 拉直多子系统嵌套结构依赖方法


def _flatten_graph(
        struct: List[Dict],
        act_uid: Union[int, str] = 1,
        nodes_cnt: int = 0
) -> Tuple[List, List, List, List, List]:
    """拉直多子系统嵌套结构依赖方法
    args:
        struct: 多个子系统的数据结构
        act_uid: 当前系统的system_ID
        nodes_cnt:总节点计数,同时也是节点合并后的ID
    return:
        node:拉平后的节点列表
        edge:拉平后的连线列表
        in_inds: 输入节点ID列表
        out_inds: 输出节点列表
        system:
    """
    nodes = []
    edges = []
    id_map = {}
    systems = {}
    in_inds = []
    out_inds = []
    start_cnt = nodes_cnt
    act_id = struct[0]["sysmap"][act_uid]
    for itmId, itm in enumerate(struct[act_id]["data"]["nodes"]):
        if itm["type"] == SYS:
            nodes_, edges_, in_inds_, out_inds_, systems_ = _flatten_graph(
                struct, act_uid=itm["properties"]["SubsystemId"], nodes_cnt=nodes_cnt)
            nodes.extend(nodes_)
            edges.extend(edges_)
            for true_ind, anchor_id in zip(in_inds_, [lin_["id"] for lin_ in sorted(itm["anchors"], key=lambda it_: it_["y"]) if lin_["type"] == "left"]):
                id_map[anchor_id] = true_ind
            for true_ind, anchor_id in zip(out_inds_, [lin_["id"] for lin_ in sorted(itm["anchors"], key=lambda it_: it_["y"]) if lin_["type"] == "right"]):
                id_map[anchor_id] = true_ind
            systems.update(systems_)
            systems[struct[0]["sysmap"][itm["properties"]["SubsystemId"]]] = {
                "info": itm,
                "name": itm["text"]["value"],
                # 该分系统本身的编号
                "SubsystemId": itm["properties"]["SubsystemId"],
                "ParentSubsystemId": act_id,  # 需要同步更新上级分系统编号
                "NodeId": itmId,  # 需要同步更新上级分系统中该分系统的队列编号
                "nodesId": [nodes_cnt+node_itm for node_itm in range(len(nodes_))]
            }
            nodes_cnt += len(nodes_)
        else:
            if itm["type"] == INPUT_NODE:
                in_inds.append([nodes_cnt, itm["properties"]["index"]])
            elif itm["type"] == OUTPUT_NODE:
                out_inds.append([nodes_cnt, itm["properties"]["index"]])
            nodes.append({
                **itm,
                "SubsystemId": act_id,  # 该节点所属的分系统编号
                "NodeId": itmId  # 需要系统中该节点的队列编号
            })
            for anchor_itm in itm["anchors"]:
                id_map[anchor_itm["id"]] = nodes_cnt
            edges.append({})
            nodes_cnt += 1
    for itm in struct[act_id]["data"]["edges"]:
        if "sourceAnchorId" in itm.keys():
            srcId = id_map[itm["sourceAnchorId"]]
        else:
            for nid, ninfo in enumerate(nodes):
                if ninfo["id"] == itm["sourceNodeId"]:
                    srcId = nid
                    break
            else:
                continue
        if "targetAnchorId" in itm.keys():
            trgId = id_map[itm["targetAnchorId"]]
        else:
            for nid, ninfo in enumerate(nodes):
                if ninfo["id"] == itm["targetNodeId"]:
                    trgId = nid
                    break
            else:
                continue
        edges[srcId -
              start_cnt][trgId] = itm.get("properties", {}).get("proba", 1.0)
    in_inds = [it[0] for it in sorted(in_inds, key=lambda it_: it_[1])]
    out_inds = [it[0] for it in sorted(out_inds, key=lambda it_: it_[1])]
    return nodes, edges, in_inds, out_inds, systems

# 拉直多子系统嵌套结构


def flatten_graph(
    struct: List[Dict]
) -> Tuple[List, List, List]:
    """拉直多子系统嵌套结构方法

    args:
        struct: 多个子系统的数据结构
            一个列表 [{'system_id': 1, 'name': 'root', 'parent_id': None, 'data': {...}, 'sysmap': {...}}, {'system_id': 2, 'name': 'RTU渚涚數绾胯矾', 'parent_id': 1, 'data': {...}}, {'system_id': 3, 'name': 'RTU1', 'parent_id': 1, 'data': {...}}, {'system_id': 4, 'name': 'RTU2', 'parent_id': 1, 'data': {...}}]

    return:
        nodes:拉平后的节点列表
            [{'id': 'f20eb5b0-9be8-4905-a8a1-d6f456eaae40', 'type': 'input-node', 'x': 430, 'y': 250, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 0}, {'id': 'e177c67f-193c-434d-8396-a106da74bf5c', 'type': 'input-node', 'x': 430, 'y': 450, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 1}, {'id': 'fcbf4878-c497-48eb-875d-b9e8b552c9e1', 'type': 'output-node', 'x': 1090, 'y': 250, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 2}, {'id': 'a750a1bb-c237-4bc7-83dc-ec078ac08dfd', 'type': 'output-node', 'x': 1090, 'y': 460, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 3}, {'id': '77fa01e3-f89b-4487-9723-3e3815371a60', 'type': 'fault-node', 'x': 600, 'y': 250, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 4}, {'id': '743cb19a-066e-4ac7-9b90-05ecb98aaf32', 'type': 'fault-node', 'x': 750, 'y': 250, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 5}, {'id': '91814791-9384-44b2-b21d-af1a1a66b338', 'type': 'fault-node', 'x': 600, 'y': 460, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 6}, {'id': 'f67d498d-c6e7-4bf7-b9a2-d6b4f166d19d', 'type': 'fault-node', 'x': 750, 'y': 460, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 7}, {'id': 'f2ff1e8a-1995-465d-b3de-9294d0532a22', 'type': 'fault-node', 'x': 920, 'y': 380, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 8}, {'id': 'c46d02b8-464f-4d7b-9fab-fba6c83de55c', 'type': 'fault-node', 'x': 950, 'y': 590, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 9}, {'id': '71033dab-8117-4c3c-9c22-8055971ce97a', 'type': 'input-node', 'x': 460, 'y': 260, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 2, 'NodeId': 0}, {'id': 'dd9e8d0b-f168-4995-99d8-215ff4a2158c', 'type': 'input-node', 'x': 460, 'y': 390, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 2, 'NodeId': 1}, {'id': '7fffaba6-920f-45cb-a034-f75cdff7c08e', 'type': 'input-node', 'x': 450, 'y': 510, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 2, 'NodeId': 2}, {'id': '8752b633-a136-4c85-9f1c-eb9948e34f74', 'type': 'fault-node', 'x': 760, 'y': 260, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 2, 'NodeId': 3}, ...]
        edges:拉平后的连线列表
            [{4: 1.0}, {6: 1.0}, {12: 1.0}, {21: 1.0}, {5: 1.0}, {2: 1.0}, {7: 1.0}, {3: 1.0}, {2: 1.0}, {3: 1.0}, {13: 1.0, 14: 1.0, 15: 1.0, 16: 1.0}, {13: 1.0}, {16: 1.0}, {19: 1.0}, ...]
        system:
            {1: {'info': {...}, 'name': 'RTU渚涚數绾胯矾', 'SubsystemId': 2, 'ParentSubsystemId': 0, 'NodeId': 0, 'nodesId': [...]}, 2: {'info': {...}, 'name': 'RTU1', 'SubsystemId': 3, 'ParentSubsystemId': 0, 'NodeId': 1, 'nodesId': [...]}, 3: {'info': {...}, 'name': 'RTU2', 'SubsystemId': 4, 'ParentSubsystemId': 0, 'NodeId': 2, 'nodesId': [...]}}
    """
    struct[0]["sysmap"] = dict([(itm["system_id"], itmId)
                               for itmId, itm in enumerate(struct)])
    for ele in struct:
        if ele["parent_id"] == None:
            root_id = ele["system_id"]
    nodes, edges, _, _, system = _flatten_graph(struct, root_id)
    return nodes, edges, system


def _render_edge(sysnodes, sysedges):
    sysedges_ = []
    for srcInd, trgInds in enumerate(sysedges):
        if len(trgInds) > 0 and not all(map(lambda trgInd: isinstance(trgInd, Iterable), trgInds)):
            trgInds = [trgInds]
        for srcgrpind, trgInditm in enumerate(trgInds):
            for trgInd in trgInditm:
                if isinstance(trgInd, Iterable):
                    trggrpind, trgInd = trgInd
                else:
                    trggrpind = 0
                srcgrpind = min(srcgrpind, len(
                    [anchor for anchor in sysnodes[srcInd]["anchors"] if anchor["type"] == "right"])-1)

                srcAnc = [anchor for anchor in sysnodes[srcInd]
                          ["anchors"] if anchor["type"] == "right"][srcgrpind]
                trgAnc = [anchor for anchor in sysnodes[trgInd]
                          ["anchors"] if anchor["type"] == "left"][trggrpind]
                sysedges_.append({
                    "id": f"{sysnodes[srcInd]['id']}-{sysnodes[trgInd]['id']}-aslink",
                    "type": EDGE,
                    "sourceNodeId": sysnodes[srcInd]["id"],
                    "targetNodeId": sysnodes[trgInd]["id"],
                    "startPoint": {"x": srcAnc.get("x", -1), "y": srcAnc.get("y", -1)},
                    "endPoint": {"x": trgAnc.get("x", -1), "y": trgAnc.get("y", -1)},
                    "properties": {},
                    "pointsList": [
                        # {"x": srcAnc.get("x", -1), "y": srcAnc.get("y", -1)},
                        # {"x": (srcAnc.get("x", -1)+trgAnc.get("x", -1))/2, "y": srcAnc.get("y", -1)},
                        # {"x": (srcAnc.get("x", -1)+trgAnc.get("x", -1))/2, "y": trgAnc.get("y", -1)},
                        # {"x": trgAnc.get("x", -1), "y": trgAnc.get("y", -1)}
                    ],
                    "sourceAnchorId": srcAnc["id"],
                    "targetAnchorId": trgAnc["id"],
                })
    return [noditm for noditm in sysnodes if noditm], sysedges_


def _flatten_edge(edge):
    if all(map(lambda itm: isinstance(itm, Iterable), edge)):
        edge = [ed for edg in edge for ed in edg]
    return [f"{edg[0]}#{edg[1]}" if isinstance(edg, Iterable) else f"0#{edg}" for edg in edge]


def _check_node(node):
    node["id"] = node.get("id", uuid.uuid1())
    return node


def _getalledge(eid, pure_ind, edges):
    if eid in pure_ind:
        return [pure_ind.index(eid)]
    else:
        edges_ = []
        for eid_ in edges[eid]:
            edges_.extend(_getalledge(eid_, pure_ind, edges))
        return edges_


def _wash_nes(nodes, edges, system):
    pure_ind, nodes = zip(*[[itmId, node] for itmId, node in enumerate(nodes)
                          if node["type"] not in [INPUT_NODE, OUTPUT_NODE]])
    pure_ind = list(pure_ind)
    nodes = list(nodes)
    system = {k: {**itm, "nodesId": [pure_ind.index(ind) for ind in itm.get(
        "nodesId", []) if ind in pure_ind]} for k, itm in system.items()}
    allnodes = [i for i in range(len(pure_ind))]
    if max([len(itm["nodesId"]) for itm in system.values()]) != len(nodes):
        system[len(system)] = {"name": "root", "nodesId": allnodes}
    edges_ = [[] for _ in range(len(pure_ind))]
    for ind, rind in enumerate(pure_ind):
        for eid in edges[rind]:
            edges_[ind].extend(_getalledge(eid, pure_ind, edges))
    return nodes, [[[0, eit] for eit in eitm] for eitm in edges_], system


def reconstruct_graph(nodes, edges, system):
    struct = []
    node2sys = {}
    nodes = [_check_node(node) for node in nodes]
    nodes, edges, system = _wash_nes(nodes, edges, system)
    system = sorted(system.values(), key=lambda itm: len(itm["nodesId"]))
    system_names = [itm["name"] for itm in system]
    sysalllen = len(system)
    nodeLen = len(nodes)
    for sysind, sysinfo in enumerate(system):
        xmin, xmax = float("inf"), -float("inf")
        ymin, ymax = float("inf"), -float("inf")
        sysnodeInd = sorted(set([node2sys.get(ind, ind)
                            for ind in sysinfo["nodesId"]]))
        for sysinfoid in sysnodeInd:
            xmin = min(xmin, nodes[sysinfoid]["x"])
            xmax = max(xmax, nodes[sysinfoid]["x"])
            ymin = min(ymin, nodes[sysinfoid]["y"])
            ymax = max(ymin, nodes[sysinfoid]["y"])
            if nodes[sysinfoid]["type"] == SYS:
                node_name = nodes[sysinfoid]["text"]["value"]
                sysinnerind = system_names.index(node_name)
                struct[sysinnerind]["parent_id"] = sysalllen - sysind
        in_map = {}
        out_map = {}
        sysnodes = [{
            "anchors": [{**anc, "x": anc["x"]-xmin, "y": anc["y"]-ymin} for anc in nodes[ind]["anchors"]],
            "text": {
                "x": nodes[ind]["text"]["x"]-xmin,
                "y": nodes[ind]["text"]["y"]-ymin,
                "value": nodes[ind]["text"]["value"]
            },
            "type": nodes[ind]["type"],
            "id": nodes[ind]["id"],
            "x": nodes[ind]["x"]-xmin,
            "y": nodes[ind]["y"]-ymin,
            "properties": nodes[ind]["properties"]} for ind in sysnodeInd]
        sysedges = [[] for _ in sysnodeInd]
        for srcNind, trgNinds in enumerate(edges):
            if srcNind in sysnodeInd:
                srcInnerInd = sysnodeInd.index(srcNind)
                for trgNind in _flatten_edge(trgNinds):
                    if int(trgNind.split("#")[1]) in sysnodeInd:
                        trgportId, trgNind = map(int, trgNind.split("#"))
                        trgInnerInd = sysnodeInd.index(trgNind)
                        if trgInnerInd not in _flatten_edge(edges[srcInnerInd]):
                            sysedges[srcInnerInd].append(
                                [trgportId, trgInnerInd])
                    elif trgNind not in out_map.keys():
                        out_map[trgNind] = {srcInnerInd}
                    else:
                        out_map[trgNind].add(srcInnerInd)
            else:
                for trgNind in _flatten_edge(trgNinds):
                    if int(trgNind.split("#")[1]) in sysnodeInd:
                        trgportId, trgNind = map(int, trgNind.split("#"))
                        trgInnerInd = sysnodeInd.index(trgNind)
                        if srcNind not in in_map.keys():
                            in_map[srcNind] = {f"{trgportId}#{trgInnerInd}"}
                        else:
                            in_map[srcNind].add(f"{trgportId}#{trgInnerInd}")
        cnt = len(sysnodeInd)
        if nodeLen == len(sysinfo["nodesId"]):
            sysnodes = wash_node_pos(
                sysnodes, width=NODEWIDTH, height=HEIGHT, padding=PADDING, sys=SYS)

            sysnodes_, sysedges_ = _render_edge(sysnodes, sysedges)
            struct.append({
                "data": {
                    "nodes": sysnodes_,
                    "edges": sysedges_,
                },
                "name": sysinfo["name"],
                "system_id": sysalllen-sysind,
                "parent_id": None,
            })
        else:
            out_map_filter = []
            for trgNind, innerNindGrp in out_map.items():
                trgportId, trgNind = map(int, trgNind.split("#"))
                nodeRef = nodes[node2sys.get(trgNind, trgNind)]
                for itmId, itm in enumerate(out_map_filter):
                    if itm["nodeInds"] == innerNindGrp:
                        out_map_filter[itmId]["trgNinds"].append(
                            [trgportId, trgNind])
                else:
                    out_map_filter.append({
                        "name": f"输出{len(out_map_filter)+1}",
                        "config": {
                            "anchors": [{
                                "x": xmax-xmin+round(NODEWIDTH*1.5)+PADDING*round(1.25*NODEWIDTH/HEIGHT)-NODEWIDTH/2,
                                "y": len(out_map_filter)*(PADDING + HEIGHT),
                                "id": nodeRef["id"]+f"_lef{len(out_map_filter)+1}t",
                                "type": "left"
                            }],
                            "text": {
                                "x": xmax-xmin+round(NODEWIDTH*1.5)+PADDING*round(1.25*NODEWIDTH/HEIGHT),
                                "y": len(out_map_filter)*(PADDING + HEIGHT),
                                "value": f"输出{len(out_map_filter)+1}"},
                            "type": "output-node",
                            "id": nodeRef["id"] + f"-asoutput{len(out_map_filter)+1}",
                            "x": xmax-xmin+round(NODEWIDTH*1.5)+PADDING*round(1.25*NODEWIDTH/HEIGHT),
                            "y": len(out_map_filter)*(PADDING + HEIGHT),
                            "properties": {
                                "showType": "edit",
                                "collision": False,
                                "detectable": True,
                                "fuzzible": False,
                                "fuzzy_state": 0,
                                "state": 0,
                                "icon": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAsIDAsIDQwLCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBjb2xvcj0iIzAwMCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTU0MCAtOTg3LjM2KSI+PHBhdGggZD0iTTU2NS40MyAxMDAxLjljNi41NjIgMi4wODkgMTEuMzE2IDguMjMzIDExLjMxNiAxNS40ODggMCA4Ljk3NS03LjI3NSAxNi4yNS0xNi4yNSAxNi4yNXMtMTYuMjUtNy4yNzUtMTYuMjUtMTYuMjVjMC0yLjgwMi43MS01LjQzOCAxLjk1OC03Ljc0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHlsZT0iaXNvbGF0aW9uOmF1dG87bWl4LWJsZW5kLW1vZGU6bm9ybWFsIi8+PGNpcmNsZSBjeD0iNTYwIiBjeT0iMTAwMS40IiByPSIxLjUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjMiIHN0eWxlPSJpc29sYXRpb246YXV0bzttaXgtYmxlbmQtbW9kZTpub3JtYWwiLz48cGF0aCBkPSJNNTYwIDEwMTQuNGMtMS4yMDYgMC0xMS0xMC45OTktMTIuMzU0LTkuOTc1UzU1NyAxMDE2LjE0OCA1NTcgMTAxNy40czEuMzYgMyAzIDMgMy0xLjM2MSAzLTMtMS43OTQtMy0zLTN6IiBmaWxsPSIjZmZmIi8+PC9nPjwvc3ZnPg0K",
                                "typeColor": "#edc3ae",
                                "flevel": 0,
                                "width": 100,
                                "ui": "node-red",
                                "index": len(out_map_filter)+1,
                            },
                        },
                        "trgNinds": [[trgportId, trgNind]],
                        "nodeInds": innerNindGrp,
                        "nodecnt": cnt,
                    })
                    cnt += 1
            in_map_filter = []
            for srcNind, innerNindGrp in in_map.items():
                for itmId, itm in enumerate(in_map_filter):
                    if itm["nodeInds"] == innerNindGrp:
                        in_map_filter[itmId]["srcNinds"].append(srcNind)
                else:
                    nodeRef = nodes[node2sys.get(srcNind, srcNind)]
                    in_map_filter.append({
                        "name": f"输入{len(in_map_filter)+1}",
                        "config": {
                            "anchors": [{
                                "x": -round(NODEWIDTH*1.5)-PADDING*round(1.25*NODEWIDTH/HEIGHT)+NODEWIDTH/2,
                                "y": len(in_map_filter)*(PADDING + HEIGHT),
                                "id": nodeRef["id"]+f"_right{len(out_map_filter)+1}",
                                "type": "right"
                            }],
                            "text": {
                                "x": -round(NODEWIDTH*1.5)-PADDING*round(1.25*NODEWIDTH/HEIGHT),
                                "y": len(in_map_filter)*(PADDING + HEIGHT),
                                "value": f"输入{len(in_map_filter)+1}"},
                            "type": "input-node",
                            "id": nodeRef["id"] + f"-asinput{len(in_map_filter)+1}",
                            "x": -round(NODEWIDTH*1.5)-PADDING*round(1.25*NODEWIDTH/HEIGHT),
                            "y": len(in_map_filter)*(PADDING + HEIGHT),
                            "properties": {
                                "showType": "edit",
                                "collision": False,
                                "detectable": True,
                                "fuzzible": False,
                                "fuzzy_state": 0,
                                "state": 0,
                                "icon": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAsIDAsIDQwLCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBjb2xvcj0iIzAwMCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTU0MCAtOTg3LjM2KSI+PHBhdGggZD0iTTU2NS40MyAxMDAxLjljNi41NjIgMi4wODkgMTEuMzE2IDguMjMzIDExLjMxNiAxNS40ODggMCA4Ljk3NS03LjI3NSAxNi4yNS0xNi4yNSAxNi4yNXMtMTYuMjUtNy4yNzUtMTYuMjUtMTYuMjVjMC0yLjgwMi43MS01LjQzOCAxLjk1OC03Ljc0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHlsZT0iaXNvbGF0aW9uOmF1dG87bWl4LWJsZW5kLW1vZGU6bm9ybWFsIi8+PGNpcmNsZSBjeD0iNTYwIiBjeT0iMTAwMS40IiByPSIxLjUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjMiIHN0eWxlPSJpc29sYXRpb246YXV0bzttaXgtYmxlbmQtbW9kZTpub3JtYWwiLz48cGF0aCBkPSJNNTYwIDEwMTQuNGMtMS4yMDYgMC0xMS0xMC45OTktMTIuMzU0LTkuOTc1UzU1NyAxMDE2LjE0OCA1NTcgMTAxNy40czEuMzYgMyAzIDMgMy0xLjM2MSAzLTMtMS43OTQtMy0zLTN6IiBmaWxsPSIjZmZmIi8+PC9nPjwvc3ZnPg0K",
                                "typeColor": "#edc3ae",
                                "flevel": 0,
                                "width": 100,
                                "ui": "node-red",
                                "index": len(in_map_filter)+1,
                            },
                        },
                        "srcNinds": [srcNind],
                        "nodeInds": [[int(it) for it in trgItem.split("#")] for trgItem in innerNindGrp],
                        "nodecnt": cnt,
                    })
                    cnt += 1
            sysnodes.extend([itm["config"] for itm in out_map_filter])
            sysnodes.extend([itm["config"] for itm in in_map_filter])
            sysedges.extend([[] for _ in range(len(sysnodes)-len(sysedges))])
            for itm in out_map_filter:
                for srcind in itm["nodeInds"]:
                    sysedges[srcind].append([0, itm["nodecnt"]])
            for itm in in_map_filter:   
                sysedges[itm["nodecnt"]] = [
                    sorted(itm["nodeInds"], key=lambda itm: itm[1]+itm[0]/100)]
            sysnodes = wash_node_pos(sysnodes, width=NODEWIDTH, height=HEIGHT, padding=PADDING, sys=SYS)
            sysnodes_, sysedges_ = _render_edge(sysnodes, sysedges)
            struct.append({
                "data": {
                    "nodes": sysnodes_,
                    "edges": sysedges_,
                },
                "name": sysinfo["name"],
                "system_id": sysalllen-sysind,
                "parent_id": None,
            })
            sysNodeRef = sysnodes_[0]
            sysnode = {
                "id": sysNodeRef["id"]+"-assys",
                "type": SYS,
                "x": round((xmax+xmin)/2),
                "y": round((ymax+ymin)/2),
                "properties": {
                    "tableName": "",
                    "SubsystemId": sysalllen-sysind,
                    "fields": {
                        "input": len(in_map_filter),
                        "output": len(out_map_filter),
                    },
                },
                "text": {
                    "x": round((xmax+xmin)/2),
                    "y": round((ymax+ymin)/2) + HEIGHT*(0.5-max(len(in_map_filter), len(out_map_filter))/2),
                    "value": sysinfo["name"],
                },
                "anchors": [
                    {
                        "x": round((xmax+xmin)/2) - WIDTH/2,
                        "y": round((ymax+ymin)/2) + HEIGHT*(1.5-max(len(in_map_filter), len(out_map_filter))/2+itmId),
                        "id": sysNodeRef["id"]+f"-assys-left-{itmId+1}",
                        "edgeAddable": False,
                        "type": "left",
                    } for itmId, itm in enumerate(in_map_filter)] +
                [
                    {
                        "x": round((xmax+xmin)/2) + WIDTH/2,
                        "y": round((ymax+ymin)/2) + HEIGHT*(1.5-max(len(in_map_filter), len(out_map_filter))/2+itmId),
                        "id": sysNodeRef["id"]+f"-assys-right-{itmId+1}",
                        "edgeAddable": False,
                        "type": "right",
                    } for itmId, itm in enumerate(out_map_filter)]

            }
            for nid in sysnodeInd:
                nodes[nid] = {}
                edges[nid] = []
            nodes.append(sysnode)
            edges.append([[]])
            for itmId, itm in enumerate(out_map_filter):
                edges[-1][0].extend(itm["trgNinds"])
            for itmId, itm in enumerate(in_map_filter):
                for srcId in itm["srcNinds"]:
                    edgesSys = [itmId for itmId, itm in enumerate(edges[srcId]) if any(
                        map(lambda it_: it_[1] in sysnodeInd if isinstance(
                            it_, Iterable) else it_ in sysnodeInd, itm)
                    )]
                    edgraw, edges[srcId] = edges[srcId], []
                    for itm_ in edgraw:
                        edges[srcId].append([])
                        for itm in itm_:
                            if not isinstance(itm, Iterable):
                                itm = [0, itm]
                            itmport, itmv = itm
                            if itmv not in sysnodeInd:
                                edges[srcId].extend(
                                    [[] for _ in range(itmport+1-len(edges[srcId]))])
                                edges[srcId][itmport].append(itmv)
                    for srcport in edgesSys:
                        edges[srcId].extend(
                            [[] for _ in range(srcport+1-len(edges[srcId]))])
                        edges[srcId][srcport].append([itmId, len(nodes)-1])
            node2sys.update({ind: len(nodes)-1 for ind in sysinfo["nodesId"]})
    return struct[::-1]


# D矩阵转化
def to_D_mat(
    nodes: List,
    edges: List,
    system: List,
    eps: float = 1e-9,
    raise_collision: bool = True
) -> Tuple[np.ndarray, List, List, List, List, List, List]:
    """将节点和连线 转化为D矩阵

    args:
        nodes: 节点列表
            [{'id': 'f20eb5b0-9be8-4905-a8a1-d6f456eaae40', 'type': 'input-node', 'x': 430, 'y': 250, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 0}, {'id': 'e177c67f-193c-434d-8396-a106da74bf5c', 'type': 'input-node', 'x': 430, 'y': 450, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 1}, {'id': 'fcbf4878-c497-48eb-875d-b9e8b552c9e1', 'type': 'output-node', 'x': 1090, 'y': 250, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 2}, {'id': 'a750a1bb-c237-4bc7-83dc-ec078ac08dfd', 'type': 'output-node', 'x': 1090, 'y': 460, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 3}, {'id': '77fa01e3-f89b-4487-9723-3e3815371a60', 'type': 'fault-node', 'x': 600, 'y': 250, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 4}, {'id': '743cb19a-066e-4ac7-9b90-05ecb98aaf32', 'type': 'fault-node', 'x': 750, 'y': 250, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 5}, {'id': '91814791-9384-44b2-b21d-af1a1a66b338', 'type': 'fault-node', 'x': 600, 'y': 460, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 6}, {'id': 'f67d498d-c6e7-4bf7-b9a2-d6b4f166d19d', 'type': 'fault-node', 'x': 750, 'y': 460, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 7}, {'id': 'f2ff1e8a-1995-465d-b3de-9294d0532a22', 'type': 'fault-node', 'x': 920, 'y': 380, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 8}, {'id': 'c46d02b8-464f-4d7b-9fab-fba6c83de55c', 'type': 'fault-node', 'x': 950, 'y': 590, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 1, 'NodeId': 9}, {'id': '71033dab-8117-4c3c-9c22-8055971ce97a', 'type': 'input-node', 'x': 460, 'y': 260, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 2, 'NodeId': 0}, {'id': 'dd9e8d0b-f168-4995-99d8-215ff4a2158c', 'type': 'input-node', 'x': 460, 'y': 390, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 2, 'NodeId': 1}, {'id': '7fffaba6-920f-45cb-a034-f75cdff7c08e', 'type': 'input-node', 'x': 450, 'y': 510, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 2, 'NodeId': 2}, {'id': '8752b633-a136-4c85-9f1c-eb9948e34f74', 'type': 'fault-node', 'x': 760, 'y': 260, 'properties': {...}, 'text': {...}, 'anchors': [...], 'SubsystemId': 2, 'NodeId': 3}, ...]        
        edges:边列表
            [{4: 1.0}, {6: 1.0}, {12: 1.0}, {21: 1.0}, {5: 1.0}, {2: 1.0}, {7: 1.0}, {3: 1.0}, {2: 1.0}, {3: 1.0}, {13: 1.0, 14: 1.0, 15: 1.0, 16: 1.0}, {13: 1.0}, {16: 1.0}, {19: 1.0}, ...]
        system:
        eps:
        raise_collision: 是否启动成环检测

    return:
        D_mat:D矩阵
            <38x8 sparse matrix of type '<class 'numpy.float32'>' with 57 stored elements in Compressed Sparse Row format>
        testName:测试节点列表
            ({'x': 1280, 'y': 310, 'value': '娴嬭瘯'}, {'x': 1270, 'y': 380, 'value': '娴嬭瘯'}, {'x': 1270, 'y': 460, 'value': '娴嬭瘯'}, {'x': 1280, 'y': 540, 'value': '娴嬭瘯'}, {'x': 1280, 'y': 650, 'value': '娴嬭瘯'}, {'x': 1280, 'y': 730, 'value': '娴嬭瘯'}, {'x': 1310, 'y': 790, 'value': '娴嬭瘯'}, {'x': 1310, 'y': 860, 'value': '娴嬭瘯'})
        faultName:故障节点列表
            ({'x': 430, 'y': 250, 'value': '杈撳叆1'}, {'x': 430, 'y': 450, 'value': '杈撳叆2'}, {'x': 1090, 'y': 250, 'value': '杈撳嚭1'}, {'x': 1090, 'y': 460, 'value': '杈撳嚭2'}, {'x': 610, 'y': 250, 'value': '鏁呴殰'}, {'x': 760, 'y': 250, 'value': '鏁呴殰'}, {'x': 610, 'y': 460, 'value': '鏁呴殰'}, {'x': 760, 'y': 460, 'value': '鏁呴殰'}, {'x': 930, 'y': 380, 'value': '鏁呴殰'}, {'x': 960, 'y': 590, 'value': '鏁呴殰'}, {'x': 460, 'y': 260, 'value': '杈撳叆1'}, {'x': 460, 'y': 390, 'value': '杈撳叆2'}, {'x': 450, 'y': 510, 'value': '杈撳叆3'}, {'x': 770, 'y': 260, 'value': '鏁呴殰'}, ...)
        testLoc:
        faultLoc:
        collision_node: 成环节点列表    
    """
    faultInd, faultName, faultLoc = zip(*[[nodeId, node["text"]["value"], (node["SubsystemId"], node["NodeId"])]
                                        for nodeId, node in enumerate(nodes) if node["type"] in FAULTTYPE])
    testInd, testName, testLoc = zip(*[[nodeId, node["text"]["value"], (node["SubsystemId"], node["NodeId"])]
                                     for nodeId, node in enumerate(nodes) if node["type"] in TESTTYPE])
    try:
        ConnInd, ConnName, ConnLoc = zip(*[[nodeId, node["text"]["value"], (node["SubsystemId"], node["NodeId"])] for nodeId, node in enumerate(nodes) if node["type"] in INPUT_NODE + OUTPUT_NODE])
    except:
        ConnInd, ConnName, ConnLoc = [], [], []
    ConnIds = [faultInd.index(ind) for ind in ConnInd]

    faultMap = [[faultInd.index(srcId), faultInd.index(trgId), edgeP] for srcId, edge in enumerate(
        edges) for trgId, edgeP in edge.items() if trgId in faultInd]
    testMap = [[faultInd.index(srcId), testInd.index(trgId), edgeP] for srcId, edge in enumerate(
        edges) for trgId, edgeP in edge.items() if trgId in testInd]

    if len(testMap) == 0:
        test_mat = coo_matrix(([0], ([0], [0])), shape=(
            len(faultName), len(testName)), dtype="float32")
        test_mat.eliminate_zeros()
    else:
        xid, yid, p = zip(*testMap)
        test_mat = coo_matrix((p, (xid, yid)), shape=(
            len(faultName), len(testName)), dtype="float32")

    inner_forward_map = {}
    if len(faultMap) == 0:
        fault_mat = coo_matrix(([0], ([0], [0])), shape=(
            len(faultName), len(faultName)), dtype="float32")
        fault_mat.eliminate_zeros()
    else:
        for xid_, yid_, p_ in faultMap:
            if yid_ in inner_forward_map.keys():
                inner_forward_map[yid_][xid_] = p_
            else:
                inner_forward_map[yid_] = {xid_: p_}
        collision_node = set()
        for _ in edges:
            lin_cnt = 0
            for yid_, itm in inner_forward_map.items():
                for xid_, p_1 in list(itm.items()):
                    for x_id_new, p_2 in inner_forward_map.get(xid_, {}).items():
                        if yid_ == x_id_new:
                            collision_node.add(yid_)
                            continue
                        pre_p = inner_forward_map[yid_].get(x_id_new, 0)
                        inner_forward_map[yid_][x_id_new] = max(
                            pre_p, p_1*p_2 if p_1*p_2 > eps else 0)
                        lin_cnt += inner_forward_map[yid_][x_id_new] - pre_p
            if lin_cnt < eps:
                break
        if collision_node and raise_collision:
            raise Exception(
                f"[LoopError] It exists {len(collision_node)} Cause-Effect Loop on Fault Node list(collision_node)")
    ckpt_map = {}

    if testMap:
        for xid_, yid_, p_ in testMap:
            if yid_ not in ckpt_map.keys():
                ckpt_map[yid_] = {}
            ckpt_map[yid_][xid_] = max(ckpt_map[yid_].get(xid_, 0), p_)
            for trgid_, p_2 in inner_forward_map.get(xid_, {}).items():
                ckpt_map[yid_][trgid_] = max(ckpt_map[yid_].get(trgid_, 0), p_*p_2)
        xid, yid, p = zip(*[[xid_, yid_, p_] for yid_,
                        itm in ckpt_map.items() for xid_, p_ in itm.items()])
        D_mat = coo_matrix((p, (xid, yid)), shape=(
            len(faultName), len(testName)), dtype="float32").tocsr()
        D_mat.eliminate_zeros()
    else:
        D_mat = coo_matrix(([0], ([0], [0])), shape=(len(faultName), len(testName)), dtype="float32").tocsr()


    sysmap = {
        sysk: {
            "ParentSubsystemId": sysv["ParentSubsystemId"],
            "NodeId": sysv["NodeId"],
            "nodesId": [faultInd.index(nid) for nid in sysv["nodesId"] if nid in faultInd]
        } for sysk, sysv in system.items()
    }
    return D_mat, testName, faultName, ConnIds, testLoc, faultLoc, sysmap, collision_node

# D矩阵推理依赖方法


def _cal_failure(D_mat, p_test, eps=1e-20):
    return np.exp(D_mat.dot(np.log(p_test + eps)[:, None]))


def _divide_sparse_neg_log_1p(vector_, denom_mat, eps=1e-20):
    return denom_mat._with_data(np.log(1-vector_[denom_mat.indices]/denom_mat.data+eps)).tocsr()


def _cal_fuzzy(D_mat, p_fault, eps=1e-20):
    # ε-slack
    # logc_p_fault = np.log(1-p_fault + eps)
    # p_eff = np.exp(D_mat.T.dot(logc_p_fault))
    # D_mat_bool = (D_mat > eps).astype("float32").tocsr()
    # denom_mat = (- D_mat.multiply(logc_p_fault - eps).expm1()).tocsr()
    # D_eff = _divide_sparse(D_mat, denom_mat)
    # return p_fault*np.exp(D_eff.dot(np.log(1-p_eff + eps)))
    c_p_fault = 1 - p_fault + eps
    logc_p_fault = np.log(c_p_fault)
    D_mat_bool = (D_mat > eps).astype("float32")
    DmatT = D_mat.T.tocsr()
    itm = DmatT._with_data(logc_p_fault[DmatT.indices, 0]/DmatT.data).T.tocsr()
    log_p_eff_diff = D_mat.multiply(
        _divide_sparse_neg_log_1p(
            np.exp(D_mat.T.dot(logc_p_fault)).flatten(),
            itm._with_data(np.exp(itm.data)).tocsr(), eps=eps
            )
        )
    log_p_eff = log_p_eff_diff.sum(axis=-1).A
    return p_fault*np.minimum(1, np.exp(log_p_eff))



def _or_failure_fuzzy(p_failure, p_fuzzy):
    return {
        "proba": float(1-np.prod([1-itm for itm in p_failure])**(1/len(p_failure))),
        "fuzzy_proba": float(1-np.prod([1-itm for itm in p_fuzzy])**(1/len(p_fuzzy)))
    }

# D矩阵推理


def detect_by_D_mat(
    p_test: np.ndarray,
    D_mat: np.ndarray,
    sysmap: Dict = {},
    ConnIds=[],
    eps: float = 1e-10,
    n_round: int = 5
) -> Tuple[np.ndarray, np.ndarray, Dict]:
    '''根据测试结果与D矩阵得到诊断结果

    args:
        p_test: 测点测试结果
            array([0., 1., 0., 1., 0., 0., 0., 0.], dtype=float32)
        D_mat: D矩阵 numpy 稀疏矩阵
            <38x8 sparse matrix of type '<class 'numpy.float32'>' with 57 stored elements in Compressed Sparse Row format>
        sysmap: 子系统索引信息
            {1: {'ParentSubsystemId': 0, 'NodeId': 0, 'nodesId': [...]}, 2: {'ParentSubsystemId': 0, 'NodeId': 1, 'nodesId': [...]}, 3: {'ParentSubsystemId': 0, 'NodeId': 2, 'nodesId': [...]}}
        eps: 
        n_round: 保留小数点后位数

    return:
        p_fault: 故障节点
            array([1., 0., 1., 0., 1., 1., 0., 0., 1., 0., 1., 0., 1., 0., 0., 1., 1.,0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.,1., 0., 0., 0.], dtype=float32)
        p_fuzzy: 模糊节点
            array([1., 0., 1., 0., 1., 1., 0., 0., 1., 0., 1., 0., 1., 0., 0., 1., 1.,0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.,1., 0., 0., 0.], dtype=float32)
        sysres: 子系统模糊性
            {1: {'proba': 1.0, 'fuzzy_proba': 1.0}, 2: {'proba': 1.0, 'fuzzy_proba': 1.0}, 3: {'proba': 0.0, 'fuzzy_proba': 0.0}}

    '''
    p_fault = _cal_failure(D_mat, p_test, eps=eps**2)
    DmatT = D_mat.T.tocsr()
    if len(ConnIds) == 0:
        p_fuzzy = _cal_fuzzy(D_mat, p_fault, eps=eps**2)
    else:
        Dpure = DmatT._with_data(np.array([0 if i in ConnIds else v for i, v in zip(
            DmatT.indices, DmatT.data)], dtype="float32")).T.tocsr()
        Dpure.eliminate_zeros()
        p_fuzzy = _cal_fuzzy(Dpure, p_fault, eps=eps**2)
    sysres = {sysk: _or_failure_fuzzy(
        *zip(*[[p_fault[nId], p_fuzzy[nId]] for nId in sysv["nodesId"]])) for sysk, sysv in sysmap.items()}
    return np.round(p_fault.flatten(), n_round), np.round(p_fuzzy.flatten(), n_round), sysres

# D矩阵推理（含渲染）


def detect_with_render(
    p_test: np.ndarray,
    D_mat: np.ndarray,
    struct: List[Dict],
    testLoc: List,
    faultLoc: List,
    sysmap: Dict,
    ConnIds=[],
    eps: float = 1e-9,
    n_round: int = 5
) -> List[Dict]:
    '''根据测试结果与D矩阵得到诊断结果，并改变节点中的属性，便于前端显示测试结果

    args:
        p_test: 测点测试结果
            array([0., 1., 0., 1., 0., 0., 0., 0.], dtype=float32)
        D_mat: D矩阵 numpy 稀疏矩阵
            <38x8 sparse matrix of type '<class 'numpy.float32'>' with 57 stored elements in Compressed Sparse Row format>
        struct: 多个子系统的数据结构
            一个列表 [{'system_id': 1, 'name': 'root', 'parent_id': None, 'data': {...}, 'sysmap': {...}}, {'system_id': 2, 'name': 'RTU渚涚數绾胯矾', 'parent_id': 1, 'data': {...}}, {'system_id': 3, 'name': 'RTU1', 'parent_id': 1, 'data': {...}}, {'system_id': 4, 'name': 'RTU2', 'parent_id': 1, 'data': {...}}]
        testLoc:
        faultLoc:
        sysmap: 子系统索引信息
            {1: {'ParentSubsystemId': 0, 'NodeId': 0, 'nodesId': [...]}, 2: {'ParentSubsystemId': 0, 'NodeId': 1, 'nodesId': [...]}, 3: {'ParentSubsystemId': 0, 'NodeId': 2, 'nodesId': [...]}}
        eps: 
        n_round: 保留小数点后位数

    return:
        struct: 多个子系统的数据结构 已经根据测试结果修改节点的属性
            一个列表 [{'system_id': 1, 'name': 'root', 'parent_id': None, 'data': {...}, 'sysmap': {...}}, {'system_id': 2, 'name': 'RTU渚涚數绾胯矾', 'parent_id': 1, 'data': {...}}, {'system_id': 3, 'name': 'RTU1', 'parent_id': 1, 'data': {...}}, {'system_id': 4, 'name': 'RTU2', 'parent_id': 1, 'data': {...}}]

    '''
    p_fault, p_fuzzy, sysres = detect_by_D_mat(p_test, D_mat, sysmap, ConnIds=ConnIds, eps=eps/10)
    ## 渲染步骤
    struct = copy.deepcopy(struct)
    for t_ind, p_fault_ in enumerate(p_test):
        act_id, node_id = testLoc[t_ind]
        struct[act_id]["data"]["nodes"][node_id]["properties"]["showType"] = "analyse"
        struct[act_id]["data"]["nodes"][node_id]["properties"]["proba"] = float(p_fault_)
        struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzy_proba"] = 0
    f_ind = 0
    for p_failure_, p_fuzzy_ in zip(p_fault, p_fuzzy):
        act_id, node_id = faultLoc[f_ind]
        struct[act_id]["data"]["nodes"][node_id]["properties"]["showType"] = "analyse"
        if struct[act_id]["data"]["nodes"][node_id]["properties"].get("detectable") is False:
            struct[act_id]["data"]["nodes"][node_id]["properties"]["proba"] = float(p_failure_)
            struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzy_proba"] = float(p_fuzzy_)
            f_ind += 1
        else: ## 补充不可测试测点的逻辑
            struct[act_id]["data"]["nodes"][node_id]["properties"]["proba"] = 0
            struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzy_proba"] = 1
    for key, sysr_ in sysres.items():
        parent_sys_id = sysmap[key]["ParentSubsystemId"]
        node_id = sysmap[key]["NodeId"]
        struct[parent_sys_id]["data"]["nodes"][node_id]["properties"]["showType"] = "analyse"
        struct[parent_sys_id]["data"]["nodes"][node_id]["properties"]["proba"] = float(p_failure_)
        struct[parent_sys_id]["data"]["nodes"][node_id]["properties"]["fuzzy_proba"] = float(p_fuzzy_)
        struct[key]["data"]["properties"] = {**struct[key]["data"].get("properties", {}), **sysr_}
    return struct

def qualitat_detect_by_D_mat(p_test, D_mat):
    norm_test = np.where(p_test<0.5)[0]
    D_mat_ = D_mat[:, norm_test]
    D_mat_.eliminate_zeros()
    norm_fault = set(np.where(np.diff(D_mat_.indptr)>0.5)[0])
    f_f_fault = set(range(D_mat.shape[0])) - norm_fault
    if f_f_fault:
        D_mat_ = D_mat[:, list(set(range(len(p_test)))-set(norm_test))].tocsc()[list(f_f_fault), :].tocsr()
        D_mat_.eliminate_zeros()
        fuzzy_fault = set(np.where(D_mat_.indptr>1.5)[0])
    else:
        fuzzy_fault = f_f_fault
    return zip(*[[float(i not in norm_fault), float(i in fuzzy_fault)] for i in range(D_mat.shape[0])])


# 解算依赖导出为Json

def to_json(
    D_mat: np.array,
    struct: List[Dict],
    testLoc: List,
    faultLoc: List,
    sysmap: Dict,
    testName: List,
    faultName: List,
    collision_node: List = [],
    ConnIds: List = []
) -> str:
    return json.dumps({
        "struct": struct,
        "testLoc": testLoc,
        "faultLoc": faultLoc,
        "sysmap": sysmap,
        "testName": testName,
        "faultName": faultName,
        "collision_node": [int(ind) for ind in collision_node],
        "ConnIds": [int(ind) for ind in ConnIds],
        "D_mat": [
            D_mat.indptr.tolist(),
            D_mat.indices.tolist(),
            D_mat.data.tolist()
        ]
    })

# 解算依赖从Json导入


def from_json(
    configJson: str
) -> Tuple[np.array, List[Dict], List, List, Dict, List, List, List, List]:
    config = json.loads(configJson)
    struct = config["struct"]
    testLoc = config["testLoc"]
    faultLoc = config["faultLoc"]
    sysmap = config["sysmap"]
    testName = config["testName"]
    faultName = config["faultName"]
    D_indptr, D_indices, D_values = config["D_mat"]
    D_mat = csr_matrix((D_values, D_indices, D_indptr), shape=(
        len(faultName), len(testName)), dtype="float32")
    collision_node = config["collision_node"]
    ConnIds = config["ConnIds"]
    return D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName, collision_node, ConnIds


def _get_detect_isolat_ratio(checkLen, fuzzyLen, faultLen, testLen):
    return [
        checkLen/faultLen,
        fuzzyLen/checkLen,
        1 - max(0, min(1, (checkLen-fuzzyLen)/testLen))
    ]

# 流图性能评测


def check_graph(convertStruct, eps=1e-9):
    D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName, collision_node, ConnIds = from_json(convertStruct)
    fnodes = [struct[act_id]["data"]["nodes"][node_id] for act_id, node_id in faultLoc]
    validNodes = [nodeId for nodeId, node in enumerate(fnodes) if node["type"] not in [INPUT_NODE, OUTPUT_NODE]]
    unCheckIdList_ = np.where(np.asarray(D_mat.sum(axis=1)).flatten() < 0.5)[0]
    DmatT = D_mat.T.tocsr()
    Dpure = DmatT._with_data(np.array([0 if i in ConnIds else v for i, v in zip(DmatT.indices, DmatT.data)], dtype="float32")).T.tocsr()
    Dpure.eliminate_zeros()
    fuzzyList = np.where(_cal_fuzzy(Dpure, np.ones((len(faultName),1), dtype="float32"), eps=eps**2).flatten() >= 0.5 - eps)[0]

    collision_node = {f"{faultLoc[f_ind][0]}#{faultLoc[f_ind][1]}" for f_ind in collision_node}
    unCheckIdList_in = {f"{faultLoc[f_ind][0]}#{faultLoc[f_ind][1]}" for f_ind in unCheckIdList_}
    fuzzyList_in = {f"{faultLoc[f_ind][0]}#{faultLoc[f_ind][1]}" for f_ind in fuzzyList}
    
    for act_id, _ in enumerate(struct):
        for node_id, _ in enumerate(struct[act_id]["data"]["nodes"]):
            struct[act_id]["data"]["nodes"][node_id]["properties"]["collision"] = False
            struct[act_id]["data"]["nodes"][node_id]["properties"]["detectable"] = True
            struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzible"] = True
            struct[act_id]["data"]["nodes"][node_id]["properties"]["showType"] = "check"
            if f"{act_id}#{node_id}" in collision_node:
                struct[act_id]["data"]["nodes"][node_id]["properties"]["collision"] = True
            if f"{act_id}#{node_id}" in unCheckIdList_in:
                struct[act_id]["data"]["nodes"][node_id]["properties"]["detectable"] = False
            if f"{act_id}#{node_id}" in fuzzyList_in:
                struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzible"] = False
    for subsysId, subsysInfo in sysmap.items():
        act_id = subsysInfo["ParentSubsystemId"]
        node_id = subsysInfo["NodeId"]
        if isinstance(act_id, int):
            struct[act_id]["data"]["nodes"][node_id]["properties"]["detectable"] = all(map(lambda itm: itm in unCheckIdList_in, subsysInfo["nodesId"]))
            struct[act_id]["data"]["nodes"][node_id]["properties"]["collision"] = any(map(lambda itm: itm in collision_node, subsysInfo["nodesId"]))
            struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzible"] = any(map(lambda itm: itm in fuzzyList_in, subsysInfo["nodesId"]))
    fLen = len(faultName)
    checkLen = fLen - len([nodeInd for nodeInd in unCheckIdList_ if nodeInd in validNodes])
    fuzzyLen = len([nodeInd for nodeInd in fuzzyList if nodeInd in validNodes])
    return {
        "data": struct,
        "D_mat": D_mat.todense().tolist(),
        "col_names": testName,
        "row_names": faultName,
        "detect_isolat_ratio": _get_detect_isolat_ratio(checkLen, fuzzyLen, fLen, len(testName)),
        }

def convert_fmeca(
    df: pd.DataFrame
):
    nodes, edges, system = read_fmeca(
        df,
        check_invalid_col=CHECK_INVALID_COL,
        component_col=COMPONENT_COL,
        faultcause_col=FAULTCAUSE_COL,
        faultmode_col=FAULTMODE_COL,
        detection_col=DETECTION_COL,
        self_effect_col=SELF_EFFECT_COL,
        trans_effect_col=TRANS_EFFECT_COL,
        final_effect_col=FINAL_EFFECT_COL,
        ckptnode=CKPT, resnode=RES)
    nodes = render_node_pos(nodes, edges, width=NODEWIDTH,
                            height=HEIGHT, padding=PADDING)
    return reconstruct_graph(nodes, edges, system)


def optimize_struct(struct, p_min=0.25):
    nodes, edges, _ = flatten_graph(struct)
    faultInd, faultName, faultLoc = zip(*[[nodeId, node["text"]["value"], (node["SubsystemId"], node["NodeId"])] for nodeId, node in enumerate(nodes) if node["type"] in FAULTTYPE])
    testInd, testName, testLoc = zip(*[[nodeId, node["text"]["value"], (node["SubsystemId"], node["NodeId"])] for nodeId, node in enumerate(nodes) if node["type"] in TESTTYPE])
    try:
        ConnInd, ConnName, ConnLoc = zip(*[[nodeId, node["text"]["value"], (node["SubsystemId"], node["NodeId"])] for nodeId, node in enumerate(nodes) if node["type"] in INPUT_NODE + OUTPUT_NODE])
    except:
        ConnInd, ConnName, ConnLoc = [], [], []
    ConnIds = [faultInd.index(ind) for ind in ConnInd]

    faultMap = [[faultInd.index(srcId), faultInd.index(trgId)] for srcId, edge in enumerate(edges) for trgId, edgeP in edge.items() if trgId in faultInd if edgeP > p_min]
    testMap = [[faultInd.index(srcId), testInd.index(trgId)] for srcId, edge in enumerate(edges) for trgId, edgeP in edge.items() if trgId in testInd if edgeP > p_min]

    inner_forward_map = {}
    for xid_, yid_ in faultMap:
        if yid_ in inner_forward_map.keys():
            inner_forward_map[yid_].add(xid_)
        else:
            inner_forward_map[yid_] = {xid_}
    for _ in edges:
        lin_cnt = 0
        for yid_, itm in inner_forward_map.items():
            for xid_ in set(itm):
                for x_id_new in inner_forward_map.get(xid_, set()):
                    if yid_ == x_id_new:
                        continue
                    if x_id_new in inner_forward_map[yid_]:
                        lin_cnt += 1
                    else:
                        inner_forward_map[yid_].add(x_id_new)
        if lin_cnt < 0.5:
            break
    ckpt_map = {ind: set() for ind in range(len(testInd))}
    for xid_, yid_ in testMap:
        ckpt_map[yid_] |= {xid_}
        ckpt_map[yid_] |= inner_forward_map.get(xid_, set())
    ckptinds = sorted(ckpt_map.keys(), key=lambda itm: len(ckpt_map[itm]))
    for ckptsortid, ckptind in enumerate(ckptinds):
        cons = -1; inner_forward_map_ = set(ckpt_map[ckptind])
        for ckptinnerid in ckptinds[:ckptsortid]:
            if len(ckpt_map[ckptind]) < len(ckpt_map[ckptinnerid]):
                break
            elif len(ckpt_map[ckptinnerid] - ckpt_map[ckptind]) > 0:
                continue
            elif len(ckpt_map[ckptinnerid] - ckpt_map[ckptind]) == 0 and \
                 len(ckpt_map[ckptind] - ckpt_map[ckptinnerid]) == 0:
                cons = ckptinnerid
                break
            inner_forward_map_ -= ckpt_map[ckptinnerid]
        if cons != -1:
            act_id, node_id = testLoc[cons]
            struct[act_id]["data"]["nodes"][node_id]["properties"]["redundancy"] = 0.1
            act_id_, node_id_ = testLoc[ckptind]
            struct[act_id_]["data"]["nodes"][node_id_]["properties"]["redundancy"] = 0.5
        elif len(inner_forward_map_) == 0:
            act_id, node_id = testLoc[ckptind]
            struct[act_id]["data"]["nodes"][node_id]["properties"]["redundancy"] = 1
        else:
            act_id, node_id = testLoc[ckptind]
            struct[act_id]["data"]["nodes"][node_id]["properties"]["redundancy"] = 0
    return struct

if __name__ == "__main__":

    with open(os.path.join(DIR_PATH, "dataRTU.json"), "r+") as f:
        struct = json.load(f)["SystemData"]
    nodes, edges, system = flatten_graph(struct)
    structInverse = reconstruct_graph(nodes, edges, system)
    D_mat, testName, faultName, ConnIds, testLoc, faultLoc, sysmap, collision_node = to_D_mat(
        nodes, edges, system)
    p_test = (np.random.uniform(0, 1, len(testName)) > 0.5).astype("float32")
    p_fault, p_fuzzy, sysres = detect_by_D_mat(p_test, D_mat, sysmap, ConnIds)
    print("P_FAULT:", p_fault.tolist(), "\tP_FUZZY:", p_fuzzy.tolist())
    structNew = detect_with_render(
        p_test, D_mat, struct, testLoc, faultLoc, sysmap, ConnIds, eps=1e-10, n_round=5)
    structJson = to_json(D_mat, struct, testLoc, faultLoc,
                         sysmap, testName, faultName, collision_node, ConnIds)
    checkRes = check_graph(structJson)
    print(checkRes["detect_isolat_ratio"])
    D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName, collision_node, ConnIds = from_json(
        structJson)
    import pandas as pd
    struct2 = convert_fmeca(pd.read_excel("FMECA范例.xlsx"))
    struct = optimize_struct(struct, p_min=0.25)
