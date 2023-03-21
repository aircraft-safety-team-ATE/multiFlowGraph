import math

_globalParas = "{{GlobalParas}}"
_eps = 0.001
_alias = {
        "and": "_and", 
        "or": "_or", 
        "xor": "_xor", 
        "not": "_not", 
        ">=": "_ge", 
        "<=": "_le", 
        ">": "_gt", 
        "<": "_lt", 
        "==": "_eq", 
        "!=": "_neq", 
        "+": "_plus", 
        "-": "_minus", 
        "*": "_mul", 
        "/": "_div", 
        "//": "_intdiv", 
        "%": "_mod", 
        "**": "_pow", 
        "&": "_bitand", 
        "|": "_bitor", 
        "^": "_bitxor", 
        "~": "_bitnot", 
        "[]": "_allcond", 
        "<>": "_anycond", 
        "{}": "_partialcond", 
        "int": "_int", 
        "log": "_log", 
        "exp": "_exp", 
        "abs": "_abs", 
        "sin": "_sin",
        "cos": "_cos",
        "tan": "_tan",
        "asin": "_asin",
        "acos": "_acos",
        "atan": "_atan",
        "atan2": "_atan2"
    }

def _prod(args):
    try:
        res = 1
        for arg in args:
            res *= arg
        return res
    except Exception as e:
        return float('nan')

def _mean(value_):
    if value_:
        return sum(value_)/len(value_)
    else:
        return float("nan")

def _getTimeByTime(value_, time_, actualTime, deltaTime, trigTime=None):
    if not time_:
        return float('nan')
    splitTime = actualTime - deltaTime
    idStart = 0; idEnd = len(time_) - 1
    startTime = time_[idStart]; endTime = time_[idEnd]
    if not trigTime is None and \
       (splitTime < trigTime or endTime < trigTime):
        return float('nan')
    if startTime > splitTime:
        return float("nan")
    elif endTime  <= splitTime:
        return time_[-1]
    while idStart + 5 < idEnd:
        idPredict = idStart + \
                    max(1, round((endTime-splitTime)/(endTime-startTime)*(idEnd - idStart)))
        if time_[idPredict] > splitTime:
            idEnd = idPredict
            endTime = time_[idEnd]
        else:
            idStart = idPredict
            startTime = time_[idStart]
    for idTime in reversed(range(idStart, idEnd)):
        if time_[idTime] <= splitTime:
            break
    if trigTime is None or time_[idTime] >= trigTime:
        return time_[idTime]
    else:
        return float('nan')

def _getValueByTime(value_, time_, actualTime, deltaTime, trigTime=None):
    if not time_:
        return float('nan')
    splitTime = actualTime - deltaTime
    idStart = 0; idEnd = len(time_) - 1
    startTime = time_[idStart]; endTime = time_[idEnd]
    if not trigTime is None and \
       (splitTime < trigTime or endTime < trigTime):
        return float('nan')
    if startTime > splitTime:
        return float("nan")
    elif endTime  <= splitTime:
        return value_[-1]
    while idStart + 5 < idEnd:
        idPredict = idStart + \
                    max(1, round((endTime-splitTime)/(endTime-startTime)*(idEnd - idStart)))
        if time_[idPredict] > splitTime:
            idEnd = idPredict
            endTime = time_[idEnd]
        else:
            idStart = idPredict
            startTime = time_[idStart]
    for idTime in reversed(range(idStart, idEnd)):
        if time_[idTime] <= splitTime:
            break
    if trigTime is None or time_[idTime] >= trigTime:
        return value_[idTime]
    else:
        return float('nan')

def _getRangeByTime(value_, time_, actualTime, deltaTime, trigTime=None):
    if not time_:
        return []
    splitTime = actualTime - deltaTime if trigTime is None else max(actualTime - deltaTime, trigTime)
    idStart = 0; idEnd = len(time_) - 1
    startTime = time_[idStart]; endTime = time_[idEnd]
    if splitTime > endTime:
        return []
    if startTime >= splitTime:
        return value_[:]
    while idStart + 5 < idEnd:
        idPredict = idStart + \
                    max(1, round((endTime-splitTime)/(endTime-startTime)*(idEnd - idStart)))
        if time_[idPredict] > splitTime:
            idEnd = idPredict
            endTime = time_[idEnd]
        else:
            idStart = idPredict
            startTime = time_[idStart]
    for idTime in range(idStart, idEnd):
        if time_[idTime] >= splitTime:
            break
        idTime += 1
    return value_[idTime:]

def _getTimeByFrame(value_, time_, deltaFrame, trigTime=None):
    if len(value_) < deltaFrame+1:
        return float("nan")
    elif trigTime is None or time_[-deltaFrame-1] >= trigTime:
        return time_[-deltaFrame-1]
    else:
        return float("nan")

def _getValueByFrame(value_, time_, deltaFrame, trigTime=None):
    if len(value_) < deltaFrame+1:
        return float("nan")
    elif trigTime is None or time_[-deltaFrame-1] >= trigTime:
        return value_[-deltaFrame-1]
    else:
        return float("nan")
    
def _getRangeByFrame(value_, time_, deltaFrame, trigTime=None):
    if trigTime is None:
        return value_[-deltaFrame-1:]
    for frame_, timeForFrame in enumerate(time_[-deltaFrame-1:]):
        if timeForFrame >= trigTime:
            break
        frame_ += 1
    return value_[-deltaFrame-1:][frame_:]

class FuncBase:
    ## and | or | xor | not
    @staticmethod
    def _and(data, args, trigTime=None):
        result = True; score = 1
        for _, arg in enumerate(args):
            try:
                res, sco = getResult(data, arg, trigTime=trigTime)
            except Exception as e:
                if result:
                    return None, 0
            if arg[0] == "Trigger":
                if res:
                    trigTime = data["Trigger"][f"{arg[0]}||{arg[2]}"]["trigTime"] + arg[1]
                    continue
                else:
                    return False, 0
            if res is None:
                if result:
                    result = None
                score = min(score, sco)
            elif not res:
                result = False
                score = min(score, sco)
        return result, score
        
    @staticmethod
    def _or(data, args, trigTime=None):
        result = False; score = 0
        for _, arg in enumerate(args):
            try:
                res, sco = getResult(data, arg, trigTime=trigTime)
            except Exception as e:
                result = None
                continue
            if res:
                return True, 1
            elif res is None:
                result = None
            score = max(score, sco)
        return result, score

    @staticmethod
    def _xor(data, args, trigTime=None):
        TrueCount = 0; score = 0
        for _, arg in enumerate(args):
            try:
                res, sco = getResult(data, arg, trigTime=trigTime)
            except Exception:
                return None, 0
            if res:
                TrueCount += 1
            elif res in None: # 存在1个None，异或便无法运算
                return None, 0
            else:
                score = max(score, sco)
        if TrueCount%2: # True个数为偶数<=>结果为False
            return False, score
        else:
            return True, 1

    @staticmethod
    def _not(data, args, trigTime=None): ## score = 0 / 1
        try:
            res, sco = getResult(data, args[0], trigTime=trigTime)
        except Exception as e:
            return None, 0
        if res is None:
            return None, 1 - max(sco, _eps)
        elif res:
            return False, 0
        else:
            return True, 1

    ## >= | <= | > | < | == | !=
    @staticmethod
    def _ge(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
        except Exception as e:
            return None, 0
        if math.isnan(res1) or math.isnan(res2):
            return None, 0
        elif res1 >= res2:
            return True, 1
        else: ## (b-a)/2max(|a|,|b|)
            return False, 1 - max((res2 - res1)/2/max(abs(res1), abs(res2)), _eps)

    @staticmethod
    def _le(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
        except Exception as e:
            return None, 0
        if math.isnan(res1) or math.isnan(res2):
            return None, 0
        elif res1 <= res2:
            return True, 1
        else: ## (a-b)/2max(|a|,|b|)
            return False, 1 - max((res1 - res2)/2/max(abs(res1), abs(res2)), _eps)

    @staticmethod
    def _gt(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
        except Exception as e:
            return None, 0
        if math.isnan(res1) or math.isnan(res2):
            return None, 0
        elif res1 > res2:
            return True, 1
        else: ## (b-a)/2(max(|a|,|b|) + _eps)  ``+_eps to avoid |a|=|b|=0``
            return False, 1 - max((res2 - res1)/2/(max(abs(res1), abs(res2))+_eps), _eps)

    @staticmethod
    def _lt(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
        except Exception as e:
            return None, 0
        if math.isnan(res1) or math.isnan(res2):
            return None, 0
        elif res1 < res2:
            return True, 1
        else: ## (a-b)/2(max(|a|,|b|) +_eps)  ``+_eps to avoid |a|=|b|=0``
            return False, 1 - max((res1 - res2)/2/(max(abs(res1), abs(res2))+_eps), _eps)

    @staticmethod
    def _eq(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
        except Exception as e:
            return None, 0
        if math.isnan(res1) or math.isnan(res2):
            return None, 0
        elif res1 == res2:
            return True, 1
        else:  ## |a-b|/2max(|a|,|b|)
            return False, 1 - max(abs(res1 - res2)/2/max(abs(res1), abs(res2)), _eps)

    @staticmethod
    def _neq(data, args, trigTime=None): ## score = 0 / 1
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
        except Exception as e:
            return None, 0
        if math.isnan(res1) or math.isnan(res2):
            return None, 0
        elif res1 != res2:
            return True, 1
        else:
            return False, 0

    ## + | - | * | / | // | % | ** | & | | | ^ | ~
    @staticmethod
    def _plus(data, args, trigTime=None):
        try:
            return sum(map(lambda arg: getResult(data, arg, \
                                                 trigTime=trigTime)[0], args)), 0
        except Exception as e:
            return float('nan'), 0
        
    @staticmethod
    def _minus(data, args, trigTime=None):
        try:
            return getResult(data, args[0])[0] - \
                   sum(map(lambda arg: getResult(data, arg, \
                                                 trigTime=trigTime)[0], args[1:])), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _mul(data, args, trigTime=None):
        try:
            return _prod(map(lambda arg: getResult(data, arg, \
                                                   trigTime=trigTime)[0], args)), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _div(data, args, trigTime=None):
        try:
            return getResult(data, args[0])[0] / \
                   _prod(map(lambda arg: getResult(data, arg, \
                                                   trigTime=trigTime)[0], args[1:])), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _intdiv(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
            return res1 // res2, 0
        except Exception as e:
            return float('nan'), 0
            
    @staticmethod
    def _mod(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
            return res1 % res2, 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _pow(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
            return res1 ** res2, 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _bitand(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
            return int(res1) & int(res2), 0
        except Exception as e:
            return float('nan'), 0
            
    @staticmethod
    def _bitor(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
            return int(res1) | int(res2), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _bitxor(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
            return int(res1) ^ int(res2), 0
        except Exception as e:
            return float('nan'), 0
            
    @staticmethod
    def _bitnot(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return ~int(res1), 0
        except Exception as e:
            return float('nan'), 0

    ## int | log | exp
    @staticmethod
    def _int(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return int(res1, base=int(args[1])), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _log(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.log(res1), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _exp(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.exp(res1), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _abs(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.abs(res1), 0
        except Exception as e:
            return float('nan'), 0
    
    @staticmethod
    def _sin(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.sin(res1), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _cos(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.cos(res1), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _tan(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.tan(res1), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _asin(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.asin(res1), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _acos(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.acos(res1), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _atan(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            return math.atan(res1), 0
        except Exception as e:
            return float('nan'), 0

    @staticmethod
    def _atan2(data, args, trigTime=None):
        try:
            res1, _ = getResult(data, args[0], trigTime=trigTime)
            res2, _ = getResult(data, args[1], trigTime=trigTime)
            return math.atan2(res1, res2), 0
        except Exception as e:
            return float('nan'), 0
    
    ## [] | <> | {}
    @staticmethod
    def _allcond(data, args, trigTime=None):
        try:
            allCondName, t = args
            lastFalseTime = data["[]"][allCondName]["lastFalseTime"]
            lastTime = data["[]"][allCondName]["lastTime"]
            if  (not trigTime is None and lastTime < trigTime) or \
               data["actualTime"] - lastTime > t:
                return None, 0
            elif lastFalseTime is None or data["actualTime"] - lastFalseTime > t:
                return True, 1
            else:
                return False, min((data["actualTime"] - lastFalseTime)/t, 1-_eps)
        except Exception as e:
            return None, 0

    @staticmethod
    def _anycond(data, args, trigTime=None):
        try:
            anyCondName, t = args
            lastTrueTime = data["<>"][anyCondName]["lastTrueTime"]
            lastTime = data["<>"][anyCondName]["lastTime"]
            if (not trigTime is None and lastTime < trigTime) or \
               data["actualTime"] - lastTime > t:
                return None, 0
            elif data["actualTime"] - lastTrueTime < t:
                return True, 1
            else:
                return False, min(t/(data["actualTime"] - lastTrueTime), 1-_eps)
        except Exception as e:
            return None, 0
 
    @staticmethod
    def _partialcond(data, args, trigTime=None):
        try:
            partialCondName, m, n = args
            value_ = data["{}"][partialCondName]["value"][-m:]
            score_ = data["{}"][partialCondName]["score"][-m:]
            time_ = data["{}"][partialCondName]["time"][-m:]
            startId = 0
            if not trigTime is None:
                for t_ in time_:
                    if t_ < trigTime:
                        startId += 1
                    else:
                        break
            value_ = value_[startId:]
            if len(value_) < n:
                return False, 0
            else:
                trueCount = sum(value_)
                if trueCount >= n:
                    return True, 1
                else:
                    return False, sorted(score_[startId:])[-m]
        except Exception as e:
            return None, 0

    @staticmethod
    def Para(data, args, trigTime=None):
        try:
            paraData = data["Para"][args[0]]
            if args[2]: ## istime = 1 => Time Mode
                return _getValueByTime(paraData["value"], paraData["time"], \
                                      data["actualTime"], args[1], trigTime=trigTime), 0
            else: ## istime = 0 => Frame Mode
                return _getValueByFrame(paraData["value"], paraData["time"], \
                                       args[1], trigTime=trigTime), 0
        except Exception as e:
            return float("nan"), 0

    @staticmethod
    def Time(data, args, trigTime=None):
        try:
            if args[0] == _globalParas:
                return data["actualTime"]
            paraData = data["Para"][args[0]]
            if args[2]: ## istime = 1 => Time Mode
                return _getTimeByTime(paraData["value"], paraData["time"], \
                                      data["actualTime"], args[1], trigTime=trigTime), 0
            else: ## istime = 0 => Frame Mode
                return _getTimeByFrame(paraData["value"], paraData["time"], \
                                       args[1], trigTime=trigTime), 0
        except Exception as e:
            return float("nan"), 0

    @staticmethod
    def Max(data, args, trigTime=None):
        try:
            paraData = data["MMM"][args[0]]
            if args[2]: ## istime = 1 => Time Mode
                return max(_getRangeByTime(paraData["value"], paraData["time"], \
                                          data["actualTime"], args[1], trigTime=trigTime)), 0
            else: ## istime = 0 => Frame Mode
                return max(_getRangeByFrame(paraData["value"], paraData["time"], \
                                           args[1], trigTime=trigTime)), 0
        except Exception as e:
            return float("nan"), 0

    @staticmethod
    def Min(data, args, trigTime=None):
        try:
            paraData = data["MMM"][args[0]]
            if args[2]: ## istime = 1 => Time Mode
                return min(_getRangeByTime(paraData["value"], paraData["time"], \
                                          data["actualTime"], args[1], trigTime=trigTime)), 0
            else: ## istime = 0 => Frame Mode
                return min(_getRangeByFrame(paraData["value"], paraData["time"], \
                                           args[1], trigTime=trigTime)), 0
        except Exception as e:
            return float("nan"), 0

    @staticmethod
    def Mean(data, args, trigTime=None):
        try:
            paraData = data["MMM"][args[0]]
            if args[2]: ## istime = 1 => Time Mode
                return _mean(_getRangeByTime(paraData["value"], paraData["time"], \
                                          data["actualTime"], args[1], trigTime=trigTime)), 0
            else: ## istime = 0 => Frame Mode
                return _mean(_getRangeByFrame(paraData["value"], paraData["time"], \
                                           args[1], trigTime=trigTime)), 0
        except Exception as e:
            return float("nan"), 0

    @staticmethod
    def Increase(data, args, trigTime=None):
        try:
            creaseData = data["Crease"][args[0]]
            if args[2]: ## istime = 1 => Time Mode
                splitTime = data["actualTime"] - args[1] if trigTime is None \
                        else max(data["actualTime"] - args[1], trigTime)
                if len(creaseData["time"]) < 2 or creaseData["time"][-2] <= splitTime:
                    return None, 0
                elif creaseData["lastDecTime"] is None or creaseData["lastDecTime"] <= splitTime:
                    return True, 1
                else:
                    return False, (data["actualTime"] - creaseData["lastDecTime"])/args[1]
            else: ## istime = 0 => Frame Mode
                if trigTime is None:
                    value_ = data["value"][-args[1]+1:]
                    trueCount = sum([1 if v is None or v else 0 for v in value_]); allCount = len(value_)
                    if allCount:
                        return trueCount == allCount, trueCount/allCount
                    else:
                        return None, 0
                else:
                    for frame_, timeForFrame in enumerate(data["time"][-args[1]+1:]):
                        if timeForFrame >= trigTime:
                            break
                        frame_ += 1
                    trueCount = sum([1 if v is None or v else 0 for v in value_]); allCount = len(value_)
                    if allCount:
                        return trueCount == allCount, trueCount/allCount
                    else:
                        return None, 0
        except Exception as e:
            return None, 0

    @staticmethod
    def Decrease(data, args, trigTime=None):
        try:
            creaseData = data["Crease"][args[0]]
            if args[2]: ## istime = 1 => Time Mode
                splitTime = data["actualTime"] - args[1] if trigTime is None \
                        else max(data["actualTime"] - args[1], trigTime)
                if len(creaseData["time"]) < 2 or creaseData["time"][-2] <= splitTime:
                    return None, 0
                elif creaseData["lastIncTime"] is None or creaseData["lastIncTime"] <= splitTime:
                    return True, 1
                else:
                    return False, (data["actualTime"] - creaseData["lastIncTime"])/args[1]
            else: ## istime = 0 => Frame Mode
                if trigTime is None:
                    value_ = data["value"][-args[1]+1:]
                    trueCount = sum([1 if not v else 0 for v in value_]); allCount = len(value_)
                    if allCount:
                        return trueCount == allCount, trueCount/allCount
                    else:
                        return None, 0
                else:
                    for frame_, timeForFrame in enumerate(data["time"][-args[1]+1:]):
                        if timeForFrame >= trigTime:
                            break
                        frame_ += 1
                    trueCount = sum([1 if not v else 0 for v in value_]); allCount = len(value_)
                    if allCount:
                        return trueCount == allCount, trueCount/allCount
                    else:
                        return None, 0
        except Exception as e:
            return None, 0

    @staticmethod
    def PreCond(data, args, trigTime=None):
        try:
            if (trigTime is None or data["PreCond"][args[0]]["validedTime"] > trigTime) and \
               data["actualTime"] > data["PreCond"][args[0]]["validedTime"] + args[1]:
                res, sco = getResult(data, args[2])
                return res, sco/2 + 0.5
            else:
                return False, 0.5 * (data["actualTime"] - data["PreCond"][args[0]]["validedTime"])/args[1]
        except Exception as e:
            return None, 0

    @staticmethod
    def Trigger(data, args, trigTime=None):
        try:
            trigTime_ = data["Trigger"][f"{args[0]}||{args[2]}"]["trigTime"]
            if trigTime_ == -1:
                return False, 0
            elif trigTime is None or trigTime < trigTime_:
                if trigTime_ + args[1] <= data["actualTime"]:
                    return True, 1
                else:
                    return False, ( data["actualTime"] - trigTime_) / args[1]
            else:
                return None, 0
        except Exception as e:
            return None, 0

    @staticmethod
    def Fault(data, args, trigTime=None):
        try:
            faultInfo = data["Fault"][f"{args[0]},{args[1]}"]
            if trigTime is None or trigTime < faultInfo["time"]:
                return faultInfo["state"], faultInfo["score"]
            else:
                return None, 0
        except Exception as e:
            return None, 0

def getResult(data, args, trigTime=None):
    if isinstance(args, list):
        funcname_ = _alias.get(args[0]) or args[0]
        func_ = getattr(FuncBase, funcname_)
        return func_(data, args[1:], trigTime=trigTime)
    else:
        return args, 0 if args != True else 1

if __name__ == "__main__":
    value_ = list(range(1,11))
    time_ = [1000+i*0.2 for i in range(1,11)]
    print({k:v for k,v in zip(time_, value_)})
    print(_getTimeByTime(value_, time_, 1002, 0.5, trigTime=None))#1001.5))
    print(_getTimeByFrame(value_, time_, 5, trigTime=None))#1001.5))
    print(_getValueByTime(value_, time_, 1002, 0.5, trigTime=None))#1001.5))
    print(_getValueByFrame(value_, time_, 5, trigTime=None))#1001.5))
    print(_getRangeByTime(value_, time_, 1002, 0.6, trigTime=None))#1001.5))
    print(_getRangeByFrame(value_, time_, 5, trigTime=None))#1001.5))
