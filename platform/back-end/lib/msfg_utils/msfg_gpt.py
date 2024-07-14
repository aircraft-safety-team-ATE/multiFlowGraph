from openai import OpenAI
import base64
import json
api_key = "sk-rOPJxOgX9wrselOID497D08e3d8b4d78B07eC89e5d8d2179"
api_base = "https://api.fantasyfinal.cn/v1"
client = OpenAI(api_key=api_key, base_url=api_base)

# completion = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Hello!"}
#     ]
# )

# print(completion.choices[0].message)


def analyse_multiinfo(content):
    '''
    利用GPT-4o模型进行多信号流图的故障诊断
    content: str 对于GPT 提问的内容
    '''

    struct = '''graph TD
        A[左翼] -->|连接| B[机身]
        C[右翼] -->|连接| B[机身]
        B -->|连接| D[空速管]
        E[机舱] -->|连接| F[温度计]'''

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个故障诊断领域的大师，尤其擅长利用多信号流图进行故障诊断，多信号流图通过构建系统的信号联系关系，帮助你分析系统的故障传播路径。"},
            {"role": "user", "content": content+"以下是你需要进行分析的多信号流图:"+struct}
        ]
    )
    print(completion.choices[0].message.content)
    return str(completion.choices[0].message.content)


def abstract_multiinfo(content):
    '''
    利用GPT-4o模型进行实体抽取
    content: str 对于GPT 提问的内容
    '''
    main_content = {
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
        ]
    }

    main_content['input'] = content

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是航空航电设备领域专门进行实体抽取的专家。请从input中抽取出符合schema定义的实体，不存在的实体类型返回空列表。请按照JSON字符串的格式回答。你可以参考example进行抽取。"},
            {"role": "user", "content": str(main_content)}
        ]
    )
    print(completion.choices[0].message.content)
    return str(completion.choices[0].message.content)


# def abstract_multinfo_byimage(base64_image):
#     '''
#     利用GPT-4o模型进行实体抽取
#     base64_image: str base64编码的图片
#     '''

#     completion = client.chat.completions.create(
#         model="gpt-4o",
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": "请用mermaid语言描述以下多信号流图，不要附带多余信息"},
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}",
#                         },
#                     },
#                 ],
#             }
#         ]
#     )
#     print(completion.choices[0].message.content)
#     return str(completion.choices[0].message.content)

def abstract_multiinfo_bytext(content):
    '''
    利用GPT-4o模型进行文本的多信号流图生成
    content: str 对于GPT 提问的内容
    '''

    struct = '''graph TD
        A[左翼] -->|连接| B[机身]
        C[右翼] -->|连接| B[机身]
        B -->|连接| D[空速管]
        E[机舱] -->|连接| F[温度计]'''

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """
             你是一个故障诊断领域的大师，尤其擅长构建多信号流图，多信号流图通过构建系统的信号联系关系，帮助分析系统的故障传播路径。
             接下来你需要从文本中构建多信号流图，请用以下json格式描述多信号流图,将每个符号的代号简化为最简单的ABCD等序号,不要附带多余信息,回答格式如下
             不要有'''json ''' 也不要前后的文字表示 只有json格式字符串

             
        {
  "nodes": [
    {"id": "2", "l": "First Order Hold"},
    {"id": "3", "l": "First Order Hold1"},
    {"id": "4", "l": "First Order Hold2"},
    {"id": "5", "l": "Subsystem"}
  ],
  "edges": [
    {"s": "2", "t": "5", "l": "0_5#in:1"},
    {"s": "5", "t": "3", "l": "1_3#in:1"},
    {"s": "5", "t": "4", "l": "2_4#in:1"}
  ]
}            
             """},
            {"role": "user", "content": "以下是你需要进行分析的内容:"+content}
        ]
        # n=1,
        # response_format="json"

    )

    print(completion.choices[0].message.content)
    return str(completion.choices[0].message.content)


def abstract_multinfo_byimage(base64_image):
    '''
    利用GPT-4o模型进行实体抽取
    base64_image: str base64编码的图片
    '''

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": """
                     请用json语言描述以下多信号流图，不要附带多余信息
                     如例子 
                     {
    "nodes": [
        {"id": "A", "label": "故障"},
        {"id": "B", "label": "RTU1"},
        {"id": "C", "label": "RTU2"},
        {"id": "D", "label": "测试"},
        {"id": "E", "label": "RTU供电线路"}
    ],
    "edges": [
        {"from": "A", "to": "B", "label": "IN 1"},
        {"from": "A", "to": "B", "label": "IN 2"},
        {"from": "A", "to": "B", "label": "IN 3"},
        {"from": "A", "to": "C", "label": "IN 1"},
        {"from": "A", "to": "C", "label": "IN 2"},
        {"from": "A", "to": "C", "label": "IN 3"},
        {"from": "B", "to": "D", "label": "OUT 1"},
        {"from": "B", "to": "D", "label": "OUT 2"},
        {"from": "B", "to": "D", "label": "OUT 3"},
        {"from": "B", "to": "D", "label": "OUT 4"},
        {"from": "C", "to": "D", "label": "OUT 1"},
        {"from": "C", "to": "D", "label": "OUT 2"},
        {"from": "C", "to": "D", "label": "OUT 3"},
        {"from": "C", "to": "D", "label": "OUT 4"},
        {"from": "E", "to": "B", "label": "IN 1"},
        {"from": "E", "to": "C", "label": "IN 2"}
    ]
}

                     """},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ]
    )
    print(completion.choices[0].message.content)
    return str(completion.choices[0].message.content)


if __name__ == "__main__":

    def test1_analyse_multiinfo():
        content = "如果空速管发生故障 根据多信号流图 那么哪些部件发生故障"
        analyse_multiinfo(content)

    # test1_analyse_multiinfo()

    def test2_analyse_multiinfo():
        content = "甚高频通信收发机型号是VHF-4000，由RC提供。VHF-4000是多信道的收发机，能够提供118.00MHz到136.975MHz频率范围内的DSB（双边带）AM（调幅）音频通信，并能提供25KHz和8.33KHz的频道间隔选择。"
        abstract_multiinfo(content)

    def test3_abstract_multinfo_byimage():
        image_file = r"D:\Document\Study\PGY-2_project\1.Ground-based-inference-and-intelligent-maintenance-support-subsystems\SourceCode\multiFlowGraph\platform\test_data\image\1.jpg"
        with open(image_file, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode()
        abstract_multinfo_byimage(base64_image)

    def test4_abstract_multinfo_bytext():
        content = "甚高频通信收发机型号是VHF-4000，由RC提供。VHF-4000是多信道的收发机，能够提供118.00MHz到136.975MHz频率范围内的DSB（双边带）AM（调幅）音频通信，并能提供25KHz和8.33KHz的频道间隔选择。"
        ans = abstract_multiinfo_bytext(content)
        print(json.loads(ans))
        print(ans)

    test4_abstract_multinfo_bytext()
    # test2_analyse_multiinfo()
    # test3_abstract_multinfo_byimage()
