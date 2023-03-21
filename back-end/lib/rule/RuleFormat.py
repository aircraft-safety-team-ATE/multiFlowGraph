import re
import warnings

FUNCS = ["int(rule[num], num=10)->num", "log(rule[num])->num", "exp(rule[num])->num", "abs(rule[num])->num", \
                 "sin(rule[num])->num", "cos(rule[num])->num", "tan(rule[num])->num",  \
                 "asin(rule[num])->num", "acos(rule[num])->num", "atan(rule[num])->num", "atan2(rule[num],rule[num])->num", \
                 "Para(pname,time|frame=0,istime=0)->num",\
                 "Increase(rule[num],time|frame,istime=0)->bool","Decrease(rule[num],time|frame,istime=0)->bool",\
                 "Max(rule[num],time|frame,istime=0)->num","Min(rule[num],time|frame,istime=0)->num", \
                 "Mean(rule[num],time|frame,istime=0)->num",\
                 "PreCond(rule[bool],time,rule[bool])->bool", "Trigger(rule[bool],time,rule[bool])->bool",\
                 "Time(pname={{GlobalParas}})->num", "Fault(fname, frame=1)->bool"]

FUNC_SPECIAL = ["and(*rule[bool])->bool", "or(*rule[bool])->bool", "not(rule[bool])->bool",  "xor(*rule[bool])->bool",\
                ">=(*rule[num])->bool", "<=(*rule[num])->bool", ">(*rule[num])->bool", "<(*rule[num])->bool", \
                "==(*rule[num])->bool", "!=(rule[num], rule[num])->bool",\
                "+(*rule[num])->num", "-(*rule[num])->num", "*(*rule[num])->num", "/(rule[num], rule[num])->num", \
                "**(rule[num], rule[num])->num", "//(rule[num], rule[num])->num", "%(rule[num], rule[num])->num",
                "&(*rule[num])->num", "|(*rule[num])->num", "^(*rule[num])->num", "~(rule[num])->num",\
                "[](rule[bool],time)->bool", "<>(rule[bool],time)->bool", "{}(rule[bool],frame,frame)->bool"]

FUNC_TIME = ["Increase", "Decrease", "Max", "Mean", "Min", "PreCond", "Trigger", "Time","[]", "<>", "{}"]

def convert_func(rules, globalParas="{{GlobalParas}}", func={}):
    for rule in rules:
        rule = rule.replace(" ","").replace("\'","\"")
        funcInfo = re.findall(
            r"([A-Za-z][A-Za-z0-9_]*|[\>\<\=\!\+\-\*/\\\%\&\|\^\~\[\]\{\}]+)\(([^\(\)]*)\)-?>?([A-Za-z]*)", rule)
        if len(funcInfo) != 1:
            warnings.warn(f"Function couldn\'t be translated | {rule}")
            continue
        # print(rule, funcInfo)
        func_name, func_args, func_out = funcInfo[0]
        if not (func_name and func_out in ["num", "bool"]):
            warnings.warn(f"Function should announce its name and output-type | {rule}")
            continue
        if not func_args:
            func[func_name] = [[], func_out, False]
            continue
        func_args = func_args.split(",")
        args = []
        multinput=False; ruleInterupt = False
        for func_pos, func_arg in enumerate(func_args):
            if ruleInterupt:
                break
            if not func_arg:
                ruleInterupt = True
                warnings.warn(f"Function couldn\'t announce a vide input position | {rule}")
                continue
            if func_arg[0] == "*":
                if func_pos+1 !=  len(func_args):
                    ruleInterupt = True
                    warnings.warn(f"Function could only announce one multi-input at last position | {rule}")
                    continue
                multinput = True
                func_arg = func_arg[1:]
            arg_info = re.findall(r"([a-zA-Z][a-zA-Z\[\]\|]*)\=?([^\(^\)]*)", func_arg)
            if len(arg_info) != 1:
                ruleInterupt = True
                warnings.warn(f"Function's {func_pos}-th input could not be translated | {rule}")
                continue
            arg_type, arg_default = arg_info[0]
            if arg_type not in ["num","bool","rule[num]","rule[bool]",\
                                "time","frame","time|frame","istime","pname","fname"]:
                ruleInterupt = True
                warnings.warn(f"Function's {func_pos}-th input should follow a valid format | {rule}")
                continue
            if not arg_default:
                arg_default = None
            elif "bool" in arg_type:
                if arg_default.lower() == "true":
                    arg_default = True
                elif arg_default.lower() == "false":
                    arg_default = False
                elif arg_default.lower() in ["none", "null"]:
                    arg_default = "NoneType"
                else:
                    ruleInterupt = True
                    warnings.warn(f"Function's {func_pos}-th input's default isn't boolean | {rule}")
                    continue
            elif "num" in arg_type or "time" in arg_type or "frame" in arg_type:
                try:
                    arg_default = int(arg_default)
                except Exception as e:
                    try:
                        arg_default = float(arg_default)
                    except Exception as e:
                        ruleInterupt = True
                        warnings.warn(f"Function's {func_pos}-th input's default isn't numeric | {rule}")
                        continue
            elif arg_default.lower() == "{{GlobalParas}}":
                arg_default = globalParas
            elif arg_default.lower() in ["none", "null"]:
                arg_default = "NoneType"
            elif arg_default[0] == "\"" and arg_default[-1] == "\"" and len(arg_default) >= 2:
                arg_default = arg_default[1:-1]
            if arg_type == "istime":
                args = [[func_pos, "value", arg_type, arg_default]] + args
            else:
                if "[" in func_arg:
                    type_in, type_want = arg_type[:-1].split("[",1)
                    args.append([func_pos, type_in, type_want,  arg_default])
                else:
                    type_in = arg_type
                    args.append([func_pos, "value", arg_type,  arg_default])
        if func_name in func.keys():
            warnings.warn(f"Rewriting on an announced function [{func_name}] is executed | {rule}")
        func[func_name] = [args, func_out, multinput]
    return func

FUNC_FORMAT = convert_func(FUNCS + FUNC_SPECIAL)

if __name__ == "__main__":
    from pprint import pprint
    pprint(FUNC_FORMAT)
