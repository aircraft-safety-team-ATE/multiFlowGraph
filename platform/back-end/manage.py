import os, json
import pandas as pd
from io import BytesIO
from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
from lib.msfgEngine import multiInfoGraph
from lib.simulinkReader import simulink_reader
app = Flask(__name__, static_folder=os.path.join(r".", "static"), static_url_path='/static')#, template_folder=os.path.join(r".", "templates"), )

CORS(app)

# def after_request(res):
#     res.headers["Access-Control-Allow-Origin"] = "*"
#     res.headers["Access-Control-Allow-Methods"] = "GET,POST"
#     return res

# app.after_request(after_request)

#app.jinja_env.auto_reload = True
#app.config['TEMPLATES_AUTO_RELOAD'] = True
#app.jinja_env.variable_start_string = '||<-EL PSY CONGROO->||'
#app.jinja_env.variable_end_string = '||<-EL PSY CONGROO->||'

# 上传流图配置（[{modelFile： JSON File}] -> axios -> ↓ -> [{nodes:...,edges:...}] -> axios)
@app.route("/multi-info-edit/upload-model/",methods=['POST'])
def upload_multi_info_edit():
    graphStruct = json.load(request.files.get("modelFile"))
    return jsonify(graphStruct)

# 上传流图配置（[{modelFile： CSV File}] -> axios -> ↓ -> [{nodes:...,edges:...}] -> axios)
@app.route("/multi-info-edit/upload-fmeca/",methods=['POST'])
def upload_fmeca():
    graphStruct = pd.read_excel(request.files.get("modelFile"), sheet_name="body")
    MIG = multiInfoGraph()
    MIG.from_fmeca(graphStruct)
    return json.dumps({
        "data": MIG.state["data"],
        }).replace("NaN", "null")

#
@app.route("/multi-info-edit/upload-simulink/", methods=['POST'])
def upload_simulink():
    file = request.files.get("modelFile")
    if file:
        content = file.readlines()
        content = [byte.decode('utf-8') for byte in content]
        G_DATA = simulink_reader(content)
        # print(G_DATA)
        return jsonify({"data": G_DATA})

# 导出流图配置（[{nodes:...,edges:...}] -> axios -> ↓ -> [JSON File(BytesFlow)] -> axios)
@app.route("/multi-info-edit/export-model/",methods=['POST'])
def export_multi_info_edit():
    with BytesIO() as io_out:
        io_out.write(json.dumps(json.loads(request.form.get("modelInfo")), indent=4, ensure_ascii=False).encode())
        io_out.seek(0)
        filename = "多信号流图结构数据.json"
        return send_file(io_out, as_attachment=True, download_name=filename)

# 检查流图配置（[{graphStruct: {nodes:...,edges:...}}] -> axios -> ↓ -> [{data:{nodes:...,edges:...}, ...}] -> axios)
@app.route("/multi-info-edit/optimize-graph/",methods=['POST'])
def optimize_graph():
    graphStruct = json.loads(request.form.get("graphStruct"))
    MIG = multiInfoGraph(graphStruct)
    MIG.optimize_test()
    return json.dumps({
        "data": MIG.state["data"],
        }).replace("NaN", "null")

# 检查流图配置（[{graphStruct: {nodes:...,edges:...}}] -> axios -> ↓ -> [{data:{nodes:...,edges:...}, ...}] -> axios)
@app.route("/multi-info-edit/check-graph/",methods=['POST'])
def check_graph():
    graphStruct = json.loads(request.form.get("graphStruct"))
    MIG = multiInfoGraph(graphStruct)
    return json.dumps({
        "data": MIG.state["data"],
        "D_mat": MIG.D_mat_list,
        "col_names": MIG.ckpts_algos,
        "row_names": MIG.faults,
        "detect_isolat_ratio": MIG.detect_isolat_ratio,
        }).replace("NaN", "null")

# 上传流图配置（[{modelFile： JSON File}] -> axios -> ↓ -> [{nodes:...,edges:...}] -> axios)
@app.route("/multi-info-analyse/upload-model/",methods=['POST'])
def upload_multi_info_analyse():
    graphStruct = json.load(request.files.get("modelFile"))
    return jsonify(graphStruct)

# 更新流图结果（[{graphStruct: {nodes:...,edges:...}, dataFile: File(.csv)}] -> axios -> ↓ -> [{data: {nodes:...,edges:...}, ...}] -> axios)
@app.route("/multi-info-analyse/analyse-data/",methods=['GET','POST'])
def result_analyse_main():
    graphStruct = json.loads(request.form.get("graphStruct"))
    values = dict(map(lambda itm: (itm["text"], itm["state"]), pd.read_csv(request.files.get("dataFile"), header=0, encoding="gbk").T.to_dict().values()))
    MIG = multiInfoGraph(graphStruct)
    MIG.refresh(values)
    return json.dumps(MIG.state).replace("NaN", "null")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IP:Port Configutation")
    parser.add_argument("--addr", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    app.run(host=args.addr, port=args.port, debug=True)
