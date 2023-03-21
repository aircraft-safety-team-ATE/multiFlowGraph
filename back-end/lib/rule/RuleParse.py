import re

try:
    from .RuleFormat import FUNC_TIME, FUNC_FORMAT
except:
    from RuleFormat import FUNC_TIME, FUNC_FORMAT

class ruleParse:
    def __init__(self, pnames=[], fnames=[], videArgSymb=["_", "\\", "#"]):
        self.funcDict = FUNC_FORMAT
        self.videArgSymb = videArgSymb
        self.pnames = pnames
        self.fnames = fnames

    def convert(self, rule):
        self.raw_rule = rule # Class to be a class
        
        self.seqs = {func_name: {} for func_name in FUNC_TIME}
        self.seqOrder = []
        self.relatPara = {}
        self.relatFault = set()
        self.log = []
        self.warning = 0
        self.error = 0
        
        rule = rule.replace("\'","\"").replace("\\\"","\'")
        rule_useful = "".join(rule.replace("!=","").split("\"")[::2])
        if "&&" in rule_useful or "||" in rule_useful or "!" in rule_useful:
            self.log.append(f"|[Warning]| [{rule}]请勿适用&&、||、!等逻辑运算符写法")
            self.warning += 1
            rule = rule.replace("&&", " and ").replace("||", " or ").replace("!=", "~=").replace("!", " not ").replace("~=", "!=")
        result, typ = self._func_convert(rule)
        if typ not in ["Unknown", "bool"]:
            self.log.append(f"|[Error]| [{rule}]必须为布尔值")
            self.error += 1
        self.rule = result # Class to be a class
        return result

    def _func_convert(self, rule, seqs_=[]):
        seqs = seqs_.copy()
        rule_ = rule = re.sub(r" +", " ", rule)
        rule_split = list(re.finditer(r"\[[0-9\.,\+\-\*/\%\&\|\~\^]+\]|<[0-9\.,\+\-\*/\%\&\|\~\^]+>|{[0-9\.,\+\-\*/\%\&\|\~\^]+}|[Α-Ωα-ωa-zA-Z][Α-Ωα-ωa-zA-Z0-9_]*\(", rule))
        for r_split in reversed(rule_split):
            a, b = r_split.span()
            if rule[a:b-1] in ["and", "or", "xor", "not"]:
                continue
            if rule[a] in ["[", "<", "{"]: # Type1 - "[time]", "<time>", "{frame_all,frame_threshold}"
                ### Case like "1<3>2" should be avoided
                # in fact, <n> should be applied in and only in the following case:
                #  1 - "[ ]<n>xxx";   2 - "xxx,[ ]<n>xxx";      3 - "xxx([ ]<n>xxx"
                #  4 - "xxx and|or|xor|not <n>xxx";        5 - "xxx)and|or|xor <n>xxx"
                #  6 - "xxx(not <n>xxx"         P.S. [ ] represent a space could be negligated
                if rule[a] == "<" and a != 0:
                    rule_pre = rule[:a-1] if rule[a-1] == " " else rule[:a]
                    if not(rule_pre) and \
                       not(rule_pre[-1] in ["(", ","] or \
                           rule_pre.split(" ")[-1].split(")")[-1].split("(")[-1] in ["and", "or", "xor", "not"]):
                        continue
                ### Focus on "[time]", "<time>", "{frame_all,frame_threshold}"
                condition = rule[a+1:b-1].replace(" ","").split(",")
                if rule[a] == "{":
                    if len(condition) > 2:
                        self.log.append(f"|[Warning]| [{self._backlog(rule[a:b], seqs)}]输入过多")
                        self.warning += 1
                    elif len(condition) < 2:
                        self.log.append(f"|[Error]| [{self._backlog(rule[a:b], seqs)}]输入过少")
                        self.error += 1
                    try:
                        secondframe1 = int(float(condition[0]))
                        if "." in condition[0]:
                            self.log.append(f"|[Warning]| [{self._backlog(rule[a:b], seqs)}]输入1必须为整数")
                            self.warning += 1
                    except Exception as e:
                        try:
                            secondframe1 = int(eval(condition[0]))
                            self.log.append(f"|[Warning]| [{self._backlog(rule[a:b], seqs)}]输入1不能为表达式")
                            self.warning += 1
                        except  Exception as e:
                            self.log.append(f"|[Error]| [{self._backlog(rule[a:b], seqs)}]输入1格式有误")
                            self.error += 1
                            secondframe1 = None
                    try:
                        secondframe2 = int(float(condition[1]))
                        if "." in condition[1]:
                            self.log.append(f"|[Warning]| [{self._backlog(rule[a:b], seqs)}]输入2必须为整数")
                            self.warning += 1
                    except Exception as e:
                        try:
                            secondframe2 = int(eval(condition[0]))
                            self.log.append(f"|[Warning]| [{self._backlog(rule[a:b], seqs)}]输入1不能为表达式")
                            self.warning += 1
                        except  Exception as e:
                            self.log.append(f"|[Error]| [{self._backlog(rule[a:b], seqs)}]输入1格式有误")
                            self.error += 1
                            secondframe2 = None
                    if (not secondframe1 is None) and (not secondframe2 is None) and secondframe1 < secondframe2:
                        secondframe1, secondframe2 = secondframe2, secondframe1
                        self.log.append(f"|[Warining]| [{self._backlog(rule[a:b], seqs)}]输入1必须不小于输入2")
                        self.warining += 1
                else:
                    if len(condition) > 1:
                        self.log.append(f"|[Warning]| [{self._backlog(rule[a:b], seqs)}]输入过多")
                        self.warning += 1
                    elif len(condition) < 1:
                        self.log.append(f"|[Error]| [{self._backlog(rule[a:b], seqs)}]输入过少")
                        self.error += 1
                    try:
                        secondframe1 = float(condition[0])
                    except Exception as e:
                        try:
                            secondframe1 = float(eval(condition[0]))
                            self.log.append(f"|[Warning]| [{self._backlog(rule[a:b], seqs)}]输入不能为表达式")
                            self.warning += 1
                        except  Exception as e:
                            self.log.append(f"|[Error]| [{self._backlog(rule[a:b], seqs)}]输入格式有误")
                            self.error += 1
                            secondframe1 = None

                ### Focus on Expression after "[time]", "<time>", "{frame_all,frame_threshold}"
                if rule[b] != "(":
                    warned = True
                else:
                    warned = False
                left = 0
                for i in range(b, len(rule)-1):
                    if left == 0:
                        ## Since unable to know whether user use () to pack expression, expend the translation to case without ()
                        # Case [n](A+B)*C is unpacked even if "(" follows "]"
                        # Only Cases 1 - "[n]xxxx)"; 2 - "[n]xxx,"; 3 - "[n]xxx and|or|xor|not "; 4 - "[n]xxx and|or|xor|not(" could correspond []'s logic.
                        # where, () should be complet in substring xxx
                        if rule[i] in [")", ","] or \
                           (rule[i] == " " and (not(rule[i+1:]) or rule[i+1:].split("(")[0].split(" ")[0] in ["and", "or", "xor", "not"])):
                            break
                        elif i != b:
                            warned = True
                    if rule[i] == "(":
                        left += 1
                    elif rule[i] == ")":
                        left -= 1
                if left > 0:
                    i = len(rule)
                    if rule[len(rule)-1] == ")":
                        left -= 1
                rule_origin = self._backlog(rule[a:i], seqs)
                if warned:
                    self.log.append(f"|[Warning]| [{rule_origin}]表达式需用\"()\"包裹")
                    self.warning += 1
                if left > 0: # lack some ), which means meanwhile i reaches end
                    self.log.append(f"|[Warning]| [{rule_origin}]缺少{left}个\")\"")
                    self.warning += 1
                express = rule[b:i] + ")"*left
                result, typ = self._stringconvert(express, seqs)
                if typ not in ["Unknown", "bool"]:
                    self.log.append(f"|[Error]| [{rule_origin}]输出应为布尔值")
                    self.error += 1
                
                ### Translate expression
                express_origin = self._backlog(express, seqs)
                if rule[a] == "[":
                    seqs.append((["[]", express_origin, secondframe1], "bool", rule_origin))
                    if express_origin in self.seqs["[]"].keys():
                        self.seqs["[]"][express_origin] = (self.seqs["[]"][express_origin][0], \
                                                           [max(self.seqs["[]"][express_origin][1], \
                                                                secondframe1 if not secondframe1 is None else 0)])
                    else:
                        self.seqs["[]"][express_origin] = (result, \
                                                           [secondframe1 if not secondframe1 is None else 0])
                        self.seqOrder.append(("[]", express_origin))
                elif rule[a] == "<":
                    seqs.append((["<>", express_origin, secondframe1], "bool", rule_origin))
                    if express_origin in self.seqs["<>"].keys():
                        self.seqs["<>"][express_origin] = (self.seqs["<>"][express_origin][0], \
                                                           [max(self.seqs["<>"][express_origin][1], \
                                                                secondframe1 if not secondframe1 is None else 0)])
                    else:
                        self.seqs["<>"][express_origin] = (result, \
                                                           [secondframe1 if not secondframe1 is None else 0])
                        self.seqOrder.append(("<>", express_origin))
                else:
                    seqs.append((["{}", express_origin, secondframe1, secondframe2], "bool", rule_origin))
                    if express_origin in self.seqs["{}"].keys():
                        self.seqs["{}"][express_origin] = (self.seqs["{}"][express_origin][0], \
                                                           [max(self.seqs["{}"][express_origin][1], \
                                                                secondframe1 if not secondframe1 is None else 0)])
                    else:
                        self.seqs["{}"][express_origin] = (result, \
                                                           [secondframe1 if not secondframe1 is None else 0])
                        self.seqOrder.append(("{}", express_origin))
                rule = f"{rule[:a]} 00seqs_{len(seqs)-1}_ {rule[i:]}"

            else: # Type2 - Special Functions "funcName("
                ## Focus on Function Name
                func_name = rule[a:b-1]
                
                ### Focus on Expression (In this case, expression must be packed by "()")
                left = 1
                for i in range(b, len(rule)):
                    if left == 0:
                        break
                    if rule[i] == "(":
                        left += 1
                    elif rule[i] == ")":
                        left -= 1
                        if left == 0 and i == len(rule) - 1:
                            i += 1
                            break
                if left > 0:
                    i = len(rule) + 1
                rule_origin = self._backlog(rule[a:i], seqs)
                
                if left > 0:
                    self.log.append(f"|[Warning]| [{rule_origin}]缺少{left-1}个\")\"")
                    self.warning += 1
                    args = (rule[b:]+")"*(left-1)).split(",")
                else:
                    args = rule[b:i-1].split(",")
                    
                ## Translate Expression
                if func_name in self.funcDict.keys():
                    args_need, func_out, multinput = self.funcDict[func_name]
                    result, seq, timeCount, express_origin, express_res = self._convert_args(args, args_need, multinput, rule_origin, seqs, func_name)
                    if result is None:
                        seqs.append(([func_name, None], "Unknown", rule_origin))
                        if func_name in self.seqs.keys():
                            if express_origin in self.seqs[func_name].keys():
                                self.seqs[func_name][express_origin] = (self.seqs[func_name][express_origin][0], \
                                                                        self._refresh_time_count(self.seqs[func_name][rule_origin][1], timeCount))
                            else:
                                self.seqs[func_name][express_origin] = (None, timeCount)
                                self.seqOrder.append((func_name, express_origin))
                    else:
                        seqs.append(([func_name]+result, func_out, rule_origin))
                        if func_name in self.seqs.keys():
                            if express_origin in self.seqs[func_name].keys():
                                self.seqs[func_name][express_origin] = (self.seqs[func_name][express_origin][0], \
                                                                        self._refresh_time_count(self.seqs[func_name][rule_origin][1], timeCount))
                            else:
                                self.seqs[func_name][express_origin] = (express_res, timeCount)
                                self.seqOrder.append((func_name, express_origin))
                elif func_name in self.pnames:
                    args_need, func_out, multinput = self.funcDict["Para"]
                    result , seqs, timeCount,_,_ = self._convert_args([func_name]+args, args_need, multinput, rule_origin, seqs, "Para")
                    if result is None:
                        seqs.append(([func_name, None], "Unknown", rule_origin))
                    else:
                        seqs.append(([func_name]+result, func_out, rule_origin))
                else:
                    self.log.append(f"|[Error]| {rule_origin}函词{func_name}未定义")
                    self.error += 1
                    if args[0].replace(" ",""):
                        seqs.append(([func_name]+[self._stringconvert(arg, seqs)[0] for arg in args], "Unknown", rule_origin))
                    else:
                        seqs.append(([func_name], "Unknown", rule_origin))
                rule = f"{rule[:a]} 00seqs_{len(seqs)-1}_ {rule[i:]}"

        if not rule.replace(" ",""):
            return None, "Unknown"
        if "[" in rule or "{" in rule or "]" in rule or "}" in rule:
            self.log.append(f"|[Warning]| {rule_} 中存在非函词的特殊括号")
            self.warning += 1
        rule = self._complete(rule.replace("[", "(").replace("]", ")").replace("{", "(").replace("}", ")"), seqs)
        result, typ = self._stringconvert(rule, seqs)
        return result, typ

    def _refresh_time_count(self, timeCount_, timeCount):
        timeCount_post = []
        for timeC_, timeC in zip(timeCount_, timeCount):
            if isinstance(timeC_, list):
                timeCount_post.append([max(timeC_[0], timeC[0]),max(timeC_[1], timeC[1])])
            else:
                timeCount_post.append(max(timeC_, timeC))
        return timeCount_post
    
    def _convert_args(self, args, args_need, multinput, rule_origin, seqs_, func_name):
        seqs = seqs_.copy()
        if len(args) > len(args_need):
            if not multinput:
                self.log.append(f"|[Warning]| [{rule_origin}]输入过多")
                self.warning += 1
            else:
                args_need.extend([args_need[-1]]*(len(args) - len(args_need))) 
        args_ = [None]*len(args_need); isCond = True
        timeCount = []; express_origin = ""; express_res = []
        time_frame = "frame" ## [istime] could switch two-state type [time|frame]
        for func_pos, typin, typwant, arg_default in args_need:
            if func_pos >= len(args):
                if arg_default is None:
                    self.log.append(f"|[Error]| [{rule_origin}]缺少输入{func_pos}")
                    self.error += 1
                elif arg_default != "NoneType":
                    args_[func_pos] = arg_default
                    if typwant == "istime":
                        time_frame = "time" if args_[func_pos] else "frame"
                    if typwant == "time|frame":
                        doubleType = True
            elif typin == "rule": ## rule[xxx]
                args[func_pos] = re.sub(r" +", " ", args[func_pos])
                if args[func_pos][:1] == " ":
                    args[func_pos] = args[func_pos][1:]
                if args[func_pos][-1:] == " ":
                    args[func_pos] = args[func_pos][:-1]
                if args[func_pos][:1] == "\"":
                    args[func_pos] = args[func_pos][1:]
                if args[func_pos][-1:] == "\"":
                    args[func_pos] = args[func_pos][:-1]
                if not args[func_pos].replace(" ","") or args[func_pos].replace(" ","") in self.videArgSymb:
                    if arg_default is None:
                        self.log.append(f"|[Error]| [{rule_origin}]缺少输入{func_pos}")
                        self.error += 1
                    elif arg_default != "NoneType":
                        args_[func_pos] = arg_default
                else:
                    result, typreal = self._stringconvert(args[func_pos], seqs)
                    arg = self._backlog(args[func_pos], seqs)
                    if typreal not in ["Unknown", typwant]:
                        self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}为{typreal}类型(应为{typwant}类型)")
                        self.error += 1
                    else:
                        if func_name in self.seqs.keys() and (isCond or func_name == "Trigger"):
                            args_[func_pos] = arg
                        else:
                            args_[func_pos] = result
                if func_name in self.seqs.keys() and (isCond or func_name == "Trigger"):
                    express_origin  += f"||{self._backlog(args[func_pos], seqs)}"
                    express_res.append(result if isinstance(result, list) else [result])
                    isCond = False
            else: ## xxx
                if not args[func_pos].replace(" ","")  or args[func_pos].replace(" ","") in self.videArgSymb:
                    if arg_default is None:
                        self.log.append(f"|[Error]| [{rule_origin}]缺少输入{func_pos}")
                        self.error += 1
                    elif arg_default != "NoneType":
                        args_[func_pos] = arg_default
                        if typwant == "istime":
                            time_frame = "time" if args_[func_pos] else "frame"
                    continue
                if typwant == "time|frame":
                    typwant = time_frame
                    doubleType = True
                else:
                    doubleType = False
                if typwant == "istime":
                    try:
                        istime = int(args[func_pos])
                        if istime not in [0, 1]:
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}(istime类型)必须为0/1")
                            self.warning += 1
                        time_frame = "time" if istime else "frame"
                        args_[func_pos] = 1 if istime else 0
                    except Exception as e:
                        self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}(istime类型)必须为0/1")
                        self.error += 1
                elif typwant == "time":
                    try:
                        arg_ = float(args[func_pos].replace(" ",""))
                        if arg_ < 0:
                            self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}应大于0")
                            self.error += 1
                        else:
                            args_[func_pos] = arg_
                    except Exception as e:
                        try:
                            arg_ = float(eval(args[func_pos]))
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}不应为表达式")
                            self.warning += 1
                            if arg_ < 0:
                                self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}应大于0")
                                self.error += 1
                            else:
                                args_[func_pos] = arg_
                        except Exception as e:
                            self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}无法解析")
                            self.error += 1
                    if doubleType:
                        timeCount.append([0, args_[func_pos] if not args_[func_pos] is None else 0])
                    else:
                        timeCount.append(args_[func_pos] if not args_[func_pos] is None else 0)
                elif typwant == "frame":
                    try:
                        arg_ = float(args[func_pos])
                        if arg_ != int(arg_):
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}应为整数")
                            self.warning += 1
                        if arg_ < 0:
                            self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}应大于0")
                            self.error += 1
                        else:
                            args_[func_pos] = int(arg_)
                    except Exception as e:
                        try:
                            arg_ = int(eval(args[func_pos]))
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}不应为表达式")
                            self.warning += 1
                            if arg_ < 0:
                                self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}应大于0")
                                self.error += 1
                            else:
                                args_[func_pos] = arg_
                        except Exception as e:
                            if not arg_default is None:
                                args_[func_pos] = arg_default
                                self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}无法解析")
                                self.warning += 1
                            else:
                                self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}无法解析")
                                self.error += 1
                    if doubleType:
                        timeCount.append([args_[func_pos] if not args_[func_pos] is None else 0, 0])
                    else:
                        timeCount.append(args_[func_pos] if not args_[func_pos] is None else 0)
                elif typwant == "num":
                    arg_ = args[func_pos].replace(" ","")
                    if arg_[0] == "0" and len(arg_)>1:
                        if arg_[1] == "x":
                            try:
                                args_[func_pos] = int(arg_,base=16)
                            except Exception as e:
                                self.log.append(f"|[Error]| {arg_}不可解析")
                                self.error += 1
                            continue
                        elif arg_[1]== "b":
                            try:
                                args_[func_pos] = int(arg_,base=2)
                            except Exception as e:
                                self.log.append(f"|[Error]| {arg_}不可解析")
                                self.error += 1
                            continue
                        elif arg_[1] == "o":
                            try:
                                args_[func_pos] = int(arg_,base=8)
                            except Exception as e:
                                self.log.append(f"|[Error]| {arg_}不可解析")
                                self.error += 1
                            continue
                    try:
                        args_[func_pos] = float(args[func_pos].replace(" ",""))
                    except Exception as e:
                        try:
                            args_[func_pos] = float(eval(args[func_pos]))
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}不应为表达式")
                            self.warning += 1
                        except Exception as e:
                            if not arg_default is None:
                                args_[func_pos] = arg_default
                                self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}无法解析")
                                self.warning += 1
                            else:
                                self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}无法解析")
                                self.error += 1
                elif typwant == "bool":
                    if args[func_pos].lower() == "true":
                        args_[func_pos] = True
                    elif args[func_pos].lower() == "false":
                        args_[func_pos] = False
                    elif args[func_pos].lower() not in ["none", "null"]:
                        if not arg_default is None:
                            args_[func_pos] = arg_default
                        if not arg_default is None:
                            args_[func_pos] = arg_default
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}无法解析")
                            self.warning += 1
                        else:
                            self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}无法解析")
                            self.error += 1
                elif typwant == "pname":
                    arg_ = args[func_pos].replace(" ","").replace("\"","")
                    if arg_ not in self.pnames:
                        if not arg_default is None:
                            args_[func_pos] = arg_default
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}参数名[{arg_}]无法解析")
                            self.warning += 1
                        else:
                            args_[func_pos] = arg_
                            self.log.append(f"|[Error]| [{rule_origin}]输入{func_pos}参数名[{arg_}]无法解析")
                            self.error += 1
                    else:
                        if func_name == "Para":
                            args_[func_pos] = arg_
                        else:
                            args_[func_pos] = ["Para", arg_, 0, 0]
                elif typwant == "fname":
                    arg_ = args[func_pos].replace(" ","").replace("\"","")
                    if arg_ not in self.fnames and func_name != "Fault":
                        if not arg_default is None:
                            args_[func_pos] = arg_default
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}故障名[{arg_}]无法解析")
                            self.warning += 1
                        else:
                            args_[func_pos] = arg_
                            self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}故障名[{arg_}]无法解析")
                            self.warning += 1
                    else:
                        args_[func_pos] = arg_
                else:
                    args_[func_pos] = arg_default
        if func_name == "Para":
            if args_[2]:
                if arg_ in self.relatPara.keys() and not args_[1] is None:
                    self.relatPara[args_[0]] = [self.relatPara[args_[0]][0], \
                                                max(args_[1], self.relatPara[args_[0]][1])]
                else:
                    self.relatPara[args_[0]] = [0, 0 if args_[1] is None else args_[1]]
            else:
                if arg_ in self.relatPara.keys() and not args_[1] is None:
                    self.relatPara[args_[0]] = [max(args_[1], self.relatPara[args_[0]][0]), \
                                                self.relatPara[args_[0]][1]]
                else:
                    self.relatPara[args_[0]] = [0 if args_[1] is None else args_[1], 0]
        elif func_name == "Fault":
            if f"{arg_[0]},{arg_[1]}" not in self.fnames:
                self.log.append(f"|[Warning]| [{rule_origin}]输入{func_pos}故障名[{arg_}]无法解析")
                self.warning += 1
            self.relatFault.add(f"{args_[0]},{1 if args_[1] is None else args_[1]}")
            
        return args_, seqs, timeCount, express_origin[2:], express_res

    ## 补全括号
    def _complete(self, rule, seqs_):
        seqs = seqs_.copy()
        left = 0; l = 0; cons = True
        if "(" in rule or ")" in rule:
            for i in range(len(rule)):
                if rule[i + l] == "\"":
                    cons = not cons
                if not cons:
                    continue
                if rule[i + l] == "(":
                    left += 1
                elif rule[i + l] == ")":
                    left -= 1
            if not cons:
                self.log.append(f"|[Error]| [{self._backlog(rule,seqs)}] 引号不匹配")
                self.error += 1
                rule += "\""
            if left < 0:
                self.log.append(f"|[Error]| [{self._backlog(rule,seqs)}] 缺少{-left}个\"\(\"")
                self.error += 1
                rule = "("*(-left) + rule
            elif left > 0:
                self.log.append(f"|[Error]| [{self._backlog(rule,seqs)}] 缺少{left}个\"\)\"")
                self.error += 1
                rule += ")"*left
        return rule

    ## Treat "\""
    def _stringconvert(self,rule,seqs_):
        seqs = seqs_.copy()
        rulesplit = rule.split("\"")
        if len(rulesplit)%2 != 1:
            self.log.append(f"|[Error]| [{self._backlog(rule, seqs)}]引号不匹配")
            self.error += 1
        for i in range(len(rulesplit)//2):
            seqs.append((["Para", rulesplit[2*i+1],0,0],"num",self._backlog(rulesplit[2*i+1],seqs)))
            rulesplit[2*i+1] = " 00seqs_%d_ "%(len(seqs)-1)
        rule_ = "".join(rulesplit)
        rule = rule_.replace("=","==").replace("====","==").replace("!==","!=").replace("<==","<=")\
               .replace(">==",">=").replace("（","(").replace("）",")").replace("，",",")\
               .replace("！","!")
        if rule != rule_:
            self.log.append(f"|[Warning]| [{self._backlog(rule_, seqs)}]存在非法字符")
            self.warning += 1
        if "," in rule:
            rule, rule_ = rule.split(",",1)
            self.log.append(f"|[Error]| [{self._backlog(rule_, seqs)}]为多余部分")
            self.error += 1
        return self._parentheseconvert(self._complete(rule,seqs),seqs)

    ## Treat "()"
    def _parentheseconvert(self,rule,seqs_):
        seqs = seqs_.copy()
        rule_ = rule = re.sub(r" +"," ",rule)
        rule = re.sub(r"\( *\)","",rule)
        if not rule.replace(" ",""):
            return None, "Unknown"
        if rule[:1] == " ":
            rule = rule[1:]
        if rule[-1:] == " ":
            rule = rule[:-1]
        rule_origin = self._backlog(rule_, seqs)
        warnComplet = False
        while "(" in rule or ")" in rule:
            if "(" in rule and not ")" in rule:
                rule += ")"
                if not warnComplet:
                    self.log.append(f"|[Error]| [{rule_origin}]缺少\"(\"")
                    self.error += 1; warnComplet = True
            elif ")" in rule and not "(" in rule:
                rule = "(" + rule
                if not warnComplet:
                    self.log.append(f"|[Error]| [{rule_origin}]缺少\")\"")
                    self.error += 1; warnComplet = True
            if rule[0] == "(" and rule[-1] == ")" and "(" not in rule[1:-1]:
                result, typ = self._logicconvert(rule[1:-1], seqs)
                return result, typ
            l = 0
            for subrule in re.finditer(r"\([^\(\)]+\)",rule):
                a,b = subrule.span()
                result, typ = self._logicconvert(rule[a-l+1:b-l-1], seqs)
                seqs.append((result, typ,self._backlog(rule[a-l+1:b-l-1],seqs)))
                rule = "%s 00seqs_%d_ %s"%(rule[:a], len(seqs)-1 ,rule[b:])
                l += (b-a) - (9 + len(str(len(seqs)-1)))
        result, typ = self._logicconvert(rule,seqs)
        return result, typ

    ## Treat logic operator(and|or|xor|not)
    def _logicconvert(self, rule, seqs_):
        seqs = seqs_.copy()
        rule = re.sub(r" +", " ", f" {rule} ")
        rule_origin = self._backlog(rule, seqs)
        rule_split = list(re.finditer(r" and | or | xor ", rule))
        if not rule_split:
            while rule[:8]=="not not ":
                rule = rule[8:]
                if cons:
                    self.log.append(f"[Warning] [{seq_origin}]中存在无用not")
                    self.warning += 1
                    cons = False
            ## Supprime wrong [not] in end(Case [not not xxx])
            if rule[-1:] == " ":
                rule = rule[:-1]
            while rule[-4:]==" not":
                rule = rule[-4:]
                if cons:
                    self.log.append(f"|[Error]| [{seq_origin}]中存在未知not")
                    self.error += 1
                    cons = False
            if not rule.replace(" ",""):
                rule = None
                self.log.append(f"|[Error]| [{rule_origin}]中两逻辑关联词间缺少成分")
                self.error += 1
            elif rule[:4]=="not ":
                rule_a, typ = self._compareconvert(rule_[4:],seqs)
                if typ not in ["bool","Unknown"]:
                    self.log.append(f"|[Error]| [{seq_origin}] not后非布尔类型")
                    self.error += 1
                return ["not", rule_a], "bool"
            result, typ = self._compareconvert(rule,seqs)
            return result, typ
        else:
            result = []
            len_split = len(rule_split)
            for i in range(len_split):
                a,b = rule_split[i].span()
                if i==len_split-1:
                    fin = len(rule)
                else:
                    fin = rule_split[i+1].span()[0]
                rule_ = rule[b:fin]; cons = True
                seq_origin = self._backlog(rule_, seqs)
                ## Supprime useless not (Case [not not xxx])
                while rule_[:8]=="not not ":
                    rule_ = rule_[8:]
                    if cons:
                        self.log.append(f"[Warning] [{seq_origin}]中存在无用not")
                        self.warning += 1
                        cons = False
                ## Supprime wrong [not] in end(Case [not not xxx])
                if rule_[-1:] == " ":
                    tule_ = rule_[:-1]
                while rule_[-4:]==" not":
                    rule_ = rule_[-4:]
                    if cons:
                        self.log.append(f"|[Error]| [{seq_origin}]中存在未知not")
                        self.error += 1
                        cons = False
                if not rule_.replace(" ",""):
                    rule_ = None
                    self.log.append(f"|[Error]| [{rule_origin}]中两逻辑关联词间缺少成分")
                    self.error += 1
                elif rule_[:4]=="not ":
                    rule_a, typ = self._compareconvert(rule_[4:],seqs)
                    if typ not in ["bool","Unknown"]:
                        self.log.append(f"|[Error]| [{seq_origin}] not后非布尔类型")
                        self.error += 1
                    rule_ = ["not", rule_a]
                else:
                    rule_a,typ = self._compareconvert(rule_,seqs)
                    if typ not in ["bool","Unknown"]:
                        self.log.append(f"|[Error]| [{seq_origin}] [{rule[a+1:b-1]}]后非布尔类型")
                        self.error += 1
                    rule_ = rule_a
                if result:
                    if former == rule[a+1:b-1]:
                        result.append(rule_)
                    else:
                        result = [rule[a+1:b-1], result, rule_]
                else:
                    rule1 = rule[:a]; cons = True
                    if rule1[-1:] == " ":
                        rule1 = rule1[:-1]
                    while rule1[-4:] == " not":
                        rule1 = rule1[-4:]
                        if cons:
                            self.log.append(f"|[Warning]| [{seq_origin}]中存在无用not")
                            self.warning += 1
                            cons = False
                    while rule1[:8]=="not not ":
                        rule1 = rule1[8:]
                    if not rule1.replace(" ",""):
                        rule1 = None
                        self.log.append(f"|[Error]| [{rule_origin}]中两逻辑关联词间缺少成分")
                        self.error += 1
                    elif rule1[:4]=="not ":
                        rule_a, typ = self._compareconvert(rule1[4:],seqs)
                        if typ  not in ["bool","Unknown"]:
                            self.log.append(f"|[Error]| [{seq_origin}]not后非布尔类型")
                            self.error += 1
                        rule1 = ["not", rule_a]
                    else:
                        rule_a,typ = self._compareconvert(rule1,seqs)
                        if typ not in ["bool","Unknown"]:
                            self.log.append(f"|[Error]| [{seq_origin}]{rule[a+1:b-1]}前非布尔类型")
                            self.error += 1
                        rule1 = rule_a
                    result = [rule[a+1:b-1], rule1, rule_]
                    former = rule[a+1:b-1]
        return result, "bool"
    
    ## Treat compare operator(<|>|<=|>=|!=|==)
    def _compareconvert(self, rule, seqs_):
        seqs = seqs_.copy()
        rule = rule.replace(" ","")
        rule_origin = self._backlog(rule, seqs)
        result = []
        rule_split = list(re.finditer(r"<=?|>=?|==|!=",rule))
        if not rule_split:
            result, typ = self._plusminusconvert(rule,seqs)
            return result, typ
        else:
            len_split = len(rule_split)
            for i in range(len_split):
                a,b = rule_split[i].span()
                if i == len_split-1:
                    fin = len(rule)
                else:
                    fin = rule_split[i+1].span()[0]
                rule_ = rule[b:fin]
                if not rule_:
                    rule_ = None
                    self.log.append(f"|[Error]| [{rule_origin}]中两逻辑关联词间缺少成分")
                    self.error += 1
                else:
                    seq_origin = self._backlog(rule_, seqs)
                    rule_a, typ = self._plusminusconvert(rule_,seqs)
                    if typ not in ["num","Unknown"]:
                        self.log.append(f"|[Error]| [{seq_origin}]{rule[a:b]}后非数值类型")
                        self.error += 1
                    rule_ = rule_a
                if result:
                     result.append([rule[a:b],rule1,rule_])
                else:
                    rule1 = rule[:a]
                    if not rule1:
                        rule1 = None
                        self.log.append(f"|[Error]| [{rule_origin}]中两逻辑关联词间缺少成分")
                        self.error += 1
                    else:
                        rule_a,typ = self._plusminusconvert(rule1,seqs)
                        if typ not in ["num","Unknown"]:
                            self.log.append(f"|[Error]| [{self._backlog(rule1,seqs)}]{rule[a:b]}前非数值类型")
                            self.error += 1
                        rule1 = rule_a
                    result = ["and",[rule[a:b],rule1,rule_]]
                rule1 = rule_
            if len(result) == 2:
                result =result[1]
        return result, "bool"

    ## Treat +/-(Ignore negative sign)
    def _plusminusconvert(self,rule,seqs_):
        seqs = seqs_.copy()
        rule = rule.replace(" ","")
        rule_origin = self._backlog(rule,seqs)
        if "+-" in rule or "-+" in rule or "++" in rule:
            self.log.append(f"|[Warning]| [{rule_origin}] 存在冗余正号")
            self.warning += 1
        if "--" in rule:
            self.log.append(f"|[Warning]| [{rule_origin}] 存在负号与减号的叠加")
            self.warning += 1
        while "--" in rule or "+-" in rule or "-+" in rule:
            rule = rule.replace("--", "+").replace("-+", "-").replace("+-", "-").replace("++", "+")
        result = []
        rule_split = list(re.finditer(r"\+|-",rule))
        a_ = 0
        if not rule_split:
            result, typ = self._proddivconvert(rule,seqs)
            return result, typ
        else:
            len_split = len(rule_split)
            for i in range(len_split):
                a,b = rule_split[i].span()
                rule1 = rule[a_:a]
                if not rule1 or rule[a-1] in ["*","/","^","|","&","%","~"] or \
                   (rule[a-1].lower() == "e" and (a==1 or rule[a-2] in [' ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])):
                    continue
                rule_a, typ = self._proddivconvert(rule1,seqs)
                if typ not in ["num","Unknown"]:
                    self.log.append(f"|[Error]| [{self._backlog(rule1,seqs)}] {rule[a:b]}前非数值类型")
                    self.error += 1
                if result:
                    if former == "+":
                        result[1].append(rule_a)
                    else:
                        result.append(rule_a)
                    former = rule[a:b]
                else:
                    result = ["-",["+",rule_a]]
                    former = rule[a:b]
                a_ = b
            rule1 = rule[a_:]
            if not rule1:
                self.log.append("|[Error]| 句末多余加减号")
                self.error += 1
            else:
                rule_a, typ = self._proddivconvert(rule1,seqs)
                if typ not in ["num","Unknown"]:
                    self.log.append(f"|[Error]| [{self._backlog(rule1,seqs)}]{rule[a:b]}前非数值类型")
                    self.error += 1
                if result:
                    if former == "+":
                        result[1].append(rule_a)
                    else:
                        result.append(rule_a)
                else:
                    result = ["-",["+",rule_a]]
            if len(result) == 2:
                result =result[1]   # multi-plus
                if len(result) == 2:
                    result = result[1]
            elif len(result[1]) == 2:
                result = ["-", result[1][1]] + result[2:] # multi-minus
        return result, "num"

    ## Treat *|/|//|%
    def _proddivconvert(self,rule,seqs_):
        seqs = seqs_.copy()
        rule = rule.replace(" ","").replace("**","=") ## Replace "**" with "=" which exists no more
        result = []
        rule_split = list(re.finditer(r"\*|//?|%",rule))
        if not rule_split:
            result, typ = self._powerconvert(rule.replace("=","**"),seqs)
            return result, typ
        else:
            len_split = len(rule_split)
            for i in range(len_split):
                a,b = rule_split[i].span()
                if i == len_split-1:
                    fin = len(rule)
                else:
                    fin = rule_split[i+1].span()[0]
                rule_ = rule[b:fin]
                if not rule_:
                    rule_ = None
                    self.log.append(f"|[Error]| [{self._backlog(rule.replace('=','**'),seqs)}]中两乘除号间缺少成分")
                    self.error += 1
                else:
                    rule_a, typ = self._powerconvert(rule_.replace("=","**"),seqs)
                    if typ not in ["num","Unknown"]:
                        self.log.append(f"|[Error]| [{self._backlog(rule_.replace('=','**'),seqs)}] {rule[a:b]}后非数值类型")
                        self.error += 1
                    rule_ = rule_a
                func_name = rule[a:b].replace(" ","")
                if result:
                    if func_name == "*":
                        result[1].append(rule_)
                    elif func_name == "/":
                        result.append(rule_)
                    else:
                        if len(result) == 2:
                            result =result[1]
                            if len(result) == 2:
                                result = result[1]
                        elif len(result[1]) == 2:
                            result = ["/", result[1][1]]+result[2:]
                        result = ["/",["*",result]]
                else:
                    rule1 = rule[:a]
                    if not rule1.replace(" ",""):
                        rule1 = None
                        self.log.append(f"|[Error]| [{self._backlog(rule.replace('=','**'),seqs)}]中两乘除关联词间缺少成分")
                        self.error += 1
                    else:
                        rule_a, typ = self._powerconvert(rule1.replace("=","**"),seqs)
                        if typ not in ["num","Unknown"]:
                            self.log.append(f"|[Error]| [{self._backlog(rule1.replace('=','**'),seqs)}]{rule[a:b]}前非数值类型")
                            self.error += 1
                        rule1 = rule_a
                    if func_name == "*":
                        result = ["/",["*",rule1,rule_]]
                    elif func_name == "/":
                        result = ["/",["*",rule1],rule_]
                    else:
                        result = ["/",["*",[func_name,rule1,rule_]]]
            if len(result) == 2:
                result =result[1]
                if len(result) == 2:
                    result = result[1]
            elif len(result[1]) == 2:
                result = ["/", result[1][1]]+result[2:]
        return result, "num"

    ## Treate(**)
    def _powerconvert(self,rule,seqs_):
        seqs = seqs_.copy()
        rule = rule.replace(" ","")
        result = []
        if "***" in rule:
            self.log.append(f"|[Error]| [{self._backlog(rule[b:fin],seqs)}]中两(阶)乘号\"***\"间缺少成分")
            self.error += 1
            rule = re.sub(r"\*\*\**", "**", rule)
        rule_split = list(re.finditer(r"\*\*", rule))
        if not rule_split:
            result, typ = self._bitoperatorconvert(rule,seqs)
            return result, typ
        else:
            len_split = len(rule_split)
            for i in range(len_split):
                a,b = rule_split[i].span()
                if i == len_split-1:
                    fin = len(rule)
                else:
                    fin = rule_split[i+1].span()[0]
                rule_ = rule[b:fin]
                if not rule_:
                    rule_ = None
                    self.log.append(f"|[Error]| [{self._backlog(rule[b:fin],seqs)}]中两阶乘号\"**\"间缺少成分")
                    self.error += 1
                else:
                    rule_a, typ = self._bitoperatorconvert(rule_,seqs)
                    if typ not in ["num","Unknown"]:
                        self.log.append(f"|[Error]| [{self._backlog(rule_,seqs)}]  **后为非数值类型")
                        self.error += 1
                    rule_ = rule_a
                if result:
                    result = ["**",result,rule_]
                else:
                    rule1 = rule[:a]
                    if not rule1.replace(" ",""):
                        rule1 = None
                        self.log.append(f"|[Error]| [{self._backlog(rule[:a],seqs)}]中两阶乘号\"**\"间缺少成分")
                        self.error += 1
                    else:
                        rule_a, typ = self._bitoperatorconvert(rule1,seqs)
                        if typ not in ["num","Unknown"]:
                            self.log.append(f"|[Error]| [{self._backlog(rule1,seqs)}]**前非数值类型")
                            self.error += 1
                        rule1 = rule_a
                    result = ["**",rule1,rule_]
        return result, "num"

    ## Treat &| | |^|~ -> Treat TagN -> Translate value|bool|panme
    def _bitoperatorconvert(self,rule,seqs_):
        seqs = seqs_.copy()
        rule = rule.replace(" ","")
        if not rule:
            return None, "Unknown"
        if "~~" in rule:
            self.log.append(f"|[Warning]| [{self._backlog(rule_,seqs)}]存在冗余~")
            self.warning += 1
            while "~~" in rule:
                rule = rule.replace("~~", "")
        result = []
        rule_split = list(re.finditer(r"\^|\||\&",rule))
        if not rule_split:
            if rule[:1] == "~":
                rule_ = rule[1:]
                rule_a, typ = self._bitoperatorconvert(rule_,seqs)
                if typ not in ["num","Unknown"]:
                    self.log.append(f"|[Error]| [{self._backlog(rule_,seqs)}] {rule[a:b]}后非数值类型")
                    self.error += 1
                return ["~", rule_a], "num"
            if rule[0] == "+":
                rule_ = rule[1:]
                rule_a, typ = self._bitoperatorconvert(rule_,seqs)
                if typ not in ["num","Unknown"]:
                    self.log.append(f"|[Error]| [{self._backlog(rule_,seqs)}] {rule[a:b]}后非数值类型")
                    self.error += 1
                return rule_a, "num"
            if rule[0] == "-":
                rule_ = rule[1:]
                rule_a, typ = self._bitoperatorconvert(rule_,seqs)
                if typ not in ["num","Unknown"]:
                    self.log.append(f"|[Error]| [{self._backlog(rule_,seqs)}] {rule[a:b]}后非数值类型")
                    self.warning += 1
                    return None, "Unknown"
                if isinstance(rule_a, int) or isinstance(rule_a, float):
                    return rule_a*-1, "num"
                else:
                    return ["*", rule_a, -1], "num"
            if rule.replace(" ","").lower() in ["inf","np.inf","numpy.inf","math.inf"]:
                return float("inf"), "num"
            elif rule.replace(" ","").lower() == "true":
                return True, "bool"
            elif rule.replace(" ","").lower() == "false":
                return False, "bool"
            elif rule.replace(" ","").lower() in ["null","none"]:
                return None, "bool"
            elif rule.replace(" ","").lower() in ["nan","math.nan","np.nan","numpy.nan"]:
                return float("nan"), "num"
            nums = rule.split("00seqs_")
            if len(nums) > 2:
                self.log.append("|[Error]| 存在若干括号附近缺少运算符")
                self.error += 1
                try:
                    result, typ, _ = seqs[int(nums[1][:-1])]
                    return result, typ
                except Exception as e:
                    return None, "Unknown"
            elif len(nums) == 2:
                if nums[0]:
                    self.log.append("|[Error]| 存在若干括号附近缺少运算符")
                    self.error += 1
                try:
                    result, typ, _ = seqs[int(nums[1][:-1])]
                    return result, typ
                except Exception as e:
                    self.log.append("|[Error]| 存在若干括号附近缺少运算符")
                    self.error += 1
                    return None, "Unknown"
            elif rule in self.pnames:
                if rule not in self.relatPara.keys():
                    self.relatPara[rule] = [0, 0]
                return ["Para", rule, 0, 0], "num"
            elif f"{rule},0" in self.fnames:
                self.relatFault.add(f"{rule},0")
                return ["Fault", rule, 0], "num"
            elif "." in rule or "e" in rule.lower():
                try:
                    return float(rule), "num"
                except Exception as e:
                    self.log.append(f"|[Error]| {rule}不可解析")
                    self.error += 1
                    return None, "Unknown"
            elif rule[0] == "0" and len(rule)>1:
                if rule[1] == "x":
                    try:
                        return int(rule,base=16), "num"
                    except Exception as e:
                        self.log.append(f"|[Error]| {rule}不可解析")
                        self.error += 1
                        return None, "Unknown"
                elif rule[1]== "b":
                    try:
                        return int(rule,base=2), "num"
                    except Exception as e:
                        self.log.append(f"|[Error]| {rule}不可解析")
                        self.error += 1
                        return None, "Unknown"
                elif rule[1] == "o":
                    try:
                        return int(rule,base=8), "num"
                    except Exception as e:
                        self.log.append(f"|[Error]| {rule}不可解析")
                        self.error += 1
                        return rule, "Unknown"
            else:
                try:
                    return int(rule), "num"
                except Exception as e:
                    self.log.append(f"|[Error]| {rule}不可解析")
                    self.error += 1
                    return ["Para", rule, 0, 0], "Unknown"
        else:
            len_split = len(rule_split)
            for i in range(len_split):
                a,b = rule_split[i].span()
                if i == len_split-1:
                    fin = len(rule)
                else:
                    fin = rule_split[i+1].span()[0]
                rule_ = rule[b:fin]
                if not rule_:
                    rule_ = None
                    self.log.append(f"|[Error]| [{self._backlog(rule[b:fin],seqs)}]中两位操作间缺少成分")
                    self.error += 1
                else:
                    rule_a, typ = self._bitoperatorconvert(rule_,seqs)
                    if typ not in ["num","Unknown"]:
                        self.log.append(f"|[Error]| [{self._backlog(rule[a:b],seqs)}] {rule[a:b]}后为非数值类型")
                        self.error += 1
                    rule_ = rule_a
                func_name = rule[a:b]
                if result:
                    result = [func_name,result,rule_]
                else:
                    rule1 = rule[:a]
                    if not rule1:
                        rule1 = None
                        self.log.append(f"|[Error]| [{self._backlog(rule[:a+10],seqs)}]中两位操作间缺少成分")
                        self.error += 1
                    else:
                        rule_a, typ = self._bitoperatorconvert(rule1,seqs)
                        if typ not in ["num","Unknown"]:
                            self.log.append(f"|[Error]| [{self._backlog(rule1,seqs)}] {rule[a:b]}后非数值类型")
                            self.error += 1
                        rule1 = rule_a
                    result = [func_name, rule1, rule_]
        return result, "num"

    def _backlog(self, rule, seqs_):
        if rule is None:
            return ""
        if seqs_:
            seqs = seqs_.copy()
            while True:
                nums = re.findall(r"00seqs_([0-9]+)_", f" {rule} ")
                if not nums:
                    break
                for num in nums:
                    rule = rule.replace(f"00seqs_{num}_", f" {seqs[int(num)][2]} ").replace("  ", " ").replace(" ", "  ")
        rule = re.sub(r" +"," ", rule); rule = re.sub(r" *\) *",")", rule); rule = re.sub(r" *\( *","(", rule)
        if rule[:1] == " ":
            rule = rule[1:]
        if rule[-1:] == " ":
            rule = rule[:-1]
        return rule

if __name__ == "__main__":
    from pprint import pprint
    rule = "B+int(A)==-5 and PreCond([5](1+~Para(\"A\", 5, 1))**B>-6 and Fault(\"dasda\"), 5, Max(-A,5)>-6)"
    rp = ruleParse()
    print(f">> Rule String:   {rule}\n\n>> Translated Rule:")
    pprint(rp.convert(rule))
    print("\n>> Folded Branches:")
    dictPrint = lambda dict_:  '\n   ** '.join([f"{k_}: \n      {v_}" for k_,v_ in dict_.items()])
    print("\n".join([f" * {k} : \n   ** {dictPrint(v)}" for k,v in rp.seqs.items() if v]))
    print(f" >> Order:   {rp.seqOrder}")
    print(f"* Para : \n   ** {rp.relatPara}")
    print(f"* Fault : \n   ** {list(rp.relatFault)}")
    print(f"\n======== {rp.error} Errors & {rp.warning} Warnings ========")
    print("  * "+"\n  * ".join(rp.log))
