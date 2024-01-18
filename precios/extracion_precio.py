import pandas as pd

fila_inicial_fijo = 1
fila_inicial_indexado = 3

fijo = pd.read_excel('datos/precios_luz.xlsx', sheet_name='FIJO', skiprows=fila_inicial_fijo).iloc[:,2:]
indexado_energia = pd.read_excel('datos/precios_luz.xlsx', sheet_name='INDEXADO', skiprows=fila_inicial_indexado).iloc[:,1:12]
indexado_potencia = pd.read_excel('datos/precios_luz.xlsx', sheet_name='INDEXADO', skiprows=fila_inicial_indexado).iloc[:,13:24]
indexado_potencia = indexado_potencia.dropna()

nombres_columnas_energia = ['SISTEMA', 'TARIFA', 'CIA', 'MES', 'FEE', 'P1.', 'P2.', 'P3.', 'P4.', 'P5.', 'P6.']
nombres_columnas_potencia = ['SISTEMA', 'CIA', 'PRODUCTO', 'PRODUCTO_CIA', 'TARIFA', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6']
nombres_columnas_energia = [elemento.lower() for elemento in nombres_columnas_energia]
nombres_columnas_potencia = [elemento.lower() for elemento in nombres_columnas_potencia]


# Asigna los nombres de las columnas a los DataFrames
indexado_energia.columns = nombres_columnas_energia
indexado_potencia.columns = nombres_columnas_potencia

columns_to_convert = ['P1.', 'P2.', 'P3.', 'P4.', 'P5.', 'P6.']

for column in columns_to_convert:
    fijo[column] = pd.to_numeric(fijo[column], errors='coerce')

fijo = fijo.rename(columns={'producto cia': 'producto_cia'})

fijo.dropna(inplace=True)
indexado_energia.dropna(inplace=True)
indexado_potencia.dropna(inplace=True)

fijo = fijo.rename(columns={'P1':'p1','P2':'p2','P3':'p3','P4':'p4','P5':'p5','P6':'p6','P1.':'p1_','P2.':'p2_','P3.':'p3_','P4.':'p4_','P5.':'p5_','P6.':'p6_'})
indexado_energia = indexado_energia.rename(columns={'p1.':'p1_','p2.':'p2_','p3.':'p3_','p4.':'p4_','p5.':'p5_','p6.':'p6_'})
indexado_potencia = indexado_potencia.rename(columns={'p1':'p1','p2':'p2','p3':'p3','p4':'p4','p5':'p5','p6':'p6'})

fijo.to_csv('datos/fijo.csv',index=False)
indexado_energia.to_csv('datos/indexado_energia.csv',index=False)
indexado_potencia.to_csv('datos/indexado_potencia.csv',index=False)

from sqlalchemy import create_engine
import psycopg2

user = 'postgres'
password = 'DesafioNG1'
host = '35.241.146.138'
port = '5432' 
database = 'postgres'

connection_string = f'postgresql://{user}:{password}@{host}:{port}/{database}'
engine = create_engine(connection_string)


fijo.to_sql('precios_fijo', con=engine, if_exists='replace', index=False)


indexado_energia.to_sql('precios_index_energia', con=engine, if_exists='replace', index=False)


indexado_potencia.to_sql('precios_index_potencia', con=engine, if_exists='replace', index=False)