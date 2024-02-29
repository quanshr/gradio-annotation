import pandas as pd
import os



def make_excel(excel):
    df = pd.read_excel(os.path.join('rawdata', excel))
    df.fillna('', inplace=True)
    columns = ['data_id', 'settings', 'comments', 'dataflow']
    for x in ['a', 'b', 'c']:
        columns += [f'session_{x}', f'session_{x}_revise']
    out_df = pd.DataFrame(columns=columns)

    for index, row in df.iterrows():
        data_id = row['data_id']
        if 'settings' in row.keys():
            settings = row['settings'].replace('<br>', '\n')
        else:
            settings = ''

        if 'comments' in row.keys():
            comments = row['comments'].replace('<br>', '\n')
        else:
            comments = ''

        session_info = []
        for x in ['a', 'b', 'c']:
            session = ''
            for i in range(16):
                if f'query_{i}' not in row.keys():
                    break
                src = row[f'query_{i}']
                if src != src:
                    break
                tgt = row[f'response_{i}{x}']
                if tgt != tgt:
                    tgt = ''
                session += f'<turn>{i}\n<User>：  {src}\n<Bot>：  {tgt}\n<End>\n\n\n'
            session.replace('<br>', '\n')
            session_revise = session
            session_info += [session, session_revise]
        dataflow = '仅保存'
        out_df.loc[len(out_df)] = [data_id, settings, comments, dataflow] + session_info

    out_df.to_excel(os.path.join('excels', excel))


def dump_excel(excel):
    df = pd.read_excel(f"excels/{excel}.xlsx")
    df.fillna('', inplace=True)
    columns = ['data_id', 'settings', 'comments', 'dataflow']
    for i in range(16):
        columns += ['query' + str(i)]
        for x in ['a', 'b', 'c']:
            columns += [f'response_{i}{x}', f'response_{i}{x}_revise', f'response_{i}{x}_ischange']
    
    out_df = pd.DataFrame(columns=columns)
    for index, row in df.iterrows():
        out_df.loc[index] = [row['data_id'], row['settings'], row['comments'], row['dataflow']] + [''] * (len(columns) - 4)
        for x in ['a', 'b', 'c']:
            src = row[f'session_{x}']
            src_revise = row[f'session_{x}_revise']
            for i in range(16):
                begin_str = '<turn>' + str(i) + '\n<User>：  '
                p = src.find(begin_str)
                if p == -1:
                    break
                p_revise = src_revise.find(begin_str)
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
                out_df.loc[index, f'response_{i}{x}'] = src[q:r]
                out_df.loc[index, f'response_{i}{x}_revise'] = src_revise[q_revise:r_revise] if flg != -1 else ''
                out_df.loc[index, f'response_{i}{x}_ischange'] = 1 if src[p:r] != src_revise[p_revise:r_revise] else 0
    out_df.to_excel(f"download/download_{excel}.xlsx")


if __name__ == '__main__':
    excel = '0202.xlsx'
    make_excel(excel)
    dump_excel(excel.split('.')[0])