import warnings
warnings.filterwarnings("ignore")

import json
from scipy.sparse import coo_matrix, csr_matrix, csc_matrix
import numpy as np
import pandas as pd

try:
    from .fmecaReader import read_fmeca
except:
    from fmecaReader import read_fmeca

CKPT = "test-node" ## 测点
ALGO = "algo-node" ## 算法节点
RES = "fault-node" ## 故障节点
UNRES = "inter-fault-node" ## 中间节点
SW = "switch-node" ## 开关节点
SUBSYS = "sub-system" ## 子系统
TESTTYPE = [ALGO]
FAULTTYPE = [RES, UNRES, SW]

def _fuse_scores(scores, levels):
    """
    [scores]: [0.9, 0.6, 0.5] => Fault Probability of each Fault
    [Levels]: [0,   1,   1  ] => Fault Level of each Fault
    """
    fMax = max(levels)
    if fMax > 0:
        scoreList = [0 for _ in range(fMax)]
        countList = [0 for _ in range(fMax)]
        for s,l in zip(scores, levels):
            if l < 1: continue
            scoreList[l-1] += s
            countList[l-1] += 1
        scoreRes = [s/c if c!=0 else 0 for s,c in zip(scoreList, countList)]
        score = sum([itm/2**min(1+flevel,fMax-1) for flevel, itm in enumerate(scoreRes[::-1])])
        if fMax == 1:
            return score
        for flevel in range(1, fMax):
            if score < 1/2**(fMax - flevel):
                if flevel == 1:
                    return score*2**(fMax-flevel)/fMax     
                else:
                    return (score-1/2**(fMax+1-flevel))/(1/2**(fMax-flevel)-1/2**(fMax+1-flevel))/fMax + (flevel-1)/fMax
        return (score-0.5)/(1-0.5)/fMax + 1 - 1/fMax
    else:
        return sum(scores)/len(scores)

def calcul_fault_fuzzy_proba(D_mat, fuzzy_mat, ckpts, F_or_mat=None, eps=1e-16, n_precision=9):
    fault_proba = np.exp(D_mat.dot(np.log(ckpts+eps)[:,None]))
    fuzzy_proba = 1 - np.exp(fuzzy_mat.dot(np.log(1-fault_proba+eps)))

    if not F_or_mat is None:
        fault_proba += 1 - np.exp(F_or_mat.dot(np.log(1-fault_proba+eps)))
        fuzzy_proba += 1 - np.exp(F_or_mat.dot(np.log(1-fuzzy_proba+eps)))
        
    return np.round(fault_proba, decimals=n_precision), \
           np.round(np.maximum(fuzzy_proba, 0), decimals=n_precision)

class multiInfoGraph:
    def __init__(self, graph=None, description={}, eps=1e-16, n_precision=9, non_check=False):
        self._description = description
        self._eps = eps
        self._n_precision = n_precision
        self.re_init(graph=graph, non_check=non_check)

    def re_init(self, graph=None, non_check=False):
        if not graph is None:
            self._init = True

            self._nodeMap = {node["text"]: node for node in graph["nodes"]}
            
            self._nodes = graph["nodes"]
            self._edges = graph["edges"]
            
            self._faultIdList = [nodeId for nodeId, node in enumerate(self._nodes) if node["type"] in FAULTTYPE]
            self._flevels  = [node.get("showConfig", {}).get("properties", {}).get('flevel', 0) for nodeId, node in enumerate(self._nodes) if node["type"] in FAULTTYPE]
            self._testIdList = [nodeId for nodeId, node in enumerate(self._nodes) if node["type"] in TESTTYPE or (node["type"]==CKPT and self._checkCkpt(nodeId))]
            
            self._F_mat, self._D_mat, self._fuzzy_mat, self._testName, self._faultName = self.get_Dmat()
            self._D_mat_full, self.F_or_mat = self.get_or_flow()

            self._subsysMap = self.get_subsysMap()
            
            self._ckptState = np.zeros(len(self._testIdList))

            if not non_check:
                self.check()
            
        else:
            self._init = False

    def from_fmeca(self, df, non_check=False):
        if isinstance(df, str):
            if df.split(".")[-1].lower() in ["xls", "xlsx"]:
                df = pd.read_excel(df)
            elif df.split(".")[-1].lower() == "csv":
                df = pd.read_csv(df)
            else:
                raise Exception("[TypeError] Uploaded File isn't Tabular File.")
        self.re_init(graph=read_fmeca(df), non_check=non_check)

    def get_or_flow(self):
        testedNode = np.where(self._D_mat.sum(axis=1))[0]

        faultMap = [
            [self._faultName.index(edge["to"]), self._faultName.index(edge["from"])]
            for edge in self._edges if (edge["to"] in self._faultName and edge["from"] in self._faultName \
                                        and self._faultName.index(edge["to"]) not in testedNode)]
        if faultMap:
            fault_mat = coo_matrix(([1]*len(faultMap), zip(*faultMap)),shape=(len(self._faultName), len(self._faultName)), dtype=np.int).T
            for _ in self._edges:
                fault_mat_pre = fault_mat
                fault_mat_pre = (fault_mat_pre + fault_mat.dot(fault_mat)) > 0.75
                if np.max(np.abs(fault_mat_pre-fault_mat)) < 0.25:
                    break
            return ((self._D_mat.T + self._D_mat.T.dot(fault_mat)) > 0.75).T.astype(np.int), fault_mat.T.astype(np.int)
        else:
            return self._D_mat, None
        
    def optimize_test(self):
        testMap = [[self._testName.index(edge["to"]), self._faultName.index(edge["from"])] for edge in self._edges if (edge["to"] in self._testName and edge["from"] in self._faultName)]
        faultMap = [[self._faultName.index(edge["to"]), self._faultName.index(edge["from"])] for edge in self._edges if (edge["to"] in self._faultName and edge["from"] in self._faultName)]
        test_mat = coo_matrix(([1]*len(testMap), zip(*testMap)),shape=(len(self._testName), len(self._faultName)), dtype=np.int).tocsr()
        fault_mat = coo_matrix(([1]*len(faultMap), zip(*faultMap)),shape=(len(self._faultName), len(self._faultName)), dtype=np.int).tocsc()

        #print(test_mat.todense())
        ckpt_count = np.asarray(test_mat.sum(axis=1)).flatten() ## Optimization of ckpt ## fuzzibility caused by checkpoint
        #print(ckpt_count)
        
        inutile_ind = np.where(np.asarray(fault_mat.sum(axis=1)) > 1.75)[0]
        fault_mat[inutile_ind, :] = 0
        fault_mat.eliminate_zeros()

        startNode = set(np.where(np.asarray(fault_mat.sum(axis=0)) < 0.25)[1])
        ckptId = set()
        registreNode = set()
        while startNode:
            newStartNode = set()
            for faultId in startNode:
                #print(self._faultName[faultId])
                if faultId in registreNode:
                    continue
                ckptId_ = np.where(test_mat[:, faultId].toarray()>0.75)[0]
                faulttId_ = np.where(fault_mat[faultId, :].toarray()>0.75)[1]
                faultSum = fault_mat[faultId, :].sum()
                if ckptId_.size:
                    ckptIdBest = ckptId_[np.argmin([ckpt_count[itm] for itm in ckptId_])] ## Mimimunize the fuzzibility caused by checkpoint
                    ckptId.add(ckptIdBest)
                    if faulttId_:
                        if ckpt_count[ckptIdBest] == 1: ## If checkpoint is fuzzy, continue to operate on the next fault-node
                            registreNode |= set(np.where(self._F_mat[faultId, :].toarray()>0.75)[1])
                        else:
                            newStartNode.add(faulttId_[0])
                elif faulttId_.size:
                    newStartNode.add(faulttId_[0])
            startNode = newStartNode
            
        _del_testName = [self._testName[i] for i in set(range(len(self._testName)))-ckptId]
        self._testName = [self._testName[i] for i in sorted(ckptId)]
        
        self._nodes = [node for node in self._nodes if node["text"] not in _del_testName]
        self._edges = [edge for edge in self._edges if edge["to"] not in _del_testName]
        
        self._faultIdList = [nodeId for nodeId, node in enumerate(self._nodes) if node["type"] in FAULTTYPE]
        self._testIdList = [nodeId for nodeId, node in enumerate(self._nodes) if node["type"] in TESTTYPE or (node["type"]==CKPT and self._checkCkpt(nodeId))]
        
        self._F_mat, self._D_mat, self._fuzzy_mat, self._testName, self._faultName = self.get_Dmat()
        self._D_mat_full, self.F_or_mat = self.get_or_flow()

        self._subsysMap = self.get_subsysMap()            
        self._ckptState = np.zeros(len(self._testIdList))
        self.check()

    def get_Dmat(self):
        faultName = [node["text"] for node in self._nodes if node["type"] in FAULTTYPE]
        testName = [node["text"] for nodeId, node in enumerate(self._nodes) if node["type"] in TESTTYPE or (node["type"]==CKPT and self._checkCkpt(nodeId))]
        
        faultMap = [[faultName.index(edge["to"]), faultName.index(edge["from"])] for edge in self._edges if (edge["to"] in faultName and edge["from"] in faultName)]
        testMap = [[testName.index(edge["to"]), faultName.index(edge["from"])] for edge in self._edges if (edge["to"] in testName and edge["from"] in faultName)]

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

        fault_mat = coo_matrix(([1]*len(faultMap), zip(*faultMap)),shape=(len(faultName), len(faultName)), dtype=np.int)
        test_mat = coo_matrix(([1]*len(testMap), zip(*testMap)),shape=(len(testName), len(faultName)), dtype=np.int)
        if faultMap_pure:
            fault_mat_pure = coo_matrix(([1]*len(faultMap_pure), zip(*faultMap_pure)),shape=(len(faultName), len(faultName)), dtype=np.int)
        else:
            fault_mat_pure = coo_matrix(([0], ([0],[0])),shape=(len(faultName), len(faultName)), dtype=np.int)
        if testMap_pure:
            test_mat_pure = coo_matrix(([1]*len(testMap_pure), zip(*testMap_pure)),shape=(len(testName), len(faultName)), dtype=np.int)
        else:
            test_mat_pure = coo_matrix(([0], ([0],[0])),shape=(len(testName), len(faultName)), dtype=np.int)

        m = len(faultName)
        E = coo_matrix(([1]*m, (range(m), range(m))), shape=(m,m), dtype=np.int)
        
        for _ in self._edges:
            fault_mat_pre = fault_mat
            fault_mat = (fault_mat + fault_mat.dot(fault_mat)) > 0.75
            if np.max(np.abs(fault_mat_pre-fault_mat)) < 0.25:
                break

        for _ in self._edges:
            fault_mat_pure_pre = fault_mat_pure
            fault_mat_pure = (fault_mat_pure + fault_mat_pure.dot(fault_mat_pure)) > 0.75
            if np.max(np.abs(fault_mat_pure_pre-fault_mat_pure)) < 0.25:
                break

        D_mat = (test_mat.dot(E+fault_mat) > 0.75).astype(np.int)
        D_mat.eliminate_zeros()

        D_mat_pure = (test_mat_pure.dot(E+fault_mat_pure) > 0.75).astype(np.int)
        D_mat_pure.eliminate_zeros()
        unfuzzy_node = D_mat_pure.indices.tolist()
    
        fuzzy_mat = ((D_mat.T.dot(D_mat) - fault_mat - fault_mat.T - E).tocsr()> 0.75).astype(np.int)
        fuzzy_mat[unfuzzy_node, :] = 0
        fuzzy_mat.eliminate_zeros()

        F_mat = ((fault_mat- E)> 0.75).astype(np.int)
        F_mat.eliminate_zeros()
        
        return F_mat, D_mat.T, fuzzy_mat, testName, faultName

    def _checkCkpt(self, nodeId):
        return any(map(lambda edge: self._nodeMap[edge["from"]]["type"]!=ALGO, filter(lambda itm: itm["to"] == self._nodes[nodeId]["text"],self._edges)))

    def to_json(self):
        config = {
            "nodes": self._nodes,
            "edges": self._edges,
            "D_mat": [
                self._D_mat.indptr.tolist(),
                self._D_mat.indices.tolist()
                ],
            "F_mat": [
                self._F_mat.indptr.tolist(),
                self._F_mat.indices.tolist()
                ],
            "fuzzy_mat": [
                self._fuzzy_mat.indptr.tolist(),
                self._fuzzy_mat.indices.tolist()
                ],
            "faultIdList": self._faultIdList,
            "testIdList": self._testIdList,
            "testName": self._testName,
            "faultName": self._faultName,
            }
        return json.dumps(config)

    def from_json(self, configJson):
        config = json.loads(configJson)
        self._nodes = config["nodes"]
        self._edges = config["edges"]
        
        self._faultIdList = config["faultIdList"]
        self._testIdList = config["testIdList"]
        
        self._testName = config["testName"]
        self._faultName = config["faultName"]
        
        D_indptr, D_indices = config["D_mat"]
        self._D_mat = csc_matrix(([1]*len(D_indices), D_indices, D_indptr),shape=(len(self._faultName), len(self._testName)), dtype=np.int)

        F_indptr, F_indices = config["F_mat"]
        self._F_mat = csr_matrix(([1]*len(F_indices), F_indices, F_indptr),shape=(len(self._faultName), len(self._faultName)), dtype=np.int)

        fuzzy_indptr, fuzzy_indices = config["fuzzy_mat"]
        self._fuzzy_mat = csr_matrix(([1]*len(fuzzy_indices), fuzzy_indices, fuzzy_indptr),shape=(len(self._faultName), len(self._faultName)), dtype=np.int)

        self._D_mat_full, self.F_or_mat = self.get_or_flow()
        
        self._subsysMap = self.get_subsysMap()
        self._ckptState = np.zeros(len(self._testIdList))

    def refresh(self, ckpts):
        if not self._init:
            raise Exception("[GRAPH-VIDE ERROR] Graph hasn't been initialized")
        
        for ckpt, state in ckpts.items():
            if not ckpt in self._testName:
                continue
            self._ckptState[self._testName.index(ckpt)] = float(state)

    
    @property
    def nodes_edges(self): ## 获得最终结果    
        return {"nodes": self._nodes, "edges": self._edges}

    @property
    def state(self): ## 获得最终结果    
        fault_proba, fuzzy_proba = calcul_fault_fuzzy_proba(self._D_mat, self._fuzzy_mat, self._ckptState, self.F_or_mat, 
                                                            eps=self._eps, n_precision=self._n_precision)
        
        for tId, testNodeId in enumerate(self._testIdList):
            self._nodes[testNodeId]["state"] = self._ckptState[tId]
            self._nodes[testNodeId]["fuzzy_state"] = 0
            
        for fId, fNodeId in enumerate(self._faultIdList):
            self._nodes[fNodeId]["state"] = fault_proba[fId,0]
            self._nodes[fNodeId]["fuzzy_state"] = fuzzy_proba[fId,0]

        for subsysId, subsysInfo in self._subsysMap.items():
            self._nodes[subsysId]["state"] = _fuse_scores([fault_proba[fId] for fId in subsysInfo], [self._flevels[fId] for fId in subsysInfo])[0]
            
        return {
            "data": {"nodes": self._nodes, "edges": self._edges},
            "baseInfo": self._description
            }

    def check(self):
        unCheckIdList_ = np.where(np.asarray(self._D_mat.sum(axis=1)) < 0.25)[0]

        fuzzyIdList_ = np.where(np.asarray(self._fuzzy_mat.sum(axis=1)) > 0.75)[0]

        m, _ = self._F_mat.shape
        #E = coo_matrix(([1]*m, (range(m), range(m))), shape=(m,m), dtype=np.int)
        indices = [(sId,fId) for sId, fId in zip(self._F_mat.indices, [ind for ind, count in enumerate(np.diff(self._F_mat.indptr)) for _ in range(count)]) if sId!=fId]
        collisionList_ = [sId for sId, fId in indices if (fId, sId) in indices]

        for tId, tNodeId in enumerate(self._testIdList):
            self._nodes[tNodeId]["detectable"] = True
            self._nodes[tNodeId]["fuzzible"] = False
            self._nodes[tNodeId]["collision"] = False

        detectList = []
        fuzzyList = []
        collisionList = []
        for fId, fNodeId in enumerate(self._faultIdList):
            self._nodes[fNodeId]["detectable"] = fId not in unCheckIdList_
            self._nodes[fNodeId]["fuzzible"] = fId in fuzzyIdList_
            self._nodes[fNodeId]["collision"] = fId in collisionList_
            detectList.append(self._nodes[fNodeId]["detectable"])
            fuzzyList.append(self._nodes[fNodeId]["fuzzible"])
            collisionList.append(self._nodes[fNodeId]["collision"])

        for subsysId, subsysInfo in self._subsysMap.items():
            self._nodes[subsysId]["detectable"] = all(map(lambda itm: detectList[itm], subsysInfo))
            self._nodes[subsysId]["fuzzible"] = any(map(lambda itm: fuzzyList[itm], subsysInfo))
            self._nodes[subsysId]["collision"] = any(map(lambda itm: collisionList[itm], subsysInfo))

    @property
    def detect_isolat_ratio(self):
        unCheckIdList = np.where(np.sum(self._D_mat_full, axis=1)<0.25)[0]

        fuzzyIdList = [faultId for ckptId in np.where(np.asarray(self._D_mat.sum(axis=0))<1.25)[1] \
                       if np.max(self._D_mat[:, ckptId])>0.75 for faultId in (self._D_mat[:, ckptId]>0.75)[0]]

        faultMap = [[self._faultName.index(edge["to"]), self._faultName.index(edge["from"])] \
                    for edge in self._edges if (edge["to"] in self._faultName and edge["from"] in self._faultName)]
        
        srcList, trgList = zip(*faultMap)
        return [
            1-len(unCheckIdList)/len(self._faultIdList),
            len(fuzzyIdList)/len(self._faultIdList),
            1 - len(set(srcList)-set(trgList))/(len(self._testIdList)+len(unCheckIdList))
            ]

    def clear(self):
        self._ckptState = np.zeros(len(self._testIdList))

    @property
    def D_mat(self):
        if not self._init:
            raise Exception("[GRAPH-VIDE ERROR] Graph hasn't been initialized")
        return self._D_mat, self._testName, self._faultName

    @property
    def D_mat_list(self):
        if not self._init:
            raise Exception("[GRAPH-VIDE ERROR] Graph hasn't been initialized")
        return self._D_mat.todense().tolist()#, self._testName, self._faultName

    @property
    def D_mat_df(self):
        if not self._init:
            raise Exception("[GRAPH-VIDE ERROR] Graph hasn't been initialized")
        return pd.DataFrame(self._D_mat.todense(), index=self._faultName, columns=self._testName)

    @property
    def D_mat_full(self):
        if not self._init:
            raise Exception("[GRAPH-VIDE ERROR] Graph hasn't been initialized")
        return self._D_mat_full, self._testName, self._faultName

    @property
    def D_mat_full_list(self):
        if not self._init:
            raise Exception("[GRAPH-VIDE ERROR] Graph hasn't been initialized")
        return self._D_mat_full.todense().tolist()#, self._testName, self._faultName

    @property
    def D_mat_full_df(self):
        if not self._init:
            raise Exception("[GRAPH-VIDE ERROR] Graph hasn't been initialized")
        return pd.DataFrame(self._D_mat_full.todense(), index=self._faultName, columns=self._testName)

    @property
    def algos(self):
        return [node for nodeId, node in enumerate(self._nodes) if node["type"]==ALGO]

    @property
    def ckpts_algos(self):
        return self._testName

    @property
    def faults(self):
        return self._faultName

    def get_subsysMap(self):
        subsysMap={nodeId :node["children"] for nodeId, node in enumerate(self._nodes) if node["type"] in SUBSYS}
        subsysInnerMap={node["text"] :node["children"] for node in self._nodes if node["type"] in SUBSYS}
        return {k:self._refresh_subsysMap(v, subsysInnerMap) for k,v in subsysMap.items()}

    def _refresh_subsysMap(self, v, subsysMap):
        children_ = []
        for v_ in v:
            if v_ in subsysMap.keys():
                children_.extend(self._refresh_subsysMap(subsysMap[v_], subsysMap))
            elif v_ in self._faultName: 
                children_.append(self._faultName.index(v_))
        return children_

    ## UseLess
    def evaluateCkpts(self, ckptHot):
        ckpts_algos = self.ckpts_algos
        forbidden_ckpts = [ckpts_algos[ind] for ind, val in enumerate(ckptHot) if val < 0.5]
        mig = multiInfoGraph(
                {
                    "nodes": [node for node in self._nodes if node["text"]  not in forbidden_ckpts],
                    "edges": [edge for edge in self._edges if edge["from"] not in forbidden_ckpts and edge["to"] not in forbidden_ckpts]
                    }
            )
        return mig.detect_isolat_ratio


if __name__ == "__main__":
    with open("data.json", "r+", encoding="utf-8") as f:
        data = json.load(f)
    mig = multiInfoGraph(data)
    print("测点名称：", mig.ckpts_algos)
    print("D矩阵：", mig.D_mat_df)
    print("广义D矩阵：", mig.D_mat_full_df)
    mig.refresh({"测试1": 1})
    print(mig.state)

    ## 测点优化
    mig.optimize_test()
    print("测点名称：", mig.ckpts_algos)
    print("D矩阵：", mig.D_mat_df)
    print("广义D矩阵：", mig.D_mat_full_df)
