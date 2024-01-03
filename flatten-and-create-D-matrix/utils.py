import copy
import json
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix, csc_matrix
SYS = "subsystem-node"
INPUT_NODE = "input-node"
OUTPUT_NODE = "output-node"
RES = "fault-node"  # 故障节点
SW = "switch-node"  # 开关节点
CKPT = "test-node"  # 测点
TESTTYPE = [CKPT]
FAULTTYPE = [INPUT_NODE, OUTPUT_NODE, RES, SW]


def _flatten_graph(struct, act_uid=1, nodes_cnt=0):
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
                "SubsystemId": itm["properties"]["SubsystemId"],  # 该分系统本身的编号
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


def flatten_graph(struct):
    struct[0]["sysmap"] = dict([(itm["system_id"], itmId)
                               for itmId, itm in enumerate(struct)])
    for ele in struct:
        if ele["parent_id"] == None:
            root_id = ele["system_id"]
    nodes, edges, _, _, system = _flatten_graph(struct, root_id)
    return nodes, edges, system

# D矩阵转化


def to_D_mat(nodes, edges, system, eps=1e-9):
    faultInd, faultName, faultLoc = zip(*[[nodeId, node["text"], (node["SubsystemId"], node["NodeId"])]
                                        for nodeId, node in enumerate(nodes) if node["type"] in FAULTTYPE])
    testInd, testName, testLoc = zip(*[[nodeId, node["text"], (node["SubsystemId"], node["NodeId"])]
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
        for _ in edges:
            lin_cnt = 0
            for yid_, itm in inner_forward_map.items():
                for xid_, p_1 in list(itm.items()):
                    for x_id_new, p_2 in inner_forward_map.get(xid_, {}).items():
                        if yid_ == x_id_new:
                            raise Exception(
                                f"[LoopError] It exists a Cause-Effect Loop on Fault Node [{faultName[yid_]}]")
                        pre_p = inner_forward_map[yid_].get(x_id_new, 0)
                        inner_forward_map[yid_][x_id_new] = max(
                            pre_p, p_1*p_2 if p_1*p_2 > eps else 0)
                        lin_cnt += inner_forward_map[yid_][x_id_new] - pre_p
            if lin_cnt < eps:
                break
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
    return D_mat, testName, faultName, testLoc, faultLoc, sysmap

# D矩阵推理依赖方法


def _cal_failure(D_mat, p_test, eps=1e-18):
    return 1 - np.exp(D_mat.dot(np.log(1 - p_test + eps)[:, None]))


def _divide_sparse(matrix, denom_mat):
    return matrix._binopt(denom_mat, '_eldiv_').tocsr()


def _cal_fuzzy(D_mat, p_fault, eps=1e-20):
    # ε-slack
    logc_p_fault = np.log(1-p_fault + eps)
    p_eff = np.exp(D_mat.T.dot(logc_p_fault))
    D_mat_bool = (D_mat > eps).astype("float32").tocsr()
    denom_mat = (- D_mat.multiply(logc_p_fault - eps).expm1()).tocsr()
    D_eff = _divide_sparse(D_mat, denom_mat)
    return p_fault*np.exp(D_eff.dot(np.log(1-p_eff + eps)))


def _or_failure_fuzzy(p_failure, p_fuzzy):
    return {
        "proba": float(1-np.prod([1-itm for itm in p_failure])**(1/len(p_failure))),
        "fuzzy_proba": float(1-np.prod([1-itm for itm in p_fuzzy])**(1/len(p_fuzzy)))
    }

# D矩阵推理


def detect_by_D_mat(p_test, D_mat, sysmap={}, eps=1e-10, n_round=5):
    p_fault = _cal_failure(D_mat, p_test, eps=eps)
    p_fuzzy = _cal_fuzzy(D_mat, p_fault, eps=eps)
    sysres = {sysk: _or_failure_fuzzy(
        *zip(*[[p_fault[nId], p_fuzzy[nId]] for nId in sysv["nodesId"]])) for sysk, sysv in sysmap.items()}
    return np.round(p_fault.flatten(), n_round), np.round(p_fuzzy.flatten(), n_round), sysres

# D矩阵推理（含渲染）


def detect_with_render(p_test, D_mat, struct, testLoc, faultLoc, sysmap, eps=1e-10, n_round=5):
    p_fault, p_fuzzy, sysres = detect_by_D_mat(p_test, D_mat, sysmap)
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


def to_json(D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName):
    return json.dumps({
        "struct": struct,
        "testLoc": testLoc,
        "faultLoc": faultLoc,
        "sysmap": sysmap,
        "testName": testName,
        "faultName": faultName,
        "D_mat": [
            D_mat.indptr.tolist(),
            D_mat.indices.tolist(),
            D_mat.data.tolist()
        ]
    })

# 解算依赖从Json导入


def from_json(configJson):
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
    return D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName


if __name__ == "__main__":
    with open(r"import-multiGraph-from-file\data.json", "r+") as f:
        struct = json.load(f)["SystemData"]
    nodes, edges, system = flatten_graph(struct)
    D_mat, testName, faultName, testLoc, faultLoc, sysmap = to_D_mat(
        nodes, edges, system)
    p_test = (np.random.uniform(0, 1, len(testName)) > 0.5).astype("float32")
    p_fault, p_fuzzy, sysres = detect_by_D_mat(p_test, D_mat, sysmap)
    structNew = detect_with_render(
        p_test, D_mat, struct, testLoc, faultLoc, sysmap, eps=1e-10, n_round=5)
    structJson = to_json(D_mat, struct, testLoc, faultLoc,
                         sysmap, testName, faultName)
    D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName = from_json(
        structJson)
