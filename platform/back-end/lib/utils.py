# 前端基本配置
import uuid
import copy
import json
from .fmecaReader import read_fmeca
from .gui_utils import render_node_pos
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
EDGE = "custom-edge"
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
PADDING = 10


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
        edges[id_map[itm["sourceAnchorId"]]-start_cnt][id_map[itm["targetAnchorId"]]
                                                       ] = itm.get("properties", {}).get("proba", 1.0)
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
                        {"x": srcAnc.get("x", -1), "y": srcAnc.get("y", -1)},
                        {"x": (srcAnc.get("x", -1)+trgAnc.get("x", -1)) /
                         2, "y": srcAnc.get("y", -1)},
                        {"x": (srcAnc.get("x", -1)+trgAnc.get("x", -1)) /
                         2, "y": trgAnc.get("y", -1)},
                        {"x": trgAnc.get("x", -1), "y": trgAnc.get("y", -1)}
                    ],
                    "sourceAnchorId": srcAnc["id"],
                    "targetAnchorId": trgAnc["id"],
                })
    return [noditm for noditm in sysnodes if noditm], sysedges_


def _flatten_edge(edge):
    if all(map(lambda itm: isinstance(itm, Iterable), edge)):
        edge = [ed for edg in edge for ed in edg]
    return [edg[0] if isinstance(edg, Iterable) else edg for edg in edge]


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
    return nodes, edges_, system


def reconstruct_graph(nodes, edges, system):
    struct = []
    node2sys = {}
    sysalllen = len(system)
    nodes = [_check_node(node) for node in nodes]
    nodes, edges, system = _wash_nes(nodes, edges, system)
    nodeLen = len(nodes)
    for sysind, sysinfo in enumerate(sorted(system.values(), key=lambda itm: len(itm["nodesId"]))):
        for sysinfoid in [node2sys[ind] for ind in sysinfo["nodesId"] if ind in node2sys.keys()]:
            nodes[sysinfoid]["parent_id"] = sysalllen - sysind
        sysnodeInd = sorted(set([node2sys.get(ind, ind)
                            for ind in sysinfo["nodesId"]]))
        node2sys.update({ind: len(nodes) for ind in sysinfo["nodesId"]})
        in_map = {}
        out_map = {}
        sysnodes = [nodes[ind] for ind in sysnodeInd]
        sysedges = [[] for _ in sysnodeInd]
        for srcNind, trgNinds in enumerate(edges):
            if srcNind in sysnodeInd:
                srcInnerInd = sysnodeInd.index(srcNind)
                for trgNind in _flatten_edge(trgNinds):
                    if trgNind in sysnodeInd:
                        trgInnerInd = sysnodeInd.index(trgNind)
                        if trgInnerInd not in _flatten_edge(edges[srcInnerInd]):
                            sysedges[srcInnerInd].append(trgInnerInd)
                    elif trgNind not in out_map.keys():
                        out_map[trgNind] = {srcInnerInd}
                    else:
                        out_map[trgNind].add(srcInnerInd)
            else:
                for trgNind in _flatten_edge(trgNinds):
                    if trgNind in sysnodeInd:
                        trgInnerInd = sysnodeInd.index(trgNind)
                        if srcNind not in in_map.keys():
                            in_map[srcNind] = {trgInnerInd}
                        else:
                            in_map[srcNind].add(trgInnerInd)
        cnt = len(sysnodeInd)
        if nodeLen == len(sysinfo["nodesId"]):
            sysnodes_, sysedges_ = _render_edge(sysnodes, sysedges)
            struct.append({
                "data": {
                    "nodes": sysnodes_,
                    "edges": sysedges_,
                },
                "system_id": sysalllen-sysind,
                "parent_id": None,
            })
        else:
            out_map_filter = []
            for trgNind, innerNindGrp in out_map.items():
                for itmId, itm in enumerate(out_map_filter):
                    if itm["nodeInds"] == innerNindGrp:
                        out_map_filter[itmId]["trgNinds"].append(srcNind)
                else:
                    for ind in sorted(innerNindGrp):
                        if nodes[ind]:
                            nodeRef = nodes[ind]
                            break
                    else:
                        raise Exception(
                            "[SubsysError] No vaild Node in subsystem")
                    out_map_filter.append({
                        "name": f"输出{len(out_map_filter)+1}",
                        "config": {
                            "anchors": [anchor for anchor in nodeRef["anchors"] if anchor["type"] == "left"],
                            "text": {**nodeRef.get("text", {}), "value": f"输出{len(out_map_filter)+1}"},
                            "type": "output-node",
                            "id": nodeRef["id"] + "-asoutput",
                            "x": nodeRef.get("x", -1),
                            "y": nodeRef.get("y", -1),
                            "properties": nodeRef.get("properties"),
                        },
                        "trgNinds": [trgNind],
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
                    nodeRef = None
                    for ind in sorted(innerNindGrp):
                        if nodes[ind]:
                            nodeRef = nodes[ind]
                            break
                    else:
                        raise Exception(
                            "[SubsysError] No vaild Node in subsystem")
                    in_map_filter.append({
                        "name": f"输入{len(in_map_filter)+1}",
                        "config": {
                            "anchors": [anchor for anchor in nodeRef["anchors"] if anchor["type"] == "right"],
                            "text": {**nodeRef.get("text", {}), "value": f"输入{len(out_map_filter)+1}"},
                            "type": "input-node",
                            "id": nodeRef["id"] + "-asinput",
                            "x": nodeRef.get("x", -1),
                            "y": nodeRef.get("y", -1),
                            "properties": nodeRef.get("properties"),
                        },
                        "srcNinds": [srcNind],
                        "nodeInds": innerNindGrp,
                        "nodecnt": cnt,
                    })
                    cnt += 1
            sysnodes.extend([itm["config"] for itm in out_map_filter])
            sysnodes.extend([itm["config"] for itm in in_map_filter])
            sysedges.extend([[] for _ in range(len(sysnodes)-len(sysedges))])
            for itm in out_map_filter:
                for srcind in itm["nodeInds"]:
                    sysedges[srcind].append(itm["nodecnt"])
            for itm in in_map_filter:
                sysedges[itm["nodecnt"]] = sorted(itm["nodeInds"])
            sysnodes_, sysedges_ = _render_edge(sysnodes, sysedges)
            struct.append({
                "data": {
                    "nodes": sysnodes_,
                    "edges": sysedges_,
                },
                "system_id": sysalllen-sysind,
                "parent_id": None,
            })
            sysNodeRef = sysnodes_[0]
            sysnode = {
                "id": sysNodeRef["id"]+"-assys",
                "type": SYS,
                "x": sysNodeRef.get("x", -1),
                "y": sysNodeRef.get("y", -1),
                "properties": {
                    "tableName": "",
                    "SubsystemId": sysalllen-sysind,
                    "fields": {
                        "input": len(in_map_filter),
                        "output": len(out_map_filter),
                    },
                },
                "text": {
                    "x": sysNodeRef.get("x", -1),
                    "y": sysNodeRef.get("x", -1),
                    "value": sysinfo["name"],
                },
                "anchors": [
                    {
                        "x": sysNodeRef.get("x", -1) - WIDTH/2,
                        "y": sysNodeRef.get("y", -1) + WIDTH*(1.5+itmId),
                        "id": sysNodeRef["id"]+f"-assys-left-{itmId+1}",
                        "edgeAddable": False,
                        "type": "left",
                    } for itmId, itm in enumerate(in_map_filter)] +
                [
                    {
                        "x": sysNodeRef.get("x", -1) + WIDTH/2,
                        "y": sysNodeRef.get("y", -1) + WIDTH*(1.5+itmId),
                        "id": sysNodeRef["id"]+f"-assys-right-{itmId+1}",
                        "edgeAddable": False,
                        "type": "right",
                    } for itmId, itm in enumerate(out_map_filter)]

            }
            for nid in sysnodeInd:
                nodes[nid] = {}
                edges[nid] = []
            nodes.append(sysnode)
            edges.append([])
            for itmId, itm in enumerate(out_map_filter):
                edges[-1].append(itm["trgNinds"])
            for itmId, itm in enumerate(in_map_filter):
                for srcId in itm["srcNinds"]:
                    edges[srcId] = [itm for itm in edges[srcId] if itm in sysnodeInd or (
                        isinstance(itm, Iterable) and itm[1] in sysnodeInd)]
                    edges[srcId].append([itmId, len(nodes)-1])
    return struct


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

    if len(faultMap) == 0:
        fault_mat = coo_matrix(([0], ([0], [0])), shape=(
            len(faultName), len(faultName)), dtype="float32")
        fault_mat.eliminate_zeros()
    else:
        inner_forward_map = {}
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
        xid, yid, p = zip(*[[xid_, yid_, p_] for yid_,
                          itm in inner_forward_map.items() for xid_, p_ in itm.items()])
        fault_mat = coo_matrix((p, (xid, yid)), shape=(
            len(faultName), len(faultName)), dtype="float32")
    D_mat = fault_mat.dot(test_mat).tocsr()
    D_mat.eliminate_zeros()

    sysmap = {
        sysk: {
            "ParentSubsystemId": sysv["ParentSubsystemId"],
            "NodeId": sysv["NodeId"],
            "nodesId": [faultInd.index(nid) for nid in sysv["nodesId"] if nid in faultInd]
        } for sysk, sysv in system.items()
    }
    collision_node = []
    return D_mat, testName, faultName, testLoc, faultLoc, sysmap, collision_node

# D矩阵推理依赖方法


def _cal_failure(D_mat, p_test, eps=1e-20):
    return 1 - np.exp(D_mat.dot(np.log(1 - p_test + eps)[:, None]))


def _divide_sparse(vector_, denom_mat):
    return denom_mat._with_data(vector_[denom_mat.indices]/denom_mat.data).tocsr()


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
    # itm = D_mat.multiply(logc_p_fault)
    DmatT = D_mat.T.tocsr()
    itm = DmatT._with_data(logc_p_fault[DmatT.indices, 0]/DmatT.data).T.tocsr()
    log_p_eff_diff = D_mat.multiply(
        (
            -_divide_sparse(
                np.exp(D_mat.T.dot(logc_p_fault)).flatten(),
                itm._with_data(np.exp(itm.data)).tocsr()
            )
        ).log1p()
    )
    log_p_eff = log_p_eff_diff.sum(axis=-1).A
    return p_fault*np.exp(log_p_eff)


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
    p_fuzzy = _cal_fuzzy(D_mat, p_fault, eps=eps**2)
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
    p_fault, p_fuzzy, sysres = detect_by_D_mat(
        p_test, D_mat, sysmap, eps=eps/10)
    # 渲染步骤
    struct = copy.deepcopy(struct)
    for t_ind, p_fault_ in enumerate(p_test):
        act_id, node_id = testLoc[t_ind]
        struct[act_id]["data"]["nodes"][node_id]["properties"]["proba"] = float(
            p_fault_)
        struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzy_proba"] = 0
    f_ind = 0
    for p_failure_, p_fuzzy_ in zip(p_fault, p_fuzzy):
        act_id, node_id = faultLoc[f_ind]
        struct[act_id]["data"]["nodes"][node_id]["properties"]["proba"] = float(
            p_failure_)
        struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzy_proba"] = float(
            p_fuzzy_)
        f_ind += 1
    for key, sysr_ in sysres.items():
        parent_sys_id = sysmap[key]["ParentSubsystemId"]
        node_id = sysmap[key]["NodeId"]
        struct[parent_sys_id]["data"]["nodes"][node_id]["properties"]["proba"] = float(
            p_failure_)
        struct[parent_sys_id]["data"]["nodes"][node_id]["properties"]["fuzzy_proba"] = float(
            p_fuzzy_)
        struct[key]["data"]["properties"] = {
            **struct[key]["data"].get("properties", {}), **sysr_}
    return struct

# 解算依赖导出为Json


def to_json(
    D_mat: np.array,
    struct: List[Dict],
    testLoc: List,
    faultLoc: List,
    sysmap: Dict,
    testName: List,
    faultName: List,
    collision_node: List = []
) -> str:
    return json.dumps({
        "struct": struct,
        "testLoc": testLoc,
        "faultLoc": faultLoc,
        "sysmap": sysmap,
        "testName": testName,
        "faultName": faultName,
        "collision_node": list(collision_node),
        "D_mat": [
            D_mat.indptr.tolist(),
            D_mat.indices.tolist(),
            D_mat.data.tolist()
        ]
    })

# 解算依赖从Json导入


def from_json(
    configJson: str
) -> Tuple[np.array, List[Dict], List, List, Dict, List, List, List]:
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
    return D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName, collision_node


def _get_detect_isolat_ratio(checkLen, fuzzyLen, faultLen, testLen):
    return [
        checkLen/faultLen,
        fuzzyLen/checkLen,
        1 - max(0, min(1, (checkLen-fuzzyLen)/testLen))
    ]

# 流图性能评测
def check_graph(convertStruct, eps=1e-9):
    D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName, collision_node = from_json(
        convertStruct)
    fnodes = [struct[act_id]["data"]["nodes"][node_id]
              for act_id, node_id in faultLoc]
    validNodes = [nodeId for nodeId, node in enumerate(
        fnodes) if node["type"] not in [INPUT_NODE, OUTPUT_NODE]]
    unCheckIdList_ = np.where(np.asarray(D_mat.sum(axis=1)) < eps)[0]
    fuzzyList = np.where(_cal_fuzzy(D_mat, np.ones(
        (len(faultName), 1), dtype="float32")).flatten() > 1 - eps)[0]
    print(fuzzyList)
    for f_ind in collision_node:
        act_id, node_id = faultLoc[f_ind]
        struct[act_id]["data"]["nodes"][node_id]["properties"]["collision"] = True
    for f_ind in unCheckIdList_:
        act_id, node_id = faultLoc[f_ind]
        struct[act_id]["data"]["nodes"][node_id]["properties"]["detectable"] = False
    for f_ind in fuzzyList:
        act_id, node_id = faultLoc[f_ind]
        struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzible"] = False
    for subsysId, subsysInfo in sysmap.items():
        act_id = subsysInfo["ParentSubsystemId"]
        node_id = subsysInfo["NodeId"]
        if isinstance(act_id, int):
            struct[act_id]["data"]["nodes"][node_id]["properties"]["detectable"] = all(
                map(lambda itm: itm in unCheckIdList_, subsysInfo["nodesId"]))
            struct[act_id]["data"]["nodes"][node_id]["properties"]["collision"] = any(
                map(lambda itm: itm in collision_node, subsysInfo["nodesId"]))
            struct[act_id]["data"]["nodes"][node_id]["properties"]["fuzzible"] = any(
                map(lambda itm: itm in fuzzyList, subsysInfo["nodesId"]))
    fLen = len(unCheckIdList_)
    checkLen = fLen - \
        len([nodeInd for nodeInd in unCheckIdList_ if nodeInd in validNodes])
    fuzzyLen = len([nodeInd for nodeInd in fuzzyList if nodeInd in validNodes])
    # print("checkLen", checkLen)
    # print("fuzzyLen", fuzzyLen)
    fLen = 10
    checkLen = 4
    fuzzyLen = 3
    print("D_mat2", D_mat.todense())

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


if __name__ == "__main__":

    with open(os.path.join(DIR_PATH, "dataRTU.json"), "r+") as f:
        struct = json.load(f)["SystemData"]
    nodes, edges, system = flatten_graph(struct)
    structInverse = reconstruct_graph(nodes, edges, system)
    D_mat, testName, faultName, testLoc, faultLoc, sysmap, collision_node = to_D_mat(
        nodes, edges, system)
    p_test = (np.random.uniform(0, 1, len(testName)) > 0.5).astype("float32")
    p_fault, p_fuzzy, sysres = detect_by_D_mat(p_test, D_mat, sysmap)
    print("P_FAULT:", p_fault.tolist(), "\tP_FUZZY:", p_fuzzy.tolist())
    structNew = detect_with_render(
        p_test, D_mat, struct, testLoc, faultLoc, sysmap, eps=1e-10, n_round=5)
    structJson = to_json(D_mat, struct, testLoc, faultLoc,
                         sysmap, testName, faultName, collision_node)
    checkRes = check_graph(structJson)
    D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName, collision_node = from_json(
        structJson)
