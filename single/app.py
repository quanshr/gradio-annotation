import gradio as gr
import os
import pandas as pd
import sys
import random
import shutil
from make_excel import make_excel, dump_excel
import logging
import string

# 配置日志系统，将日志输出到文件
logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO)

# 创建日志记录器
logger = logging.getLogger(__name__)

def find_next_punctuation(text, start=0):
    # 定义标点符号集合
    punctuations = string.punctuation + '、；;，,。.！!？? \n'
    # 从指定的起始位置开始查找标点符号
    for index in range(start, len(text)):
        if text[index] in punctuations:
            return index  # 找到标点符号，返回索引
    return -1  # 没有找到标点符号，返回-1



def search(excel, character, session_id):
    def search_one(excel, character, session_id, depth=0):
        try:
            if excel == '所有':
                now_excel = random.choice(os.listdir('excels'))
            else:
                now_excel = excel + '.xlsx'
            if session_id == '所有':
                df = pd.read_excel(f"excels/{now_excel}")
                index = random.randint(0, len(df) - 1)
                row = df.iloc[index]
            else:
                df = pd.read_excel(f"excels/{now_excel}")
                index = df[df['session_id'] == session_id].index[0]
                row = df.iloc[index]
            if row["dataflow"] == '仅保存' and (character == '所有' or character != '所有' and \
                 (character in row['settings'] or lower(character) in row['settings'])):
                if row['comments'] != row['comments'] or row['comments'] == 'nan':
                    row['comments'] = ''
                return now_excel[:-5], index, row['session_id'], row['comments'], row['session'], row['session_revise'], \
                    gr.Radio(['仅保存', '低', '中', '高', 'excel低', 'excel中', 'excel高'], value='仅保存', label="数据流"), \
                    row['settings'], gr.Textbox(visible=False)
        except Exception as e:
            pass
        if depth > 200:
            return '似乎没有符合条件的数据', -1, '', '', '', '', gr.Radio(['仅保存', '低', '中', '高', 'excel低', 'excel中', 'excel高'], value='仅保存', label="数据流"), '', gr.Textbox(visible=False)
        return search_one(excel, character, session_id, depth + 1)
    return search_one(excel, character, session_id)

def submit(excel, index, comments, ckbox, session_revise):
    logger.info(f'Submit {excel} {index} !!')
    df = pd.read_excel(f"excels/{excel}.xlsx")
    df.at[index, 'comments'] = comments
    df.at[index, 'session_revise'] = session_revise
    if session_revise != df.at[index, 'session']:
        df.at[index, 'is_change'] = 1
    if ckbox[:5] == 'excel':
        ckbox = ckbox[5:]
        for index, row in df.iterrows():
            df.at[index, 'dataflow'] = ckbox
    else:
        df.at[index, 'dataflow'] = ckbox
    df.to_excel(f"excels/{excel}.xlsx")
    return gr.Textbox(visible=True, value="提交成功")

def upload(excel):
    def to_turn(text):
        excels, session_ids, characters = prepare()
        return gr.Textbox(visible=True, value=text), gr.Dropdown(['所有'] + excels, value='所有', label="Excel"), \
            gr.Dropdown(['所有'] + characters, value='所有', label="性格"), gr.Dropdown(['所有'] + session_ids, value='所有', label="data_id")

    if excel is None or len(excel) < 5 or excel[-5:] != '.xlsx':
        excels, session_ids, characters = prepare()
        return to_turn('上传失败，请选择.xlsx文件')
    save_path = 'rawdata'
    logger.info(f'Upload {excel.split("/")[-1]} !!')
    if os.path.exists(os.path.join('excels', excel.split('/')[-1])):
        return to_turn('上传失败，文件已存在')
    shutil.copy(excel.name, save_path)
    try:
        shutil.copy(excel.name, save_path)
        make_excel(excel.split('/')[-1])
    except Exception as e:
        logger.error(e)
        return to_turn('上传失败，请检查excel格式')
    return to_turn('上传成功')

def generate(excel):
    logger.info(f'Generate {excel} !!')
    dump_excel(excel)
    return os.path.join('download', excel + '.xlsx')


def prepare():
    os.makedirs('rawdata', exist_ok=True)
    os.makedirs('excels', exist_ok=True)
    os.makedirs('download', exist_ok=True)
    
    excels = [x[:-5] for x in os.listdir('excels')]
    session_ids = []
    characters = set()
    for k1 in ['E', 'I']:
        for k2 in ['N', 'S']:
            for k3 in ['F', 'T']:
                for k4 in ['P', 'J']:
                    characters.add(k1 + k2 + k3 + k4)
    for excel in excels:
        df = pd.read_excel(f"excels/{excel}.xlsx")
        for index, row in df.iterrows():
            src = row['settings']
            begin_position = src.find('性格是')
            if begin_position != -1:
                begin_position += 3
                while True:
                    next_position = find_next_punctuation(src, begin_position)
                    characters.add(src[begin_position:next_position])
                    if src[next_position] != '、':
                        break
                    begin_position = next_position + 1
        session_ids += list(df['session_id'])
    excels.sort()
    session_ids = list(set(session_ids))
    session_ids.sort()
    characters = list(characters)
    characters.sort()
    return excels, session_ids, characters


if __name__ == '__main__':
    excels, session_ids, characters = prepare()

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                upexcel = gr.components.File(label="上传或下载excel")
            with gr.Column():
                with gr.Row():
                    up_btn = gr.Button("上传excel")
                    is_uploaded = gr.Textbox(visible=False)
                with gr.Row():
                    gen_btn = gr.Button("生成当前展示excel的下载文件")

        with gr.Row():
            with gr.Column():
                excel = gr.Dropdown(['所有'] + excels, value='所有', label="Excel")
            with gr.Column():
                character = gr.Dropdown(['所有'] + characters, value='所有', label="性格")
            with gr.Column():
                session_id = gr.Dropdown(['所有'] + session_ids, value='所有', label="data_id")
        search_btn = gr.Button("查询")
        index = gr.Number(label="Index", visible=False)
        with gr.Row():
            with gr.Column():
                excel_out = gr.Textbox(label="Excel")
            with gr.Column():
                session_id_out = gr.Textbox(label="data_id")

        with gr.Row():
            settings = gr.Textbox(label="settings")

        with gr.Row():
            with gr.Column():
                session = gr.Textbox(label="session")
            with gr.Column():
                session_revise = gr.Textbox(label="session_revise")

        comments = gr.Textbox(label="Comments")
        ckbox = gr.Radio(['仅保存', '低', '中', '高', 'excel低', 'excel中', 'excel高'], value='仅保存', label="数据流")
        with gr.Row():
            with gr.Column(scale=10):
                submit_btn = gr.Button("提交")
            with gr.Column(scale=1):
                is_submitted = gr.Textbox(visible=False)


        search_btn.click(fn=search,
                        inputs=[excel, character, session_id],
                        outputs=[excel_out, index, session_id_out, comments, session, session_revise, ckbox, settings, is_submitted])
        submit_btn.click(fn=submit, inputs=[excel_out, index, comments, ckbox, session_revise], outputs=[is_submitted])
        up_btn.click(fn=upload, inputs=[upexcel], outputs=[is_uploaded, excel, character, session_id])
        gen_btn.click(fn=generate, inputs=[excel_out], outputs=[upexcel])

    # demo.launch()
    logger.info(f'Start server at http://0.0.0.0:8788')
    demo.launch(server_name="0.0.0.0", server_port=8788)
