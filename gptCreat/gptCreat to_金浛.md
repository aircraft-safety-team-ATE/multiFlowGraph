





# 基于GPT赋能多信号流图

## 商飞航电系统——甚高频通信系统多信号流图构建

### 部件实体提取

******************************************************************************************************************

**提问**

```
{
    "instruction": "你是航空航电设备领域专门进行实体抽取的专家。请从input中抽取出符合schema定义的实体，不存在的实体类型返回空列表。请按照JSON字符串的格式回答。你可以参考example进行抽取。",
    "schema": [
        "部件"
    ],
    "example": [
        {
            "input": "甚高频通信系统用于进行飞机与飞机、飞机与地面台之间的视距通信。在基本型中，该系统由两套独立的甚高频子系统组成，分别是VHF-1系统和VHF-2系统。选装型中，可能增加VHF-3系统。每个子系统包括一台甚高频通信收发机及其相关的天线",
            "output": {
                "部件": [
                    "甚高频通信系统",
                    "甚高频子系统",
                    "VHF-2系统",
                    "VHF-1系统",
                    "甚高频通信收发机",
                    "天线"
                ]
            }
        },
        {
            "input": "DPP-4抑制剂在特殊人群中的应用",
            "output": {
                "部件": []
            }
        }
    ],
    "input": "甚高频通信收发机型号是VHF-4000，由RC提供。VHF-4000是多信道的收发机，能够提供118.00MHz到136.975MHz频率范围内的DSB（双边带）AM（调幅）音频通信，并能提供25KHz和8.33KHz的频道间隔选择。"
}
```

**回答**

```
{
    "部件": [
        "甚高频通信收发机",
        "VHF-4000",
        "收发机"
    ]
}
```



****************************************************************************************************************

**提问**

```
{
    "instruction": "你是航空航电设备领域专门进行实体抽取的专家。请从input中抽取出符合schema定义的实体，不存在的实体类型返回空列表。请按照JSON字符串的格式回答。你可以参考example进行抽取。",
    "schema": [
        "部件"
    ],
    "example": [
        {
            "input": "甚高频通信系统用于进行飞机与飞机、飞机与地面台之间的视距通信。在基本型中，该系统由两套独立的甚高频子系统组成，分别是VHF-1系统和VHF-2系统。选装型中，可能增加VHF-3系统。每个子系统包括一台甚高频通信收发机及其相关的天线",
            "output": {
                "部件": [
                    "甚高频通信系统",
                    "甚高频子系统",
                    "VHF-2系统",
                    "VHF-1系统",
                    "甚高频通信收发机",
                    "天线"
                ]
            }
        },
        {
            "input": "DPP-4抑制剂在特殊人群中的应用",
            "output": {
                "部件": []
            }
        }
    ],
    "input": "甚高频天线型号为VHFA-2100。VHF-1、VHF-2、VHF-3（选装）天线分别安装在机头下部SD192、机身顶部SD400和SD744（选装）位置。甚高频天线与表面处理过的机身蒙皮直接接触进行搭接，同时天线也通过安装螺钉以及导电密封胶与机身蒙皮进行搭接，满足天线射频搭接要求。天线与收发机之间通过同轴电缆转接。"
}
```

**回答**

```
{
    "部件": [
        "甚高频天线",
        "VHFA-2100",
        "VHF-1天线",
        "VHF-2天线",
        "VHF-3天线",
        "机身蒙皮",
        "安装螺钉",
        "导电密封胶",
        "同轴电缆"
    ]
}
```



********************

****************************************************************************************************************

**提问**

```
{
    "instruction": "你是航空航电设备领域专门进行实体抽取的专家。请从input中抽取出符合schema定义的实体，不存在的实体类型返回空列表。请按照JSON字符串的格式回答。你可以参考example进行抽取。",
    "schema": [
        "部件"
    ],
    "example": [
        {
            "input": "甚高频通信系统用于进行飞机与飞机、飞机与地面台之间的视距通信。在基本型中，该系统由两套独立的甚高频子系统组成，分别是VHF-1系统和VHF-2系统。选装型中，可能增加VHF-3系统。每个子系统包括一台甚高频通信收发机及其相关的天线",
            "output": {
                "部件": [
                    "甚高频通信系统",
                    "甚高频子系统",
                    "VHF-2系统",
                    "VHF-1系统",
                    "甚高频通信收发机",
                    "天线"
                ]
            }
        },
        {
            "input": "DPP-4抑制剂在特殊人群中的应用",
            "output": {
                "部件": []
            }
        }
    ],
    "input": "正常情况下，甚高频通信系统的调谐操作由同侧RTU控制和显示。为提高系统可靠性，对侧RTU也可对甚高频系统进行控制和显示。另外，调谐操作可通过MCDU进行。应急状态下，将RSP面板上的121.5/NORM键控置于121.5位置，可以使VHF-1在121.500MHz的呼救频率上进行通话。
从飞机一开始通电到飞机断电整个期间，VHF通信设备必须始终处于工作状态，以保证与航空公司和空管部门的联系。因此VHF-1收发机由LESS DC汇流条提供28V直流电源，VHF-2收发机由R 28V DC汇流条供电。如果选装了VHF-3系统，则VHF-3收发机由L 28V DC左右汇流条供电。这种设置保证了VHF-1收发机即使在飞机处于应急状态仍能正常工作。
在选装型中，VHF-3系统除了具备语音通信功能外，还具备数据链通信功能。甚高频数据链通信系统能够在地面信息供应者和采用甚高频和SATCOM数据网的飞机之间提供双向的信息和数据文件交换。地面信息提供者处理下行数据链数据信息并将格式化的信息发送给飞机，即对下行链路的信息做出回应。
"
}
```



**回答**

```
{
    "部件": [
        "甚高频通信系统",
        "RTU",
        "MCDU",
        "RSP面板",
        "VHF-1",
        "VHF-2",
        "VHF-3",
        "VHF-1收发机",
        "LESS DC汇流条",
        "VHF-2收发机",
        "R 28V DC汇流条",
        "VHF-3收发机",
        "L 28V DC汇流条",
        "甚高频数据链通信系统",
        "SATCOM数据网"
    ]
}
```

********************
### 部件关系提取



****************************************************************************************************************

**提问**

```
{
    "instruction": "你是航空航电设备领域专门进行关系抽取的专家。请从input中抽取出符合schema定义的关系三元组，不存在的关系返回空列表。请按照JSON字符串的格式回答。你可以参考example进行抽取。",
    "schema": [
        "包含",
        "连接"
        
    ],
    "example": [
        {
            "input": "甚高频通信系统用于进行飞机与飞机、飞机与地面台之间的视距通信。在基本型中，该系统由两套独立的甚高频子系统组成，分别是VHF-1系统和VHF-2系统。选装型中，可能增加VHF-3系统。每个子系统包括一台甚高频通信收发机及其相关的天线",
            "output": {
                "包含": [
                    {
                        "subject": "甚高频通信系统",
                        "object": "甚高频子系统"
                    },
                    {
                        "subject": "甚高频子系统",
                        "object": "甚高频通信收发机"
                    },
                    {
                        "subject": "甚高频子系统",
                        "object": "天线"
                    },
                ]
            }
        },
        {
            "input": "正常情况下，甚高频通信系统的调谐操作由同侧RTU控制和显示。为提高系统可靠性，对侧RTU也可对甚高频系统进行控制和显示。另外，调谐操作可通过MCDU进行。应急状态下，将RSP面板上的121.5/NORM键控置于121.5位置，可以使VHF-1在121.500MHz的呼救频率上进行通话。
从飞机一开始通电到飞机断电整个期间，VHF通信设备必须始终处于工作状态，以保证与航空公司和空管部门的联系。因此VHF-1收发机由LESS DC汇流条提供28V直流电源，VHF-2收发机由R 28V DC汇流条供电。如果选装了VHF-3系统，则VHF-3收发机由L 28V DC左右汇流条供电。这种设置保证了VHF-1收发机即使在飞机处于应急状态仍能正常工作。
在选装型中，VHF-3系统除了具备语音通信功能外，还具备数据链通信功能。甚高频数据链通信系统能够在地面信息供应者和采用甚高频和SATCOM数据网的飞机之间提供双向的信息和数据文件交换。地面信息提供者处理下行数据链数据信息并将格式化的信息发送给飞机，即对下行链路的信息做出回应。",
            "output": {
                "包含": [
                    {
                        "subject": "VHF-3",
                        "object": "甚高频数据链通信系统"
                    }
                ],
                "连接":[
                    {
                        "subject": "VHF-1收发机",
                        "object": "LESS DC汇流条"
                    },
                    {
                        "subject": "VHF-2收发机",
                        "object": "R 28V DC汇流条"
                    },
                    {
                        "subject": "VHF-3系统",
                        "object": "L 28V DC左右汇流条"
                    },
                ]
            }
        }
    ],
    "input": "ARJ21-700飞机的通信系统主要提供飞机上的机组人员与飞机外界的通信以及飞机内部不同位置处的通信联络。飞机与外界的通信，包括飞机与地面管制人员或者与其他飞机之间的相互通信，这主要是通过无线电通信来完成的。飞机内部之间的相互通信，是靠有线通信网络来完成的。目前，最主要的通信方式还是以语音通信为主，ARJ21-700飞机的语音无线电通信包括甚高频通信子系统和高频通信子系统。随着技术的发展，数据通信在航空通信中占据越来越多的位置，在ARJ21-700飞机上，数据通信作为选装项，可根据用户的需要安装数据链通信系统，通过它可以进行空地之间的数据和信息的自动传输交换，例如，飞机的离场、起飞、着陆、进入登机门时间，发动机参数，飞机故障等可立即自动向地面报告，无需飞行员参与报告。这样可使地面随时了解飞机状态，便于进行生产调度和维修安排。
ARJ21-700飞机通信系统包括甚高频通信、高频通信、选择呼叫、旅客广播、内话和音频综合、音频记录、应急定位发射、驾驶舱门监视等子系统。
ARJ21飞机导航系统主要用来引导飞机安全准确地沿着所选定的路线，准时地到达目的地。导航系统主要由飞行环境数据、姿态和航向、着陆与滑行、自主定位、非自主定位和飞行管理计算共6类分系统组成，向机组提供保证飞机安全飞行和导引飞机按规定航线飞行的目视和音响信息。ARJ21飞机无线电导航系统由以下子系统组成：甚高频导航系统（包括指点信标、仪表着陆系统和甚高频全向信标）、测距器、自动定向仪。
"
}
```

**回答**

```
{
    "包含": [
        {
            "subject": "ARJ21-700飞机通信系统",
            "object": "甚高频通信子系统"
        },
        {
            "subject": "ARJ21-700飞机通信系统",
            "object": "高频通信子系统"
        },
        {
            "subject": "ARJ21-700飞机通信系统",
            "object": "数据链通信系统"
        },
        {
            "subject": "ARJ21飞机导航系统",
            "object": "飞行环境数据子系统"
        },
        {
            "subject": "ARJ21飞机导航系统",
            "object": "姿态和航向子系统"
        },
        {
            "subject": "ARJ21飞机导航系统",
            "object": "着陆与滑行子系统"
        },
        {
            "subject": "ARJ21飞机导航系统",
            "object": "自主定位子系统"
        },
        {
            "subject": "ARJ21飞机导航系统",
            "object": "非自主定位子系统"
        },
        {
            "subject": "ARJ21飞机导航系统",
            "object": "飞行管理计算子系统"
        },
        {
            "subject": "ARJ21飞机无线电导航系统",
            "object": "甚高频导航系统"
        },
        {
            "subject": "ARJ21飞机无线电导航系统",
            "object": "测距器"
        },
        {
            "subject": "ARJ21飞机无线电导航系统",
            "object": "自动定向仪"
        },
        {
            "subject": "甚高频导航系统",
            "object": "指点信标"
        },
        {
            "subject": "甚高频导航系统",
            "object": "仪表着陆系统"
        },
        {
            "subject": "甚高频导航系统",
            "object": "甚高频全向信标"
        }
    ],
    "连接": []
}

```



********************

### 三元组抽取


*********************************

**提问**

```
你是三元组提取专家 从以下文本尽可能提取         "甚高频通信系统",
        "RTU",
        "MCDU",
        "RSP面板",
        "VHF-1",
        "VHF-2",
        "VHF-3",
        "VHF-1收发机",
        "LESS DC汇流条",
        "VHF-2收发机",
        "R 28V DC汇流条",
        "VHF-” 部件的三元组
"正常情况下，甚高频通信系统的调谐操作由同侧RTU控制和显示。为提高系统可靠性，对侧RTU也可对甚高频系统进行控制和显示。另外，调谐操作可通过MCDU进行。应急状态下，将RSP面板上的121.5/NORM键控置于121.5位置，可以使VHF-1在121.500MHz的呼救频率上进行通话。
从飞机一开始通电到飞机断电整个期间，VHF通信设备必须始终处于工作状态，以保证与航空公司和空管部门的联系。因此VHF-1收发机由LESS DC汇流条提供28V直流电源，VHF-2收发机由R 28V DC汇流条供电。如果选装了VHF-3系统，则VHF-3收发机由L 28V DC左右汇流条供电。这种设置保证了VHF-1收发机即使在飞机处于应急状态仍能正常工作。
在选装型中，VHF-3系统除了具备语音通信功能外，还具备数据链通信功能。甚高频数据链通信系统能够在地面信息供应者和采用甚高频和SATCOM数据网的飞机之间提供双向的信息和数据文件交换。地面信息提供者处理下行数据链数据信息并将格式化的信息发送给飞机，即对下行链路的信息做出回应。
```



**回答**

```
{
    "包含": [],
    "连接": [
        {
            "subject": "甚高频通信系统",
            "object": "RTU"
        },
        {
            "subject": "甚高频通信系统",
            "object": "MCDU"
        },
        {
            "subject": "甚高频通信系统",
            "object": "RSP面板"
        },
        {
            "subject": "RSP面板",
            "object": "VHF-1"
        },
        {
            "subject": "VHF-1收发机",
            "object": "LESS DC汇流条"
        },
        {
            "subject": "VHF-2收发机",
            "object": "R 28V DC汇流条"
        },
        {
            "subject": "VHF-3系统",
            "object": "L 28V DC左右汇流条"
        }
    ]
}

```



********************

### 数据扩充

*********************************

**提问**

```
以下是一个针对航空航电系统的关系抽取数据集的样本，关系类型为“system:controlled_by”：

关系：system:controlled_by。
上下文：正常情况下，甚高频通信系统的调谐操作由同侧RTU控制和显示。为提高系统可靠性，对侧RTU也可对甚高频系统进行控制和显示。另外，调谐操作可通过MCDU进行。
头实体：甚高频通信系统。
头实体类型：SYSTEM。
尾实体：RTU。
尾实体类型：EQUIPMENT。

关系：system:controlled_by。
上下文：应急状态下，将RSP面板上的121.5/NORM键控置于121.5位置，可以使VHF-1在121.500MHz的呼救频率上进行通话。
头实体：VHF-1。
头实体类型：EQUIPMENT。
尾实体：RSP面板。
尾实体类型：EQUIPMENT。

关系：system:powered_by。
上下文：从飞机一开始通电到飞机断电整个期间，VHF通信设备必须始终处于工作状态，以保证与航空公司和空管部门的联系。因此VHF-1收发机由LESS DC汇流条提供28V直流电源，VHF-2收发机由R 28V DC汇流条供电。
头实体：VHF-1收发机。
头实体类型：EQUIPMENT。
尾实体：LESS DC汇流条。
尾实体类型：EQUIPMENT。

关系：system:powered_by。
上下文：从飞机一开始通电到飞机断电整个期间，VHF通信设备必须始终处于工作状态，以保证与航空公司和空管部门的联系。因此VHF-1收发机由LESS DC汇流条提供28V直流电源，VHF-2收发机由R 28V DC汇流条供电。
头实体：VHF-2收发机。
头实体类型：EQUIPMENT。
尾实体：R 28V DC汇流条。
尾实体类型：EQUIPMENT。

关系：system:includes。
上下文：在选装型中，VHF-3系统除了具备语音通信功能外，还具备数据链通信功能。甚高频数据链通信系统能够在地面信息供应者和采用甚高频和SATCOM数据网的飞机之间提供双向的信息和数据文件交换。
头实体：VHF-3系统。
头实体类型：SYSTEM。
尾实体：甚高频数据链通信系统。
尾实体类型：SYSTEM。

关系：system:controlled_by。
上下文：另外，调谐操作可通过MCDU进行。
头实体：甚高频通信系统。
头实体类型：SYSTEM。
尾实体：MCDU。
尾实体类型：EQUIPMENT。
Generate more samples for the relation 'system:controlled_by'.
```





**回答**

```
以下是更多关于关系“system:controlled_by”的样本：

关系：system:controlled_by。
上下文：自动驾驶系统通过飞行管理系统（FMS）进行控制，确保飞机按照预定航线飞行。
头实体：自动驾驶系统。
头实体类型：SYSTEM。
尾实体：飞行管理系统（FMS）。
尾实体类型：EQUIPMENT。

关系：system:controlled_by。
上下文：环境控制系统由中央处理器进行监控和调整，以保持客舱内适宜的温度和湿度。
头实体：环境控制系统。
头实体类型：SYSTEM。
尾实体：中央处理器。
尾实体类型：EQUIPMENT。

关系：system:controlled_by。
上下文：飞机的飞行控制系统通过操纵杆和方向舵踏板进行操作，确保飞行员能够有效地控制飞机。
头实体：飞行控制系统。
头实体类型：SYSTEM。
尾实体：操纵杆。
尾实体类型：EQUIPMENT。

关系：system:controlled_by。
上下文：导航系统的运行由惯性导航系统（INS）和全球定位系统（GPS）共同控制，确保飞机的精确定位。
头实体：导航系统。
头实体类型：SYSTEM。
尾实体：惯性导航系统（INS）。
尾实体类型：EQUIPMENT。

关系：system:controlled_by。
上下文：火警检测系统由驾驶舱控制面板上的警报器进行监控，及时提醒飞行员火灾的发生。
头实体：火警检测系统。
头实体类型：SYSTEM。
尾实体：警报器。
尾实体类型：EQUIPMENT。

关系：system:controlled_by。
上下文：飞行数据记录系统由中央计算机控制，记录所有飞行参数以备后续分析。
头实体：飞行数据记录系统。
头实体类型：SYSTEM。
尾实体：中央计算机。
尾实体类型：EQUIPMENT。

关系：system:controlled_by。
上下文：天气雷达系统由驾驶舱中的显示屏进行控制和显示，为飞行员提供实时天气信息。
头实体：天气雷达系统。
头实体类型：SYSTEM。
尾实体：显示屏。
尾实体类型：EQUIPMENT。

关系：system:controlled_by。
上下文：燃油管理系统通过中央处理单元（CPU）进行监控和管理，确保燃油的高效使用和分配。
头实体：燃油管理系统。
头实体类型：SYSTEM。
尾实体：中央处理单元（CPU）。
尾实体类型：EQUIPMENT。
```



********************

### 利用代码结构优化从文本中提取三元组的能力

*********************************

**提问**

```
from typing import List

class Rel:
    def __init__(self, name: str):
        self.name = name

class Controlled_by(Rel):
    def __init__(self, name: str):
        super().__init__(name=name)

class Powered_by(Rel):
    def __init__(self, name: str):
        super().__init__(name=name)

class Includes(Rel):
    def __init__(self, name: str):
        super().__init__(name=name)

class Entity:
    def __init__(self, name: str):
        self.name = name

class System(Entity):
    def __init__(self, name: str):
        super().__init__(name=name)

class Equipment(Entity):
    def __init__(self, name: str):
        super().__init__(name=name)

class Triple:
    def __init__(self, head: Entity, relation: Rel, tail: Entity):
        self.head = head
        self.relation = relation
        self.tail = tail

class Extract:
    def __init__(self, triples: List[Triple] = []):
        self.triples = triples
用以上逻辑描述以下文本
ARJ21-700飞机的通信系统主要提供飞机上的机组人员与飞机外界的通信以及飞机内部不同位置处的通信联络。飞机与外界的通信，包括飞机与地面管制人员或者与其他飞机之间的相互通信，这主要是通过无线电通信来完成的。飞机内部之间的相互通信，是靠有线通信网络来完成的。目前，最主要的通信方式还是以语音通信为主，ARJ21-700飞机的语音无线电通信包括甚高频通信子系统和高频通信子系统。随着技术的发展，数据通信在航空通信中占据越来越多的位置，在ARJ21-700飞机上，数据通信作为选装项，可根据用户的需要安装数据链通信系统，通过它可以进行空地之间的数据和信息的自动传输交换，例如，飞机的离场、起飞、着陆、进入登机门时间，发动机参数，飞机故障等可立即自动向地面报告，无需飞行员参与报告。这样可使地面随时了解飞机状态，便于进行生产调度和维修安排。
ARJ21-700飞机通信系统包括甚高频通信、高频通信、选择呼叫、旅客广播、内话和音频综合、音频记录、应急定位发射、驾驶舱门监视等子系统。
ARJ21飞机导航系统主要用来引导飞机安全准确地沿着所选定的路线，准时地到达目的地。导航系统主要由飞行环境数据、姿态和航向、着陆与滑行、自主定位、非自主定位和飞行管理计算共6类分系统组成，向机组提供保证飞机安全飞行和导引飞机按规定航线飞行的目视和音响信息。ARJ21飞机无线电导航系统由以下子系统组成：甚高频导航系统（包括指点信标、仪表着陆系统和甚高频全向信标）、测距器、自动定向仪。


```



**回答**

```
# 定义节点和关系
arj21_700_communication_system = System("ARJ21-700飞机通信系统")
arj21_700_voice_radio_communication = System("ARJ21-700飞机的语音无线电通信")
vhf_communication_subsystem = System("甚高频通信子系统")
hf_communication_subsystem = System("高频通信子系统")
data_link_communication_system = System("数据链通信系统")
selective_calling = System("选择呼叫")
passenger_broadcast = System("旅客广播")
interphone_and_audio_integration = System("内话和音频综合")
audio_recording = System("音频记录")
emergency_locator_transmitter = System("应急定位发射")
cockpit_door_monitoring = System("驾驶舱门监视")
arj21_navigation_system = System("ARJ21飞机导航系统")
flight_environment_data = System("飞行环境数据")
attitude_and_heading = System("姿态和航向")
landing_and_taxiing = System("着陆与滑行")
self_positioning = System("自主定位")
non_self_positioning = System("非自主定位")
flight_management_computing = System("飞行管理计算")
vhf_navigation_system = System("甚高频导航系统")
marker_beacon = System("指点信标")
instrument_landing_system = System("仪表着陆系统")
vhf_omnidirectional_radio_range = System("甚高频全向信标")
distance_measuring_equipment = System("测距器")
automatic_direction_finder = System("自动定向仪")

# 定义关系
includes = Includes("includes")

# 创建三元组
triples = [
    Triple(arj21_700_communication_system, includes, arj21_700_voice_radio_communication),
    Triple(arj21_700_voice_radio_communication, includes, vhf_communication_subsystem),
    Triple(arj21_700_voice_radio_communication, includes, hf_communication_subsystem),
    Triple(arj21_700_communication_system, includes, data_link_communication_system),
    Triple(arj21_700_communication_system, includes, selective_calling),
    Triple(arj21_700_communication_system, includes, passenger_broadcast),
    Triple(arj21_700_communication_system, includes, interphone_and_audio_integration),
    Triple(arj21_700_communication_system, includes, audio_recording),
    Triple(arj21_700_communication_system, includes, emergency_locator_transmitter),
    Triple(arj21_700_communication_system, includes, cockpit_door_monitoring),
    Triple(arj21_navigation_system, includes, flight_environment_data),
    Triple(arj21_navigation_system, includes, attitude_and_heading),
    Triple(arj21_navigation_system, includes, landing_and_taxiing),
    Triple(arj21_navigation_system, includes, self_positioning),
    Triple(arj21_navigation_system, includes, non_self_positioning),
    Triple(arj21_navigation_system, includes, flight_management_computing),
    Triple(arj21_navigation_system, includes, vhf_navigation_system),
    Triple(vhf_navigation_system, includes, marker_beacon),
    Triple(vhf_navigation_system, includes, instrument_landing_system),
    Triple(vhf_navigation_system, includes, vhf_omnidirectional_radio_range),
    Triple(arj21_navigation_system, includes, distance_measuring_equipment),
    Triple(arj21_navigation_system, includes, automatic_direction_finder)
]

# 提取
extract = Extract(triples=triples)

# 打印结果
for triple in extract.triples:
    print(f"Head: {triple.head.name}, Relation: {triple.relation.name}, Tail: {triple.tail.name}")
```



