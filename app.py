import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV
import joblib

# Carrega o modelo salvo
modelo = joblib.load('modelo_xgboost.pkl')

st.title("Previsão de Quantidade de Refeições")

# Inputs booleanos
ferias = st.checkbox('Estamos em período de férias?')
feriado = st.checkbox('Hoje é feriado?')
pre_feriado = st.checkbox('É dia anterior a um feriado?')
pos_feriado = st.checkbox('É dia após um feriado?')

# Inputs numéricos
dia_semana = st.slider('Qual o dia da semana? (1=Segunda, 5=Sexta)', 1, 5, 1)
mes = st.slider('Qual o mês do ano?', 1, 12, 1)
dia_semana_modelo = dia_semana - 1  # ajustar para 0-base

pratos = [
    'prato_almôndegas de carne', 'prato_carne ao molho', 'prato_carne suína',
    'prato_churrasquinho misto', 'prato_empadão', 'prato_estrogonofe de camarão',
    'prato_estrogonofe de carne', 'prato_estrogonofe de frango', 'prato_feriado',
    'prato_frango ao molho', 'prato_goulash', 'prato_guisado de lombo',
    'prato_lasanha de frango', 'prato_lasanha à bolonhesa', 'prato_peixe grelhado ao molho',
    'prato_picadinho', 'prato_prato não informado'
]

prato_selecionado = st.selectbox("Prato servido", ['Nenhum selecionado'] + pratos)

# Inicializa todos pratos com zero
pratos_input = {p: 0 for p in pratos}
if prato_selecionado != 'Nenhum selecionado':
    pratos_input[prato_selecionado] = 1

st.markdown("### Quantidades anteriores")
st.write("_Informe as quantidades vendidas nos 5 dias anteriores para cada polo para ajudar na previsão._")
quantidades = {}
for i in range(1, 6):
    quantidades[f'POLO_QUANTIDADE_{i}'] = st.number_input(f'Quantidade do dia -{i}', min_value=0)

if st.button("Prever quantidade"):
    # Monta o dicionário com todas as variáveis no formato esperado pelo modelo
    entrada = {
        'É_FÉRIAS': int(ferias),
        'FERIADO': int(feriado),
        'PRÉ_FERIADO': int(pre_feriado),
        'PÓS_FERIADO': int(pos_feriado),
        'DIA_SEMANA': dia_semana_modelo,
        'MES': mes
    }
    entrada.update(pratos_input)
    entrada.update(quantidades)

    # Transforma em DataFrame para manter ordem e formato (1 linha)
    entrada_df = pd.DataFrame([entrada])

    # Prediz com o modelo (XGBoost geralmente aceita DataFrame)
    pred = modelo.predict(entrada_df)

    st.success(f'Previsão da quantidade: {pred[0]:.0f}')