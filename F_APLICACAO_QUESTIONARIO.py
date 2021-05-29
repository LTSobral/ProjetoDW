import pandas as pd
import time

def extract_fact_aplicacao_questionario(conn):
    sql_questionario = '''
    select "ID_ESCOLA", "ID_ALUNO", "ID_MUNICIPIO", "ID_PROVA_BRASIL", "IN_PREENCHIMENTO", 
    "IN_PROFICIENCIA", "PROFICIENCIA_LP_SAEB", "DESVIO_PADRAO_LP_SAEB", 
    "PROFICIENCIA_MT_SAEB", "DESVIO_PADRAO_MT_SAEB"
    FROM "STAGED".resultado_aluno
    '''

    sql_localidade = '''
    select "SK_LOCALIDADE", "CD_MUNICÍPIO"
    FROM "DW"."D_LOCALIDADE"
    '''

    sql_escola = '''
    select "SK_ESCOLA", "CD_ESCOLA"
    FROM "DW"."D_ESCOLA"
    '''

    sql_aluno = '''
    select "SK_TURMA", "CD_ALUNO"
    FROM "DW"."D_TURMA"
    '''

    localidade_tbl = pd.read_sql_query(sql_localidade, conn)

    escola_tbl = pd.read_sql_query(sql_escola, conn)

    turma_tbl = pd.read_sql_query(sql_aluno, conn)

    questionario_tbl = pd.read_sql_query(sql_questionario, conn)

    return localidade_tbl, escola_tbl, turma_tbl, questionario_tbl


def treat_fact_aplicacao_questionario(localidade_tbl, escola_tbl, turma_tbl,
                                     questionario_tbl):
    questionario_tbl = questionario_tbl.merge(localidade_tbl, left_on="ID_MUNICIPIO",
                               right_on="CD_MUNICÍPIO")

    questionario_tbl = questionario_tbl.merge(escola_tbl, left_on="ID_ESCOLA",
                                            right_on="CD_ESCOLA")

    questionario_tbl = questionario_tbl.merge(turma_tbl, left_on="ID_ALUNO",
                                            right_on="CD_ALUNO")

    del questionario_tbl['ID_ALUNO']
    del questionario_tbl['ID_MUNICIPIO']
    del questionario_tbl['ID_ESCOLA']
    del questionario_tbl['CD_ALUNO']
    del questionario_tbl['CD_ESCOLA']
    del questionario_tbl['CD_MUNICÍPIO']

    questionario_tbl = questionario_tbl.rename(columns={'ID_PROVA_BRASIL': 'CD_ANO',
         'IN_PREENCHIMENTO': 'FL_PREENCHIMENTO',
         'IN_PROFICIENCIA': 'FL_PROFICIÊNCIA',
         'PROFICIENCIA_LP_SAEB': 'VL_PROFICIÊNCIA_LÍNGUA_PORTUGUESA_SAEB',
         'DESVIO_PADRAO_LP_SAEB': 'VL_DESVIO_PADRAO_LÍNGUA_PORTUGUESA_SAEB',
         'PROFICIENCIA_MT_SAEB': 'VL_PROFICIÊNCIA_MATEMÁTICA_SAEB',
         'DESVIO_PADRAO_MT_SAEB': 'VL_DESVIO_PADRAO_MATEMÁTICA_SAEB'})

    questionario_tbl['FL_PROFICIÊNCIA'] = questionario_tbl['FL_PROFICIÊNCIA'].apply(lambda x: True
            if x == 1 else False)

    questionario_tbl['FL_PREENCHIMENTO'] = questionario_tbl['FL_PREENCHIMENTO'].apply(lambda x: True
            if x == 1 else False)

    questionario_tbl['VL_PROFICIÊNCIA_LÍNGUA_PORTUGUESA_SAEB'] = questionario_tbl[
        'VL_PROFICIÊNCIA_LÍNGUA_PORTUGUESA_SAEB'].str.replace(',', '.')

    questionario_tbl['VL_DESVIO_PADRAO_LÍNGUA_PORTUGUESA_SAEB'] = questionario_tbl[
        'VL_DESVIO_PADRAO_LÍNGUA_PORTUGUESA_SAEB'].str.replace(',', '.')

    questionario_tbl['VL_PROFICIÊNCIA_MATEMÁTICA_SAEB'] = questionario_tbl[
        'VL_PROFICIÊNCIA_MATEMÁTICA_SAEB'].str.replace(',', '.',)

    questionario_tbl['VL_DESVIO_PADRAO_MATEMÁTICA_SAEB'] = questionario_tbl[
        'VL_DESVIO_PADRAO_MATEMÁTICA_SAEB'].str.replace(',', '.')

    questionario_tbl['VL_DESVIO_PADRAO_MATEMÁTICA_SAEB'] = pd.to_numeric(
        questionario_tbl['VL_DESVIO_PADRAO_MATEMÁTICA_SAEB'], errors='coerce')

    questionario_tbl['VL_PROFICIÊNCIA_MATEMÁTICA_SAEB'] = pd.to_numeric(
        questionario_tbl['VL_PROFICIÊNCIA_MATEMÁTICA_SAEB'], errors='coerce')

    questionario_tbl['VL_DESVIO_PADRAO_LÍNGUA_PORTUGUESA_SAEB'] = pd.to_numeric(
        questionario_tbl['VL_DESVIO_PADRAO_LÍNGUA_PORTUGUESA_SAEB'], errors='coerce')

    questionario_tbl['VL_PROFICIÊNCIA_LÍNGUA_PORTUGUESA_SAEB'] = pd.to_numeric(
        questionario_tbl['VL_PROFICIÊNCIA_LÍNGUA_PORTUGUESA_SAEB'], errors='coerce')

    return questionario_tbl

def load_fact_aplicacao_quetionario(fact_aplicacao_questionario, conn):
        fact_aplicacao_questionario = fact_aplicacao_questionario.grc
        fact_aplicacao_questionario.loc[temp: temp2].to_sql(
                            name='F_APLICAÇÃO_QUESTIONARIO', con=conn, schema='DW',
                            if_exists='replace', index=False, chunksize=100)



def run_fact_aplicacao_questionario(conn):
    start_time = time.time()
    localidade_tbl, escola_tbl, turma_tbl, questionario_tbl = \
        extract_fact_aplicacao_questionario(conn)

    extract_time = time.time()
    print('"F_Questionario" - extract: ', extract_time - start_time)

    fact_questionario = treat_fact_aplicacao_questionario(localidade_tbl,
        escola_tbl,
        turma_tbl,
        questionario_tbl)
    treat_time = time.time()
    print('treat: ', treat_time - extract_time)

    load_fact_aplicacao_quetionario(fact_questionario, conn)
    load_time = time.time()
    print('load: ', load_time - treat_time)

    return load_time - start_time
