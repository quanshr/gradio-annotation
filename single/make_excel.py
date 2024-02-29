import pandas as pd
import os



def make_excel(excel):
    # excel = '【导入】UGC-对话构造试标数据50session-1.xlsx'

    df = pd.read_excel(os.path.join('rawdata', excel))
    out_df = pd.DataFrame(columns=['session_id', 'settings', 'session', 'session_revise', 'is_change', \
        'comments', 'dataflow'])

    for index, row in df.iterrows():
        session_id = row['data_id']
        settings = row['system'].replace('<br>', '\n')
        session = ''
        for i in range(1, 16):
            src = row['query' + str(i)]
            if src != src:
                break
            tgt = row['response' + str(i)]
            session += '<turn>' + str(i) + '\n<User>：  ' + src + '\n<Bot>：  ' + str(tgt) + '\n<End>\n\n\n'
        session.replace('<br>', '\n')
        session_revise = session
        is_change = 0
        comments = ''
        dataflow = '仅保存'
        out_df.loc[len(out_df)] = [session_id, settings, session, session_revise, \
            is_change, comments, dataflow]

    out_df.to_excel(os.path.join('excels', excel))


def dump_excel(excel):
    df = pd.read_excel(f"excels/{excel}.xlsx")
    columns = ['data_id', 'settings', 'comments']
    for i in range(1, 16):
        columns += ['query' + str(i), 'response' + str(i), 'response' + str(i) + '_revise', 'is_change' + str(i)]
    
    out_df = pd.DataFrame(columns=columns)
    for index, row in df.iterrows():
        out_df.loc[index] = [row['session_id'], row['settings'], row['comments']] + [''] * 60
        now = 0
        now_revise = 0
        src = row['session']
        src_revise = row['session_revise']
        for i in range(1, 16):
            begin_str = '<turn>' + str(i) + '\n<User>：  '
            p = src.find(begin_str, now)
            if p == -1:
                break
            p_revise = src_revise.find(begin_str, now_revise)
            flg = p_revise
            p += len(begin_str)
            p_revise += len(begin_str)
            q = src.find('\n<Bot>：  ', p)
            q_revise = src_revise.find('\n<Bot>：  ', p_revise)
            out_df.loc[index, 'query' + str(i)] = src[p:q]
            q += len('\n<Bot>：  ')
            q_revise += len('\n<Bot>：  ')
            r = src.find('\n<End>\n', q)
            r_revise = src_revise.find('\n<End>\n', q_revise)
            out_df.loc[index, 'response' + str(i)] = src[q:r]
            out_df.loc[index, 'response' + str(i) + '_revise'] = src_revise[q_revise:r_revise] if flg != -1 else ''
            out_df.loc[index, 'is_change' + str(i)] = 1 if src[p:r] != src_revise[p_revise:r_revise] else 0
            # now = r
            # now_revise = r_revise
    out_df.to_excel(f"download/{excel}.xlsx")


if __name__ == '__main__':
    # make_excel('【导入】UGC-对话构造试标数据50session-1.xlsx')
    # dump_excel('【导入】UGC-对话构造试标数据50session-1')
    excel = '导入任务0-UGC50_2.xlsx'
    excel = '导入UGC-对话构造试标数据50session-1.xlsx'
    make_excel(excel)
    dump_excel(excel.split('.')[0])