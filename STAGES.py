import pandas as pd
import sqlalchemy as sa

def create_stg_tables_from_csv(path_location, delimiter, conn_output, coding, table_name):
    df = pd.read_csv(path_location, sep=delimiter, low_memory=False,
                                encoding=coding).to_sql(name=table_name, con=conn_output,
                                    schema='STAGED', if_exists='replace', chunksize=100)
