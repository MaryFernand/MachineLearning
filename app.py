import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta

# Carregar o modelo salvo
modelo = joblib.load('modelo_xgboost.pkl')

st.title("Previsão de Quantidade de Refeições")

# Dicionário para traduzir dias da semana
dias_semana_pt = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

# Dicionário para traduzir meses para português
meses_pt = {
    'January': 'Janeiro',
    'February': 'Fevereiro',
    'March': 'Março',
    'April': 'Abril',
    'May': 'Maio',
    'June': 'Junho',
    'July': 'Julho',
    'August': 'Agosto',
    'September': 'Setembro',
    'October': 'Outubro',
    'November': 'Novembro',
    'December': 'Dezembro'
}

# Função para obter os últimos n dias úteis antes de uma data base
def dias_uteis_anteriores(data_base, n=5):
    dias_uteis = []
    delta = timedelta(days=1)
    atual = data_base - delta
    while len(dias_uteis) < n:
        if atual.weekday() < 5:  # 0=segunda, 4=sexta
            dias_uteis.append(atual)
        atual -= delta
    return dias_uteis

# Seletor de data base da previsão
data_base = st.date_input("Selecione a data da previsão:", datetime.today())

# Imprime o dia do mês e o dia da semana em português para conferência
nome_mes_escolhido = meses_pt[data_base.strftime("%B")]
nome_dia_escolhido = dias_semana_pt[data_base.strftime("%A")]
st.markdown(f"**Data selecionada:** {data_base.day} de {nome_mes_escolhido} ({nome_dia_escolhido})")

# Determinar automaticamente o dia da semana e o mês (para o modelo)
dia_semana = data_base.weekday()  # 0=segunda, 6=domingo
mes = data_base.month

# Checkbox para Férias
ferias = st.checkbox('Período de férias?')

# Radio exclusivo para condição do feriado
feriado_opcao = st.radio(
    "Selecione a condição em relação ao feriado:",
    ('Nenhuma', 'Feriado', 'Pré-feriado', 'Pós-feriado')
)

# Mapear para variáveis binárias
feriado = 1 if feriado_opcao == 'Feriado' else 0
pre_feriado = 1 if feriado_opcao == 'Pré-feriado' else 0
pos_feriado = 1 if feriado_opcao == 'Pós-feriado' else 0

# Lista amigável para o usuário escolher prato
nomes_visiveis = [
    'Almôndegas de carne', 'Carne ao molho', 'Carne suína',
    'Churrasquinho misto', 'Empadão', 'Estrogonofe de camarão',
    'Estrogonofe de carne', 'Estrogonofe de frango', 'Sem prato (feriado/sábado/domingo)',
    'Frango ao molho', 'Goulash', 'Guisado de lombo',
    'Lasanha de frango', 'Lasanha à bolonhesa', 'Peixe grelhado ao molho',
    'Picadinho', 'Não informado (sem registro)'
]

# As chaves que o modelo espera (mesma ordem dos nomes_visiveis)
chaves_modelo = [
    'prato_almondegas_de_carne', 'prato_carne_ao_molho', 'prato_carne_suina',
    'prato_churrasquinho_misto', 'prato_empadao', 'prato_estrogonofe_de_camarao',
    'prato_estrogonofe_de_carne', 'prato_estrogonofe_de_frango', 'prato_sem_prato',
    'prato_frango_ao_molho', 'prato_goulash', 'prato_guisado_de_lombo',
    'prato_lasanha_de_frango', 'prato_lasanha_a_bolonhesa', 'prato_peixe_grelhado_ao_molho',
    'prato_picadinho', 'prato_nao_informado'
]

# Selectbox para escolher prato
prato_selecionado = st.selectbox(
    "Prato servido (escolha o prato que mais se aproxima do que foi servido):",
    ['Nenhum selecionado'] + nomes_visiveis
)

# Dica opcional sobre prato não informado
if prato_selecionado == 'Não informado (sem registro)':
    st.info("Use esta opção se não souber qual prato foi servido no dia. Não se refere à ausência de opções na lista.")

# Inicializa todos pratos com zero
pratos_input = {chave: 0 for chave in chaves_modelo}

if prato_selecionado != 'Nenhum selecionado':
    idx = nomes_visiveis.index(prato_selecionado)
    pratos_input[chaves_modelo[idx]] = 1

# Coleta das quantidades vendidas nos 5 dias úteis anteriores com dias traduzidos
st.markdown("### Informe as quantidades vendidas nos 5 dias úteis anteriores")
dias_anteriores = dias_uteis_anteriores(data_base)

quantidades = {}
for i, dia in enumerate(reversed(dias_anteriores), 1):
    nome_dia = dias_semana_pt[dia.strftime("%A")]
    data_formatada = dia.strftime("%d/%m/%Y")
    label = f"{nome_dia} ({data_formatada})"
    quantidades[f'POLO_QUANTIDADE_{i}'] = st.number_input(
        label, min_value=0, step=1, format="%d", value=0
    )

# Botão de previsão
if st.button("Prever quantidade"):
    if prato_selecionado == 'Nenhum selecionado':
        st.error("Por favor, selecione o prato servido antes de continuar.")
    elif feriado == 1 or dia_semana in [5, 6]:  # Sábado ou Domingo
        st.warning("Neste dia não há venda de quentinhas.")
        st.success("Previsão da quantidade: 0")
    else:
        entrada = {
            'É_FÉRIAS': int(ferias),
            'FERIADO': int(feriado),
            'PRÉ_FERIADO': int(pre_feriado),
            'PÓS_FERIADO': int(pos_feriado),
            'DIA_SEMANA': dia_semana,
            'MES': mes
        }
        entrada.update(pratos_input)
        entrada.update(quantidades)

        entrada_df = pd.DataFrame([entrada])
        pred = modelo.predict(entrada_df)
        st.success(f'Previsão da quantidade: {pred[0]:.0f}')

# --- RODAPÉ ---
st.markdown("---")

# Texto do rodapé justificado
st.markdown(
    "<p style='text-align: justify;'>"
    "Desenvolvido por Maria Fernanda Machado Santos, bolsista PIBIC/CNPq, "
    "como parte do projeto Aprendizado de Máquina Aplicado à Engenharia, conduzido pelo Instituto Politécnico - UFRJ, "
    "sob orientação da professora Janaina Sant'Anna Gomide Gomes."
    "</p>",
    unsafe_allow_html=True
)

# Imagens lado a lado com altura fixa e largura do container limitada
st.markdown(
    """
    <div style='max-width:700px; margin:auto; display:flex; justify-content:space-between; align-items:center;'>
        <img src='https://raw.githubusercontent.com/MaryFernand/MachineLearning/46bc13fe9f738f650cf352d3bea0c3f485a12555/ufrja.png' style='height:100px; width:auto;'/>
        <img src='https://raw.githubusercontent.com/MaryFernand/MachineLearning/15870cebb871fda086738062b98a31a83039676b/ufrj_macae.png' style='height:100px; width:auto;'/>
        <img src='https://raw.githubusercontent.com/MaryFernand/MachineLearning/15870cebb871fda086738062b98a31a83039676b/instituto_politecnico.png' style='height:100px; width:auto;'/>
        <img src='https://raw.githubusercontent.com/MaryFernand/MachineLearning/15870cebb871fda086738062b98a31a83039676b/cnpq.png' style='height:100px; width:auto;'/>
    </div>
    """,
    unsafe_allow_html=True
)

