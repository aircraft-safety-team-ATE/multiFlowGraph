SYS = "subsystem-node"
INPUT_NODE = "input-node"
OUTPUT_NODE = "output-node"
RES = "fault-node" ## 故障节点
SW = "switch-node" ## 开关节点
CKPT = "test-node" ## 测点
TESTTYPE = [CKPT]
FAULTTYPE = [INPUT_NODE, OUTPUT_NODE, RES, SW]

from scipy.sparse import coo_matrix, csr_matrix, csc_matrix
import numpy as np

def _flatten_graph(struct, act_uid=1, nodes_cnt=0):
    nodes = []; edges = []
    id_map = {}; systems = {}
    in_inds = []; out_inds = []
    start_cnt = nodes_cnt
    act_id = struct[0]["sysmap"][act_uid]
    for itmId, itm in enumerate(struct[act_id]["data"]["nodes"]):
        if itm["type"] == SYS:
            nodes_, edges_, in_inds_, out_inds_, systems_ = _flatten_graph(struct, act_uid=itm["properties"]["SubsystemId"], nodes_cnt=nodes_cnt)
            nodes.extend(nodes_)
            edges.extend(edges_)
            for true_ind, anchor_id in zip(in_inds_, [lin_["id"] for lin_ in sorted(itm["anchors"], key=lambda it_: it_["y"]) if lin_["type"]=="left"]):
                id_map[anchor_id] = true_ind
            for true_ind, anchor_id in zip(out_inds_, [lin_["id"] for lin_ in sorted(itm["anchors"], key=lambda it_: it_["y"]) if lin_["type"]=="right"]):
                id_map[anchor_id] = true_ind
            systems.update(systems_)
            systems[struct[0]["sysmap"][itm["properties"]["SubsystemId"]]] = {
                    "info": itm,
                    "SubsystemId": itm["properties"]["SubsystemId"], ## 该分系统本身的编号
                    "ParentSubsystemId": act_id, ## 需要同步更新上级分系统编号
                    "NodeId": itmId, ## 需要同步更新上级分系统中该分系统的队列编号
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
                "SubsystemId": act_id, ## 该节点所属的分系统编号
                "NodeId": itmId ## 需要系统中该节点的队列编号
                })
            for anchor_itm in itm["anchors"]:
                id_map[anchor_itm["id"]] = nodes_cnt
            edges.append([])
            nodes_cnt += 1
    for itm in struct[act_id]["data"]["edges"]:
        edges[id_map[itm["sourceAnchorId"]]-start_cnt].append(id_map[itm["targetAnchorId"]])
    in_inds = [it[0] for it in sorted(in_inds, key=lambda it_: it_[1])]
    out_inds = [it[0] for it in sorted(out_inds, key=lambda it_: it_[1])]
    return nodes, edges, in_inds, out_inds, systems

def flatten_graph(struct):
    struct[0]["sysmap"] = dict([(itm["system_id"],itmId) for itmId, itm in enumerate(struct)])
    for ele in struct:
        if ele["parent_id"]==None:
            root_id = ele["system_id"]
    nodes, edges, _, _, system = _flatten_graph(struct,root_id)
    return nodes, edges, system

def to_D_mat(nodes, edges, system):
    faultInd, faultName, faultLoc = zip(*[[nodeId, node["text"], (node["SubsystemId"], node["NodeId"])] for nodeId, node in enumerate(nodes) if node["type"] in FAULTTYPE])
    testInd, testName, testLoc = zip(*[[nodeId, node["text"], (node["SubsystemId"], node["NodeId"])] for nodeId, node in enumerate(nodes) if node["type"] in TESTTYPE])

    ##############
    faultMap = [[faultInd.index(trgId), faultInd.index(srcId)] for srcId, edge in enumerate(edges) for trgId in edge if trgId in faultInd]
    testMap = [[testInd.index(trgId), faultInd.index(srcId)] for srcId, edge in enumerate(edges) for trgId in edge if trgId in testInd]
    ##############
    
    fuzzy_fnode = [0 for _ in faultName]
    for i in map(lambda itm: itm[0], faultMap):
        fuzzy_fnode[i] += 1
    del_fnode = [fid for fid, fcnt in enumerate(fuzzy_fnode) if fcnt>1]
    faultMap_pure = [itm for itm in faultMap if itm[0] not in del_fnode]
    
    fuzzy_tnode = [0 for _ in testName]
    for i in map(lambda itm: itm[0], testMap):
        fuzzy_tnode[i] += 1
    del_tnode = [tid for tid, tcnt in enumerate(fuzzy_tnode) if tcnt>1]
    testMap_pure = [itm for itm in testMap if itm[0] not in del_tnode]

    if len(faultMap) == 0:
        fault_mat = coo_matrix(([0], ([0],[0])),shape=(len(faultName), len(faultName)), dtype=np.int)
        fault_mat.eliminate_zeros()
    else:
        fault_mat = coo_matrix(([1]*len(faultMap), zip(*faultMap)),shape=(len(faultName), len(faultName)), dtype=np.int)

    if len(testMap) == 0:
        test_mat = coo_matrix(([0], ([0],[0])),shape=(len(testName), len(faultName)), dtype=np.int)
        test_mat.eliminate_zeros()
    else:
        test_mat = coo_matrix(([1]*len(testMap), zip(*testMap)),shape=(len(testName), len(faultName)), dtype=np.int)
        
    if len(faultMap_pure) == 0:
        fault_mat_pure = coo_matrix(([0], ([0],[0])),shape=(len(faultName), len(faultName)), dtype=np.int)
        fault_mat_pure.eliminate_zeros()
    else:
        fault_mat_pure = coo_matrix(([1]*len(faultMap_pure), zip(*faultMap_pure)),shape=(len(faultName), len(faultName)), dtype=np.int)
    
    if len(testMap_pure) == 0:
        test_mat_pure = coo_matrix(([0], ([0],[0])),shape=(len(testName), len(faultName)), dtype=np.int)
        test_mat_pure.eliminate_zeros()
    else:
        test_mat_pure = coo_matrix(([1]*len(testMap_pure), zip(*testMap_pure)),shape=(len(testName), len(faultName)), dtype=np.int)            

    m = len(faultName)
    E = coo_matrix(([1]*m, (range(m), range(m))), shape=(m,m), dtype=np.int)
    
    for _ in edges:
        fault_mat_pre = fault_mat
        fault_mat = (fault_mat + fault_mat.dot(fault_mat)) > 0.75
        if np.max(np.abs(fault_mat_pre-fault_mat)) < 0.25:
            break

    for _ in edges:
        fault_mat_pure_pre = fault_mat_pure
        fault_mat_pure = (fault_mat_pure + fault_mat_pure.dot(fault_mat_pure)) > 0.75
        if np.max(np.abs(fault_mat_pure_pre-fault_mat_pure)) < 0.25:
            break
    
    D_mat = (test_mat.dot(E+fault_mat) > 0.75).astype(np.int)
    D_mat.eliminate_zeros()
    
    D_mat_pure = (test_mat_pure.dot(E +fault_mat_pure) > 0.75).astype(np.int)
    D_mat_pure.eliminate_zeros()
    
    unfuzzy_node = test_mat_pure.tocsr().indices.tolist()

    fuzzy_mat = 0.8*(D_mat.T.dot(D_mat)> 0.75).astype(np.int).tocsr() \
                + 0.2*(((D_mat.T.dot(D_mat)> 0.75).astype(np.int) - fault_mat - fault_mat.T - E).tocsr()> 0.75).astype(np.float)
    fuzzy_mat = fuzzy_mat.tolil()
    fuzzy_mat[unfuzzy_node, :] = 0
    fuzzy_mat = fuzzy_mat.tocsr()
    fuzzy_mat.eliminate_zeros()
    
    F_mat = ((fault_mat- E)> 0.75).astype(np.int)
    F_mat.eliminate_zeros()
    
    return F_mat, D_mat.T, fuzzy_mat.tocsr(), testName, faultName, testLoc, faultLoc

if __name__ == "__main__":
    import json
    import time
    start_time = time.time()
    with open(r"platform\dataRTU_extreme_extreme.json", "r+") as f:
        struct = json.load(f)["SystemData"]
    load_time = time.time()
    nodes, edges, system = flatten_graph(struct)
    flatten_time = time.time()
    F_mat, D_mat, fuzzy_mat, testName, faultName, testLoc, faultLoc = to_D_mat(nodes, edges, system)
    creatD_time = time.time()

    print("load data From Json in",load_time - start_time,"seconds")
    print("node numbers:",len(nodes))
    print("system numbers:",len(system))
    print("flatter graph in",flatten_time - load_time,"seconds")
    print("creatD in",creatD_time-flatten_time,"seconds")
