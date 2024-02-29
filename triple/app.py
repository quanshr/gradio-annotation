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


def search(excel, data_id):
    def search_one(excel, data_id, depth=0):
        try:
            if excel == '所有':
                now_excel = random.choice(os.listdir('excels'))
            else:
                now_excel = excel + '.xlsx'
            df = pd.read_excel(f"excels/{now_excel}")
            df.fillna('', inplace=True)
            if data_id == '所有':
                index = random.randint(0, len(df) - 1)
            else:
                if data_id.isdigit():
                    index = df[df['data_id'] == int(data_id)].index[0]
                else:
                    for ith, row in df.iterrows():
                        if str(row['data_id']) == data_id:
                            index = ith
                            break       
            row = df.iloc[index]
            if row['dataflow'] == '仅保存':
                return now_excel[:-5], index, row['data_id'], row['comments'], row['session_a'], row['session_a_revise'], \
                    row['session_b'], row['session_b_revise'], row['session_c'], row['session_c_revise'], \
                    gr.Radio(['仅保存', '低', '中', '高', 'excel低', 'excel中', 'excel高'], value='仅保存', label="数据流"), \
                    row['settings'], gr.Textbox(visible=False)
        except Exception as e:
            logger.error(e)
            pass
        if depth > 200:
            return '似乎没有符合条件的数据', -1, '', '', '', '', '', '', '', '', gr.Radio(['仅保存', '低', '中', '高', 'excel低', 'excel中', 'excel高'], value='仅保存', label="数据流"), '', gr.Textbox(visible=False)
        return search_one(excel, data_id, depth + 1)
    return search_one(excel, data_id)

def submit(excel, index, comments, ckbox, session_a_revise, session_b_revise, session_c_revise):
    logger.info(f'Submit {excel} {index} !!')
    df = pd.read_excel(f"excels/{excel}.xlsx")
    df.fillna('', inplace=True)
    df.at[index, 'comments'] = comments
    df.at[index, 'session_a_revise'] = session_a_revise
    df.at[index, 'session_b_revise'] = session_b_revise
    df.at[index, 'session_c_revise'] = session_c_revise
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
        excels, data_ids = prepare()
        return gr.Textbox(visible=True, value=text), gr.Dropdown(['所有'] + excels, value='所有', label="Excel"), \
            gr.Dropdown(['所有'] + data_ids, value='所有', label="data_id")

    if excel is None or len(excel) < 5 or excel[-5:] != '.xlsx':
        excels, data_ids = prepare()
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
    return os.path.join('download', f'download_{excel}.xlsx')


def prepare():
    os.makedirs('rawdata', exist_ok=True)
    os.makedirs('excels', exist_ok=True)
    os.makedirs('download', exist_ok=True)
    
    excels = [x[:-5] for x in os.listdir('excels')]
    data_ids = []
    for excel in excels:
        df = pd.read_excel(f"excels/{excel}.xlsx")
        df.fillna('', inplace=True)
        data_ids += list(df['data_id'])
    excels = [str(x) for x in excels]
    excels.sort()
    data_ids = list(set(data_ids))
    data_ids = [str(x) for x in data_ids]
    data_ids.sort()
    return excels, data_ids


if __name__ == '__main__':
    excels, data_ids = prepare()

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column():
                upexcel = gr.components.File(label="上传或下载excel")
            with gr.Column():
                with gr.Row():
                    up_btn = gr.Button("上传excel")
                    is_uploaded = gr.Textbox(visible=False)
                with gr.Row():
                    gen_btn = gr.Button("生成当前查询excel的下载文件")

        with gr.Row():
            with gr.Column():
                excel = gr.Dropdown(['所有'] + excels, value='所有', label="Excel")
            with gr.Column():
                data_id = gr.Dropdown(['所有'] + data_ids, value='所有', label="data_id")
        search_btn = gr.Button("查询")
        index = gr.Number(label="Index", visible=False)
        with gr.Row():
            with gr.Column():
                excel_out = gr.Textbox(label="Excel")
            with gr.Column():
                data_id_out = gr.Textbox(label="data_id")

        with gr.Row():
            settings = gr.Textbox(label="settings")

        with gr.Row():
            with gr.Column():
                session_a = gr.Textbox(label="session_a")
            with gr.Column():
                session_b = gr.Textbox(label="session_b")
            with gr.Column():
                session_c = gr.Textbox(label="session_c")
        with gr.Row():
            with gr.Column():
                session_a_revise = gr.Textbox(label="session_a_revise")
            with gr.Column():
                session_b_revise = gr.Textbox(label="session_b_revise")
            with gr.Column():
                session_c_revise = gr.Textbox(label="session_c_revise")


        comments = gr.Textbox(label="Comments")
        ckbox = gr.Radio(['仅保存', '低', '中', '高', 'excel低', 'excel中', 'excel高'], value='仅保存', label="数据流")
        with gr.Row():
            with gr.Column(scale=10):
                submit_btn = gr.Button("提交")
            with gr.Column(scale=1):
                is_submitted = gr.Textbox(visible=False)


        search_btn.click(fn=search,
                        inputs=[excel, data_id],
                        outputs=[excel_out, index, data_id_out, comments, session_a, session_a_revise, session_b, session_b_revise, session_c, session_c_revise, ckbox, settings, is_submitted])
        submit_btn.click(fn=submit, inputs=[excel_out, index, comments, ckbox, session_a_revise, session_b_revise, session_c_revise], outputs=[is_submitted])
        up_btn.click(fn=upload, inputs=[upexcel], outputs=[is_uploaded, excel, data_id])
        gen_btn.click(fn=generate, inputs=[excel], outputs=[upexcel])

    logger.info(f'Start server at http://0.0.0.0:8789')
    demo.launch(server_name="0.0.0.0", server_port=8789)
