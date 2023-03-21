try:
    from .FuncBase import getResult
    from .RuleParse import ruleParse
except:
    from FuncBase import getResult
    from RuleParse import ruleParse
    
import re, math, json

def _convertTag(rulesInfo):
    error = []
    faultName = re.sub(r" +","", rulesInfo["faultName"] or "")
    faultName = faultName.replace("\'","\"").replace("\\\"","\'").replace("\"","")
    if faultName[:6] == "Fault(" and faultName[:-1]==")":
        faultName = faultName[6:-1]
    if not faultName:
        error.append("|[Error]| 故障名为空")
    return faultName, error

class ruleConvertor:
    def __init__(self, pnames={}):
        """
        [RuleInfo Format]  [
                               {
                                    +* "ruleExpress": ...,
                                    +* "faultName": ...,
                                    +  "editable": ...,
                                    -  "relatPara": ...,
                                    -  "relatFault": ...,
                                    -  "subExpress": ...,
                                    -  "subExpressOrder": ...,
                                    -  "convertRule": ...
                                },
                                ...
                            ]
        """
        self.pnames = pnames

    def _check_rule(self, rulesInfo):
        result = []; checkPass = True
        faultCircle = {}
        faults, log = map(list, zip(*map(_convertTag, rulesInfo)))
        for ruleId, ruleInfo in enumerate(rulesInfo):
            if ruleInfo.get("editable", True):
                error = len(log[ruleId]); warning = 0
                if ruleInfo["ruleExpress"] and ruleInfo["ruleExpress"].replace(" ",""):
                    rp = ruleParse(pnames=self.pnames, fnames=faults)
                    rp.convert(ruleInfo["ruleExpress"])
                    fnames = list(rp.relatFault)
                    for fname in fnames:
                        fnameId = faults.index(fname)
                        if fnameId == ruleId:
                            error += 1
                            log[ruleId].append(f"|[Error]| 规则表达式不得涉及规则故障名")
                        else:
                            if ruleId in faultCircle.keys():
                                faultCircle[ruleId].append(fnameId)
                            else:
                                faultCircle[ruleId] = [fnameId]
                            if fnameId in faultCircle.keys():
                                if ruleId in faultCircle[fnameId]:
                                    error += 1
                                    log[ruleId].append(f"|[Error]| 故障与故障{faults[fnameId]}存在闭环")
                                faultCircle[ruleId].extend(faultCircle[fnameId])
                    log[ruleId].extend(rp.log)
                    error += rp.error
                    warning += rp.warning
                else:
                    error += 1
                    log[ruleId].extend(["|[Error]| 规则表达式缺失"])
                 
                ruleInfo["log"] = ";".join(log[ruleId])
                ruleInfo["faultName"] = faults[ruleId].split(",")[0]
                if error == 0:
                    if warning == 0:
                        ruleInfo["error"] = ""
                    else:
                        ruleInfo["error"] = f"警告{warning}"
                    ruleInfo["editable"] = False
                    ruleInfo["relatFault"] = fnames
                else:
                    checkPass = False
                    if warning == 0:
                        ruleInfo["error"] = f"错误{error}"
                    else:
                        ruleInfo["error"] = f"错误{error}||警告{warning}"
                    ruleInfo["editable"] = True
            else:
                if faults[ruleId] in faults[:ruleId]:
                    error += 1
                    rulePreId = faults.index(faults[ruleId])
                    log[ruleId].append(f"|[Error]| 故障名与规则{rulePreId}重复")
                for relatFaultName in ruleInfo["relatFault"]:
                    if relatFaultName not in faults:
                        error[ruleId] += 1
                        log[ruleId].append("|[Error]| 故障名{relatFaultName}未出现")
                for fname in ruleInfo["relatFault"]:
                    fnameId = faults.index(fname)
                    if fnameId == ruleId:
                        error += 1
                        log[ruleId].append(f"|[Error]| 规则表达式不得涉及规则故障名")
                    else:
                        if ruleId in faultCircle.keys():
                            faultCircle[ruleId].append(fnameId)
                        else:
                            faultCircle[ruleId] = [fnameId]
                        if fnameId in faultCircle.keys():
                            if ruleId in faultCircle[fnameId]:
                                error += 1
                                log[ruleId].append(f"|[Error]| 故障与故障{faults[fnameId]}存在闭环")
                            faultCircle[ruleId].extend(faultCircle[fnameId])
                error = len(log[ruleId])
                if  "警告" in ruleInfo["error"]:
                    ruleInfo["error"] = ruleInfo["error"].split("||")[-1]
                if error:
                    checkPass = False
                    ruleInfo["editable"] = True
                    ruleInfo["error"] = f"错误{error}||{ruleInfo['error']}"
                    ruleInfo["log"] = ";".join(log[ruleId])
                else:
                    ruleInfo["editable"] = False
            result.append(ruleInfo)
        return result, checkPass

    def _config_rule(self, rulesInfo):
        rulesInfo_ = [self._convert_item(ruleItem) for ruleItem in rulesInfo]
        rule, seqOrder, ruleOrder, data, fnames, descript = self._convert_rule(rulesInfo)
        return json.dumps([rule, seqOrder, ruleOrder, data, fnames]), rulesInfo_

    def _convert_rule(self, rulesInfo):
        rule = []
        seqOrder = []
        ruleOrder = []
        data = {
                        "Para": {}, "Fault": {},
                        "Crease": {}, "MMM": {},
                        "PreCond": {}, "Trigger": {},
                        "[]": {}, "<>": {}, "{}": {},
                    }
        faults = [ruleInfo["faultName"] for ruleInfo in rulesInfo]
        faultCircle = {}
        for ruleId, ruleInfo in enumerate(rulesInfo):
            rp = ruleParse(pnames=self.pnames,fnames=faults)
            data["Fault"][faults[ruleId]] = {"state": None, "score": 0}
            result = rp.convert(ruleInfo["ruleExpress"])
            
            rule.append(result)
            for funcInfo in rp.seqOrder:
                if not funcInfo in seqOrder:
                    seqOrder.append(funcInfo)
            for para in rp.relatPara.keys():
                if para in data["Para"].keys():
                    data["Para"][para]["frameMax"] = max(data["Para"][para]["frameMax"], rp.relatPara[para][0])
                    data["Para"][para]["timeMax"] = max(data["Para"][para]["timeMax"], rp.relatPara[para][1])
                else:
                    data["Para"][para] = {"frameMax": rp.relatPara[para][0], "timeMax": rp.relatPara[para][1], "value":[], "time":[]}
            for funcName, seqInfo in rp.seqs.items():
                if funcName in ["Time"]:
                    for para, subInfo in seqInfo.items():
                        _, subCount = subInfo
                        if para in data["Para"].keys():
                            data["Para"][para]["frameMax"] = max(data["Para"][para]["frameMax"], subCount[0][0])
                            data["Para"][para]["timeMax"] = max(data["Para"][para]["timeMax"], subCount[0][1])
                        else:
                           data["Para"][para] = {"frameMax": subCount[0][0], "timeMax": subCount[0][1], "value":[], "time":[]}
                elif funcName in ["Max", "Min", "Mean"]:
                    for subExpress, subInfo in seqInfo.items():
                        subTree, subCount = subInfo
                        if subExpress in data["MMM"].keys():
                            data["MMM"][subExpress]["frameMax"] = max(data["MMM"][subExpress]["frameMax"], subCount[0][0])
                            data["MMM"][subExpress]["timeMax"] = max(data["MMM"][subExpress]["timeMax"], subCount[0][1])
                        else:
                           data["MMM"][subExpress] = {"convertedRule": subTree[0], "frameMax": subCount[0][0],
                                                                              "timeMax": subCount[0][1], "value":[], "time":[]}
                elif funcName in ["Increase", "Decrease"]:
                    for subExpress, subInfo in seqInfo.items():
                        subTree, subCount = subInfo
                        if subExpress in data["Crease"].keys():
                            data["Crease"][subExpress]["frameMax"] = max(data["Crease"][subExpress]["frameMax"], subCount[0][0])
                            data["Crease"][subExpress]["timeMax"] = max(data["Crease"][subExpress]["timeMax"], subCount[0][1])
                        else:
                           data["Crease"][subExpress] = {"convertedRule": subTree[0], "frameMax": subCount[0][0],
                                                                              "timeMax": subCount[0][1], "value":[], "time":[], "prevalue": None,
                                                                              "lastDecTime":None, "lastIncTime": None}
                elif funcName in ["[]"]:
                    for subExpress, subInfo in seqInfo.items():
                        subTree,  _ = subInfo
                        data["[]"][subExpress] = {"convertedRule": subTree, "lastTime": None, "lastFalseTime": None}
                elif funcName in ["<>"]:
                    for subExpress, subInfo in seqInfo.items():
                        subTree, _ = subInfo
                        data["<>"][subExpress] = {"convertedRule": subTree, "lastTime": None,  "lastTrueTime": None}
                elif funcName in ["{}"]:
                    for subExpress, subInfo in seqInfo.items():
                        subTree, subCount = subInfo
                        if subExpress in data["{}"].keys():
                            data["{}"][subExpress]["frameMax"] = max(data["{}"][subExpress]["frameMax"], subCount[0])
                        else:
                           data["{}"][subExpress] = {"convertedRule": subTree, "frameMax": subCount[0], "time": [], "value": [], "score": []}
                elif funcName in ["PreCond"]:
                    for subExpress, subInfo in seqInfo.items():
                        subTree, _ = subInfo
                        data["PreCond"][subExpress] = {"convertedRule": subTree[0], "validedTime": None, "state": None}
                elif funcName in ["Trigger"]:
                    for subExpress, subInfo in seqInfo.items():
                        subTree, _ = subInfo
                        data["Trigger"][subExpress] = {"convertedRule": subTree[0], "cancelRule": subTree[1], "timeMax": subCount[0],
                                                                            "trigTime": -1, "state": None}
            for fname in rp.relatFault:
                fnameId = faults.index(fname)
                if ruleId in faultCircle.keys():
                    faultCircle[ruleId].append(fnameId) # ruleId 需要先算 fnameId
                else:
                    faultCircle[ruleId] = [fnameId]
                if fnameId in faultCircle.keys():
                    faultCircle[ruleId].extend(faultCircle[fnameId]) # 队列中需要先算的在后，后算的在后
        # 根据fnames的依赖性确定规则判断顺序
        faultDependance = [[ruleId]+faultCircle[ruleId] for ruleId in faultCircle.keys()]
        for faultDepend in sorted(faultDependance, key=lambda faultDep: -len(faultDep)):
            if faultDepend[0] in ruleOrder:
                ruleOrder.extend(faultDepend[::-1])
        ruleOrder.extend(sorted(set(range(len(rulesInfo)))-set(ruleOrder)))
        return rule, seqOrder, ruleOrder, data, faults

class ruleEvaluator:
    def __init__(self, rule, seqOrder, ruleOrder, data, fnames, pnames=[], dt=0.01):
        self.pnames = pnames
        self.rule = rule
        self.seqOrder = seqOrder
        self.ruleOrder = ruleOrder
        self.data = data
        self.fnames = fnames
        self.data["actualTime"] = 0
        self.dt = dt

    def single_validate(self, dataFrame, time_=None):
        if time_ is None:
            self.data["actualTime"] += self.dt
        else:
            self.data["actualTime"] = time_
        for paraId, para in enumerate(self.pnames):
            if para in self.data["Para"].keys():
                self.data["Para"][para]["value"].append(dataFrame[paraId])
                self.data["Para"][para]["time"].append(time_)
        for funcName, seqName in self.seqOrder:
            if funcName in ["Max", "Min", "Mean"]:
                value_, _ = getResult(self.data, self.data["MMM"][seqName]["convertedRule"])
                if not math.isnan(value_):
                    self.data["MMM"][seqName]["time"].append(time_)
                    self.data["MMM"][seqName]["value"].append(value_)
            elif funcName in ["Increase", "Decrease"]:
                value_, _ = getResult(self.data, self.data["Crease"][seqName]["convertedRule"])
                if math.isnan(value_):
                    continue
                if not self.data["Crease"][seqName]["prevalue"] is None:
                    if value_ > self.data["Crease"][seqName]["prevalue"]:
                        self.data["Crease"][seqName]["time"].append(time_)
                        self.data["Crease"][seqName]["value"].append(True)
                        self.data["Crease"][seqName]["lastIncTime"] = time_
                    elif value_ < self.data["Crease"][seqName]["prevalue"]:
                        self.data["Crease"][seqName]["time"].append(time_)
                        self.data["Crease"][seqName]["value"].append(False)
                        self.data["Crease"][seqName]["lastDecTime"] = time_
                    else:
                        self.data["Crease"][seqName]["time"].append(time_)
                        self.data["Crease"][seqName]["value"].append(None)
                self.data["Crease"][seqName]["prevalue"] = value_
            elif funcName in ["[]"]:
                value_, _ = getResult(self.data, self.data["[]"][seqName]["convertedRule"])
                if value_ is None:
                    continue
                if not value_:
                    self.data["[]"][seqName]["lastFalseTime"] = time_
                self.data["[]"][seqName]["lastTime"] = time_
            elif funcName in ["<>"]:
                value_, _ = getResult(self.data, self.data["<>"][seqName]["convertedRule"])
                if value_ is None:
                    continue
                if value_:
                    self.data["<>"][seqName]["lastTrueTime"] = time_
                self.data["<>"][seqName]["lastTime"] = time_
            elif funcName in ["{}"]:
                value_, score_ = getResult(self.data, self.data["{}"][seqName]["convertedRule"])
                if value_ is None:
                    self.data["{}"][seqName]["value"].append(value_)
                    self.data["{}"][seqName]["score"].append(score_)
                    self.data["{}"][seqName]["time"].append(time_)
            elif funcName in ["PreCond"]:
                value_, _ = getResult(self.data, self.data["PreCond"][seqName]["convertedRule"])
                if value_ is None:
                    continue
                if value_ and not self.data["PreCond"][seqName]["state"]:
                    self.data["PreCond"][seqName]["validedTime"] = time_
                self.data["PreCond"][seqName]["state"] = value_
            elif funcName in ["Trigger"]:
                value_, _ = getResult(self.data, self.data["Trigger"][seqName]["cancelRule"])
                if value_:
                    self.data["Trigger"][seqName]["trigTime"] = -1
                    self.data["Trigger"][seqName]["state"] = None
                else:
                    value_, _ = getResult(self.data, self.data["Trigger"][seqName]["convertedRule"])
                    if not value_ is None:
                        if value_ and not self.data["Trigger"][seqName]["state"]:
                            self.data["Trigger"][seqName]["trigTime"] = time_
                        self.data["Trigger"][seqName]["state"] = value_
        for ruleId in self.ruleOrder:
            # print(ruleId, self.rule[ruleId])
            res, score = getResult(self.data, self.rule[ruleId])
            self.data["Fault"][self.fnames[ruleId]]["state"] = res
            self.data["Fault"][self.fnames[ruleId]]["score"] = score
            self.data["Fault"][self.fnames[ruleId]]["time"] = time_
        # print(self.data)
        # print("=======================")
        return {fname: info["score"] for fname, info in self.data["Fault"].items()}

if __name__ == "__main__":
    pnames = ["P1", "P2"]
    times = 1000
    data = [1,6]
    rule = [
                {"showId": 0, "ruleExpress": "Max(P1+5,1,0)+5>15", "faultName":"Tag1"},
                {"showId": 1, "ruleExpress": "Max(P1+2,1,1)+5>15", "faultName":"Tag2"},
                {"showId": 2, "ruleExpress": "Increase(P2*2,1,1) and Para(P1,0.1,1)<=10", "faultName":"故障001,1"},
                {"showId": 3, "ruleExpress": "PreCond([0.1](P1<5), 0.3, Para(P1,0.1,1)>0)", "faultName":"故障002,2"}
            ]
    rule, seqOrder, ruleOrder, data, faults = ruleConvertor(pnames)._convert_rule(rule)
    print(ruleEvaluator(rule, seqOrder, ruleOrder, data, faults).single_validate(data, times))
    
            
