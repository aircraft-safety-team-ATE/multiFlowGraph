from multiprocessing import Process, Queue
import os, time, json, datetime
import pandas as pd
import numpy as np

try:
    from . import detectAlgo, predictAlgo
    from .msfgEngine import multiInfoGraph
    from .rule.RuleDetector import ruleEvaluator, ruleConvertor
except Exception as e:
    import detectAlgo, predictAlgo
    from msfgEngine import multiInfoGraph
    from rule.RuleDetector import ruleEvaluator, ruleConvertor

def RuleDetectTest(modelConfig, data, relatParas, time_, interComponent):
    V = np.ones(len(relatParas))*np.nan
    for pId, pname in relatParas:
        if pname in data.keys():
            V[pId] = data[pname]
    #time_ = data.index.values
    model = ruleEvaluator(*modelConfig) 
    interComponent.registre(model.validate(data, time_))

def MLDetectTest(modelConfig, data, relatParas, time_, interComponent):
    V = np.ones(len(relatParas))*np.nan
    for pId, pname in relatParas:
        if pname in data.keys():
            V[pId] = data[pname]
    modelInfo, test_name = modelConfig
    typ = modelInfo.get("type", "few-shot")
    modelAlgo  = modelInfo.get("model_algo", "")
    test_uuid  = modelInfo.get("test_uuid", "")
    model = getattr(detectAlgo, modelAlgo).Model(index=test_uuid, name=test_name)    
    if typ != "few-shot":
        try:
            model.load_model()
        except Exception as e:
            raise Exception(f"[ERROR] model[{test_name}#{test_uuid}] couldn't be loaded | {e}")   
    interComponent.registre({model.name: model.validate([data])})

class interComponentBase:
    def __init__(self):
        self._result_queue = Queue()
        self._state = {}

    def registre(self, item):
        self._result_queue.put(item)

    def clear(self):
        self._state = {}

    @property
    def state(self):
        while not self._result_queue.empty():
            self._state.update(result_queue.get_nowait())
        return self._state

class taskTestWorker:
    def __init__(self, multiGraphConfig, interComponent=None, worker_num=3, time_resample=0.005):
        self.worker_num = worker_num
        self.time_resample = time_resample
        self.interComponent = interComponent if not interComponent is None else interComponentBase()
        self.multiGraph = multiInfoGraph(multiGraphConfig)
        self.toDoList = self._get_toDoList()
        self.time_actual = 0

    def _get_toDoList(self):
        _toDoList = []
        _ruleConfig = []
        for node in self.multiGraph.algos:
            test_type = node.get("showConfig", {}).get("properties", {}).get("test_type", "rule")
            if test_type == "rule":
                _ruleConfig.append({
                    "ruleExpress": node.get("showConfig", {}).get("properties", {}).get("model_config", {}).get("expression", ""),
                    "faultName": node["text"]
                    })
            else:
                test_type = node.get("showConfig", {}).get("properties", {}).get("test_type", "rule")
                modelConfig = [
                    test_type,
                    node.get("showConfig", {}).get("properties", {}).get("model_config", {}),
                    node["text"]
                    ]
                relatParas = node.get("showConfig", {}).get("properties", {}).get("relat_paras", {})
                _toDoList.append(["ML", modelConfig, relatParas])
        _toDoList.append(["rule", ruleConvertor()._convert_rule(_ruleConfig), None])
        return _toDoList

    def clear():
        self.multiGraph.clear()
        self.interComponent.clear()

    def create_process(self, test_type, modelConfig, data, relatParas):
        if test_type == "rule":
            relatParas = list(model[3]["Para"].keys())
            return Process(target=RuleDetectTest, args=(modelConfig, data, relatParas, self.time_actual, self.interComponent))
        else:
            return Process(target=MLDetectTest, args=(modelConfig, data, relatParas, self.time_actual, self.interComponent))
        
    def step_process(self, data, time_=None):
        if time_ is None:
            self.time_actual += self.time_resample
        else:
            self.time_actual = time_
        workers_on = 0
        Workers = [None for _ in range(self.worker_num)]
        toDoList = self.toDoList[:]
        while True:
            if not toDoList and not workers_on:
                break
            elif not toDoList:
                time.sleep(1)
            for w in range(self.worker_num):
                if Workers[w] is None:
                    if toDoList:
                        test_type, modelConfig, relatParas = toDoList.pop(0)
                        Workers[w] = self.create_process(test_type, modelConfig, data, relatParas)
                        if Workers[w]:
                            print(f">> START[{w}] -{test_type}-{'&'.join(relatParas)}")
                            Workers[w].start()
                            workers_on += 1
                elif not Workers[w].is_alive():
                    if self.toDoList:
                        test_type, modelConfig, relatParas = toDoList.pop(0)
                        print(f">> END[{w}]")
                        Workers[w] = self.create_process(test_type, modelConfig, data, relatParas)
                        if Workers[w]:
                            print(f">> START[{w}] -{test_type}-{'/'.join(modelConfig)}-{'&'.join(relatParas)}")
                            Workers[w].start()
                        else:
                            workers_on -= 1
                            print(f">> END[{w}]")
                    else:
                        Workers[w].join()
                        Workers[w] = None
                        workers_on -= 1
                        print(f">> END[{w}]")
            time.sleep(0.1)
        self.multiGraph.refresh(self.interComponent.state)

    @property
    def state(self):
        return self.multiGraph.state

