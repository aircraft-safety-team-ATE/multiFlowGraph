import os
import json
import pandas as pd
from io import BytesIO
from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
from lib.msfgEngine import multiInfoGraph
from lib.simulinkReader import simulink_reader
from lib.utils import check_graph, flatten_graph, reconstruct_graph, to_D_mat, detect_by_D_mat, detect_with_render, to_json, convert_fmeca
# , template_folder=os.path.join(r".", "templates"), )
app = Flask(__name__, v=os.path.join(
    r".", "static"), static_url_path='/static')

CORS(app)

# def after_request(res):
#     res.headers["Access-Control-Allow-Origin"] = "*"
#     res.headers["Access-Control-Allow-Methods"] = "GET,POST"
#     return res

# app.after_request(after_request)

# app.jinja_env.auto_reload = True
# app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.jinja_env.variable_start_string = '||<-EL PSY CONGROO->||'
# app.jinja_env.variable_end_string = '||<-EL PSY CONGROO->||'

# 上传流图配置（[{modelFile： JSON File}] -> axios -> ↓ -> [{nodes:...,edges:...}] -> axios)


@app.route("/multi-info-edit/upload-model/", methods=['POST'])
def upload_multi_info_edit():
    graphStruct = json.load(request.files.get("modelFile"))
    return jsonify(graphStruct)

# 上传流图配置（[{modelFile： CSV File}] -> axios -> ↓ -> [{nodes:...,edges:...}] -> axios)


@app.route("/multi-info-edit/upload-fmeca/", methods=['POST'])
def upload_fmeca():
    graphStruct = pd.read_excel(
        request.files.get("modelFile"), sheet_name="body")

    struct = convert_fmeca(graphStruct)

    return jsonify({"data": struct})
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


@app.route("/multi-info-edit/export-model/", methods=['POST'])
def export_multi_info_edit():
    with BytesIO() as io_out:
        io_out.write(json.dumps(json.loads(request.form.get(
            "modelInfo")), indent=4, ensure_ascii=False).encode())
        io_out.seek(0)
        filename = "多信号流图结构数据.json"
        return send_file(io_out, as_attachment=True, download_name=filename)

# 检查流图配置（[{graphStruct: {nodes:...,edges:...}}] -> axios -> ↓ -> [{data:{nodes:...,edges:...}, ...}] -> axios)


@app.route("/multi-info-edit/optimize-graph/", methods=['POST'])
def optimize_graph():
    graphStruct = json.loads(request.form.get("graphStruct"))
    MIG = multiInfoGraph(graphStruct)
    MIG.optimize_test()
    return json.dumps({
        "data": MIG.state["data"],
    }).replace("NaN", "null")

# 检查流图配置（[{graphStruct: {nodes:...,edges:...}}] -> axios -> ↓ -> [{data:{nodes:...,edges:...}, ...}] -> axios)


@app.route("/multi-info-edit/check-graph/", methods=['POST'])
def check_graph_api():
    struct = json.loads(request.form.get("graphStruct"))
    nodes, edges, system = flatten_graph(struct)
    print("nodes", nodes)
    print("edges", edges)
    print("system", system)
    # structInverse = reconstruct_graph(nodes, edges, system)
    D_mat, testName, faultName,ConnIds, testLoc, faultLoc, sysmap, collision_node = to_D_mat(
        nodes, edges, system)
    print("D_mat", D_mat.todense())
    # p_test = (np.random.uniform(0, 1, len(testName)) > 0.5).astype("float32")
    # p_fault, p_fuzzy, sysres = detect_by_D_mat(p_test, D_mat, sysmap)
    # print("P_FAULT:", p_fault.tolist(), "\tP_FUZZY:", p_fuzzy.tolist())
    # structNew = detect_with_render(
    #     p_test, D_mat, struct, testLoc, faultLoc, sysmap, eps=1e-10, n_round=5)
    structJson = to_json(D_mat, struct, testLoc, faultLoc,
                         sysmap, testName, faultName, collision_node, ConnIds)
    checkRes = check_graph(structJson)

    return checkRes

# 上传流图配置（[{modelFile： JSON File}] -> axios -> ↓ -> [{nodes:...,edges:...}] -> axios)


@app.route("/multi-info-analyse/upload-model/", methods=['POST'])
def upload_multi_info_analyse():
    graphStruct = json.load(request.files.get("modelFile"))
    return jsonify(graphStruct)

# 更新流图结果（[{graphStruct: {nodes:...,edges:...}, dataFile: File(.csv)}] -> axios -> ↓ -> [{data: {nodes:...,edges:...}, ...}] -> axios)


@app.route("/multi-info-analyse/analyse-data/", methods=['GET', 'POST'])
def result_analyse_main():
    struct = json.loads(request.form.get("graphStruct"))
    # print(pd.read_csv(
    #     request.files.get("dataFile"), header=0, encoding="gbk").T.to_dict().values())
    # values = dict(map(lambda itm: (itm["text"], itm["state"]), pd.read_csv(
    #     request.files.get("dataFile"), header=0, encoding="gbk").T.to_dict().values()))
    pd_data = pd.read_csv(request.files.get("dataFile"), header=0, encoding="gbk")
    values = pd_data["state"].to_numpy()
    nodes, edges, system = flatten_graph(struct)
    D_mat, testName, faultName,ConnIds, testLoc, faultLoc, sysmap, collision_node = to_D_mat(
        nodes, edges, system)


    new_struct = detect_with_render(
        values, D_mat, struct, testLoc, faultLoc, sysmap)
    if struct == new_struct:
        print("render fail")
        
    return jsonify({"data": new_struct})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IP:Port Configutation")
    parser.add_argument("--addr", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    app.run(host=args.addr, port=args.port, debug=True)
