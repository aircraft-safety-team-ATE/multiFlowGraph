import json
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from typing import Dict
from flask import request, jsonify, send_file, Flask, make_response, send_from_directory
from .utils import convert_fmeca, flatten_graph, reconstruct_graph, to_D_mat, \
    detect_with_render, to_json, from_json, check_graph, \
    optimize_struct
from .simulinkReader import simulink_reader
from .msfg_gpt import analyse_multiinfo, abstract_multiinfo_bytext, abstract_multinfo_byimage
from werkzeug.utils import secure_filename
import os
EPS = 1e-9
DEFAULT_P = 0.2


def upload_fmeca():
    graphStruct = pd.read_excel(
        request.files.get("modelFile"), sheet_name="body")
    struct = convert_fmeca(graphStruct)
    print(struct)
    return json.dumps({
        "currentSystemId": 1,
        "SystemData": struct
    }).replace("NaN", "null")
    # return "hellow"


def upload_simulink():
    file = request.files.get("modelFile")
    if file:
        content = file.readlines()
        content = [byte.decode('utf-8') for byte in content]
        G_DATA = simulink_reader(content)
        # print(G_DATA)
        return json.dumps(G_DATA).replace("NaN", "null")


def optimize_graph():
    graphStruct = json.loads(request.form.get("graphStruct"))
    if isinstance(graphStruct, Dict):
        graphStruct = graphStruct["SystemData"]
    struct = optimize_struct(graphStruct)
    return json.dumps({
        "data": struct
    }).replace("NaN", "null")


def service_to_D_mat():
    struct = json.loads(request.form.get("graphStruct"))
    if isinstance(struct, Dict):
        struct = struct["SystemData"]
    nodes, edges, system = flatten_graph(struct)
    D_mat, testName, faultName, ConnIds, testLoc, faultLoc, sysmap, collision_node, _ = to_D_mat(
        nodes, edges, system, eps=EPS, raise_collision=False)
    return to_json(D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName, collision_node, ConnIds)


def app_check_graph():
    struct = json.loads(request.form.get("graphStruct"))
    if isinstance(struct, Dict):
        struct = struct["SystemData"]
    nodes, edges, system = flatten_graph(struct)
    D_mat, testName, faultName, ConnIds, testLoc, faultLoc, sysmap, collision_node, _ = to_D_mat(
        nodes, edges, system, eps=EPS, raise_collision=False)
    # print(D_mat)
    structJson = to_json(D_mat, struct, testLoc, faultLoc,
                         sysmap, testName, faultName, collision_node, ConnIds)
    # structJson = request.form.get("convertedStruct")
    info = check_graph(structJson, eps=EPS)
    return json.dumps(info).replace("NaN", "null")


def _fuse_p(testPs, defaultP=0.2):
    if len(testPs) == 0:
        return defaultP
    elif len(testPs) <= 2:
        return np.mean(testPs)
    else:
        testPs = np.array(testPs, dtype="float32")
        testPw = np.abs(testPs - np.median(testPs))
        testPwExp = np.exp(-testPw/testPw.max())
        testPw = testPwExp/testPwExp.sum()
        return sum(testPs*testPw)


def _washItm(testName, values, defaultP=0.2):
    testValues = {testN: [] for testN in testName}
    for ckptn, p in values:
        if ckptn in testValues.keys():
            testValues[ckptn].append(p)
    return np.array([_fuse_p(testValues[testN], defaultP=defaultP) for testN in testName], dtype="float32")


def result_analyse_main():
    struct = json.loads(request.form.get("graphStruct"))
    if isinstance(struct, Dict):
        struct = struct["SystemData"]
    nodes, edges, system = flatten_graph(struct)
    D_mat, testName, faultName, ConnIds, testLoc, faultLoc, sysmap, collision_node, _ = to_D_mat(
        nodes, edges, system, eps=EPS, raise_collision=False)
    # D_mat, struct, testLoc, faultLoc, sysmap, testName, faultName, ConnIds = from_json(request.form.get("convertedStruct"))
    p_test = _washItm(
        testName,
        [[itm["text"], itm["state"]] for itm in pd.read_csv(request.files.get(
            "dataFile"), header=0, encoding="gbk").T.to_dict().values()],
        defaultP=DEFAULT_P)
    struct = detect_with_render(
        p_test, D_mat, struct, testLoc, faultLoc, sysmap, ConnIds)
    return json.dumps({
        "data": struct
    }).replace("NaN", "null")


def GPT_analyse():
    content = request.form.get("content")
    struct = json.loads(request.form.get("struct"))

    content = analyse_multiinfo(content)

    return json.dumps({"result": content})


def abstractGraphByText():
    content = request.form.get("content")
    struct = json.loads(request.form.get("struct"))

    content = abstract_multiinfo_bytext(content)

    return json.dumps({"result": content})


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file():
    if request.method == 'OPTIONS':
        response = make_response('')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        return response, 200
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 打印此刻程序运行

        file_path = os.getcwd() + '/uploads/' + filename
        file.save(file_path)

        # 读取文件并转换为Base64
        with open(file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode()
        result = abstract_multinfo_byimage(base64_image)
        return jsonify({'filename': filename, 'result': result}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400


def uploaded_file(filename):
    return send_from_directory(os.getcwd() + '/uploads/', filename)


def msfg_route_app(app):
    app.route("/multi-info-edit/upload-fmeca/", methods=['POST'])(upload_fmeca)
    app.route("/multi-info-edit/upload-simulink/",
              methods=['POST'])(upload_simulink)
    app.route("/multi-info-edit/optimize-graph/",
              methods=['POST'])(optimize_graph)
    app.route("/multi-info-edit/check-graph/",
              methods=['POST'])(app_check_graph)
    app.route("/multi-info-edit/convert-graph/",
              methods=['POST'])(service_to_D_mat)
    app.route("/multi-info-analyse/analyse-data/",
              methods=['POST'])(result_analyse_main)
    app.route("/multi-info-GPT/analyse-data/",
              methods=['POST'])(GPT_analyse)
    app.route("/multi-info-GPT/abstract-graph-by-text/",
              methods=['POST'])(abstractGraphByText)
    app.route("/upload/",
              methods=['POST', 'OPTIONS'])(upload_file)
    app.route("/uploads/<filename>",
              methods=['GET'])(uploaded_file)
