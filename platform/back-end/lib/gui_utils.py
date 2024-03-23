from typing import Dict
import uuid
import numpy as np

TYPE_COLORS = {
        "test-node": "#eea2a4",
        "fault-node": "#edc3ae",
        "switch-node": "#96c24e",
        "input-node": "#85C1E9",
        "output-node": "#85C1E9",
        "subsystem-node": "#85C1E9",
    }

def _get_tree(topId, edges, decouvertIds=set(), root=-1):
    if topId and any([eid not in decouvertIds for eid in topId]):
        #decouvertIds_ = decouvertIds #| set(topId)
        branches = [_get_tree(
            edges[tId],
            edges,
            decouvertIds= decouvertIds | {tId},
            root=tId
            ) for t_i, tId in enumerate(topId) if tId not in decouvertIds]
        bnum = sum([bran["num"] for bran in branches])
        return {"nid": root, "num": bnum, "branches": branches}
    else:
        return {"nid": root, "num": 1, "branches": []}

def _render_tree(tree, nodes, x=0, y=0, width=100, height=24, padding=10):
    if len(tree["branches"]) == 0:
        nodes[tree["nid"]]["x"] = x
        nodes[tree["nid"]]["y"] = y
        #nodes[tree["nid"]]["type"] = nodes[tree["nid"]]["type"]
        nodes[tree["nid"]]["properties"] = {
            "showType": "edit",
            "collision": False,
            "detectable": True,
            "fuzzible": False,
            "fuzzy_state": 0,
            "state": 0,
            "icon": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAsIDAsIDQwLCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBjb2xvcj0iIzAwMCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTU0MCAtOTg3LjM2KSI+PHBhdGggZD0iTTU2NS40MyAxMDAxLjljNi41NjIgMi4wODkgMTEuMzE2IDguMjMzIDExLjMxNiAxNS40ODggMCA4Ljk3NS03LjI3NSAxNi4yNS0xNi4yNSAxNi4yNXMtMTYuMjUtNy4yNzUtMTYuMjUtMTYuMjVjMC0yLjgwMi43MS01LjQzOCAxLjk1OC03Ljc0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHlsZT0iaXNvbGF0aW9uOmF1dG87bWl4LWJsZW5kLW1vZGU6bm9ybWFsIi8+PGNpcmNsZSBjeD0iNTYwIiBjeT0iMTAwMS40IiByPSIxLjUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjMiIHN0eWxlPSJpc29sYXRpb246YXV0bzttaXgtYmxlbmQtbW9kZTpub3JtYWwiLz48cGF0aCBkPSJNNTYwIDEwMTQuNGMtMS4yMDYgMC0xMS0xMC45OTktMTIuMzU0LTkuOTc1UzU1NyAxMDE2LjE0OCA1NTcgMTAxNy40czEuMzYgMyAzIDMgMy0xLjM2MSAzLTMtMS43OTQtMy0zLTN6IiBmaWxsPSIjZmZmIi8+PC9nPjwvc3ZnPg0K",
            "typeColor": TYPE_COLORS.get(nodes[tree["nid"]]["type"], "#85C1E9"),
            "flevel": 0,
            "width": 100,
            "ui": "node-red"
            }
        nodes[tree["nid"]]["text"] = {
            "x": x + 10,
            "y": y,
            "value": nodes[tree["nid"]]["text"]["value"] if isinstance(nodes[tree["nid"]]["text"], Dict) else nodes[tree["nid"]]["text"]
            }
        nodes[tree["nid"]]["anchors"] = [
            {
                "x": x-width/2,
                "y": y,# - height/2,
                "id": nodes[tree["nid"]]["id"]+"_left",
                "type": "left"
                },
            {
                "x": x+width/2,
                "y": y,# - height/2,
                "id": nodes[tree["nid"]]["id"]+"_right",
                "type": "right"
                }
            ]
    else:
        branch_all = [bran["num"] for bran in tree["branches"]]
        area_height = sum(branch_all)*(height+padding)
        y_dev = area_height/2
        nodes[tree["nid"]]["x"] = x
        nodes[tree["nid"]]["y"] = y + y_dev
        #nodes[tree["nid"]]["type"] = nodes[tree["nid"]]["type"]
        nodes[tree["nid"]]["properties"] = {
            "showType": "edit",
            "collision": False,
            "detectable": True,
            "fuzzible": False,
            "fuzzy_state": 0,
            "state": 0,
            "icon": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAsIDAsIDQwLCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBjb2xvcj0iIzAwMCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTU0MCAtOTg3LjM2KSI+PHBhdGggZD0iTTU2NS40MyAxMDAxLjljNi41NjIgMi4wODkgMTEuMzE2IDguMjMzIDExLjMxNiAxNS40ODggMCA4Ljk3NS03LjI3NSAxNi4yNS0xNi4yNSAxNi4yNXMtMTYuMjUtNy4yNzUtMTYuMjUtMTYuMjVjMC0yLjgwMi43MS01LjQzOCAxLjk1OC03Ljc0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHlsZT0iaXNvbGF0aW9uOmF1dG87bWl4LWJsZW5kLW1vZGU6bm9ybWFsIi8+PGNpcmNsZSBjeD0iNTYwIiBjeT0iMTAwMS40IiByPSIxLjUiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjMiIHN0eWxlPSJpc29sYXRpb246YXV0bzttaXgtYmxlbmQtbW9kZTpub3JtYWwiLz48cGF0aCBkPSJNNTYwIDEwMTQuNGMtMS4yMDYgMC0xMS0xMC45OTktMTIuMzU0LTkuOTc1UzU1NyAxMDE2LjE0OCA1NTcgMTAxNy40czEuMzYgMyAzIDMgMy0xLjM2MSAzLTMtMS43OTQtMy0zLTN6IiBmaWxsPSIjZmZmIi8+PC9nPjwvc3ZnPg0K",
            "typeColor": TYPE_COLORS.get(nodes[tree["nid"]]["type"], "#85C1E9"),
            "flevel": 0,
            "width": 100,
            "ui": "node-red"
            }
        nodes[tree["nid"]]["text"] = {
            "x": x + 10,
            "y": y + y_dev,# + height/2,
            "value": nodes[tree["nid"]]["text"]["value"] if isinstance(nodes[tree["nid"]]["text"], Dict) else nodes[tree["nid"]]["text"]
            }
        nodes[tree["nid"]]["anchors"] = [
            {
                "x": x-width/2,
                "y": y + y_dev,# - height/2,
                "id": nodes[tree["nid"]]["id"]+"_left",
                "type": "left"
                },
            {
                "x": x+width/2,
                "y": y + y_dev,# - height/2,
                "id": nodes[tree["nid"]]["id"]+"_right",
                "type": "right"
                }
            ]
        for brannum, braninfo, branoffset in zip(branch_all, tree["branches"], np.cumsum([0]+branch_all)[:-1]):
            nodes = _render_tree(braninfo, nodes, x=x+round(width*1.5)+padding*round(1.25*width/height),#+(branoffset+brannum/2)*(height+padding),
                                 y=y+(branoffset+brannum/2)*(height+padding), width=width, height=height, padding=padding)
    return nodes

def render_node_pos(nodes, edges, width=100, height=24, padding=10):
    inner_forward_map = {}
    collision_node = set()
    for xid_, yids in enumerate(edges):
        inner_forward_map[xid_] = set(yids)
    for _ in edges:
        lin_cnt = 0
        for xid_, itm in inner_forward_map.items():
            for yid_ in itm:
                for y_id_new in inner_forward_map.get(xid_, set()):
                    if xid_ == y_id_new:
                        collision_node.add(xid_)
                        continue
                    inner_forward_map[xid_].add(y_id_new)
    edges_ = [[] if i in collision_node else edg for i, edg in enumerate(edges)]
    for nodid in range(len(nodes)):
        nodes[nodid]["id"] = nodes[nodid].get("id", str(uuid.uuid1()))
    redges = [[srcid for srcid, edg in enumerate(edges_) if trgid in edg] for trgid in range(len(nodes))]
    topId = [eid for eid, edg in enumerate(redges) if len(edg)==0]
    struct = _get_tree(topId, edges_, decouvertIds=set(), root=-1)
    nodes = _render_tree(struct, nodes, x=0, y=0, width=width, height=height, padding=padding)
    return nodes
    
def wash_node_pos(nodes, width=100, height=24, padding=10, sys="subsystem-node", nround=0):
    nodes_ = [
        [node["x"], node["y"] + anchId*(height + padding)]
        for node in nodes for anchId in range(max(
            node.get("properties", {}).get("fields", {}).get("inputs", 1),
            node.get("properties", {}).get("fields", {}).get("outputs", 1)
            ) + (1 if node["type"]==sys else 0))]
    x,y = [np.sort(itm) for itm in zip(*nodes_)]
    xmarks = [x[0]-width/100]
    for xitm in np.sort(x[1:]):
        if xitm - xmarks[-1] > padding*round(1.25*width/height)/2:
            xmarks.append(xitm-width/100)
    xmarks = np.array(xmarks, dtype="float32")
    print(x)
    print(xmarks)
    ymarks = [y[0]-height/100]
    for yitm in np.sort(y[1:]):
        if yitm - ymarks[-1] > padding/2:
            ymarks.append(yitm-height/100)
    ymarks = np.array(ymarks, dtype="float32")
    print(y)
    print(ymarks)
    for nId, node in enumerate(nodes):
        dx_ = round(float(np.where(nodes[nId]["x"]>xmarks)[0][-1]) * (width + padding*round(1.25*width/height)) - nodes[nId]["x"])
        dy_ = round(float(np.where(nodes[nId]["y"]>ymarks)[0][-1]) * (height + padding) - nodes[nId]["y"])
        nodes[nId]["x"] += dx_
        nodes[nId]["y"] += dy_
        nodes[nId]["text"]["x"] += dx_
        nodes[nId]["text"]["y"] += dy_
        for anchId, _ in enumerate(nodes[nId]["anchors"]):
            nodes[nId]["anchors"][anchId]["x"] += dx_
            nodes[nId]["anchors"][anchId]["y"] += dy_
    return nodes
