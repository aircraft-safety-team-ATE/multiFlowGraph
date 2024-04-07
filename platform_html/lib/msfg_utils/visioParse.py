import re
import aspose.diagram
from aspose.diagram import *
# pip install aspose-diagram-python

from zipfile import ZipFile
from io import BytesIO

def _getType(node, ckptnode="test-node", resnode="fault-node"):
    try:
        return node.props[0].value.val.lower()
    except Exception as e:
        name = node.name
        try:
            if node.line.line_pattern.value == 0:
                return "outer-conn-node"
        except Exception as e:
            pass
        if "矩形" in name or "rect" in name.lower():
            return resnode
        elif "圆形" in name or "circle" in name.lower() or "ellip" in name.lower():
            return ckptnode
        elif "六边形" in name or "hexa" in name.lower():
            return "conn-node"
        elif "连接线" in name or "connect" in name.lower():
            return "edge"
        else:
            return name.lower()
        
def _convert_structure(nodes, edges, sysname):
    return {
            "nodes": [{k: v for k,v in node.items() if k not in ["self", "width", "x"]} 
                      for node in nodes if node["type"] != "conn-node"],
            "edges": edges,
            "inputs": [node["id"] for node in sorted(
                [node for node in nodes if node["type"] == "conn-node" if node["id"] in edges.keys()],
                key=lambda itm: int(re.findall(r"[0-9]+", itm["text"])[0]))],
            "outputs": [node["id"] for node in sorted(
                [node for node in nodes if node["type"] == "conn-node" if node["id"] not in edges.keys()],
                key=lambda itm: int(re.findall(r"[0-9]+", itm["text"])[0]))],
            "sysname": sysname,
            "child_sysname": [node["text"] for node in nodes if node["type"] == "subsys-node"]
        }

def parse_each_visio(page, pagid=0, ckptnode="test-node", resnode="fault-node"):
    """从visio对应的path/ByteIO中读取单幅流图"""

    ## Visio信息读取
    nodes = []; outer_conn_ids = []; edges = {}
    for node in page.shapes:
        type_ =  _getType(node, ckptnode=ckptnode, resnode=resnode)
        if type_ == "edge":
            edge = node.get_connector_rule()
            if f"node-{pagid+1}-{edge.start_shape_id}" not in edges.keys():
                edges[f"node-{pagid+1}-{edge.start_shape_id}"] = []
            edges[f"node-{pagid+1}-{edge.start_shape_id}"].append(f"node-{pagid+1}-{edge.end_shape_id}")
            continue
        else:
            nodes.append({
                "text": node.get_display_text().replace("\n", "").replace("\r",""),
                "type": type_,
                "id": f"node-{pagid+1}-{node.id}",
                "self": node,
                "width": node.x_form.width.value,
                "x": node.x_form.pin_x.value
            })

    ## 子系统元件的整理
    discovered_outer_conn_ids = []
    nodes = sorted(nodes, key=lambda itm: itm["width"], reverse=True)
    outer_conn_ids = [nodeid for nodeid, node in enumerate(nodes) if node["type"] == "outer-conn-node"]
    for node in reversed(nodes):
        if node["type"] == resnode:
            inside_id = [cid for cid in outer_conn_ids if cid not in discovered_outer_conn_ids \
                          and node["self"].is_intersect(nodes[cid]["self"])]
            discovered_outer_conn_ids.extend(inside_id)
            if len(inside_id):
                #############################################################################
                left_ref = node["x"] + min([nodes[cid]["width"] for cid in inside_id])/2.5 ##
                #############################################################################
                node["type"] = "subsys-node"
                node["inputnames"] = [nodes[cid]["id"] for cid in inside_id if nodes[cid]["x"] < left_ref]
                node["outputnames"] = [nodes[cid]["id"] for cid in inside_id if nodes[cid]["x"] >= left_ref]
    nodes = [node for nodeid, node in enumerate(nodes) if nodeid not in outer_conn_ids]

    ## 子系统层级的整理
    submap = {}
    for node_id, node in enumerate(nodes):
        for node_r_id, node_ in enumerate(reversed(nodes[:node_id])):
            if node_["self"].is_contain(node["self"]):
                if not node_id - node_r_id - 1 in submap.keys():
                    submap[node_id - node_r_id - 1] = []
                submap[node_id - node_r_id - 1].append(node_id)
    if len(submap.keys()) == 0:
        return [_convert_structure(nodes, edges, "root")]
    else:
        return [_convert_structure(
            [nodes[node_id] for node_id in v],
            {**{
                nodes[node_id]["id"]: edges[nodes[node_id]["id"]]
                for node_id in v if nodes[node_id]["id"] in edges.keys()},
             **{
                 cid: edges[cid]
                 for node_id in v if nodes[node_id]["type"]=="subsys-node"
                 for cid in nodes[node_id]["outputnames"] if cid in edges.keys()}},
            nodes[k]["text"]) for k,v in submap.items()]

def parse_visio(path, ckptnode="test-node", resnode="fault-node"):
    """从visio对应的path/ByteIO中读取单幅流图"""
    with Diagram(path) as diagram:
        result = []
        for pagid, page in enumerate(diagram.pages):
            result.extend(parse_each_visio(page, pagid=pagid,
                                           ckptnode=ckptnode, resnode=resnode))
    result = {itm["sysname"]: itm for itm in result}
    # print(result)
    return result

def _reconn_edges(eid, conn_map):
    if eid in conn_map.keys():
        res = []
        for eid_ in conn_map[eid]:
            res.extend(_reconn_edges(eid_, conn_map))
        return res
    else:
        return [eid]

def _convert_edge(nodes, edges):
    node_map = [node["id"] for node in nodes]
    edges_conn = {k: v for k,v in edges.items() if k not in node_map}
    edges_ = {}
    for k,v in edges.items():
        if k in node_map:
            edges_[k] = []
            for v_ in edges[k]:
                edges_[k].extend(_reconn_edges(v_, edges_conn))
    return [sorted([node_map.index(n_) for n_ in edges_.get(nid, []) if n_ in node_map]) for nid in node_map]

def _tranlate_nodeid(nodes, submap):
    return {**submap, "nodesId": sorted([nodes.index(nodeId) for nodeId in set(submap["nodesId"]) if nodeId in nodes])}

def parse_visio_arrange(path, ckptnode="test-node", resnode="fault-node"):
    result = parse_visio(path, ckptnode=ckptnode, resnode=resnode)
    reverse_map = {compnb: compna for compna, v in result.items() for compnb in v["child_sysname"]}
    subsys = {}
    while len(reverse_map.keys()) != 0:
        for leaf_n in list(set(reverse_map.keys()) - set(reverse_map.values())):
            father_n = reverse_map[leaf_n]
            leaf_in_father_id = filter(
                lambda nodeid: result[father_n]["nodes"][nodeid]["text"] == leaf_n,
                range(len(result[father_n]["nodes"]))
                ).__next__()
            # print(result[father_n]["nodes"][leaf_in_father_id]["text"])
            leaf_inputs, leaf_outputs = result[leaf_n]["inputs"], result[leaf_n]["outputs"]
            leaf_in_father_inputs, leaf_in_father_outputs = result[father_n]["nodes"][leaf_in_father_id]["inputnames"], \
                                                            result[father_n]["nodes"][leaf_in_father_id]["outputnames"]
            in_map = {k: v for v,k in zip(leaf_inputs, leaf_in_father_inputs)}
            out_map = {k: v for v,k in zip(leaf_outputs, leaf_in_father_outputs)}
            result[father_n]["nodes"].extend(result[leaf_n]["nodes"])
            result[father_n]["edges"].update(result[leaf_n]["edges"])
            for c_leaf, c_father in zip(leaf_inputs, leaf_in_father_inputs):
                if c_father not in result[father_n]["edges"].keys():
                    result[father_n]["edges"][c_father] = []
                result[father_n]["edges"][c_father].append(c_leaf)
            for c_leaf, c_father in zip(leaf_outputs, leaf_in_father_outputs):
                if c_leaf not in result[father_n]["edges"].keys():
                    result[father_n]["edges"][c_leaf] = []
                result[father_n]["edges"][c_leaf].append(c_father)
            
            result[father_n]["nodes"] = result[father_n]["nodes"][:leaf_in_father_id] + result[father_n]["nodes"][leaf_in_father_id+1:]
            if father_n not in subsys.keys():
                subsys[father_n] = {"name": father_n, "nodesId": [node["id"] for node in result[father_n]["nodes"]]}
            if leaf_n in subsys.keys():
                subsys[father_n]["nodesId"].extend(subsys[leaf_n]["nodesId"])
            else:
                subsys[leaf_n] = {"name": leaf_n, "nodesId": [node["id"] for node in result[leaf_n]["nodes"]]}
                subsys[father_n]["nodesId"].extend(subsys[leaf_n]["nodesId"])

            del reverse_map[leaf_n]
            del result[leaf_n]

    sysres = list(result.keys())

    if len(sysres) > 1:
        print(f"[Warn] It exists more than one root system candidates. ({sysres})")
            
    k = sysres[0]
    
    return result[k]["nodes"], _convert_edge(result[k]["nodes"], result[k]["edges"]), \
           {k_: _tranlate_nodeid([itm["id"] for itm in result[k]["nodes"]],v) for k_,v in subsys.items()}

if __name__ == "__main__":
    nodes, edges, systems = parse_visio_arrange(r"pic.vsdx")
    print({n["text"]: [nodes[n_]["text"] for n_ in edges[nid]] for nid, n in enumerate(nodes)})
    print(systems)
