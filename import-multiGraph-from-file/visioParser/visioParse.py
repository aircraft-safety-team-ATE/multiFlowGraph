import aspose.diagram
from aspose.diagram import *
# pip install aspose-diagram-python

from zipfile import ZipFile
from io import BytesIO

def _getType(node):
    try:
        return node.props[0].value.val.lower()
    except Exception as e:
        name = node.name
        if "矩形" in name or "rect" in name.lower():
            return "fault"
        elif "圆形" in name or "circle" in name.lower():
            return "test"
        elif "连接线" in name or "connect" in name.lower():
            return "edge"
        else:
            return name.lower()

def parse_visio(path):
    """从visio对应的path/ByteIO中读取单幅流图"""
    with Diagram(path) as diagram:
        result = {"nodes": [], "edges": []}
        for node in diagram.pages[0].shapes:
            type_ =  _getType(node)
            if type_ == "edge":
                edge = node.get_connector_rule()
                result["edges"].append({
                    "from_id": edge.start_shape_id,
                    "to_id":edge.end_shape_id,
                } )
            else:
                result["nodes"].append({
                    "text": node.get_display_text().replace("\n", "").replace("\r",""),
                    "type": type_,
                    "id": node.id,
                } )
        
    return result

def parse_docx_visio(path):
    """从doc/docx对应的path/ByteIO中读取所有visio嵌入的流图"""
    figures = []
    with ZipFile(path, "r") as zipf:
        for entry in zipf.infolist():
            if entry.filename.lower().startswith('word/embeddings') and \
               (entry.filename.lower().endswith('.vsd') or \
                entry.filename.lower().endswith('.vsdx')):
                with BytesIO() as bf:
                    bf.write(zipf.read(entry.filename))
                    bf.seek(0)
                    figures.append(parse_visio(bf))
    return figures

if __name__ == "__main__":
    #result = parse_visio(r"pic.vsd")#r"pic.vsdx"
    res = parse_docx_visio("pic.docx")
