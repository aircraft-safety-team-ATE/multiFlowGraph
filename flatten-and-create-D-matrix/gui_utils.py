from typing import Dict
import uuid

def _get_tree(topId, edges, decouvertIds=set(), root=-1):
    if topId and any([eid not in decouvertIds for eid in topId]):
        decouvertIds |= {eId for tId in topId  for eId in edges[tId]}
        branches = [_get_tree(edges[tId], edges, decouvertIds=decouvertIds, root=root) for tId in topId if tId not in decouvertIds]
        bnum = sum([bran["num"] for bran in branches])
        return {"nid": root, "num": bnum, "braches": branches}
    else:
        return {"nid": root, "num": 1, "braches": []}

def _render_tree(tree, nodes, x=0, y=0, width=100, height=24, padding=10):
    if len(tree["branches"]) == 0:
        nodes[tree["nid"]]["x"] = x
        nodes[tree["nid"]]["y"] = y
        nodes[tree["nid"]]["type"] = nodes[tree["nid"]]["type"]
        nodes[tree["nid"]]["properties"] = {
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
                "y": y,
                "id": nodes[tree["nid"]]+"_left"
                }
            ]
    else:
        branch_all = [bran["num"] for bran in tree["branches"]]
        area_height = sum(branch_all)*(height+padding)
        y_dev = area_height/2
        nodes[tree["nid"]]["x"] = x
        nodes[tree["nid"]]["y"] = y + y_dev
        nodes[tree["nid"]]["type"] = nodes[tree["nid"]]["type"]
        nodes[tree["nid"]]["properties"] = {
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
            "ui": "node-red"
            }
        nodes[tree["nid"]]["text"] = {
            "x": x + 10,
            "y": y + y_dev,
            "value": nodes[tree["nid"]]["text"]["value"] if isinstance(nodes[tree["nid"]]["text"], Dict) else nodes[tree["nid"]]["text"]
            }
        nodes[tree["nid"]]["anchors"] = [
            {
                "x": x-width/2,
                "y": y + y_dev,
                "id": nodes[tree["nid"]]+"_left"
                },
            {
                "x": x+width/2,
                "y": y + y_dev,
                "id": nodes[tree["nid"]]+"_right"
                }
            ]
        for brannum, braninfo, branoffset in zip(branch_all, tree["branches"], np.cumsum([0]+branch_all)[:-1]):
            nodes = _render_tree(braninfo, nodes, x=x+(branoffset+brannum/2)*(height+padding), y=y+(branoffset+brannum/2)*(height+padding), width=width, height=height, padding=padding)
    return nodes

def render_node_pos(nodes, edges, width=100, height=24, padding=10):
    for nodid in range(len(nodes)):
        nodes[nodid]["id"] = node.get("id", uuid.uuid1())
    redges = [[srcid for srcid, edg in enumerate(edges) if trgid in edg] for trgid in range(len(node))]
    topId = [eid for eid, edg in enumerate(redges) if len(edg)==0]
    struct = _get_tree(topId, edges, decouvertIds=set(topId), root=-1)
    nodes = _render_tree(tree, nodes, x=0, y=0, width=width, height=height, padding=padding)
    return nodes
    
    
    
    
