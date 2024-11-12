# %% [markdown]
# # 1. Introdução

# %% [markdown]
# Este notebook tem como objetivo realizar uma análise detalhada dos dados relacionados ao registro de consumo dos clientes da empresa *Compass*, juntamente com suas informações cadastrais, a fim de identificar anomalias de
# consumo que indiquem desvios e fraudes. Assim, através desta análise, buscamos entender como esses dados se manifestam nos dados, o que permitirá o desenvolvimento de um modelo preditivo robusto para detectar fraudes, visando, consequentemente, não apenas mitigar riscos, mas também fortalecer e impulsionar o crescimento da empresa.

# %% [markdown]
# ## 1.1. Objetivos

# %% [markdown]
# Os principais objetivos deste notebook são:
# 
# - **Explorar e compreender os dados:** Avaliar a qualidade dos dados de consumo e informações cadastrais.
# - **Identificar anomalias e padrões fraudulentos:** Detectar comportamentos atípicos que possam indicar fraude.
# - **Desenvolver um modelo preditivo:** Criar um modelo capaz de prever possíveis fraudes com base nos padrões identificados.
# - **Gerar insights para a empresa:** Fornecer recomendações que ajudem a melhorar a segurança operacional e a eficiência no monitoramento de consumo.

# %% [markdown]
# # 2. Configuração do Ambiente

# %% [markdown]
# Importando bibliotecas

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
from sklearn.metrics import davies_bouldin_score, silhouette_score, calinski_harabasz_score, make_scorer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV

# %% [markdown]
# Leitura de todos os arquivos CSV

# %%
df_mes1 = pd.read_csv('../data_inteli/month_2.csv')
df_mes2 = pd.read_csv('../data_inteli/month_3.csv')
df_mes3 = pd.read_csv('../data_inteli/month_4.csv')
df_mes4 = pd.read_csv('../data_inteli/month_5.csv')
df_mes5 = pd.read_csv('../data_inteli/month_6.csv')
df_cadastral = pd.read_csv('../data_inteli/informacao_cadastral.csv')

# %% [markdown]
# # 3. Exploração dos Dados
# 

# %% [markdown]
# ## 3.1. Analisando Dados de Consumo

# %% [markdown]
# Combinando as bases de dados mensais em um só DataFrame

# %%
df_combined = pd.concat([df_mes1, df_mes2, df_mes3, df_mes4, df_mes5], ignore_index=True)
df_combined.info()

# %% [markdown]
# Tipo de cada variável

# %%
df_combined.dtypes

# %% [markdown]
# Variáveis categóricas

# %%
categorical_columns = df_combined.select_dtypes(include=['object']).columns
print(categorical_columns)

# %% [markdown]
# Variáveis numéricas

# %%
numerical_columns = df_combined.select_dtypes(include=['int64', 'float64']).columns
print(numerical_columns)

# %% [markdown]
# Obs: "clientIndex" está pontuada como numérica, mas ela é considerada uma variável categórica, tendo em vista o seu objetivo de identificar os tipos de medidores de cada cliente - o que caracteriza um contexto de classificação de equipamento.

# %% [markdown]
# ### 3.1.1. Análise Estatística Descritiva das Variáveis Numéricas

# %% [markdown]
# Apresentando número de valores não nulos, média dos valores, desvio padrão, valor mínimo, primeiro quartil, mediana, terceiro quartil e valor máximo das variáveis.

# %%
df_combined[numerical_columns].describe()

# %% [markdown]
# #### 3.1.1.1. Verificação de Correlações

# %% [markdown]
# Este heatmap ajuda a identificar visualmente as relações entre variáveis numéricas, destacando quais variáveis têm correlações fortes ou fracas entre si, considerando sua matriz. Os valores variam de -1 a 1:
# - 1:  Correlação linear positiva perfeita (quando uma variável aumenta, a outra também aumenta).
# - 0: Nenhuma correlação linear.
# - -1: Correlação linear negativa perfeita (quando uma variável aumenta, a outra diminui).

# %%
df_combined[numerical_columns].corr()

# Visualizando a matriz de correlação com um heatmap
sns.heatmap(df_combined[numerical_columns].corr(), annot=True, cmap='coolwarm')
plt.title("Heatmap de Correlação")
plt.show()


# %% [markdown]
# #### 3.1.1.2. Histograma das Variáveis Numéricas

# %% [markdown]
# Cada histograma mostra a distribuição dos dados em cada uma das suas colunas numérica, indicando quantas vezes (frequência) os valores caem em cada intervalo.

# %%
# Lista de colunas numéricas
numerical_columns = [
    'meterIndex', 'initialIndex', 'pulseCount',
    'gain', 'rssi', 'gatewayGeoLocation.alt',
    'gatewayGeoLocation.lat', 'gatewayGeoLocation.long'
]
# Criar o histograma para as colunas numéricas com melhorias
fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(15, 20))
# Iterar sobre cada coluna numérica e criar um histograma
for i, ax in enumerate(axes.flatten()):
    ax.hist(df_combined[numerical_columns[i]], bins=15, color='skyblue', edgecolor='black')
    ax.set_title(f'Distribuição de {numerical_columns[i]}', fontsize=14)
    ax.set_xlabel(numerical_columns[i], fontsize=12)
    ax.set_ylabel('Frequência', fontsize=12)
    ax.grid(True)
# Ajustar o layout para não sobrepor os gráficos
plt.tight_layout()
plt.show()

# %% [markdown]
# #### 3.1.1.3. Relação entre PulseCount e Gain

# %% [markdown]
# Este gráfico ajuda a visualizar como diferentes combinações de pulsos e ganhos produzem diferentes valores em metros cúbicos e pode destacar áreas de alta ou baixa concentração de valores.

# %%
# Gerando uma grade de valores para pulseCount e gain
pulseCount_range = np.linspace(df_combined['pulseCount'].min(), df_combined['pulseCount'].max(), 100)
gain_range = np.linspace(df_combined['gain'].min(), df_combined['gain'].max(), 100)
pulseCount_grid, gain_grid = np.meshgrid(pulseCount_range, gain_range)

# Calculando o valor em metros cúbicos para cada combinação na grade
meters_cubicos_grid = pulseCount_grid * gain_grid

plt.figure(figsize=(10, 6))

# Gráfico de contorno
contour = plt.contourf(pulseCount_grid, gain_grid, meters_cubicos_grid, cmap='viridis')
plt.colorbar(contour, label='Metros Cúbicos')
plt.title('Gráfico de Contorno: Valor em Metros Cúbicos por PulseCount e Gain')
plt.xlabel('PulseCount')
plt.ylabel('Gain')
plt.grid(True)
plt.show()


# %% [markdown]
# #### 3.1.1.4. Distribuição Geográfica dos Gateways (latitude, longitude e altitude)

# %% [markdown]
# Apresentando relação entre a latitude, a longitude e a altitude da instalação dos gateways.

# %%
plt.figure(figsize=(10, 8))
scatter = plt.scatter(
    df_combined['gatewayGeoLocation.long'], 
    df_combined['gatewayGeoLocation.lat'], 
    c=df_combined['gatewayGeoLocation.alt'],  # Usando a altitude para colorir os pontos
    s=50,  # Tamanho fixo das bolhas (pode ajustar conforme necessário)
    cmap='viridis',  # Colormap para representar a altitude
    alpha=0.7  # Transparência
)

plt.title('Distribuição Geográfica dos Gateways com Altitude')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.colorbar(scatter, label='Altitude')  # Barra de cores para mostrar a escala de altitude
plt.grid(True)
plt.show()

# %% [markdown]
# #### 3.1.1.5. Distribuição do Valor do Medidor e do Valor Inicial do Medidor, Considerando o seu Index

# %% [markdown]
# Relação entre os valores atuais e os valores iniciais dos medidores, por código de cada medidor.

# %%

# Certificando-se de que 'clientIndex' é uma categoria para facilitar a plotagem
df_combined['clientIndex'] = df_combined['clientIndex'].astype('category')

# Criando uma figura com dois subplots
fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 16))

# Plotando initialIndex no primeiro subplot
axes[0].scatter(df_combined['clientIndex'].cat.codes, df_combined['initialIndex'], color='orange', label='Initial Index', alpha=0.6)
axes[0].set_title('Initial Index por clientIndex')
axes[0].set_xlabel('Client Index (Código do Medidor)')
axes[0].set_ylabel('Initial Index')
axes[0].legend(loc='upper right')
axes[0].grid(True)
axes[0].set_xticks(range(len(df_combined['clientIndex'].cat.categories)))
axes[0].set_xticklabels(df_combined['clientIndex'].cat.categories, rotation=90)

# Plotando meterIndex no segundo subplot
axes[1].scatter(df_combined['clientIndex'].cat.codes, df_combined['meterIndex'], color='red', label='Meter Index', alpha=0.6)
axes[1].set_title('Meter Index por clientIndex')
axes[1].set_xlabel('Client Index (Código do Medidor)')
axes[1].set_ylabel('Meter Index')
axes[1].legend(loc='upper right')
axes[1].grid(True)
axes[1].set_xticks(range(len(df_combined['clientIndex'].cat.categories)))
axes[1].set_xticklabels(df_combined['clientIndex'].cat.categories, rotation=90)

# Ajustando o layout para evitar sobreposição de textos
plt.tight_layout()
plt.show()


# %% [markdown]
# #### 3.1.1.6. Consumo de um Cliente ao Longo dos Meses

# %% [markdown]
# Onda de consumo de um determinado cliente ao longo dos cinco meses catalogados.

# %%
# Convertendo a coluna 'date' para datetime 
df_combined['datetime'] = pd.to_datetime(df_combined['datetime'])

# Agrupando o consumo por cliente e por mês
df_combined['month'] = df_combined['datetime'].dt.to_period('M')
consumo_mensal = df_combined.groupby(['clientCode', 'month'])['meterIndex'].sum().reset_index()

# Filtrando por um cliente específico 
cliente_especifico = consumo_mensal[consumo_mensal['clientCode'] == '7f8bffd14d76f3dcf3b4ad036d6df87354f8001d5d084fb94ca3ab39cf3be551']

# Criando o gráfico
plt.figure(figsize=(10, 6))
plt.plot(cliente_especifico['month'].astype(str), cliente_especifico['meterIndex'], marker='o')

plt.title('Consumo Mensal do Cliente ao Longo do Tempo')
plt.xlabel('Mês')
plt.ylabel('Consumo (em unidades)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# %% [markdown]
# ### 3.1.2 Análise Estatística Descritiva das Variáveis Categóricas

# %% [markdown]
# Apresentando número de valores não nulos, número de valores únicos, valor mais frequente (moda) e frequência do valor mais frequente de cada variável.

# %%
df_combined[categorical_columns].describe()

# %% [markdown]
# #### 3.1.2.1. Contagem da Frequência das Variáveis

# %% [markdown]
# Quantas vezes o resultado de cada variável aparece no banco de dados.

# %%
client_code_counts = df_combined['clientCode'].value_counts()
model_counts = df_combined['model'].value_counts()
input_type_counts = df_combined['inputType'].value_counts()
date_time_counts = df_combined['datetime'].value_counts()
meterSN_counts = df_combined['meterSN'].value_counts()


print(client_code_counts)
print(model_counts)
print(input_type_counts)
print(date_time_counts)
print(meterSN_counts)


# %% [markdown]
# #### 3.1.2.2. Distribuição dos Modelos de Equipamento

# %% [markdown]
# Relação entre os dois tipos de modelos catalogados: IG1K-L-v2 e Infinity V2.

# %%
# Contar a frequência de cada modelo de equipamento
model_counts = df_combined['model'].value_counts()

# Plotar o gráfico de pizza
plt.figure(figsize=(8, 8))
plt.pie(model_counts, labels=model_counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Proporção dos Modelos de Equipamento')
plt.show()

# %% [markdown]
# #### 3.1.2.3. Distribuição do Tipo de Leitura por Modelo

# %% [markdown]
# Relacionando o tipo de modelo dos medidores, com o seu tipo de leitura.

# %%
plt.figure(figsize=(10, 6))
sns.countplot(x='inputType', hue='model', data=df_combined)
plt.title('Distribuição do Tipo de Leitura por Modelo')
plt.xlabel('Tipo de Leitura')
plt.ylabel('Contagem')
plt.show()


# %% [markdown]
# #### 3.1.2.4. Tendência de Recepção ao Longo do Tempo por Tipo de Entrada (Agrupado por Semana)

# %% [markdown]
# Relacionando os tipos de entrada dos medidores com os números de recepção, considerando o número total de semanas durante os meses de consumo.

# %%
# Converter 'datetime' para o formato datetime
df_combined['datetime'] = pd.to_datetime(df_combined['datetime'])

# Fazer o resampling (agrupamento por semana)
df_resampled = df_combined.set_index('datetime').groupby('inputType').resample('W').size().unstack(fill_value=0)

# Plotar o gráfico de linhas para cada inputType
plt.figure(figsize=(14, 8))
for input_type in df_resampled.columns:
    sns.lineplot(data=df_resampled, x=df_resampled.index, y=input_type, label=input_type)

plt.title('Tendência de Recepção ao Longo do Tempo por Tipo de Entrada (Agrupado por Semana)')
plt.xlabel('Data de Recepção')
plt.ylabel('Número de Recepções')
plt.legend(title='Tipo de Entrada')
plt.show()

# %% [markdown]
# ## 3.2. Analisando Dados Cadastrais

# %% [markdown]
# Tipo de Cada Variável

# %%
df_cadastral.dtypes

# %% [markdown]
# Variáveis Categóricas

# %%
categorical_columns_cadastral = df_cadastral.select_dtypes(include=['object']).columns
print(categorical_columns_cadastral)

# %% [markdown]
# Variáveis Numéricas

# %%
numerical_columns_cadastral = df_cadastral.select_dtypes(include=['int64', 'float64']).columns
print(numerical_columns_cadastral)

# %% [markdown]
# Obs: "clientIndex" e "condIndex" estão pontuadas como numéricas, mas elas são consideradas variáveis categóricas, tendo em vista o objetivo da primeira de identificar os tipos de medidores de cada cliente, e o objetivo da segunda de identificar cada condomínio   - o que caracteriza um contexto de classificação de equipamento e moradia.

# %% [markdown]
# ### 3.2.1. Análise Estatística Descritiva das Variáveis

# %% [markdown]
# Apresentando número de valores não nulos, número de valores únicos, valor mais frequente (moda) e frequência do valor mais frequente de cada variável.

# %%
df_cadastral[categorical_columns_cadastral].describe()

# %% [markdown]
# #### 3.2.1.1. Contagem de Frequência das Variáveis

# %% [markdown]
# Quantas vezes o resultado de cada variável aparece no banco de dados.

# %%
# Contando frequência de cada variável 
client_code_counts = df_cadastral['clientCode'].value_counts()
cep_counts = df_cadastral['cep'].value_counts()
bairro_counts = df_cadastral['bairro'].value_counts()
cidade_counts = df_cadastral['cidade'].value_counts()
categoria_counts = df_cadastral['categoria'].value_counts()
contratacao_counts = df_cadastral['contratacao'].value_counts()
situacao_counts = df_cadastral['situacao'].value_counts()
perfil_consumo_counts = df_cadastral['perfil_consumo'].value_counts()
cond_code_counts = df_cadastral['condCode'].value_counts()


print(client_code_counts)
print(cep_counts)
print(bairro_counts)
print(cidade_counts)
print(categoria_counts)
print(contratacao_counts)
print(situacao_counts)
print(perfil_consumo_counts)
print(cond_code_counts)


# %% [markdown]
# #### 3.2.1.2. Distribuição da Situação dos Clientes

# %% [markdown]
# Relação entre os  três tipos de situações de clientes catalogados: Consumindo Gás, Contratado e Desativado.

# %%
# Contar a frequência de cada modelo de equipamento
situacao_counts = df_cadastral['situacao'].value_counts()

# Plotar o gráfico de pizza
plt.figure(figsize=(8, 8))
plt.pie(situacao_counts, labels=situacao_counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Situação dos Clientes')
plt.show()

# %% [markdown]
# #### 3.2.1.3. Distribuição da Situação por Cidade

# %% [markdown]
# Relação entre os três tipos de situação dos clientes (Consumindo Gás, Desativado e Contratado), com as cidades de residência.

# %%
plt.figure(figsize=(14, 7))
sns.countplot(x='cidade', hue='situacao', data=df_cadastral, palette='Set3')
plt.title('Distribuição da Situação por Cidade')
plt.xlabel('Cidade')
plt.ylabel('Contagem')
plt.xticks(rotation=45)
plt.show()


# %% [markdown]
# Obs: dados como "São Leopoldo" e "Gravataí" se repetem como "Sao Leopoldo" e "Gravati" devido a um erro de digitação durante o seu mapeamento, ou seja, é necessário no pré-processamento uma adição das duas categorias em uma só, para uma melhor análise.
# 

# %% [markdown]
# #### 3.2.1.4. Distribuição da Categoria de Cliente

# %% [markdown]
# Relação entre os quatro tipos de clientes catalogados: Prédio Existentes Individual, Res. Unifamiliar, Construtoras Coletivo e Prédios Existentes Coletivo. 

# %%
# Contar a frequência de cada modelo de equipamento
categoria_counts = df_cadastral['categoria'].value_counts()

# Plotar o gráfico de pizza
plt.figure(figsize=(16, 10))
plt.pie(categoria_counts, labels=categoria_counts.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Categoria dos Clientes')
plt.show()

# %% [markdown]
# #### 3.2.1.5. Contratação ao Longo do Tempo

# %% [markdown]
# Evolução das contratações temporais ao longo dos anos (2011 até 2024).

# %%
df_cadastral['contratacao'] = pd.to_datetime(df_cadastral['contratacao'])
df_cadastral.set_index('contratacao').resample('M').size().plot(kind='line', figsize=(16, 6))
plt.title('Evolução Temporal das Contratações')
plt.xlabel('Data')
plt.ylabel('Número de Contratações')
plt.show()

# %% [markdown]
# #### 3.2.1.6. Categorias de Clientes por Perfil de Consumo

# %% [markdown]
# Relação entre os os quatro tipos de clientes catalogados (Prédio Existentes Individual, Res. Unifamiliar, Construtoras Coletivo e Prédios Existentes Coletivo) e os tipos de perfis de consumo (Cocção + Aquecedor, Cocção, Aquecedor, Cocção + Caldeira, Caldeira, Cocção + Aquecedor + Piscina e Vazio)

# %%
plt.figure(figsize=(18, 18))
sns.histplot(data=df_cadastral, x='categoria', hue='perfil_consumo', multiple='fill', palette='Set1')
plt.title('Distribuição Proporcional das Categorias por Perfil de Consumo')
plt.xlabel('Categoria')
plt.ylabel('Proporção')
plt.show()


# %% [markdown]
# # 4. Pré-Processamento

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Toda a seção 2. deste notebook corresponde ao que está presente na seção 4.2.2 da documentação oficial do projeto

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Entende-se por "pré-processamento de dados" o processo responsável por converter dados brutos em dados que podem, de fato, ser utilizados em projetos de análise de dados, sendo essa uma etapa indispensável para a realização da análise e modelagem dos dados. Dessa forma, o pré-processamento se faz importantíssimo, uma vez que utilizar dados não-preparados faz com que os resultados do modelo preditivo fiquem muito aquém do esperado. Portanto, realizar uma boa higienização dos dados garante um processo de modelagem mais confiável e robusto.

# %% [markdown]
# ## 4.1. Combinação de todos os meses em um dataframe
# 

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Os dados que recebemos da empresa parceira estavam pulverizados em 6 arquivos diferentes representando dados de consumo, sendo 1 arquivo para cada mês de consumo, e 1 outro arquivo representando dados cadastrais. Dessa forma, essa seção de processamento foi necessária para juntar todos estes dados em apenas um dataframe. 

# %% [markdown]
# ### 4.1.1. Importação de bibliotecas

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;De maneira inicial, foram importadas 3 principais bibliotecas (Pandas, Numpy e Matplotlib). Além disso, já foi feita a importação o módulo LabelEncoder da biblioteca SciKit Learn.

# %%
## Importação feita na seção 2. deste documento

# %% [markdown]
# ### 4.1.2. Leitura do dicionário de dados

# %%
dicionario = pd.read_excel('../data_inteli/DicionariodeDados.xlsx')
dicionario

# %% [markdown]
# ### 4.1.3. Leitura de todos os arquivos CSV

# %%
df_mes1 = pd.read_csv('../data_inteli/month_2.csv')
df_mes2 = pd.read_csv('../data_inteli/month_3.csv')
df_mes3 = pd.read_csv('../data_inteli/month_4.csv')
df_mes4 = pd.read_csv('../data_inteli/month_5.csv')
df_mes5 = pd.read_csv('../data_inteli/month_6.csv')


# %% [markdown]
# ### 4.1.4. Concatenação de todos os dataframes em um só

# %%
df_combined = pd.concat([df_mes1, df_mes2, df_mes3, df_mes4, df_mes5], ignore_index=True)
df_combined.info()

# %% [markdown]
# ## 4.2. Limpeza, tratamento e normalização dos dados

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Para esta seção, o objetivo é identificar valores que estão faltando nos dados que nos foram passados, bem como identificar valores inconsistentes, duplicados ou fora de escala. Assim, poderemos decidir tratar estes valores por meio de sua remoção ou adequação ao restante do *dataset*.

# %% [markdown]
# ### 4.2.1. Remoção de colunas consideradas inválidas para análise por possuirem, em maioria, valores nulos

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Ao realizar uma análise superficial e com auxílio de ferramentas como leitores de planilhas, identificamos quais colunas seriam descartadas na análise. Nessa busca, percebemos que 4 colunas (gatewayGeoLocation.alt, gatewayGeoLocation.lat, gatewayGeoLocation.long e rssi) possuíam, em sua grande maioria, valores atribuídos como None, ou seja, não possuíam valor. Assim, removemos essas 4 colunas da tabela:

# %%
df_combined = df_combined.drop(columns=['gatewayGeoLocation.alt', 'gatewayGeoLocation.lat', 'gatewayGeoLocation.long', 'rssi'])
df_combined.info()

# %% [markdown]
# ### 4.2.2. Conversão de coluna datetime para tipo datetime

# %%
df_combined['datetime'] = pd.to_datetime(df_combined['datetime'])
df_combined.info()

# %% [markdown]
# ### 4.2.3. Contagem de quantos registros temos para cada medidor diferente

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Outro ponto que percebemos ao realizar uma análise mais superficial é de que existe uma grande discrepância entre a quantidade de leituras de realizadas por tipos de medidores diferentes. Dessa forma, identificamos os dois modelos de medidores presentes na tabela e fizemos a contagem de quantos registros cada um possuia.

# %%
quantidade_infinity = len(df_combined[df_combined['model'] == 'Infinity V2'])
quantidade_ig = len(df_combined[df_combined['model'] == 'IG1K-L-v2'])
print(f"Infinity V2: {quantidade_infinity:.2f}")
print(f"IG1K-L-v2: {quantidade_ig:.2f}")
print(f"Diferença: IG1K-L-v2 possui {quantidade_ig - quantidade_infinity} linhas a mais")

# %% [markdown]
# ### 4.2.4. Faz encodificação ONE HOT com coluna inputType

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;A encodificação One Hot consiste em uma transformação que é aplicada em valores categóricos. Com essa encodificação, é possível criar uma espécie de tabela verdade para as categorias. No nosso caso, realizamos tal encodificação para a coluna 'model', que possui dois valores (Infinity V2 e IG1K-L-v2). Dessa forma, foram criadas duas novas colunas, cada uma com o nome de um dos medidores e contendo um valor booleano. Se o valor booleano for verdadeiro, significa que aquela leitura foi feita com tal medidor. Esta estratégia é adotada para conseguir transformar os valores categóricos dos medidos em numéricos/booleanos.

# %%
df_combined = pd.get_dummies(df_combined, columns=['model'])
df_combined

# %% [markdown]
# ### 4.2.5. Realiza a encodificação por label da coluna inputType
# 

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;A encodificação por Label consiste em determinar um rótulo ou valor numérico para cada tipo de categoria diferente que existe em um dado categórico. No nosso caso, utilizamos esta encodificação para a coluna inputType, que conta com valores como DI1, DI2, etc... Assim, definimos que cada tipo de input seria associado a um valor inteiro onde DI1 = 1, DI2 = 2 e assim em diante.

# %%
encoder = LabelEncoder()

df_combined['inputType_encoded'] = df_combined['inputType'].map({'DI1': 1, 'DI2': 2, 'DI3': 3, 'DI4': 4, 'DI5': 5, 'DI6': 6, 'DI7': 7, 'DI8': 8, 'leituraRemota': 9})

unique_inputType_encoded = df_combined['inputType_encoded'].unique()
for input_type in unique_inputType_encoded:
    first_result = df_combined[df_combined['inputType_encoded'] == input_type].iloc[0]
    print(f"InputType: {first_result['inputType']}, Encoded: {input_type}")

# %%
df_combined = df_combined.drop(columns=['inputType', 'meterSN'])
df_combined

# %% [markdown]
# ### 4.2.6. Encodificação label para clientCode

# %%
df_combined['clientCode_encoded'] = encoder.fit_transform(df_combined['clientCode'])
df_combined[['clientCode', 'clientCode_encoded']]

# %% [markdown]
# ### 4.2.7. Contagem da quantidade de clientes

# %%
len(df_combined['clientCode_encoded'].unique())

# %% [markdown]
# ### 4.2.8. Verificação de valores duplicados

# %%
df_combined.duplicated().sum() 

# %% [markdown]
# ### 4.2.9. Troca valores NaN pela moda da coluna e define todos os 'gain' do medidor Infinity como 0.

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Nesta seção, procuramos por todos os valores NaN existentes no dataframe. Valores NaN representam dados inexistentes ou não definidos. Portanto, é de nosso interesse remover todos do dataframe para que, posteriormente, eles não atrapalhem a modelagem dos dados que temos.

# %%
df_combined.isna().sum()

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;No caso abaixo, percebemo que todas as linhas que possuíam o medidor como Inifinity V2 tinham a coluna *'gain'* inexistente. Dessa forma, substituimos estes valores faltantes por 0.

# %%
df_combined.loc[df_combined['model_Infinity V2'] == True, 'gain'] = 1

# %%
df_combined.isna().sum()
df_combined.fillna(0, inplace=True)
df_combined.isna().sum()

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Por fim, também foi criada uma nova coluna chamada *timestamp*, que contém a data da linha convertida para *Unix Timestamp*, uma medida que conta quandos segundos se passaram de 1 jan. 1970 até o momento.

# %%
df_combined['timestamp'] = df_combined['datetime'].astype('int64') / 10**9
df_combined['timestamp']

# %% [markdown]
# ## 4.3. Calculando o consumo de um cliente em um mês

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Esta seção marca um importante passo na exploração dos dados. Aqui, identificamos como a coluna meterIndex armazena o valor do medidor de uma instalação elétrica, e, com isso, pudemos calcular quantos metros cúbicos um cliente consumiu em um período de tempo e também plotar um gráfico para tal período de consumo.

# %% [markdown]
# ### 4.3.1. Ordenando o consumo em relação a data

# %%
start_date = '2024-02-01'
end_date = '2024-02-28'
client_code = 'e614b6c399945209a71b7119ebb73f7c7e10ec0bded19d907bf8688d0c90a35a' # Substituia pelo clientCode de qualquer cliente
df_filtered = df_combined[(df_combined['datetime'] >= start_date) &
                          (df_combined['datetime'] <= end_date) &
                          (df_combined['clientCode'] == client_code)
                          ]

# %%
df_combined_sorted = df_filtered.sort_values('datetime')

# %% [markdown]
# ### 4.3.2. Calcula o consumo total do mês, usando o valor final menos o valor inicial

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;O cálculo é feito pela variação do meterIndex no mês, ou seja, o último valor do meterIndex no mês menos o primeiro valor.

# %%
first_value = df_combined_sorted.iloc[0]
last_value = df_combined_sorted.iloc[-1]

consume = round((last_value['meterIndex'] - first_value['meterIndex']), 3)
print(f"{consume}m³")

# %% [markdown]
# ### 4.3.3. Cálculo do preço pago pelo consumo (Valor 9.24 fornecido pela Compass)

# %%
price = consume * 9.29
print(f"R${round(price, 2)}")

# %% [markdown]
# ### 4.3.4. Construção do gráfico de consumo de um mês para o cliente específico

# %%
plt.figure(figsize=(20, 6))
plt.plot(df_combined_sorted['datetime'].dt.day, df_combined_sorted['meterIndex'])
plt.xticks(range(1,29,2))
plt.xlabel('Datetime')
plt.ylabel('Meter Index')
plt.title('Meter Index over Time')
plt.show()

# %% [markdown]
# ## 4.4. - Continuação do tratamento e normalização dos dados

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;A partir daqui, já foi realizado boa parte do tratamento da coluna de consumo de gás. Entretanto, alguns passos ainda são necessários para normalizar todos os dados a fim de deixá-los prontos para a modelagem.

# %% [markdown]
# ### 4.4.1. Aplicação de modelo IsolationForest para primeira tentativa de encontrar outliers

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;O modelo de IsolationForest funciona de uma maneira um pouco mais peculiar do que os modelos mais convencionais. Ao invés de tentar encontrar padrões e correlações entre os dados, ele procura encontrar justamente o contrário, ou seja, dados que fogem do padrão. Isso faz dele uma ótima ferramenta para tentar encontrar possíveis *outliers* (dados muito fora dos padrões) na base de dados que possuímos. 

# %%
numeric_columns = ['meterIndex', 'initialIndex', 'pulseCount', 'model_IG1K-L-v2', 'model_Infinity V2', 'inputType_encoded', 'gain', 'timestamp']

# %%
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.01, random_state=42)
df_combined['anomaly'] = model.fit_predict(df_combined[numeric_columns])

# %%
df_combined['anomaly'].value_counts()

# %%
df_combined.info()

# %% [markdown]
# ## 4.5. - Pré-processamento das informações cadastrais

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Na seção anterior, foi feito o pré-processamento das informações de consumo de gás dos clientes da Compass. Nesta seção, será feito o pré-processamento da tabela que contém as informações cadastrais dos clientes. Tais informações são extremamente úteis pois dizem, por exemplo, o tipo de instalação e consumo que cada cliente possui. Além disso, utilizaremos informações como a cidade da instalação e a data para conseguir informações de temperatura.

# %%
df_cadastro = pd.read_csv('../data_inteli/informacao_cadastral.csv')
df_cadastro

# %% [markdown]
# ### 4.5.1. - Drop de colunas que não usaremos

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Retiramos as colunas que não impactariam a análise, sendo elas as colunas 'condCode', 'contratacao' e 'cep'. Identificamos que essas colunas não impactariam inicialmente na análise pois representam dados identificadores que não serão utilizados na modelagem dos dados. Além disso, a coluna de CEP poderia ser descartada uma vez que haviam outras colunas com informações de bairro e cidade.

# %%
df_cadastro.drop(columns=['condCode', 'contratacao', 'cep'], inplace=True)
df_cadastro

# %% [markdown]
# ### 4.5.2. Encodificação One Hot da coluna situação

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Como explicado anteriormente, a encodificação One Hot cria colunas de valores booleanos que formarão uma tabela verdade em relação ao estado da coluna 'situacao'. 

# %%
df_cadastro = pd.get_dummies(df_cadastro, columns=['situacao'])
df_cadastro

# %% [markdown]
# ### 4.5.3. Contagem de valores de cada perfil de consumo

# %%
perfil_consumo_counts = df_cadastro['perfil_consumo'].value_counts()
perfil_consumo_counts

# %% [markdown]
# ### 4.5.4 - Substitui o perfil de consumo "-", desconhecido, por "Cocção + Aquecedor"

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Durante a exploração, identificamos que algumas instalações possuam um perfil de consumo igual a "-". Dessa forma, utilizamos uma estratégia muito comum e substituimos estes valores pela ocorrência mais comum da coluna: "Cocção + Aquecedor".

# %%
df_cadastro['perfil_consumo'] = df_cadastro['perfil_consumo'].replace('-', 'Cocção + Aquecedor')

# %% [markdown]
# ### 4.5.5 Encodificação One Hot da coluna perfil_consumo

# %%
df_cadastro = pd.get_dummies(df_cadastro, columns=['perfil_consumo'])
df_cadastro

# %% [markdown]
# ### 4.5.6 Identificação de categorias mais frequentes que aparecem no dataframe

# %%
categoria_counts = df_cadastro['categoria'].value_counts()
categoria_mais_frequente = categoria_counts.idxmax()
categoria_mais_frequente
categoria_counts

# %% [markdown]
# ### 4.5.7 Contagem de clientcodes unicos

# %%
len(df_combined['clientCode'].unique())

# %% [markdown]
# ### 4.5.8 Identificando se existem linhas com mesmo clientCode porem clientIndex diferentes
# 

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Esse trecho serve para comprovar a hipótese de que existem, na base dados, clientes com mais de uma instalação. 

# %%
df_combined.groupby('clientCode')['clientIndex'].nunique().gt(1).any()

# %% [markdown]
# ### 4.5.9 Identificando instalações unicas (instalação = combinação única entre clientCode e clientIndex)

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Assim como na tabela de consumo, a tabela de dados cadastrais também possui as colunas clientCode e clientIndex. Segundo o dicionário de dados, o clientCode é um valor identificador de um cliente, podendo ser, por exemplo, um CPF. Já o clientIndex é um identificador único para uma instalação de determinado cliente. Dessa forma, podemos entender que podem existir diversas linhas que possuem o mesmo clientCode porém clientIndex diferentes, e isso significa que um mesmo cliente possui mais de uma instalação em seu nome.

# %%
unique_combinations = df_combined.groupby(['clientCode', 'clientIndex']).size()
quantidade_unicas = unique_combinations.count()
print(f"Quantidade de linhas com combinações únicas de clientCode e clientIndex: {quantidade_unicas}")


# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Esse entendimento de que uma instalação é igual a uma combinação única entre clientCode e clientIndex é de extrema importância, uma vez que ele faz com que nós olhemos para a base de dados de maneira diferente. Fazendo uma comparação com um banco de dados relacional, é como se as nossas tabelas possuíssem um conjunto de dois valores que formam uma chave-primária identificadora, e não só um.

# %% [markdown]
# ### 4.5.10 Merge das colunas de cadastro e consumo

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Após finalizarmos o tratamento dos dados da tabela de cadastro, realizamos a junção desses dados com os dados de consumo, relacionando tais dados a partir da relação de clientCode e clientIndex que encontramos anteriormente.

# %%
df_merged = pd.merge(df_combined, df_cadastro, on=['clientCode', 'clientIndex'], how='left')
df_merged

# %% [markdown]
# ### 4.5.11 Corrigindo valores que ficaram sem correspondencia após merge das tabelas

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Um problema que identificamos ao explorar os dados cadastrais foi a falta de dados em relação à tabela de consumo, ou seja, existiam clientes e instalações que possuíam dados de consumo porém não possuíam dados cadastrais. Por conta disso, ao realizar a junção das tabelas, cerca de 117.000 linhas da tabela de consumo ficaram sem correspondência com a tabela de dados cadastrais. Consequentemente, foi necessário realizar uma correção nestes dados. Ademais, vale ressaltar que, por conta de boa parte das colunas que ficaram sem correspondência terem sido encodificadas com o método One Hot, precisamos ajustar cada coluna específica individualmente.

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Definimos que toda linha que estivesse sem valor de situação de contrato seria substituída pelo valor mais frequente, que é "Consumindo gás".

# %%
df_merged['situacao_CONSUMINDO GÁS'] = df_merged['situacao_CONSUMINDO GÁS'].fillna(True)
df_merged['situacao_CONTRATADO'] = df_merged['situacao_CONTRATADO'].fillna(False)
df_merged['situacao_DESATIVADO'] = df_merged['situacao_DESATIVADO'].fillna(False)

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Definimos que toda linha que não possuísse dados acerca do perfil de consumo seria substituída pelo valor mais recorrente na coluna, sendo este o "Cocção + Aquecedor".

# %%
df_merged['perfil_consumo_Cocção + Aquecedor'] = df_merged['perfil_consumo_Cocção + Aquecedor'] = df_merged['perfil_consumo_Cocção + Aquecedor'].fillna(True)
df_merged['perfil_consumo_Aquecedor'] = df_merged['perfil_consumo_Aquecedor'].fillna(False)
df_merged['perfil_consumo_Cocção'] = df_merged['perfil_consumo_Cocção'].fillna(False)
df_merged['perfil_consumo_Caldeira'] = df_merged['perfil_consumo_Caldeira'].fillna(False)
df_merged['perfil_consumo_Cocção + Aquecedor + Piscina'] = df_merged['perfil_consumo_Cocção + Aquecedor + Piscina'].fillna(False)
df_merged['perfil_consumo_Cocção + Caldeira'] = df_merged['perfil_consumo_Cocção + Caldeira'].fillna(False)

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Assim como nas células acima, substituimos os valores faltantes das colunas de categoria, bairro, cidade e condIndex pela moda da coluna, ou seja, também pelo valor mais frequente.

# %%
df_merged['categoria'] = df_merged['categoria'].fillna(categoria_mais_frequente)
df_merged['bairro'] = df_merged['bairro'].fillna(df_merged['bairro'].mode().iloc[0])
df_merged['cidade'] = df_merged['cidade'].fillna(df_merged['cidade'].mode().iloc[0])
df_merged['condIndex'] = df_merged['condIndex'].fillna(df_merged['condIndex'].mode().iloc[0])

# %%
df_merged.isna().sum()

# %%
df_merged.info()

# %% [markdown]
# #### 4.5.11 Verificando por duplicatas

# %%
duplicates = df_merged.duplicated()
print(duplicates.sum())

# %% [markdown]
# ### 4.5.12 Identificando cidades únicas no dataframe

# %%
df_merged['cidade'].unique()

# %% [markdown]
# #### 4.5.12.1 Unificando os nomes das cidades

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Aqui, foram identificadas as colunas de cidade que traziam o mesmo valor, mas escrito de forma diferente (com e sem acento). Assim, também efetuamos a concatenação e juntamos todos os valores em uma única coluna para cada cidade.

# %%
import unidecode

# Remover acentos, converter para minúsculas, e garantir consistência
df_merged['cidade'] = df_merged['cidade'].str.lower()
df_merged['cidade'] = df_merged['cidade'].apply(lambda x: unidecode.unidecode(x))
df_merged['cidade'] = df_merged['cidade'].str.strip()

# %% [markdown]
# #### 4.5.12.2 Encodificação One Hot da coluna cidade

# %%
df_merged = pd.get_dummies(df_merged, columns=['cidade'])

# %%
df_merged.rename(columns={'cidade_novo hamburgo': 'cidade_novo_hamburgo', 'cidade_porto alegre': 'cidade_porto_alegre', 'cidade_sao leopoldo':'cidade_sao_leopoldo'}, inplace=True)

# %%
df_merged.info()

# %% [markdown]
# ### 4.5.13 Encodificação One Hot da coluna categoria

# %%
df_merged = pd.get_dummies(df_merged, columns=['categoria'])

# %%
df_merged.info()

# %% [markdown]
# ### 4.5.14 Encodificação Label da coluna bairro

# %%
df_merged['bairro_encoded'] = encoder.fit_transform(df_merged['bairro'])

# %%
df_merged[['bairro', 'bairro_encoded']].value_counts()

# %%
df_merged.info()

# %% [markdown]
# ## 4.6. Adição de dados de temperatura

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Como mencionado anteriormente, o dataset possui dados que dizem a cidade, o bairro e a data de cada medição presente nas tabelas. Ou seja, sabemos o local e o dia em que cada medição foi tirada. A partir disso, conseguimos utilizar uma API que nos retorna dados históricos do clima de uma região em determinado período de tempo a fim de conseguir a informação da temperatura média de cada dia para todas as cidades presentes no dataset.

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Utilizamos o microframework de Python FastAPI e a própria API da plataforma WheaterBit. Utilizando uma conta gratuita, conseguimos uma chave de API que permite realizar um número limitado de chamadas que foi suficiente para gerar os arquivos CSV de dados históricos de temperatura para cada cidade presente no dataset.

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Exemplo de chamada da API para recolher dados de temperatura da cidade de Canoas. A API é chamada num loop 5 vezes, para os 5 meses que temos de dados. Além disso, a biblioteca Pandas é utilizada para guardar os dados num dataframe, calcular as médias dos dias do mês e exportar um arquivo csv.

# %% [markdown]
# ```python
# canoas = [-29.91288005916852, -51.183972626036535]
# @app.get("/canoas")
# def call_api_canoas():
#     months = ["02", "03", "04", "05", "06"]
#     year = "2024"
#     
#     all_records = []
#     
#     for month in months:
#         start_date = f"{year}-{month}-01"
#         end_date = f"{year}-{month}-31" if month != "02" else "2024-02-29"  # Fevereiro pode ter 29 dias
#         
#         url = f"https://api.weatherbit.io/v2.0/history/subhourly?lat={canoas[0]}&lon={canoas[1]}&start_date={start_date}&end_date={end_date}&key={os.getenv('API_KEY')}"
#         print(f"Fetching data for: {start_date} to {end_date}")
#         response = requests.get(url)
#         data = response.json()
#         
#         if response.status_code != 200:
#             print(f"Failed to fetch data for {month}/{year}. Status Code: {response.status_code}")
#             continue
# 
#         for entry in data['data']:
#             temp = entry['temp']
#             date = entry['timestamp_local'].replace("T", " ")[:10]
#             all_records.append({"date": date, "temp": round(temp, 2)})
#     
#     df = pd.DataFrame(all_records)
#     
#     daily_avg_temps = df.groupby("date")["temp"].mean().round(2).reset_index()
#     
#     daily_avg_temps.to_csv("daily_avg_temps_canoas.csv", index=False)
#     
#     city_name = data.get('city_name', 'Unknown City')
#     for _, row in daily_avg_temps.iterrows():
#         date = row['date']
#         avg_temp = row['temp']
#         print(f"City: {city_name}, Average Temperature: {avg_temp:.1f}°C, Date: {date}")
# 
#     return daily_avg_temps.to_dict(orient="records")
# ```

# %% [markdown]
# ### 4.6.1. Leitura de arquivos csv e concatenação em um dataframe 

# %%
csv_files = {
    'canoas': '../daily_avg_temps_canoas.csv',
    'gravatai': '../daily_avg_temps_gravatai.csv',
    'novo_hamburgo': '../daily_avg_temps_novo_hamburgo.csv',
    'porto_alegre': '../daily_avg_temps_porto_alegre.csv',
    'sao_leopoldo': '../daily_avg_temps_sao_leopoldo.csv'
}

## cria uma lista com os dataframes de temperatura e depois os concatena
temp_data = []
for cidade, file_name in csv_files.items():
    temp_df = pd.read_csv(file_name)
    temp_df['cidade'] = cidade  
    temp_data.append(temp_df)

df_temperatura = pd.concat(temp_data, ignore_index=True)

# %%
df_temperatura.rename(columns={'date': 'data'}, inplace=True)
df_temperatura

# %% [markdown]
# ### 4.6.2. Conversão de coluna de datas para tipo datetime

# %%
# Converter a coluna 'data' para datetime
df_temperatura['data'] = pd.to_datetime(df_temperatura['data'])

# %% [markdown]
# ### 4.6.3. Leitura das cidades do dataframe

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Aqui, foi utilizada uma técnica de chunks para que o processamento pudesse ser feito em toda a tabela. Sem isso, o kernel não possui recursos suficientes para processar a função get_cidade para todas as linhas. Com tal abordagem, o processamento 100.000 linhas por vez, sendo que o dataset inteiro possui cerca de 3.000.000 de linhas em sua totalidade.

# %%
chunk_size = 100000 ## Vai processar 100.000 linhas por vez

results = []

def get_cidade(row):
    for cidade in csv_files.keys():
        if row[f'cidade_{cidade}']:
            return cidade
    return None

for start in range(0, len(df_merged), chunk_size):
    end = min(start + chunk_size, len(df_merged))
    chunk = df_merged.iloc[start:end].copy()

    chunk['cidade'] = chunk.apply(get_cidade, axis=1)

    chunk['data'] = chunk['datetime'].dt.date

    results.append(chunk)

# %% [markdown]
# ### 4.6.4. Merge do dataframe de temperaturas com o dataframe principal

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Aqui, adicionamos todos os dados de temperatura no dataframe principal, relacionando os dados de cidade e data de ambas as tabelas.

# %%
df_merged = pd.concat(results, ignore_index=True)

df_merged['data'] = pd.to_datetime(df_merged['data']).dt.date
df_temperatura['data'] = pd.to_datetime(df_temperatura['data']).dt.date

df_merged = pd.merge(df_merged, df_temperatura, left_on=['cidade', 'data'], right_on=['cidade', 'data'], how='left')

df_merged.info()

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Por fim, removemos colunas auxiliáres que não serão mais utilizadas.

# %%
df_merged = df_merged.drop(columns=['cidade', 'data', 'anomaly'])
df_merged.info()

# %%
df_merged['clientCode']

# %% [markdown]
# ### 4.6.5. Aplicação de Standard Scaler para todas colunas numéricas

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;O StandardScaler é uma poderosa ferramenta capaz de colocar conjuntos de valores numéricos em uma mesma escala. Isso se faz necessário pois possuímos valores em escalas de 0 a 1 e outros que variam de 0 a 100, por exemplo. Sem a normalização destes dados, os valores com maior escala terão muito maior influência sobre o modelo preditivo. Portanto, é de extrema necessidade que utilizemos uma ferramenta como o StandardScaler para colocar todos os valores numéricos na mesma escala de grandeza.

# %%
numeric_columns = df_merged.select_dtypes(include=['float64', 'int64']).columns


# %%
from sklearn.preprocessing import StandardScaler

df_merged_original = df_merged.copy()

scaler = StandardScaler()
df_merged_scaled = pd.DataFrame(scaler.fit_transform(df_merged[numeric_columns]), 
                                columns=[col + '_scaled' for col in numeric_columns])

df_merged = pd.concat([df_merged_original, df_merged_scaled], axis=1)

# %%
df_merged.head()

# %%
df_merged.info()

# %% [markdown]
# ### 4.6.6 Criação da coluna de consumo multiplicando os valores de pulseCount e gain

# %%
df_merged['consumo em m^3'] = df_merged['gain'] * df_merged['pulseCount']

# %%
df_merged.head(10)

# %%
df_merged.info()

# %% [markdown]
# ### 4.6.7 Criação da coluna de variância de consumo

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Para criação da coluna de variância de consumo, foi feita a mudança de datatype de timestamp para datetime.

# %%
df_merged['timestamp'] = pd.to_datetime(df_merged['timestamp'], unit='s')


# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Ordenação do dataframe, agrupamento por instalação única, diferença entre as linhas para encontrar a variação e reset do index.

# %%

df_merged = df_merged.sort_values(by=['clientIndex', 'clientCode_encoded', 'timestamp'])

df_merged['variação_consumo'] = df_merged.groupby(['clientIndex', 'clientCode_encoded'])['consumo em m^3'].diff()

df_merged = df_merged.reset_index(drop=True)

(df_merged[['clientIndex', 'clientCode_encoded', 'timestamp', 'consumo em m^3', 'variação_consumo']])


# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Checagem das linhas de transição entre instalações.

# %%
df_merged['instalacao_change'] = (df_merged['clientIndex'] != df_merged['clientIndex'].shift(1)) | \
                                 (df_merged['clientCode_encoded'] != df_merged['clientCode_encoded'].shift(1))

(df_merged[df_merged['instalacao_change']].head(10))


# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Valores nulos das transições entre instalações únicas são preenchidos como 0.

# %%
df_merged['variação_consumo'].fillna(0, inplace=True)

# %%
(df_merged[df_merged['instalacao_change']].head(40))

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Checagem de linhas que possuem variação de consumo.

# %%
(df_merged['variação_consumo'] != 0).sum()

# %%
len(df_merged['variação_consumo'])

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Criação de gráfico para cálculo da variação do consumo total de um cliente

# %%
df_merged = df_merged.sort_values(by=['timestamp'])
df_instalacao = df_merged[(df_merged['clientIndex'] == 0) & (df_merged['clientCode_encoded'] == 0)]

plt.figure(figsize=(10, 6))
plt.plot(df_instalacao['timestamp'], df_instalacao['variação_consumo'], marker='o')
plt.title('Variação de Consumo ao Longo do Tempo - Instalação 0,0')
plt.xlabel('Timestamp')
plt.ylabel('Variação de Consumo')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# %%
df_merged = df_merged.sort_values(by=['timestamp'])
df_instalacao = df_merged[((df_merged['clientIndex'] == 0) & (df_merged['clientCode_encoded'] == 0)) & (df_merged['timestamp'] >= '2024-03-28 23:15:58') & (df_merged['timestamp'] <= '2024-05-02 00:00:00')]

plt.figure(figsize=(10, 6))
plt.plot(df_instalacao['timestamp'], df_instalacao['variação_consumo'], marker='o')
plt.title('Variação de Consumo ao Longo do Tempo - Instalação 0,0')
plt.xlabel('Timestamp')
plt.ylabel('Variação de Consumo')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Verificação de variação de consumo com valor negativo

# %%
df_merged[df_merged['variação_consumo'] < 0]

# %% [markdown]
# ## 4.7. Cálculo de Z-Score

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Para fins de teste, também foi utilizado o método z-score, uma ferramenta estatística que calcula quantos desvios-padrão um valor está de distância da média do conjunto de dados e também é utilizada para encontrar valores outliers. Ao utilizá-lo, quase 5 mil linhas foram classificadas como anomalias. Entretanto, os valores anômalos não foram retirados do conjunto de dados, pois eles podem eventualmente ser classificados como as anomalias que o modelo preditivo deve encontrar. Dessa forma, não foi realizado o drop desses valores.
# 
# &nbsp;&nbsp;&nbsp;&nbsp;O cálculo do z-score foi implementado na coluna meterIndex da seguinte forma: ao calcular a média de consumo a partir do valor mostrado pelo medidor, foi também calculado o desvio-padrão acima e abaixo do valor da média. Além disso, foi definido que os valores com distância da média acima ou abaixo de 3 desvios-padrão seriam considerados outliers.

# %%
from scipy import stats

df_merged['z_score_meterIndex'] = np.abs(stats.zscore(df_merged['meterIndex']))

threshold = 3
df_merged['outlier'] = df_merged['z_score_meterIndex'] > threshold

outliers = df_merged[df_merged['outlier']]

print(f"Outliers identificados: {len(outliers)}")

# %% [markdown]
# ### 4.7.1. Contagem de instalações únicas que foram identificadas como outliers

# %%
unique_installations = outliers.groupby(['clientCode', 'clientIndex']).size()
num_unique_installations = unique_installations.count()
print(f"Número de instalações únicas outliers: {num_unique_installations}")

# %%
unique_installations

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Por fim, é importante ressaltar que decidimos, por hora, não realizar a remoção dos *outliers* que encontramos, uma vez que estes *outliers* possam representar justamente as anomalias/fraudes que procuramos entender com este projeto.

# %% [markdown]
# ## 4.8 Análise do balanceamento de clientes por categoria de residência

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Para melhor entender o balanceamento dos dados de consumo dos clientes entre as diferentes categorias existentes e como a diferença de densidade poderia afetar os modelos não supervisionados, foi feita a análise de quantos clientes existiam por cada categoria.

# %%
categorias = df_merged[['categoria_CONSTRUTORAS COLETIVO', 'categoria_PRÉDIO EXISTENTE INDIVIDUAL', 'categoria_PRÉDIOS EXISTENTES COLETIVOS', 'categoria_RES. UNIFAMILIAR']]

# %%
total_linhas = len(categorias)

# %%
construtoras = categorias.loc[(categorias['categoria_CONSTRUTORAS COLETIVO'] == True)].sum()

porcentagem_construtoras = (construtoras / total_linhas) * 100

# %%
predio_individual = categorias.loc[(categorias['categoria_PRÉDIO EXISTENTE INDIVIDUAL'] == True)].sum()

porcentagem_predio_individual = (predio_individual / total_linhas) * 100

# %%
predio_coletivo = categorias.loc[(categorias['categoria_PRÉDIOS EXISTENTES COLETIVOS'] == True)].sum()

porcentagem_predio_coletivo = (predio_coletivo / total_linhas) * 100

# %%
res_unifamiliar = categorias.loc[(categorias['categoria_RES. UNIFAMILIAR'] == True)].sum()

porcentagem_res_unifamiliar = (res_unifamiliar / total_linhas) * 100    

# %% [markdown]
# ## 4.9 Horarização da variação de consumo

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;A coluna de variação de consumo, apesar de ser muito útil para a análise do consumo de gás de cada cliente, ainda possuía uma falta: a diluição do consumo pelo tempo que se passou desde a última medição. Assim, foi realizada a horarização do consumo, ou seja, diluição da variação de consumo em uma taxa média por horas que se passaram desde a última medição.

# %%
df_merged.sort_values(by=['clientCode', 'clientIndex', 'datetime'], inplace=True)

df_merged['delta_time'] = df_merged.groupby(['clientCode', 'clientIndex'])['datetime'].diff().dt.total_seconds() / 3600  # em horas

df_merged['delta_time'].fillna(0, inplace=True)

df_merged['consumo_horarizado'] = df_merged['variação_consumo'] / df_merged['delta_time']

df_merged['consumo_horarizado'].replace([float('inf'), -float('inf')], 0, inplace=True)
df_merged['consumo_horarizado'].fillna(0, inplace=True)

df_merged[['clientCode', 'clientIndex', 'datetime', 'variação_consumo', 'delta_time', 'consumo_horarizado']].head()

# %%
# Filtra uma instalação específica
instalacao = df_merged[(df_merged['clientCode_encoded'] == 37) & (df_merged['clientIndex'] == 0)]

# Cria o gráfico de linha
plt.figure(figsize=(10, 6))
plt.plot(instalacao['datetime'], instalacao['consumo_horarizado'], marker='o', linestyle='-', color='b', label='Consumo Horarizado')

# Configurações do gráfico
plt.xlabel('Data e Hora')
plt.ylabel('Consumo Horarizado (m³/h)')
plt.title('Distribuição do Consumo Horarizado ao longo do Tempo')
plt.xticks(rotation=45)
plt.grid(True)
plt.legend()

# Exibe o gráfico
plt.tight_layout()
plt.show()

# %% [markdown]
# # 5. Hipóteses

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Segundo o Dicionário Escolar da Língua Portuguesa (2015), a palavra "hipótese" é definida como sendo "uma explicação possível, mas que ainda não se provou [...]" <br>
# &nbsp;&nbsp;&nbsp;&nbsp;Nesse contexto, após termos realizado a primeira etapa de exploração de dados e, logo em sequência, o pré-processamento e higienização de tais dados, surgiram algumas hipóteses acerca dos dados que possuímos.
# 

# %% [markdown]
# ## 5.1. Variação de consumo de acordo com mês do ano

# %% [markdown]
# * Variação de consumo de acordo com mês do ano: A primeira hipótese que surgiu ao nos depararmos com dados de consumo de gás é de que os clientes iriam consumir mais durante meses mais frios, uma vez que a queda de temperatura causa uma demanda maior pelo gás que é utilizado para aquecer água para atividades como o banho. Abaixo, podemos verificar se a hipótese é verdadeira ou não:

# %% [markdown]
# ### 5.1.1. Plotagem de gráfico com média de consumo mensal de todos os clientes

# %%
df_merged['year_month'] = df_merged['datetime'].dt.to_period('M')

monthly_avg_consumption = df_merged.groupby('year_month')['meterIndex'].mean().reset_index()

monthly_avg_consumption['year_month'] = monthly_avg_consumption['year_month'].dt.to_timestamp()

plt.figure(figsize=(10, 6))
plt.plot(monthly_avg_consumption['year_month'], monthly_avg_consumption['meterIndex'], marker='o')
plt.title('Média de Consumo Mensal dos Clientes')
plt.xlabel('Mês')
plt.ylabel('Média de Consumo (meterIndex)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()


# %% [markdown]
# ### 5.1.2. Conclusão da Hipótese

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Ao analisar o gráfico, podemos perceber claramente que a hipótese não se mostra verdadeira. Na verdade, houve um pico de consumo na metade final do mês de Fevereiro e início de Março, porém, logo após isso, temos uma queda brusca. Este fenômeno provavelmente ocorreu por conta das grandes enchentes que ocorreram no estado do Rio Grande do Sul nessa época do ano, o que provavelmente levou diversas famílias que ficaram desabrigadas a deixar de consumir ou consumir gás em quantidades significativamente menores.

# %% [markdown]
# ## 5.2. Diferença entre números de instalações residenciais familiares e outras

# %% [markdown]
# * A segunda hipótese que trazemos é a de que a base de dados possuirá um número muito pequeno de instalações de categoria residencial unifamiliar. Essa hipótese se deu em uma conversa com a empresa parceira, que nos disse que o simples ato de fazer a instalação do encanamento do gás para uma residência comum é muito cara e não vale a pena, e, por conta disso, a maior parte das pessoas opta por utilizar outras opções de gás, como o botijão de gás. Abaixo, podemos verificar se a hipótese é verdadeira ou não:

# %% [markdown]
# ### 5.2.1. Contagem de valores e cálculo de porcentagem

# %%
df_merged['categoria_RES. UNIFAMILIAR'].value_counts()

# %%
df_res_unifamiliar = df_merged[df_merged['categoria_RES. UNIFAMILIAR'] == True]

num_instalacoes_res_unifamiliar = df_res_unifamiliar.shape[0]

num_total_instalacoes = df_merged.shape[0]

porcentagem_res_unifamiliar = (num_instalacoes_res_unifamiliar / num_total_instalacoes) * 100

print(f"Porcentagem de instalações na categoria 'RES. UNIFAMILIAR': {porcentagem_res_unifamiliar:.2f}%")


# %% [markdown]
# ### 5.2.2. Conclusão da Hipótese

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;A partir da informação obtida acima, percebemos que a hipótese se mostra verdadeira, uma vez que, dos cerca de 3.000.000 de registros, apenas 1949 são de residências unifamiliares, sendo este um percentual de 0,07%.

# %% [markdown]
# ## 5.3. Diferença de consumo para perfis de consumo que possuam caldeiras

# %% [markdown]
# * Para a última hipótese, temos a ideia de que instalações que possuam um perfil de consumo igual a "Caldeira" ou "Cocção + Caldeira" terão uma média de consumo maior do que os demais perfis, uma vez que estas instalações provavelmente estão vinculadas a indústrias ou a grandes residências prediais. Abaixo, podemos verificar se a hipótese é verdadeira ou não:

# %% [markdown]
# ### 5.3.1. Cálculo de média de consumo para perfis de consumo

# %%

grupo_caldeira = df_merged[(df_merged['perfil_consumo_Caldeira'] == True) | 
                           (df_merged['perfil_consumo_Cocção + Caldeira'] == True)]
grupo_outros = df_merged[~((df_merged['perfil_consumo_Caldeira'] == True) | 
                           (df_merged['perfil_consumo_Cocção + Caldeira'] == True))]

media_caldeira = grupo_caldeira['meterIndex'].mean()
media_outros = grupo_outros['meterIndex'].mean()


# %%
print(f"Perfis de consumo com caldeira: {round(media_caldeira, 3)}")
print(f"Outros perfis: {round(media_outros, 5)}")

# %% [markdown]
# ### 5.3.2. Conclusão da Hipótese

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Por fim, com base nas informações obtidas com o trecho de código acima, percebemos que a hipótese se mostra verdadeira, uma vez que a média de consumo das instalações que possuem um perfil de consumo com caldeira é de 0.202 e o de outros perfis é de -0.00037. Isso pode nos confirmar que a quantidade de gás que as empresas consomem é consideravelmente maior do que residências. Vale ainda ressaltar que esses valores não representam a medida real de metros cúbicos de gás que foram consumidos por conta da normalização de valores numéricos que foi feita com o *Standard Scaler*, que coloca todos os valores na mesma escala. 

# %% [markdown]
# ## 5.4. Finalidade

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;De acordo com tudo que foi explorado, percebemos que estas hipóteses são de grande utilidade para o projeto que está sendo desenvolvido. O principal exemplo disto está na exploração da primeira hipótese, onde pode-se perceber que existe uma queda brusca no consumo geral de gás por conta das enchentes que afetaram o Rio Grande do Sul. Dessa forma, essas hipóteses podem nos ajudar a entender melhor o contexto nos quais os dados que possuímos foram coletados e como devemos ajustar melhor o nosso modelo para isso (por exemplo, passamos a entender que a temperatura não se mostrará como um fator tão influente no consumo de gás).

# %% [markdown]
# # 6. Modelagem e Features 

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Nesta seção, serão apresentadas e dissertadas as features selecionadas para a criação do modelo não supervisionado, bem como a modelagem preditiva em si. Com isso, integrou-se às visualizações gráficas e discussões sobre o modelo candidato.

# %% [markdown]
# ## 6.1. Escolhas das features
# 
# &nbsp;&nbsp;&nbsp;&nbsp;Para o desenvolvimento da modelagem, foram selecionadas as features mais relevantes para a construção do nosso modelo não-supervisionado.

# %%
colunas_selecionadas = [
    'temp_scaled',
    'timestamp',
    'perfil_consumo_Aquecedor',
    'perfil_consumo_Caldeira',
    'perfil_consumo_Cocção',
    'perfil_consumo_Cocção + Aquecedor',
    'perfil_consumo_Cocção + Aquecedor + Piscina',
    'perfil_consumo_Cocção + Caldeira',
    'consumo em m^3',
    'variação_consumo',
]


# %%
df_merged[colunas_selecionadas]

# %% [markdown]
# ### 6.1.1. Justificativa das features

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;A partir de uma análise das colunas disponíveis, foram selecionadas as features para o desenvolvimento da modelagem, levando em consideração o impacto que esses dados podem ter na detecção de anomalias no consumo de gás natural. Sendo assim, a seguir estão as justificativas das escolhas de cada uma dessas features.
# 
# &nbsp;&nbsp;&nbsp;&nbsp;A feature “temp_scaled” foi selecionada, pois a temperatura ambiente influencia significativamente o consumo de gás. Em períodos mais frios, por exemplo, é comum que o consumo aumente devido ao uso intensificado de aquecedores e caldeiras. Assim, é importante incluir essa feature para analisar possíveis anomalias, sempre considerando a temperatura média do dia em uma determinada região. Dessa maneira, essa análise pode ajudar a explicar mudanças de consumo que sejam resultado de variações climáticas e não de comportamentos anômalos.
# 
# &nbsp;&nbsp;&nbsp;&nbsp;As features “perfil_consumo_Aquecedor”, “perfil_consumo_Caldeira”, “perfil_consumo_Cocção”, “perfil_consumo_Cocção + Aquecedor”, “perfil_consumo_Cocção + Aquecedor + Piscina” e “perfil_consumo_Cocção + Caldeira” foram incluídas para representar o perfil de consumo do cliente, isto é, em que tipo de equipamentos o cliente utiliza o gás natural. Esses perfis variam entre aquecedores, cocção, caldeiras e piscinas. Em muitos casos, os clientes podem utilizar o gás em mais de uma dessas aplicações, como ilustrado pela feature “perfil_consumo_Cocção + Aquecedor”, o que significa que o consumo pode ser maior que aquele que utiliza apenas um equipamento.
# 
# &nbsp;&nbsp;&nbsp;&nbsp;A feature “consumo em m^3” é uma nova coluna que foi criada a partir da multiplicação das colunas “gain” e “pulseCount”, resultando na quantidade de gás consumido pelo cliente em metros cúbicos. Além disso, gerou-se uma segunda coluna chamada “variação_consumo”, que permite ver a variação do consumo em um determinado período de tempo. Dessa forma, essas duas novas features, “consumo em m^3” e “variação_consumo”, mostram-se relevantes para o modelo, uma vez que nos dá informações indispensáveis para a análise.  
# 
# &nbsp;&nbsp;&nbsp;&nbsp;A feature “timestamp” representa a quantidade de segundos que se passaram desde 1º de janeiro de 1970 até a data definida. Com essa coluna é possível analisar padrões de consumo de gás em diferentes períodos, como picos em determinadas horas, dias ou meses. Assim, é possível realizar uma análise temporal mais detalhada, o que facilita a detecção de anomalias relacionadas a intervalos específicos de tempo.
# 
# &nbsp;&nbsp;&nbsp;&nbsp;Além das features escolhidas, também há aquelas que não foram selecionadas, e suas exclusões foram analisadas com base no impacto insignificante na detecção de anomalias ou por redundância em relação a outras variáveis. Por exemplo, as features relacionadas à localização, como "bairro_encoded", "cidade_canoas", "cidade_gravatai", entre outras, não foram consideradas essenciais, pois a análise já inclui a coluna de temperatura, que registra a média da temperatura do ambiente em um determinado dia e influencia diretamente o consumo de gás, tornando as variáveis de localização redundantes para esse fim.
# 
# &nbsp;&nbsp;&nbsp;&nbsp;Portanto, as justificativas apresentadas evidenciam a importância dessas features na modelagem, destacando como elas podem influenciar na detecção de anomalias no consumo de gás natural. Assim, com essa seleção, o processo de análise de dados torna-se mais centrado e objetivo, garantindo menor tempo de processamento da análise e maior precisão na identificação de padrões anômalos.
# 

# %% [markdown]
# ## 6.2 Modelagem do problema

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;No contexto de aprendizado de máquina, depois que um *dataset* passa pelos processos de tratamento e pré-processamento ou demais metodologias iniciais, deve-se implementar operações, lógicas e algoritmos sobre a base de dados normalizada para evidenciar relações entre as colunas, tentando identificar e representar visualmente padrões em  entre os registros (Géron, 2019).<br>
# &nbsp;&nbsp;&nbsp;&nbsp;No presente projeto de aprendizado de máquina não supervisionado, ou seja, descontido de rótulos prévios dos padrões desejados, será utilizado o modelo de clusterização — categorização — *k-means*, o qual funciona dividindo um conjunto de dados em k grupos, sendo k um valor definido pelo usuário ou pela equipe. O processo começa com a seleção de k centróides (pontos iniciais que representam cada grupo). Em seguida, cada ponto da base de dados é atribuído ao seu centróide mais próximo através de um cálculo de distância entre pontos no plano cartesiano. Com isso, os centróides são recalculados como a média dos pontos atribuídos a eles, e o processo se repete até que os centróides não apresentarem mais mudanças significativas (Filho, 2017). Com isso, busca-se a aplicação do modelo para identificar e agrupar padrões de consumo de gás natural, para assim detectar dados extrapolantes ou suspeitos que possam indicar anomalias na utilização.

# %% [markdown]
# ### 6.2.1 Importação das bibliotecas utilizadas

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Como bibliotecas necessárias para a aplicação dos modelos, tem-se os componentes *KMeans* e *silhouette_score* da biblioteca *Sklearn* para a composição de gráficos com as features selecionadas para a modelagem.<br>

# %%
# from sklearn.cluster import KMeans
# from sklearn.metrics import silhouette_score


# # %% [markdown]
# # ### 6.2.2 Armazenamento das principais features em uma variável

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Com o objetivo de selecionar um repertório com as colunas mais importantes do *DataFrame* normalizado, de forma a acarretar uma análise bem direcionada sobre o consumo de gás natural, de 51 colunas foram escolhidas 9 como mais relevantes para compor os gráficos do modelo.

# # %%
# colunas_selecionadas = [
#     'temp_scaled',
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'perfil_consumo_Cocção + Caldeira',
#     'consumo em m^3',
#     'variação_consumo',
# ]


# # %% [markdown]
# # ### 6.2.3 Redução do tamanho do DataFrame

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para a simplificação da testagem do algoritmo de modelo, armazenou-se um recorte de 12% de registros aleatórios do DataFrame "*df_merged*", compondo, assim, o novo DataFrame "*df_sample*". Esse recorte pode ser ajustado conforme critério do usuário que desejar testar a plotagem do modelo, podendo-se, também, plotar o conjunto de dados completo ao substituir o valor de *frac* por 1. Nesse sentido, tem-se a visualização dessa nova tabela com o método .info().

# # %%
# df_sample = df_merged.sample(frac=0.12, random_state=42) # 12% dos dados
# ## Converte valores booleanos para int (True = 1, False = 0)
# df_sample[colunas_selecionadas] = df_sample[colunas_selecionadas].astype(int)
# df_sample[colunas_selecionadas].info()

# # %% [markdown]
# # ### 6.2.4 Aplicação do K-means e visualização dos clusters

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após a realização do cálculo de *k* (número de *clusters*), alcançando-se o valor 3, construiu-se o algoritmo do k-means exposto e comentado abaixo. Com a execução do código, será exposto o gráfico que categoriza os 3 clusters considerando valores de data (timestamp) e variação de consumo. O critério utilizado para a definição das anomalias consistiu nos 5% de pontos com maiores distâncias dos clusters encontrados.<br>
# # &nbsp;&nbsp;&nbsp;&nbsp;No gráfico abaixo, os pontos de mesma cor são de mesma categoria, e foram apenas considerados os pontos de variação positiva de consumo de gás natural, em metros cúbicos. Nesse sentido, em hipótese, os pontos laranja representam em maior parte as linhas de consumo em que não houve, ou houve muito pouca, variação de consumo. Os pontos em azul significam uma diferença de consumo mais significativa, ao longo do tempo. Já os pontos em verde apresentam variação do consumo praticamente nula. No geral, uma parte reduzida dos dados que compõem o modelo evidencia variação; das 2.900.000 linhas, só 400.000 tem diferença e o restante não apresenta variação.

# # %%
# # Número de k definido pela equipe
# k = 3

# # Aplicando o K-Means, com o número de clusters 3
# kmeans = KMeans(n_clusters=k, random_state=42)
# kmeans.fit(df_sample[colunas_selecionadas]) #Adaptação do k-means às colunas selecionadas do dataframe

# # Atribuindo os clusters
# df_sample['cluster'] = kmeans.labels_

# # Calculando a distância aos centroides para cada ponto do gráfico
# df_sample['distance_to_centroid'] = np.min(kmeans.transform(df_sample[colunas_selecionadas]), axis=1)

# # Definindo um limiar para identificar anomalias, os 5% de pontos com maiores distâncias serão consideradas como anomalias
# threshold = np.percentile(df_sample['distance_to_centroid'], 95)

# # Identificando anomalias de acordo com o cálculo acima
# df_sample['anomaly'] = df_sample['distance_to_centroid'] > threshold

# df_sample_positive = df_sample[df_sample['variação_consumo'] >= 0]

# plt.figure(figsize=(10, 6))

# for cluster in range(k):
#     cluster_data = df_sample_positive[df_sample_positive['cluster'] == cluster]
#     plt.scatter(cluster_data['timestamp'], 
#                 cluster_data['variação_consumo'], 
#                 label=f'Cluster {cluster}')

# plt.title('Clusters de Variação de Consumo de Gás (Apenas Variação de Consumo Positiva)')
# plt.xlabel('Timestamp')
# plt.ylabel('Consumo em m³')
# plt.legend()

# plt.grid(True)
# plt.show()



# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A seguir, evidencia-se outro gráfico que representa o consumo de gás natural em metros cúbicos acumulado ao longo do tempo, e não a variação.

# # %% [markdown]
# # ### 6.2.5. Visualização de clusters em relação ao consumo acumulado 

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Como observado nos resultados do gráfico abaixo, os pontos em laranja representam o menor consumo acumulado, seguidos dos pontos em azul que possuem consumo mais significativo, observando-se, por fim, os pontos em verde que evidenciam uma utilização exacerbada de gás natural, o que pode ser levado como aspecto de atenção para a detecção de anomalias.

# # %%
# plt.figure(figsize=(10, 6))

# ## Loop para plotar os clusters
# for cluster in range(k):
#     cluster_data = df_sample_positive[df_sample_positive['cluster'] == cluster]
#     plt.scatter(cluster_data['timestamp'], 
#                 cluster_data['consumo em m^3'], 
#                 label=f'Cluster {cluster}')

# plt.title('Clusters de Consumo de Gás Acumulado')
# plt.xlabel('Timestamp')
# plt.ylabel('Consumo acumulado em m³ (pulsecount * gain)')
# plt.legend()

# plt.grid(True)
# plt.show()


# # %% [markdown]
# # ### 6.2.6. Visualização da quantidade de dados para cada cluster

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A seguir, com base nos resultados nas últimas representações do modelo preditivo, o gráfico mostra a quantidade de valores obtidos em cada um dos 3 clusters.

# # %%
# cluster_counts = df_sample_positive['cluster'].value_counts()

# plt.figure(figsize=(8, 5))
# plt.bar(cluster_counts.index, cluster_counts.values, color='skyblue')

# plt.title('Quantidade de Valores em Cada Cluster')
# plt.xlabel('Clusters')
# plt.ylabel('Quantidade de Valores')

# ## Adicionando os valores acima das barras
# for i, v in enumerate(cluster_counts.values):
#     plt.text(cluster_counts.index[i] - 0.1, v + 10, str(v), color='black', fontweight='bold')

# plt.grid(axis='y')
# plt.show()


# # %% [markdown]
# # ### 6.2.7. Cálculo do coeficiente de silhueta

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Por fim, como método de validação da quantificação de dados encontrados em cada cluster, tem-se o cálculo do coeficiente de silhueta, que ajuda a avaliar o modelo e detectar valores adequados, ou não, para o coeficiente k de clusters. A variação do coeficiente deve estar entre -1 e 1, sendo valores negativos ou mais próximos de zero indicadores de um agrupamento inadequado de clusters, e valores próximos de 1 representantes um agrupamento cada vez mais delimitado, o que é desejado para o modelo preditivo (Scaldelai, 2022).

# # %%
# ## Contagem dos valores considerados anômalos
# df_sample_positive['anomaly'].value_counts()

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após a execução do modelo, tem-se como output o coeficiente de silhueta no valor 0.9790473924065777 (97%), que significa que os pontos estão muito bem agrupados dentro dos seus clusters e bem separados dos pontos de outros clusters. Apesar de que, quanto maior este coeficiente, melhor, nem sempre isso se mostra como verdade. Um coeficiente de 97% indica que os dados estão agrupados de forma quase excelente, havendo o risco de se indicar que pode ter ocorrido um *overfitting* dos dados.

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Abaixo, temos o algoritmo utilizado para calcular o coeficiente de silhueta para o modelo K-Means. Ressaltamos que, por conta da complexidade do algoritmo, o mesmo demora de 20 e 35 minutos para ser executado. Por conta disso, optamos por rodar o código uma vez e, após isso, comentá-lo, a fim de não impactar a execução de todo o Jupyter Notebook.

# # %%
# # Remover possíveis anomalias para calcular a silhueta apenas para os dados normais (sem outliers)
# #df_sample_no_anomalies = df_sample_positive[df_sample_positive['anomaly'] == False]

# # Selecionar as colunas utilizadas para a criação dos clusters
# #X = df_sample_no_anomalies[colunas_selecionadas]

# # Calcular o coeficiente da silhueta
# #silhouette_avg = silhouette_score(X, df_sample_no_anomalies['cluster'])

# #print(f'Coeficiente da Silhueta: {silhouette_avg}')
# ## Output: Coeficiente da Silhueta: 0.9790473924065777


# # %% [markdown]
# # Coeficiente da Silhueta: 0.9790473924065777

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Conclui-se que a equipe alcançou êxito na aplicação da base de dados normalizada para a implementação do modelo preditivo K-Means, demonstrando pensamento crítico e competência na aplicação dos conhecimentos de programação adquiridos na Sprint para a escolha de algoritmos e a preparação dos dados. O alto coeficiente de silhueta de 0.979 indica uma possível eficácia do modelo em identificar padrões e possíveis anomalias no consumo de gás natural, entretanto, também evidencia uma possibilidade de overfitting do modelo, algo que necessitará correção. Esses resultados servirão de base para discussões sobre as áreas de aprimoramento, além de contribuir para a evolução do modelo no contexto de detecção de anomalias.

# # %% [markdown]
# # # 7. Modelo e Discussão

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O K-means é um algoritmo de clusterização (agrupamento) não supervisionado, baseado na definição de centróides que representam clusters. O “K” refere-se ao número de centróides (clusters) definidos previamente e o “Means” à média dos pontos em cada cluster que determina a posição de seu centróide. Desse modo, o K-means foi utilizado para o modelo preditivo atual, tendo em vista a sua simplicidade e facilidade na sua compreensão e aplicação. </br>

# # %% [markdown]
# # ## 7.1 Apresentando o Modelo

# # %%
# # Número de k definido pela equipe
# k = 3

# # Aplicando o K-Means, com o número de clusters 3
# kmeans = KMeans(n_clusters=k, random_state=42)
# kmeans.fit(df_sample[colunas_selecionadas]) #Adaptação do k-means às colunas selecionadas do dataframe

# # Atribuindo os clusters
# df_sample['cluster'] = kmeans.labels_

# # Calculando a distância aos centroides para cada ponto do gráfico
# df_sample['distance_to_centroid'] = np.min(kmeans.transform(df_sample[colunas_selecionadas]), axis=1)

# # Definindo um limiar para identificar anomalias, os 5% de pontos com maiores distâncias serão consideradas como anomalias
# threshold = np.percentile(df_sample['distance_to_centroid'], 95)

# # Identificando anomalias de acordo com o cálculo acima
# df_sample['anomaly'] = df_sample['distance_to_centroid'] > threshold

# import matplotlib.pyplot as plt

# df_sample_positive = df_sample[df_sample['variação_consumo'] >= 0]

# plt.figure(figsize=(10, 6))

# for cluster in range(k):
#     cluster_data = df_sample_positive[df_sample_positive['cluster'] == cluster]
#     plt.scatter(cluster_data['timestamp'], 
#                 cluster_data['variação_consumo'], 
#                 label=f'Cluster {cluster}')

# plt.title('Clusters de Variação de Consumo de Gás (Apenas Variação de Consumo Positiva)')
# plt.xlabel('Timestamp')
# plt.ylabel('Consumo em m³')
# plt.legend()

# plt.grid(True)
# plt.show()


# # %% [markdown]
# # ### 7.1.1 Pontos Positivos

# # %% [markdown]
# # #### 7.1.1.1 Uso de Clusters com K-means

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O modelo K-means foi adaptado para trabalhar com 9 colunas (features) do dataframe, o que permite uma maior compreensão dos padrões de consumo de gás, indo além das três variáveis tradicionais. Isso pode melhorar a segmentação dos clusters e a detecção de anomalias, já que mais informações estão sendo utilizadas na análise. Desse modo, abaixo podemos ver um gráfico do modelo com a identificação das anomalias.

# # %%
# import matplotlib.pyplot as plt

# # Separando os dados positivos para variação de consumo
# df_sample_positive = df_sample[df_sample['variação_consumo'] >= 0]

# plt.figure(figsize=(10, 6))

# # Plotando os clusters
# for cluster in range(k):
#     cluster_data = df_sample_positive[df_sample_positive['cluster'] == cluster]
#     plt.scatter(cluster_data['timestamp'], 
#                 cluster_data['variação_consumo'], 
#                 label=f'Cluster {cluster}', alpha=0.6)

# # Destacando as anomalias
# anomalies = df_sample_positive[df_sample_positive['anomaly'] == True]
# plt.scatter(anomalies['timestamp'], 
#             anomalies['variação_consumo'], 
#             c='red', 
#             label='Anomalias', 
#             marker='x', 
#             s=100)

# # Configurando o gráfico
# plt.title('Clusters de Variação de Consumo de Gás com Anomalias (Limiar de 95%)')
# plt.xlabel('Timestamp')
# plt.ylabel('Consumo em m³')
# plt.legend()

# plt.grid(True)
# plt.show()


# # %% [markdown]
# # #### 7.1.1.2 Cálculo da Distância aos Centróides

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; A inclusão da distância aos centróides (distance_to_centroid) para cada ponto de dado é uma abordagem útil para identificar anomalias. Isso ajuda a distinguir dados que estão afastados dos centros dos clusters, que podem ser considerados comportamentos fora do padrão (anômalos). No código abaixo podemos identificar a distância média e a distância máxima dos centróides, além do percentual de anomalias detectadas. 

# # %%
# # Analisando as distâncias médias e máximas até os centroides
# mean_distance = df_sample['distance_to_centroid'].mean()
# max_distance = df_sample['distance_to_centroid'].max()

# print(f"Distância média aos centroides: {mean_distance}")
# print(f"Distância máxima aos centroides: {max_distance}")

# # Percentual de anomalias detectadas
# anomalias_percentual = df_sample['anomaly'].mean() * 100
# print(f"Percentual de anomalias detectadas: {anomalias_percentual:.2f}%")


# # %% [markdown]
# # #### 7.1.1.3 Limiar para Anomalias

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; A definição de um limiar (os 5% com maior distância, no caso do modelo apresentado) para detectar anomalias torna o processo automático e facilita a identificação de possíveis outliers no consumo de gás. Essa abordagem quantitativa é vantajosa, pois apresenta de maneira clara a distorção dos dados ao longo do modelo. Abaixo é possível identificar o gráfico do modelo, fazendo a repartição do limiar escolhido.

# # %%
# import matplotlib.pyplot as plt

# # Separando os dados positivos e negativos para variação de consumo positiva e negativa
# df_sample_positive = df_sample[df_sample['variação_consumo'] >= 0]

# plt.figure(figsize=(10, 6))

# # Plotando os clusters
# for cluster in range(k):
#     cluster_data = df_sample_positive[df_sample_positive['cluster'] == cluster]
#     plt.scatter(cluster_data['timestamp'], 
#                 cluster_data['variação_consumo'], 
#                 label=f'Cluster {cluster}')

# # Adicionando a linha de limiar
# plt.axhline(y=threshold, color='r', linestyle='--', label='Limiar 95%')

# # Configurando o gráfico
# plt.title('Clusters de Variação de Consumo de Gás com Limiar de 95% (Apenas Variação de Consumo Positiva)')
# plt.xlabel('Timestamp')
# plt.ylabel('Consumo em m³')
# plt.legend()

# plt.grid(True)
# plt.show()


# # %% [markdown]
# # #### 7.1.1.4 Gráfico de Clusters por Variação Positiva no Consumo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; Os colunas escolhidas para apresentar o modelo, que mostra apenas a variação positiva no consumo de gás, é bem informativo, pois foca em dados que podem ser mais relevantes para a análise (aumento de consumo). Essa abordagem ajuda a simplificar a visualização e a destacar padrões importantes.

# # %% [markdown]
# # ### 7.1.2 Pontos Negativos e Limitações

# # %% [markdown]
# # #### 7.1.2.1 Avaliar Diferentes Limiares

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; Testar diferentes percentuais ou estratégias para definir o limiar de anomalias é fundamental para adaptar o modelo à distribuição dos dados. Isso garante uma detecção mais precisa, evitando a sub ou superestimação de anomalias. Ajustes adequados aumentam a eficácia na identificação de padrões anômalos, otimizando a performance do modelo. Abaixo podemos identificar não mais só o limiar de 95% do modelo, mas também o de 90% e o de 93%.

# # %%
# import matplotlib.pyplot as plt
# import numpy as np

# # Definindo os limiares para os percentis de 90%, 95% e 99%
# thresholds = [90, 93, 95]

# # Separando os dados positivos de variação de consumo
# df_sample_positive = df_sample[df_sample['variação_consumo'] >= 0]

# # Criando os gráficos
# plt.figure(figsize=(18, 12))

# for i, threshold_percent in enumerate(thresholds):
#     # Calculando o limiar para o percentil atual
#     threshold_value = np.percentile(df_sample_positive['distance_to_centroid'], threshold_percent)
    
#     # Criando subplots para cada gráfico
#     plt.subplot(2, 2, i+1)
    
#     # Plotando os clusters
#     for cluster in range(k):
#         cluster_data = df_sample_positive[df_sample_positive['cluster'] == cluster]
#         plt.scatter(cluster_data['timestamp'], 
#                     cluster_data['variação_consumo'], 
#                     label=f'Cluster {cluster}', alpha=0.6)

#     # Adicionando a linha do limiar
#     plt.axhline(y=threshold_value, color='r', linestyle='--', label=f'Limiar {threshold_percent}%')

#     # Configurando o gráfico
#     plt.title(f'Clusters com Limiar de {threshold_percent}% (Apenas Variação de Consumo Positiva)')
#     plt.xlabel('Timestamp')
#     plt.ylabel('Consumo em m³')
#     plt.legend()
#     plt.grid(True)

# # Ajuste do layout dos subplots
# plt.tight_layout()
# plt.show()


# # %% [markdown]
# # #### 7.1.2.2 Número de Clusters Fixo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O número de clusters no K-means é um parâmetro que deve ser ajustado manualmente. Se o número de clusters não for escolhido corretamente, o modelo pode sub ou superestimar os grupos, impactando a detecção de anomalias. Embora exista o Método do Cotovelo para encontrar o k, um valor fixo de clusters não é interessante no que diz respeito o contexto de anomalias, considerando que ele é baseado na suposição de que todos os clusters são representativos de padrões normais, o que pode não ser ideal no cenário trabalhado. Abaixo podemos identificar o gráfico com os possíveis valores de k.

# # %%
# from sklearn.cluster import KMeans
# import matplotlib.pyplot as plt

# # Testando diferentes valores de K para encontrar o ideal
# inertia = []
# K_range = range(1, 10)
# for K in K_range:
#     kmeans_test = KMeans(n_clusters=K, random_state=42)
#     kmeans_test.fit(df_sample[colunas_selecionadas])
#     inertia.append(kmeans_test.inertia_)

# plt.figure(figsize=(8, 6))
# plt.plot(K_range, inertia, marker='o')
# plt.title('Elbow Method - Inércia para diferentes valores de K')
# plt.xlabel('Número de clusters (K)')
# plt.ylabel('Inércia')
# plt.grid(True)
# plt.show()


# # %% [markdown]
# # #### 7.1.2.3 Detecção de Anomalias

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O K-means não é originalmente um modelo de detecção de anomalias (BUENO, 2021). Ele pode ser usado para esse fim ao identificar pontos que estão distantes dos centróides dos clusters, mas isso pode não ser tão eficiente quanto métodos mais específicos, como Isolation Forest ou DBSCAN, que são projetados para identificar outliers. Desse modo, abaixo podemos identificar a utilização breve do modelo Isolation Forest, com o resultado do Davies-Bouldin Index do modelo.

# # %%
# from sklearn.ensemble import IsolationForest
# from sklearn.metrics import davies_bouldin_score, classification_report
# import pandas as pd

# # Supondo que df_sample e colunas_selecionadas já estão definidos

# # Aplicando o Isolation Forest
# iso_forest = IsolationForest(contamination=0.05, random_state=42)
# df_sample['isof_anomaly'] = iso_forest.fit_predict(df_sample[colunas_selecionadas])

# # Convertendo a saída para binário (1 = anomalia, 0 = normal)
# df_sample['isof_anomaly'] = df_sample['isof_anomaly'].apply(lambda x: 1 if x == -1 else 0)

# # Verificando se temos pelo menos dois grupos para calcular o DBI
# if len(df_sample['isof_anomaly'].unique()) > 1:
#     # Calculando o Davies-Bouldin Index
#     dbi_score = davies_bouldin_score(df_sample[colunas_selecionadas], df_sample['isof_anomaly'])
#     print(f"Davies-Bouldin Index (DBI) com Isolation Forest: {dbi_score}")
# else:
#     print("Não é possível calcular o Davies-Bouldin Index devido à falta de variação nas anomalias detectadas.")

# # Exemplo adicional de avaliação (se rótulos verdadeiros estiverem disponíveis)
# # df_sample['true_labels'] = ... # Rótulos verdadeiros (se disponíveis)
# # print(classification_report(df_sample['true_labels'], df_sample['isof_anomaly']))


# # %% [markdown]
# # #### 7.1.2.4 Utilização de Apenas um Modelo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;  Modelos diferentes podem ter desempenhos distintos para o mesmo conjunto de dados. O K-means, apesar de ser eficaz em muitas situações, pode não capturar todas as anomalias, especialmente em dados complexos. Testar mais de um modelo permite avaliar qual oferece as melhores previsões e identifica os padrões de maneira mais precisa. É fundamental comparar os resultados de cada modelo em termos de precisão, recall, e taxa de falsos positivos. A análise deve incluir essas métricas para justificar por que um modelo pode ser preferido ao outro. Dessa forma, abaixo podemos ver uma breve comparação entre o modelo K-Means e o modelo Isolation Forest.

# # %%
# import numpy as np
# import pandas as pd
# from sklearn.cluster import KMeans
# from sklearn.ensemble import IsolationForest
# from sklearn.metrics import davies_bouldin_score
# from sklearn.preprocessing import StandardScaler

# # Verificação dos dados
# if df_sample.empty:
#     raise ValueError("O DataFrame df_sample está vazio.")
# if not all(col in df_sample.columns for col in colunas_selecionadas):
#     raise ValueError("Uma ou mais colunas selecionadas não estão presentes no DataFrame.")

# # Pré-processamento dos dados
# scaler = StandardScaler()
# df_scaled = scaler.fit_transform(df_sample[colunas_selecionadas])

# # ---- K-Means ----
# try:
#     k = 3
#     kmeans = KMeans(n_clusters=k, random_state=42)
#     df_sample['cluster'] = kmeans.fit_predict(df_scaled)
    
#     # Calculando o Davies-Bouldin Index (DBI) para K-Means
#     dbi_kmeans = davies_bouldin_score(df_scaled, df_sample['cluster'])
#     print(f"Davies-Bouldin Index (DBI) K-Means: {dbi_kmeans:.4f}")
# except Exception as e:
#     print(f"Erro ao aplicar K-Means: {e}")

# # ---- Isolation Forest ----
# try:
#     iso_forest = IsolationForest(contamination=0.05, random_state=42)
#     df_sample['anomaly_isoforest'] = iso_forest.fit_predict(df_scaled)
#     df_sample['anomaly_isoforest'] = df_sample['anomaly_isoforest'].map({1: False, -1: True})
    
#     # Para o Isolation Forest, criamos uma abordagem alternativa para DBI
#     df_sample['iso_forest_cluster'] = df_sample['anomaly_isoforest'].astype(int)
    
#     # Calculando o Davies-Bouldin Index (DBI) para o Isolation Forest (pseudo-clustering)
#     dbi_isoforest = davies_bouldin_score(df_scaled, df_sample['iso_forest_cluster'])
#     print(f"Davies-Bouldin Index (DBI) Isolation Forest: {dbi_isoforest:.4f}")
# except Exception as e:
#     print(f"Erro ao aplicar Isolation Forest: {e}")

# # ---- Comparação ----
# print("\nComparação dos modelos:")
# print(f"DBI K-Means: {dbi_kmeans:.4f}")
# print(f"DBI Isolation Forest (pseudo-clustering): {dbi_isoforest:.4f}")


# # %% [markdown]
# # #### 7.1.2.5 Dificuldade da Visualização das Anomalias do Modelo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;  O gráfico inicialmente escolhido não representa adequadamente a disposição dos clusters, pois alguns deles se sobrepõem, dificultando a visualização e a identificação das anomalias. Para melhorar a clareza, apresentamos uma nova visualização que inclui uma coluna adicional, o "timestamp". Essa nova visualização agrupa as amostras dos clusters de maneira mais eficaz, facilitando a análise e identificação das anomalias.

# # %%
# colunas_selecionadas = [
#     'timestamp',
#     'temp_scaled',
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'perfil_consumo_Cocção + Caldeira',
#     'consumo em m^3',
#     'variação_consumo',
# ]
# df_sample = df_merged.sample(frac=0.06, random_state=42) # 12% dos dados
# df_sample[colunas_selecionadas] = df_sample[colunas_selecionadas].astype('int64') # Convertendo para int

# df_sample[colunas_selecionadas].info()



# # %%
# # Número de k definido pela equipe
# k = 3

# # Aplicando o K-Means, com o número de clusters 3
# kmeans = KMeans(n_clusters=k, random_state=42)
# kmeans.fit(df_sample[colunas_selecionadas]) #Adaptação do k-means às colunas selecionadas do dataframe

# # Atribuindo os clusters
# df_sample['cluster'] = kmeans.labels_

# # Calculando a distância aos centroides para cada ponto do gráfico
# df_sample['distance_to_centroid'] = np.min(kmeans.transform(df_sample[colunas_selecionadas]), axis=1)

# # Definindo um limiar para identificar anomalias, os 5% de pontos com maiores distâncias serão consideradas como anomalias
# threshold = np.percentile(df_sample['distance_to_centroid'], 95)

# # Identificando anomalias de acordo com o cálculo acima
# df_sample['anomaly'] = df_sample['distance_to_centroid'] > threshold

# import matplotlib.pyplot as plt

# df_sample_positive = df_sample[df_sample['variação_consumo'] >= 0]

# plt.figure(figsize=(10, 6))

# for cluster in range(k):
#     cluster_data = df_sample_positive[df_sample_positive['cluster'] == cluster]
#     plt.scatter(cluster_data['timestamp'], 
#                 cluster_data['variação_consumo'], 
#                 label=f'Cluster {cluster}')

# plt.title('Clusters de Variação de Consumo de Gás (Apenas Variação de Consumo Positiva)')
# plt.xlabel('Timestamp')
# plt.ylabel('Consumo em m³')
# plt.legend()

# plt.grid(True)
# plt.show()


# # %%
# import matplotlib.pyplot as plt

# # Separando os dados positivos para variação de consumo
# df_sample_positive = df_sample[df_sample['variação_consumo'] >= 0]

# plt.figure(figsize=(10, 6))

# # Plotando os clusters
# for cluster in range(k):
#     cluster_data = df_sample_positive[df_sample_positive['cluster'] == cluster]
#     plt.scatter(cluster_data['timestamp'], 
#                 cluster_data['variação_consumo'], 
#                 label=f'Cluster {cluster}', alpha=0.6)

# # Destacando as anomalias
# anomalies = df_sample_positive[df_sample_positive['anomaly'] == True]
# plt.scatter(anomalies['timestamp'], 
#             anomalies['variação_consumo'], 
#             c='red', 
#             label='Anomalias', 
#             marker='x', 
#             s=100)

# # Configurando o gráfico
# plt.title('Clusters de Variação de Consumo de Gás com Anomalias (Limiar de 95%)')
# plt.xlabel('Timestamp')
# plt.ylabel('Consumo em m³')
# plt.legend()

# plt.grid(True)
# plt.show()


# # %% [markdown]
# # ## 7.2 Discussão dos resultados do modelo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O modelo de aprendizagem não-supervisionada *K-Means*, identificado anteriormente na seção 7.1, não possui rótulos para os dados anômalos e foi utilizado para encontrar padrões que o ajude a diferenciar os dados com base em suas características. Por conta desse aspecto dos modelos não-supervisionados, técnicas e métricas para análise de resultados como a precisão, a acurácia e o *recall* não podem ser utilizadas por se basearem na comparação de predições do modelo e dos dados reais. Assim, foram utilizados outros métodos para melhor entender o desempenho do modelo: o teste de Komogorov-Smirnov, a análise das features em relação aos *clusters* delimitados e o Silhouette Score.

# # %% [markdown]
# # ### 7.2.1 Análise da quantidade de anomalias identificadas

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Primeiramente, foi feita a análise da quantidade de dados que foram classificados como anomalias pelo modelo, sendo a mesma antes e depois da aplicação do PCA. Entretanto, por se tratar de uma métrica pré-definida na modelagem dos dados, foi necessário realizar mais testes com os resultados.

# # %%
# num_anomalies = df_sample['anomaly'].sum()
# total_points = len(df_sample)
# anomaly_percentage = ((num_anomalies / total_points) * 100).round(4)
# print(f'Porcentagem de anomalias detectadas: {anomaly_percentage}%')

# # %% [markdown]
# # ### 7.2.2 Aplicação do teste de Kolmogorov-Smirnov

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para analisar quão bem separados estão os *clusters* delimitados pelo modelo, foi aplicado o teste de Kolmogorov-Smirnov. Esse algoritmo realiza um teste estatístico (teste de hipóteses) que compara a distribuição de dados em dois diferentes *clusters* e aceita ou não a hipótese de que as distribuições são consideravelmente diferentes. Além disso, o teste de Kolmogorov-Smirnov é um teste não-paramétrico, ou seja, funciona para diferentes distribuições. 
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Para medição do resultado, o teste KS conta com duas métricas: o KS Statistic reflete a maior diferença entre as distribuições cumulativas das duas amostras, enquanto que o p-value reflete a probabilidade de que as distribuições sejam diferentes e é a significância do teste. Assim, resultados com alto KS e baixo p-value indicam diferentes distribuições. Nesse sentido, quanto mais o valor do KS se aproxima de 1 e quanto mais o valor do p-value se aproxima de 0, maiores são as evidências de que os dados regulares e os dados anômalos foram bem divididos pelo modelo.
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Assim, para analisar os valores de KS e p-value e as distribuições dos dados, foram realizadas as comparações das *features* nos 3 *clusters* utilizados no *K-means*.
# # 

# # %%
# from scipy import stats
# from tqdm import tqdm

# # Lista de clusters presentes
# clusters = df_sample['cluster'].unique()

# # Dicionários para armazenar resultados
# p_values = {}
# p_stats = {}

# resultados = []

# # Iterando sobre as colunas selecionadas
# for col in tqdm(colunas_selecionadas):
#     for i in range(len(clusters)):
#         for j in range(i + 1, len(clusters)):
#             cluster_i = df_sample[df_sample['cluster'] == clusters[i]]
#             cluster_j = df_sample[df_sample['cluster'] == clusters[j]]
            
#             if len(cluster_i) > 0 and len(cluster_j) > 0:
#                 # Executando o KS test entre dois clusters
#                 stats_, pvalue = stats.kstest(cluster_i[col], cluster_j[col])
#                 p_values[f'{col}_cluster_{clusters[i]}_vs_{clusters[j]}'] = pvalue
#                 p_stats[f'{col}_cluster_{clusters[i]}_vs_{clusters[j]}'] = stats_

#             # Adicionando os resultados à lista
#                 resultados.append({
#                     'Comparação': f'{col}_cluster_{clusters[i]}_vs_{clusters[j]}',
#                     'KS Statistic': stats_,
#                     'P-value': pvalue
#                 })

# # Convertendo para DataFrame
# df_resultados = pd.DataFrame(resultados)

# # Exibindo os resultados
# for key in p_stats:
#     print(f"Comparação: {key}, KS Statistic: {p_stats[key]:.4f}, P-value: {p_values[key]:.4f}")


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para melhor visualização da relação e comparação entre as features nos diferentes agrupamentos de dados utilizados no modelo, foram analisados graficamente o KS statistic e o p-value de cada comparação para a identificação das melhores comparações.
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;A análise começou separadamente, tentando identificar quais as comparações entre *clusters* com menor p-value e qual as features que foram comparadas. No gráfico, é possível visualizar comparações com p-value menores que 5%, o que indica um bom resultado.

# # %%
# df_resultados

# # Ordenar o DataFrame pelos menores p-values
# df_ks_sorted = df_resultados.sort_values(by='P-value', ascending=True)

# # Filtrar os n melhores resultados (exemplo: os 10 melhores)
# n = 10
# df_top_n = df_ks_sorted.head(n)

# # Plotar um gráfico de barras com as comparações que melhor performaram
# plt.figure(figsize=(10, 6))
# sns.barplot(x='P-value', y='Comparação', data=df_top_n, palette='viridis')

# # Personalizações
# plt.title(f'Top {n} Comparações com Menores P-values (Teste KS)', fontsize=16)
# plt.xlabel('P-value', fontsize=12)
# plt.ylabel('Comparação', fontsize=12)
# plt.grid(True)
# plt.show()

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Depois, foram analisadas as comparações em relação ao valor de KS. Nesse sentido, foram identificadas as comparações entre *clusters* com os maiores valores de KS e dentre eles, apenas 3 possuem KS maior que 0.8, o que indica distribuições de dados que não são drasticamente diferentes e apenas as comparações com KS = 1 indicam distribuições diferentes.

# # %%
# # Ordenar o DataFrame pelos maiores KS Statistics
# df_ks_sorted_by_stat = df_resultados.sort_values(by='KS Statistic', ascending=False)

# # Filtrar os n melhores resultados (exemplo: os 10 maiores KS Statistics)
# df_top_n_stat = df_ks_sorted_by_stat.head(n)

# # Plotar um gráfico de barras com as comparações que tiveram os maiores KS Statistics
# plt.figure(figsize=(10, 6))
# sns.barplot(x='KS Statistic', y='Comparação', data=df_top_n_stat, palette='magma')

# # Personalizações
# plt.title(f'Top {n} Comparações com Maiores KS Statistics', fontsize=16)
# plt.xlabel('KS Statistic', fontsize=12)
# plt.ylabel('Comparação', fontsize=12)
# plt.grid(True)
# plt.show()


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Posteriormente, os dados das comparações com melhor KS (KS próximo de 1) e melhor p-value (p-value próximo de 0) foram analisados juntos em um único gráfico. Assim, a melhor comparação foi feita na *feature* de consumo em metro cúbico entre os clusters 0 e 2, pois possui KS igual a 1 e p-value igual a 0.

# # %%
# n = 10

# # Ordenar por p-value (ascendente) e KS Statistic (descendente)
# df_sorted_by_pvalue = df_resultados.sort_values(by='P-value', ascending=True)
# df_sorted_by_ks = df_resultados.sort_values(by='KS Statistic', ascending=False)

# # Selecionar as top n comparações
# top_n_pvalue = df_sorted_by_pvalue.head(n)
# top_n_ks = df_sorted_by_ks.head(n)

# # Fazer a interseção das comparações que aparecem em ambos os rankings
# df_best_combinations = pd.merge(top_n_pvalue, top_n_ks, on='Comparação')


# # %%
# plt.figure(figsize=(10, 6))

# # Criar o scatter plot (gráfico de dispersão)
# sns.scatterplot(x='P-value_x', y='KS Statistic_y', data=df_best_combinations, hue='Comparação', palette='coolwarm', s=100)

# # Adicionar título e rótulos aos eixos
# plt.title('Comparações com Menores P-values e Maiores KS Statistics', fontsize=16)
# plt.xlabel('P-value', fontsize=12)
# plt.ylabel('KS Statistic', fontsize=12)

# # Exibir a legenda
# plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Comparação')

# # Exibir a grade
# plt.grid(True)

# # Mostrar o gráfico
# plt.show()


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Por fim, foi analisada a porcentagem e quantidade de comparações relevantes e bem dispersas pelo modelo. Foi utilizado um filtro para os resultados com significância (p-value) menores que 5% e KS maiores que 80%, e os dados obtidos foram comparados com o total de comparações geradas pelo teste de Komorogov-Smirnov.

# # %%
# # Filtrar as comparações que atendem aos critérios
# filtro = (df_resultados['P-value'] < 0.05) & (df_resultados['KS Statistic'] > 0.7)

# # Número de comparações que atendem aos critérios
# num_comparacoes = filtro.sum()

# # Total de comparações
# total_comparacoes = len(df_resultados)

# # Porcentagem
# porcentagem = (num_comparacoes / total_comparacoes) * 100

# # Exibir a porcentagem
# print(f'Porcentagem de comparações com P-value < 0.05 e KS Statistic > 0.7: {porcentagem:.4f}%')


# # %% [markdown]
# # ### 7.2.3 Análise do dataframe de anomalias e relações entre features

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A próxima etapa da análise dos resultados é caracterizada pela investigação mais profunda dos dados e das relações entre as features entre as linhas que foram classificadas como anomalias pelo modelo.
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Primeiro, os dados anômalos foram armazenados em um *dataframe* separado, para facilitar o manuseio dos mesmos.

# # %%
# # Filtrando os dados identificados como anomalias
# df_anomalias = df_sample[df_sample['anomaly'] == True]

# # Visualizando as primeiras linhas dos dados de anomalias
# df_anomalias.head(10)


# # %% [markdown]
# # #### 7.2.3.1 Distribuição da variação de consumo por cluster

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Foram investigadas as relações das features dentro dos *clusters*, começando pela análise de distribuições da variação de consumo entre os *clusters*. Assim, é possível identificar as anomalias de registro ou possíveis fraudes dentro do *cluster* 2, também identificadas no pré-processamento.

# # %%
# sns.boxplot(x='cluster', y='variação_consumo', data=df_anomalias)
# plt.title('Distribuição da Variação de Consumo por Cluster')
# plt.show()


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após identificar as anomalias de registro de consumo negativo, os dados foram analisados mais de perto. Assim, 4 dados no *cluster 2* possuem registros negativos com clientes diferentes, mas datas próximas, e devem ser observados posteriormente.

# # %%
# df_anomalias.loc[(df_anomalias['cluster'] == 1) & (df_anomalias['variação_consumo'] < 0)]


# # %% [markdown]
# # #### 7.2.3.2 Relação entre a distância ao centróide e a variação de consumo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Depois, foram analisados os dados anômalos em relação à distância dos centróides e à variação de consumo. Foram identificados dados anômalos muito próximos ao centróide, o que pode indicar uma classificação não efetiva, pois o critério utilizado no modelo *K-means* é que maiores distâncias representam possíveis anomalias.

# # %%
# sns.scatterplot(x='distance_to_centroid', y='variação_consumo', hue='anomaly', data=df_anomalias)
# plt.title('Relação entre Distância ao Centróide e Variação de Consumo')
# plt.show()


# # %% [markdown]
# # #### 7.2.3.3 Quantidade de anomalias por categoria da residência

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Por fim, foi analisada a quantidade de anomalias pela categoria da residência e as do tipo de prédio existente individual obtiveram a maior quantidade de anomalias, possivelmente indicando que residências desse tipo devem ser observadas posteriormente.

# # %%
# # Filtrando as colunas de categoria que são booleanas (True/False)
# colunas_categoria = ['categoria_CONSTRUTORAS COLETIVO', 
#                      'categoria_PRÉDIO EXISTENTE INDIVIDUAL',
#                      'categoria_PRÉDIOS EXISTENTES COLETIVOS', 
#                      'categoria_RES. UNIFAMILIAR']

# # Criando um DataFrame para plotagem
# df_categoria = df_anomalias.melt(id_vars='anomaly', value_vars=colunas_categoria, 
#                                  var_name='Categoria', value_name='Valor')

# # Filtrando apenas as linhas onde a categoria é True
# df_categoria_true = df_categoria[df_categoria['Valor'] == True]

# # Plotando o gráfico
# plt.figure(figsize=(10, 6))
# sns.countplot(x='Categoria', hue='anomaly', data=df_categoria_true, palette='coolwarm')

# # Personalizando
# plt.title('Comparação de Anomalias por Categoria', fontsize=16)
# plt.xlabel('Categoria', fontsize=12)
# plt.ylabel('Contagem', fontsize=12)
# plt.xticks(rotation=45)
# plt.legend(title='Anomalia', loc='upper right')
# plt.show()



# # %% [markdown]
# # # 8. Métricas

# # %% [markdown]
# # ## 8.1. Definição do K do modelo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Modelos de aprendizagem não-supervisionada são aqueles que devem ser utilizados em casos de análise de dados onde tais dados não estão rotulados. No caso atual, como não existe nenhum tipo de rótulo sobre anomalias/fraudes no consumo de gás na base de dados, o modelo a ser usado será um não-supervisionado. Como discutido acima, utilizaremos, inicialmente, o modelo K-Means, e a presente seção tem como objetivo rodar um algoritmo que consiga identificar qual o melhor valor de K para rodar este modelo.

# # %% [markdown]
# # ### 8.1.2 Cálculo do K

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O algoritmo abaixo roda o Kmeans para diversos valores em um intervalo de 1 a 10 e analisa a inercia em cada caso, ou seja, o quanto de variação existe entre um K e outro.

# # %%
# from sklearn.cluster import KMeans

# inercia = []
# colunas = [
#     'temp_scaled',
#     'meterIndex',
#     'initialIndex',
#     'pulseCount',
#     'gain',
#     'model_IG1K-L-v2',
#     'model_Infinity V2',
#     'inputType_encoded',
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Caldeira',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'consumo em m^3',
#     'variação_consumo'    
# ]

# K_range = range(1, 11)


# for k in K_range:
#     kmeans = KMeans(n_clusters=k, random_state=42)
#     kmeans.fit(df_merged[colunas])
#     inercia.append(kmeans.inertia_)


# # %% [markdown]
# # ### 8.1.3. Gráfico do cotovelo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A partir da inércia obtida no algoritmo acima, podemos plotar um gráfico para a inércia respectiva de cada K. O processo de escolher o valor de K consiste em analisar o gráfico e identificar o "cotovelo", ou seja, o local de quebra do gráfico, onde a variação entre um K e o seguinte deixa de ser relevante.

# # %%
# ## Plotagem do gráfico do cotovelo
# plt.figure(figsize=(8, 5))
# plt.plot(K_range, inercia, 'bo-')
# plt.xlabel('Número K de clusters')
# plt.ylabel('Inércia')
# plt.title('Método do Cotovelo para escolher o K ideal')
# plt.show()

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;De acordo com o gráfico, definimos inicialmente um valor de K = 3.

# # %% [markdown]
# # # 9. Sistema de Recomendação

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Os sistemas de recomendação são ferramentas que utilizam algoritmos especializados e técnicas de aprendizado de máquina para processar dados e fornecer sugestões personalizadas. Esses sistemas conseguem identificar padrões e prever preferências com base em interações anteriores. A aplicação desses algoritmos permite que empresas ofereçam uma experiência mais personalizada, aumentando a satisfação e o engajamento do cliente.

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para o desenvolvimento de um sistema de recomendação, o grupo definiu três cenários distintos: uso geral (para todos os clientes), uso empresarial (focado em clientes corporativos e condomínios) e uso residencial (destinado a clientes que utilizam gás em suas residências). Com base nesses cenários, planejamos segmentar os picos de consumo em intervalos de 4 horas, permitindo identificar os períodos de maior demanda e calcular a média de consumo nos blocos de menor utilização. A partir dessa análise, será possível propor à Compass um esquema otimizado de quatro intervalos de horários para o uso do gás, ajudando a mitigar sobrecargas no sistema e melhorar a eficiência do fornecimento.

# # %% [markdown]
# # ## 9.1. Cenário 1 - Consumo de gás de todos os clientes

# # %% [markdown]
# # Importando bibliotecas necessárias para o sistema de recomendação  

# # %%
# from sklearn.neighbors import NearestNeighbors
# from sklearn.preprocessing import MinMaxScaler

# # %% [markdown]
# # Determinando clientes com padrões de consumo similares em blocos de 4 horas

# # %%
# #ransformar a coluna 'datetime' em formato datetime
# df_merged['datetime'] = pd.to_datetime(df_merged['datetime'])

# #Criar blocos de 4 horas, dividindo o dia em 6 blocos (0-3h, 4-7h, etc.)
# df_merged['hour_block'] = (df_merged['datetime'].dt.hour // 4) * 4  # Agrupa as horas em blocos de 4

# #Agrupar os dados por 'clientCode' e 'hour_block' para calcular a média de consumo em cada bloco de 4 horas para cada cliente
# client_block_consumption = df_merged.groupby(['clientCode_encoded', 'hour_block'])['variação_consumo'].mean().reset_index()

# #Criar uma tabela pivotada, onde cada linha é um cliente, cada coluna é um bloco de 4 horas, e os valores são as médias de consumo
# pivot_table = client_block_consumption.pivot(index='clientCode_encoded', columns='hour_block', values='variação_consumo').fillna(0)

# #Normalizar os dados (opcional, mas pode ajudar nos cálculos de similaridade)
# scaler = MinMaxScaler()
# pivot_table_scaled = scaler.fit_transform(pivot_table)

# #Criar o modelo de vizinhos mais próximos
# knn = NearestNeighbors(metric='cosine', algorithm='auto')
# knn.fit(pivot_table_scaled)

# #Definir uma função para recomendar clientes com padrões de consumo similares com base nos blocos de 4 horas
# def recomendar_horario_similar(client_id, num_recommendations=5):
#     # Pegar os dados de consumo do cliente especificado
#     client_index = pivot_table.index.get_loc(client_id)
#     client_data = pivot_table_scaled[client_index].reshape(1, -1)

#     # Encontrar os vizinhos mais próximos (clientes com padrões de consumo mais similares)
#     distances, indices = knn.kneighbors(client_data, n_neighbors=num_recommendations+1)

#     # Exibir os IDs dos clientes recomendados (excluindo o próprio cliente)
#     recommended_clients = pivot_table.index[indices.flatten()[1:]]

#     return recommended_clients

# recomendacoes = recomendar_horario_similar(0, num_recommendations=100)
# print("Clientes com padrões de consumo similares:", recomendacoes)

# # %% [markdown]
# # Gerando gráfico de calor demonstrando blocos de horas com maior consumo

# # %%
# #Função para gerar o mapa de calor destacando picos de uso mais semelhantes
# def plot_recommended_heatmap_with_peaks(recommended_clients):
#     plt.figure(figsize=(12, 8))
    
#     # Filtrar a pivot_table para incluir apenas os clientes recomendados
#     filtered_pivot_table = pivot_table.loc[recommended_clients]
    
#     # Encontrar os picos de consumo para cada cliente (maiores valores de cada linha)
#     peak_values = filtered_pivot_table.max(axis=1)
    
#     # Criar uma matriz de anotações, com destaque para os picos de consumo
#     annotations = np.empty_like(filtered_pivot_table.values, dtype=str)
    
#     for i, client in enumerate(filtered_pivot_table.index):
#         for j, block in enumerate(filtered_pivot_table.columns):
#             if filtered_pivot_table.loc[client, block] == peak_values[client]:
#                 # Destacar o valor do pico
#                 annotations[i, j] = f'⬤'
#             else:
#                 annotations[i, j] = ''
    
#     # Criar o heatmap com anotações dos picos
#     sns.heatmap(filtered_pivot_table, cmap="YlGnBu", cbar=True, annot=annotations, fmt='', linewidths=.5, linecolor='white')
    
#     # Ajustar os rótulos dos blocos de horas no eixo X (0-3h, 4-7h, etc.)
#     block_labels = [f'{block}-{block+3}h' for block in filtered_pivot_table.columns]
#     plt.xticks(ticks=np.arange(len(block_labels)) + 0.5, labels=block_labels, rotation=45)

#     plt.title('Mapa de Calor - Picos de Consumo Semelhantes por Blocos de 4 Horas (Clientes Recomendados)')
#     plt.xlabel('Bloco de Horas')
#     plt.ylabel('Cliente (Código)')
    
#     # Exibir o gráfico
#     plt.tight_layout()
#     plt.show()

# # Chamar a função com os clientes recomendados
# plot_recommended_heatmap_with_peaks(recomendacoes)

# # %% [markdown]
# # Gerando sistema de recomendação de bloco de hora com menor consumo

# # %%
# #Função para recomendar o melhor horário de consumo com base nos padrões temporais dos clientes recomendados
# def recomendar_melhor_horario(client_id, num_recommendations=5):
#     # Obter os clientes com padrões de consumo similares
#     recommended_clients = recomendar_horario_similar(client_id, num_recommendations)

#     # Filtrar a pivot_table para incluir apenas os clientes recomendados
#     filtered_pivot_table = pivot_table.loc[recommended_clients]

#     # Calcular a média de consumo em cada bloco de horas para os clientes recomendados
#     mean_consumption_per_block = filtered_pivot_table.mean(axis=0)

#     # Identificar o bloco de horário com menor consumo médio (ou ajustar a lógica para maximizar a eficiência)
#     # Aqui, menor consumo médio pode ser interpretado como um horário mais "eficiente"
#     best_hour_block = mean_consumption_per_block.idxmin()

#     # Retornar o bloco de horário recomendado
#     return best_hour_block, mean_consumption_per_block[best_hour_block]


# melhor_horario, consumo_medio = recomendar_melhor_horario(0, num_recommendations=1716)
# print(f"O melhor horário recomendado para consumo é o bloco que inicia as: {melhor_horario}h, com um consumo médio de {consumo_medio:.2f} m³")

# # %% [markdown]
# # ## 9.2. Cenário 2 - Consumo de gás empresarial

# # %% [markdown]
# # Determinando empresas com padrões de consumo similares em blocos de 4 horas

# # %%
# # Filtrar dados apenas empresariais, agrupando as condições entre parênteses
# df_empresarial = df_merged[(df_merged['categoria_CONSTRUTORAS COLETIVO']) | (df_merged['categoria_PRÉDIOS EXISTENTES COLETIVOS'])]

# # Criar pivot table para consumo empresarial
# client_block_consumption_empresarial = df_empresarial.groupby(['clientCode_encoded', 'hour_block', 'clientIndex'])['variação_consumo'].mean().reset_index()
# pivot_table_empresarial = client_block_consumption_empresarial.pivot(index='clientCode_encoded', columns='hour_block', values='variação_consumo').fillna(0)

# # Normalizar e criar modelo KNN
# scaler = MinMaxScaler()
# pivot_table_scaled_empresarial = scaler.fit_transform(pivot_table_empresarial)
# knn_empresarial = NearestNeighbors(metric='cosine', algorithm='auto')
# knn_empresarial.fit(pivot_table_scaled_empresarial)

# # Função para recomendação empresarial
# def recomendar_horario_similar_empresarial(client_id, num_recommendations=5):
#     try:
#         client_index = pivot_table_empresarial.index.get_loc(client_id)
#     except KeyError:
#         print(f"Cliente {client_id} não encontrado.")
#         return []

#     client_data = pivot_table_scaled_empresarial[client_index].reshape(1, -1)
#     distances, indices = knn_empresarial.kneighbors(client_data, n_neighbors=num_recommendations + 1)
#     recommended_clients = pivot_table_empresarial.index[indices.flatten()[1:]]
#     return recommended_clients

# # Exemplo de uso: testar com um ID válido
# recomendacoes_empresarial = recomendar_horario_similar_empresarial(115, num_recommendations=39)
# print(recomendacoes_empresarial)

# # %% [markdown]
# # Gerando gráfico de calor demonstrando blocos de horas com maior consumo

# # %%
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np

# def plot_empresarial_heatmap_with_peaks(recommended_clients):
#     plt.figure(figsize=(12, 8))

#     # Filtrar a tabela de pivot para os clientes recomendados
#     filtered_pivot_table_empresarial = pivot_table_empresarial.loc[recommended_clients]
    
#     # Encontrar os valores máximos para marcar os picos
#     peak_values = filtered_pivot_table_empresarial.max(axis=1)
    
#     # Criar anotações para os picos
#     annotations = np.empty_like(filtered_pivot_table_empresarial.values, dtype=str)
#     for i, client in enumerate(filtered_pivot_table_empresarial.index):
#         for j, block in enumerate(filtered_pivot_table_empresarial.columns):
#             value = filtered_pivot_table_empresarial.loc[client, block]
#             if value == 0:
#                 annotations[i, j] = ''
#             elif value == peak_values[client]:
#                 annotations[i, j] = '⬤'
#             else:
#                 annotations[i, j] = ''

#     # Criar o heatmap
#     sns.heatmap(filtered_pivot_table_empresarial, cmap="YlGnBu", cbar=True, annot=annotations, fmt='', linewidths=.5, linecolor='white')

#     # Configurar os rótulos dos blocos de horas
#     block_labels = [f'{block}-{block+3}h' for block in filtered_pivot_table_empresarial.columns]
#     plt.xticks(ticks=np.arange(len(block_labels)) + 0.5, labels=block_labels, rotation=45)

#     plt.title('Mapa de Calor - Picos de Consumo Empresarial')
#     plt.xlabel('Bloco de Horas')
#     plt.ylabel('Cliente (Código)')
#     plt.tight_layout()
#     plt.show()

# # Exibir o gráfico com um ID de cliente válido
# recomendacoes_empresarial = recomendar_horario_similar_empresarial(115, num_recommendations=39)
# plot_empresarial_heatmap_with_peaks(recomendacoes_empresarial)

# # %% [markdown]
# # Gerando sistema de recomendação de bloco de hora com menor consumo

# # %%
# def recomendar_melhor_horario_empresarial(client_id, num_recommendations=5):
#     recommended_clients = recomendar_horario_similar_empresarial(client_id, num_recommendations)
#     filtered_pivot_table_empresarial = pivot_table_empresarial.loc[recommended_clients]
#     mean_consumption_per_block = filtered_pivot_table_empresarial.mean(axis=0)
#     best_hour_block = mean_consumption_per_block.idxmin()
#     return best_hour_block, mean_consumption_per_block[best_hour_block]

# melhor_horario_empresarial, consumo_medio_empresarial = recomendar_melhor_horario_empresarial(877, num_recommendations=39)
# print(f"O melhor horário recomendado para consumo empresarial é o bloco que se inicia as: {melhor_horario_empresarial}h, com consumo médio de {consumo_medio_empresarial:.2f} m³")

# # %% [markdown]
# # ## 9.3. Cenário 3 - Consumo de gás residencial

# # %% [markdown]
# # Determinando clientes com padrões de consumo similares em blocos de 4 horas

# # %%
# # Filtrar dados apenas residenciais
# df_residencial = df_merged[~((df_merged['categoria_CONSTRUTORAS COLETIVO']) | (df_merged['categoria_PRÉDIOS EXISTENTES COLETIVOS']))]

# # Criar pivot table para consumo residencial
# client_block_consumption_residencial = df_residencial.groupby(['clientCode_encoded', 'hour_block'])['variação_consumo'].mean().reset_index()
# pivot_table_residencial = client_block_consumption_residencial.pivot(index='clientCode_encoded', columns='hour_block', values='variação_consumo').fillna(0)

# # Normalizar e criar modelo KNN
# pivot_table_scaled_residencial = scaler.fit_transform(pivot_table_residencial)
# knn_residencial = NearestNeighbors(metric='cosine', algorithm='auto')
# knn_residencial.fit(pivot_table_scaled_residencial)

# # Função para recomendação residencial
# def recomendar_horario_similar_residencial(client_id, num_recommendations=5):
#     client_index = pivot_table_residencial.index.get_loc(client_id)
#     client_data = pivot_table_scaled_residencial[client_index].reshape(1, -1)
#     distances, indices = knn_residencial.kneighbors(client_data, n_neighbors=num_recommendations + 1)
#     recommended_clients = pivot_table_residencial.index[indices.flatten()[1:]]
#     return recommended_clients

# recomendacoes_residencial = recomendar_horario_similar_residencial(0, num_recommendations=80)


# # %% [markdown]
# # Gerando gráfico de calor demonstrando blocos de horas com maior consumo

# # %%
# def plot_residencial_heatmap_with_peaks(recommended_clients):
#     plt.figure(figsize=(12, 8))

#     filtered_pivot_table_residencial = pivot_table_residencial.loc[recommended_clients]
#     peak_values = filtered_pivot_table_residencial.max(axis=1)
#     annotations = np.empty_like(filtered_pivot_table_residencial.values, dtype=str)
    
#     for i, client in enumerate(filtered_pivot_table_residencial.index):
#         for j, block in enumerate(filtered_pivot_table_residencial.columns):
#             if filtered_pivot_table_residencial.loc[client, block] == peak_values[client]:
#                 annotations[i, j] = '⬤'
#             else:
#                 annotations[i, j] = ''

#     sns.heatmap(filtered_pivot_table_residencial, cmap="YlGnBu", cbar=True, annot=annotations, fmt='', linewidths=.5, linecolor='white')

#     block_labels = [f'{block}-{block+3}h' for block in filtered_pivot_table_residencial.columns]
#     plt.xticks(ticks=np.arange(len(block_labels)) + 0.5, labels=block_labels, rotation=45)

#     plt.title('Mapa de Calor - Picos de Consumo Residencial')
#     plt.xlabel('Bloco de Horas')
#     plt.ylabel('Cliente (Código)')
#     plt.tight_layout()
#     plt.show()

# # Exibir o gráfico
# plot_residencial_heatmap_with_peaks(recomendacoes_residencial)


# # %% [markdown]
# # Gerando sistema de recomendação de bloco de hora com menor consumo

# # %%
# def recomendar_melhor_horario_residencial(client_id, num_recommendations=5):
#     recommended_clients = recomendar_horario_similar_residencial(client_id, num_recommendations)
#     filtered_pivot_table_residencial = pivot_table_residencial.loc[recommended_clients]
#     mean_consumption_per_block = filtered_pivot_table_residencial.mean(axis=0)
#     best_hour_block = mean_consumption_per_block.idxmin()
#     return best_hour_block, mean_consumption_per_block[best_hour_block]

# melhor_horario_residencial, consumo_medio_residencial = recomendar_melhor_horario_residencial(0, num_recommendations=1676)
# print(f"O melhor horário recomendado para o cenário de análise residencial é o bloco: {melhor_horario_residencial}h, com consumo médio de {consumo_medio_residencial:.2f} m³")

# # %% [markdown]
# # # 10. Isolation Forest

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O Isolation Forest é um algoritmo de aprendizado não supervisionado, utilizado para detecção de anomalias em conjuntos de dados (LIU, 2008). Desse modo, diferente de outros métodos, ele não requer rótulos para identificar padrões incomuns, pois o algoritmo funciona isolando pontos de dados por meio de divisões aleatórias, criando árvores de decisão. Assim, pontos que são rapidamente isolados, ou seja, separados com poucas divisões, são considerados anomalias, pois eles diferem do comportamento geral dos dados. Esse método é eficiente e escalável, sendo amplamente usado para detectar outliers em grandes volumes de dados.

# # %% [markdown]
# # ## 10.1 Criação do Modelo e Ultilização das Métricas

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Abaixo podemos identificar o desenvolvimento do modelo Isolation Forest, usando as métricas Davies-Bouldin Index (DBI), Calinski-Harabasz Index (CH Index) e Silhouette Score:

# # %%
# colunas_selecionadas = [
#     'temp_scaled',
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'perfil_consumo_Cocção + Caldeira',
#     'consumo em m^3',
#     'variação_consumo',
# ]


# # %%
# import numpy as np
# import pandas as pd
# from sklearn.ensemble import IsolationForest
# from sklearn.metrics import davies_bouldin_score, silhouette_score, calinski_harabasz_score
# from sklearn.preprocessing import StandardScaler

# # Função auxiliar para checar e validar dados
# def validar_dados(df, colunas):
#     if df.empty:
#         raise ValueError("O DataFrame df_sample está vazio.")
#     if not all(col in df.columns for col in colunas):
#         raise ValueError("Uma ou mais colunas selecionadas não estão presentes no DataFrame.")
#     return True

# # Validação dos dados
# validar_dados(df_sample, colunas_selecionadas)

# # Pré-processamento dos dados
# scaler = StandardScaler()
# df_scaled = scaler.fit_transform(df_sample[colunas_selecionadas])

# # ---- Isolation Forest ----
# try:
#     # Configurando o modelo Isolation Forest
#     contamination = 0.05  # Ajuste conforme a análise de anomalias
#     iso_forest = IsolationForest(contamination=contamination, random_state=42)
    
#     # Detectando anomalias
#     df_sample['anomaly_isoforest'] = iso_forest.fit_predict(df_scaled)
#     df_sample['anomaly_isoforest'] = df_sample['anomaly_isoforest'].map({1: 0, -1: 1})  # 0 para normal, 1 para anomalia
    
#     # Informando a quantidade de anomalias detectadas
#     num_anomalias = df_sample['anomaly_isoforest'].sum()
#     print(f"Número de anomalias detectadas: {num_anomalias} de {len(df_sample)} amostras.")
    
#     # Calculando o Davies-Bouldin Index (DBI)
#     dbi_isoforest = davies_bouldin_score(df_scaled, df_sample['anomaly_isoforest'])
#     print(f"Davies-Bouldin Index (DBI) Isolation Forest: {dbi_isoforest:.4f}")
    
#     # Calculando o Calinski-Harabasz Index (CH Index)
#     ch_index_isoforest = calinski_harabasz_score(df_scaled, df_sample['anomaly_isoforest'])
#     print(f"Calinski-Harabasz Index (CH Index) Isolation Forest: {ch_index_isoforest:.4f}")
    
#     # Verificação condicional para o Silhouette Score
#     if num_anomalias > 0 and num_anomalias < len(df_sample):
#         # Calculando o Silhouette Score com uma amostragem de 10% dos dados
#         sample_size = 0.1
#         df_sampled = df_sample.sample(frac=sample_size, random_state=42)
#         silhouette_isoforest = silhouette_score(df_sampled[colunas_selecionadas], df_sampled['anomaly_isoforest'])
#         print(f"Silhouette Score Isolation Forest (amostragem): {silhouette_isoforest:.4f}")
#     else:
#         print("Não foi possível calcular o Silhouette Score, pois não há uma separação adequada entre anomalias e normais.")
    
# except Exception as e:
#     print(f"Erro ao aplicar Isolation Forest: {e}")


# # %% [markdown]
# # ## 10.2 Análise dos Resultados das Métricas

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; Analisar os resultados das métricas de um modelo preditivo não supervisionado de detecção de anomalias é crucial para avaliar a eficácia do modelo em identificar padrões anômalos sem o uso de rótulos previamente definidos. Métricas como o Índice de Silhueta, o Índice de Davies-Bouldin (DBI) e o Índice de Calinski-Harabasz (CH) fornecem insights sobre a coesão e separação dos grupos detectados, ajudando a entender a qualidade da segmentação entre os dados normais e anômalos. Uma análise cuidadosa dessas métricas permite refinar o modelo, identificar limitações e ajustar parâmetros para obter maior precisão na detecção de anomalias, garantindo que o modelo atenda às expectativas do projeto (STRAUSS, 2022).

# # %% [markdown]
# # ### 10.2.1 Contagem: Normal vs Anomalia

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O objetivo deste gráfico é visualizar a distribuição das amostras classificadas pelo modelo Isolation Forest, destacando a quantidade de amostras normais em comparação com as anômalas. Ao exibir essas contagens de forma clara, o gráfico permite uma análise rápida da proporção de anomalias detectadas em relação ao total de amostras, facilitando a compreensão da eficácia do modelo na identificação de padrões fora do comum dentro do conjunto de dados.

# # %%
# import seaborn as sns
# import matplotlib.pyplot as plt

# # Contagem de normais vs anomalias 
# sns.countplot(x='anomaly_isoforest', hue='anomaly_isoforest', data=df_sample, palette='coolwarm', legend=False)
# plt.title('Contagem de Amostras: Normais vs Anomalias')
# plt.xlabel('0: Normal, 1: Anomalia')
# plt.ylabel('Contagem')
# plt.show()


# # %% [markdown]
# # ### 10.2.2 Variação de Consumo vs Consumo em m³ (Normal vs Anomalia)

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O objetivo desse gráfico de dispersão é visualizar a relação entre a variação de consumo e o consumo em m³, diferenciando as amostras normais e anômalas detectadas pelo modelo Isolation Forest. Ao utilizar cores distintas para normais e anomalias, o gráfico permite identificar padrões ou desvios que podem indicar comportamentos atípicos no consumo, facilitando a análise visual de onde as anomalias ocorrem em relação ao consumo normal. Isso ajuda a avaliar a eficácia do modelo em destacar padrões anômalos e entender melhor a dinâmica do consumo.

# # %%
# plt.figure(figsize=(8, 6))
# sns.scatterplot(x='variação_consumo', y='consumo em m^3', hue='anomaly_isoforest', data=df_sample, palette='coolwarm')
# plt.title('Variação de Consumo vs Consumo em m³ (Normais vs Anomalias)')
# plt.xlabel('Variação de Consumo')
# plt.ylabel('Consumo em m³')
# plt.legend(title='Anomalia')
# plt.show()


# # %% [markdown]
# # ### 10.2.3 Gráfico 3D: Variação de Consumo, Consumo em m³ e Perfil de Consumo (Normal vs Anomalia)

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O objetivo deste gráfico 3D é visualizar e diferenciar visualmente as anomalias em um conjunto de dados de consumo de gás, usando o modelo de detecção de anomalias Isolation Forest. O gráfico apresenta três dimensões relevantes: variação de consumo, consumo em m³ e perfil de consumo do aquecedor. Os pontos normais são representados em azul, enquanto as anomalias são destacadas em vermelho. Essa visualização permite identificar padrões e comportamentos distintos entre dados normais e anômalos, ajudando na análise e validação da eficácia do modelo de detecção de anomalias.

# # %%
# from mpl_toolkits.mplot3d import Axes3D

# # Preparando o gráfico 3D
# fig = plt.figure(figsize=(10, 8))
# ax = fig.add_subplot(111, projection='3d')

# # Dados de normais e anomalias
# normais = df_sample[df_sample['anomaly_isoforest'] == 0]
# anomalias = df_sample[df_sample['anomaly_isoforest'] == 1]

# # Plotando os pontos normais
# ax.scatter(normais['variação_consumo'], normais['consumo em m^3'], normais['perfil_consumo_Aquecedor'],
#            c='blue', s=120, edgecolor='black', label='Normal', marker='o', alpha=0.7)

# # Plotando as anomalias sem edgecolor
# ax.scatter(anomalias['variação_consumo'], anomalias['consumo em m^3'], anomalias['perfil_consumo_Aquecedor'],
#            c='red', s=120, label='Anomalia', marker='x', alpha=0.9)

# # Configurações dos eixos e visualização
# ax.set_xlabel('Variação de Consumo')
# ax.set_ylabel('Consumo em m³')
# ax.set_zlabel('Perfil de Consumo Aquecedor')
# ax.view_init(elev=20, azim=60)  # Alterando o ângulo de visualização

# plt.title('Gráfico 3D: Variação de Consumo, Consumo em m³ e Perfil de Consumo')
# plt.legend()
# plt.show()


# # %% [markdown]
# # ### 10.2.4 Perfis de Consumo (Normal vs Anomalia)

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O objetivo deste gráfico de barras empilhadas é comparar os valores dos diferentes perfis de consumo com a ocorrência de anomalias, conforme identificado pelo modelo de detecção de anomalias Isolation Forest. Utilizando o DataFrame `df_perfis`, o gráfico ilustra a distribuição dos valores dos perfis de consumo — como Aquecedor, Caldeira, e Cocção — divididos entre casos normais e anômalos. As barras empilhadas ajudam a visualizar a contribuição relativa de cada perfil de consumo para os dados classificados como normais e anômalos, facilitando a identificação de padrões ou discrepâncias entre os perfis de consumo associados a cada categoria de anomalia.

# # %%
# # Criando o DataFrame para perfis de consumo e anomalias
# df_perfis = df_sample.melt(id_vars=['anomaly_isoforest'], 
#                            value_vars=['perfil_consumo_Aquecedor', 'perfil_consumo_Caldeira', 'perfil_consumo_Cocção', 'perfil_consumo_Cocção + Aquecedor', 'perfil_consumo_Cocção + Aquecedor'],
#                            var_name='Perfil de Consumo', 
#                            value_name='Valor do Perfil')

# # Plotando o gráfico de barras empilhadas
# plt.figure(figsize=(17, 6))
# sns.barplot(x='Perfil de Consumo', y='Valor do Perfil', hue='anomaly_isoforest', data=df_perfis, palette='coolwarm')

# # Customizando o título da legenda para indicar o que 0 e 1 significam
# leg = plt.legend(title='Anomalia')
# leg.texts[0].set_text('0 = Normal')  # Define que 0 é normal
# leg.texts[1].set_text('1 = Anomalia')  # Define que 1 é anomalia

# # Definindo os títulos e rótulos
# plt.title('Gráfico de Barras Empilhadas: Perfis de Consumo vs Anomalias')
# plt.ylabel('Valor do Perfil')
# plt.xlabel('Perfil de Consumo')

# # Mostrando o gráfico
# plt.show()


# # %% [markdown]
# # ### 10.2.5 Consumo em m³ vs Perfis de Consumo (Normal vs Anomalia)

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; O objetivo deste conjunto de gráficos é visualizar a relação entre o consumo em m³ e diferentes perfis de consumo, destacando a distinção entre dados normais e anômalos detectados pelo modelo Isolation Forest. Cada gráfico mostra um perfil específico — Aquecedor, Caldeira, Cocção, Cocção + Aquecedor e Cocção + Caldeira — com linhas representando os dados normais e pontos de dispersão destacando as anomalias. Essa abordagem permite analisar como os padrões de consumo variam entre diferentes perfis e identificar visualmente quaisquer discrepâncias associadas às anomalias. A utilização de diferentes cores e marcadores ajuda a diferenciar os dados normais dos anômalos e a avaliar a eficácia da detecção de anomalias em cada perfil de consumo.

# # %%
# import matplotlib.pyplot as plt

# # Configurações gerais
# plt.figure(figsize=(18, 14))
# plt.title('Gráficos de Dispersão: Perfis de Consumo vs Consumo em m³ (Normais vs Anomalias)', fontsize = 16, pad = 30)


# # Gráfico 1: Aquecedor
# plt.subplot(3, 2, 1)
# plt.plot(df_sample[df_sample['anomaly_isoforest'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_isoforest'] == 0]['perfil_consumo_Aquecedor'], 
#          label='Aquecedor - Normal', color='blue', marker='o', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_isoforest'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_isoforest'] == 1]['perfil_consumo_Aquecedor'], 
#             label='Aquecedor - Anomalia', color='red', s=100, marker='x')
# plt.title('Aquecedor')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Gráfico 2: Caldeira
# plt.subplot(3, 2, 2)
# plt.plot(df_sample[df_sample['anomaly_isoforest'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_isoforest'] == 0]['perfil_consumo_Caldeira'], 
#          label='Caldeira - Normal', color='green', marker='s', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_isoforest'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_isoforest'] == 1]['perfil_consumo_Caldeira'], 
#             label='Caldeira - Anomalia', color='red', s=100, marker='x')
# plt.title('Caldeira')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Gráfico 3: Cocção
# plt.subplot(3, 2, 3)
# plt.plot(df_sample[df_sample['anomaly_isoforest'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_isoforest'] == 0]['perfil_consumo_Cocção'], 
#          label='Cocção - Normal', color='orange', marker='^', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_isoforest'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_isoforest'] == 1]['perfil_consumo_Cocção'], 
#             label='Cocção - Anomalia', color='red', s=100, marker='x')
# plt.title('Cocção')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Gráfico 4: Cocção + Aquecedor
# plt.subplot(3, 2, 4)
# plt.plot(df_sample[df_sample['anomaly_isoforest'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_isoforest'] == 0]['perfil_consumo_Cocção + Aquecedor'], 
#          label='Cocção + Aquecedor - Normal', color='purple', marker='x', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_isoforest'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_isoforest'] == 1]['perfil_consumo_Cocção + Aquecedor'], 
#             label='Cocção + Aquecedor - Anomalia', color='red', s=100, marker='x')
# plt.title('Cocção + Aquecedor')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Gráfico 5: Cocção + Caldeira
# plt.subplot(3, 2, 5)
# plt.plot(df_sample[df_sample['anomaly_isoforest'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_isoforest'] == 0]['perfil_consumo_Cocção + Caldeira'], 
#          label='Cocção + Caldeira - Normal', color='black', marker='d', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_isoforest'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_isoforest'] == 1]['perfil_consumo_Cocção + Caldeira'], 
#             label='Cocção + Caldeira - Anomalia', color='red', s=100, marker='x')
# plt.title('Cocção + Caldeira')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Exibir os gráficos
# plt.tight_layout()
# plt.show()


# # %% [markdown]
# # ## 10.3 Fine tuning de hiperparâmetros do Isolation Forest

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Os hiperparâmetros são variáveis de configuração externa de modelos de aprendizado de máquina. Eles atuam fora da instância dos parâmetros de treinamento do modelo e criam as definições que alteram diretamente o treinamento de dados (AWS, 2024).
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;O modelo utilizado no projeto foi o *Isolation Forest*, o qual possui como hiperparâmetros:
# # - n_estimators: quantidade de árvores;
# # - max_samples: número de amostras para construção das árvores;
# # - contamination: proporção de anomalias que é esperada;
# # - max_features: número de features utilizadas em cada nó;
# # - bootstrap: permissão para que amostras sejam escolhidas de forma repetida ou não;
# # - n_jobs: número de processadores usados para treinar o modelo;
# # - verbose: permissão para acompanhar o progresso ;
# # - warm_start: permissão para utilizar as soluções anteriores em vez de rodar o modelo do zero.
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Para escolha da melhor combinação de hiperparâmetros, é realizado o processo de *fine tuning*, no qual diferentes algoritmos e ferramentas realizam a combinação dos diferentes valores de hiperparâmetros e permitem a escolha das melhores de acordo com alguma métrica escolhida previamente. Para isso, foi escolhida a ferramenta RandomizedSearchCV, a qual realiza o teste de combinações de hiperparâmetros automaticamente e aleatoriamente com base no número de iterações escolhido.
# # 

# # %% [markdown]
# # ### 10.3.1 Aplicação do algoritmo RandomizedSearchCV

# # %% [markdown]
# # #### 10.3.1.1 Definição dos hiperparâmetros

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para funcionamento do RandomizedSearchCV, é necessário definir quais os valores de hiperparâmetro que o algoritmo deve testar. Para isso, foi criado o dicionário param_dist, no qual foram armazenados os hiperparâmetros do modelo Isolation Forest e os possíveis valores.

# # %%
# from sklearn.metrics import make_scorer, davies_bouldin_score, silhouette_score, calinski_harabasz_score
# from sklearn.model_selection import RandomizedSearchCV

# param_dist = {
#     'n_estimators': [50, 100, 150, 200, 300],
#     'max_samples': ['auto', 0.5, 0.75, 1.0],
#     'contamination': [0.01, 0.05, 0.1, 'auto'],
#     'max_features': [0.5, 0.75, 1.0],
#     'bootstrap': [True, False],
#     'n_jobs': [-1, 1],
#     'warm_start': [True, False],
#     'verbose': [0, 1]
# }

# # %% [markdown]
# # #### 10.3.1.2 Criação de uma função única para as 3 métricas: CH Index, DBI e Silhueta

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após isso, é necessário que se escolha uma métrica que o algoritmo utilizará para decidir quais combinações de hiperparâmetros performou melhor. Desse modo, foi criada a função custom_scoring para que as 3 métricas utilizadas (coeficiente da silhueta, DBI e CH Index) pudessem ser utilizadas ao mesmo tempo pelo algoritmo de fine tuning.

# # %%
# def custom_scoring(estimator, X):
#     labels = estimator.fit_predict(X)
#     sil_score = silhouette_score(X, labels)
#     dbi_score = davies_bouldin_score(X, labels)
#     ch_score = calinski_harabasz_score(X, labels)
#     return sil_score

# scorer = make_scorer(custom_scoring)

# # %% [markdown]
# # #### 10.3.1.3 Definição do algoritmo de fine tuning

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para que o algoritmo de fine tuning possa ser implementado, algumas configurações são necessárias, como o modelo de ML, os hiperparâmetros do modelo, o número de iterações do algoritmo, a métrica utilizada e a quantidade de validações cruzadas.

# # %%
# random_search = RandomizedSearchCV(
#     iso_forest, 
#     param_distributions=param_dist, 
#     n_iter=50,
#     cv=5, 
#     scoring=scorer, 
#     n_jobs=-1,
#     verbose=1
# )

# # %% [markdown]
# # #### 10.3.1.4 Descoberta dos melhores hiperparâmetros

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após rodar o algoritmo de fine tuning, os melhores hiperparâmetros que fizessem o modelo ter melhor performance foram encontrados.

# # %%
# # random_search.fit(df_scaled)

# # print("Melhores hiperparâmetros encontrados:")
# # print(random_search.best_params_)


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Melhores hiperparâmetros encontrados: <br>
# # {'warm_start': True, 'verbose': 0, 'n_jobs': 1, 'n_estimators': 150, 'max_samples': 1.0, 'max_features': 1.0, 'contamination': 'auto', 'bootstrap': False}

# # %% [markdown]
# # #### 10.3.1.5 Treinamento do modelo com os melhores hiperparâmetros encontrados

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Depois de encontrados, os melhores hiperparâmetros foram utilizados para treinar novamente o modelo em busca de validar a melhoria de performace.

# # %%
# iso_forest_tuning = random_search.best_estimator_
# iso_forest_tuning.fit(df_scaled)
# labels_iso_forest_tuning = iso_forest_tuning.predict(df_scaled)

# # %% [markdown]
# # #### 10.3.1.6 Definição de resultados das métricas para o modelo treinado com os melhores hiperparâmetros

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Por fim, foram calculadas as métricas de coeficiente da silhueta, DBI e CH Index para o novo modelo, as quais permitiram identificar a melhor clusterização e divisão entre os dados normais e anômalos.

# # %%
# #silhouette_best = silhouette_score(df_scaled, labels_iso_forest_tuning)
# #dbi_best = davies_bouldin_score(df_scaled, labels_iso_forest_tuning)
# #ch_best = calinski_harabasz_score(df_scaled, labels_iso_forest_tuning)

# # print(f"\nMelhores resultados para o modelo otimizado:")
# # print(f"Silhouette Score: {silhouette_best:.4f}")
# # print(f"Davies-Bouldin Index: {dbi_best:.4f}")
# # print(f"Calinski-Harabasz Index: {ch_best:.4f}")

# # %% [markdown]
# # Melhores resultados para o modelo otimizado:
# # 
# # * Silhouette Score: 0.8526
# # * Davies-Bouldin Index: 2.5454
# # * Calinski-Harabasz Index: 10685.4068

# # %% [markdown]
# # ### 10.4 Análise dos resultados do modelo Isolation Forest após fine tuning de hiperparâmetros

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para que se possa entender como o modelo treinado com os melhores hiperparâmetros se comporta e realizar a comparação desses modelos, é necessário realizar uma nova análise de resultados para encontrar as diferenças e nuances no que tange as anomalias identificadas pelo Isolation Forest após o fine tuning.

# # %% [markdown]
# # #### 10.4.1 Contagem de anomalias e dados normais

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Primeiro, foi feita a contagem de anomalias detectadas pelo modelo. Nessa análise, foi identificado que o número de anomalias detectadas dobrou, chegando a mais de 17 mil dados classificados como anômalos.

# # %%
# # Adicionando as predições do modelo ajustado ao DataFrame
# df_sample['anomaly_iso_forest_tuning'] = labels_iso_forest_tuning

# # Mapeando as anomalias: 1 para anomalia e 0 para normal
# df_sample['anomaly_iso_forest_tuning'] = df_sample['anomaly_iso_forest_tuning'].map({1: 0, -1: 1})

# num_anomalias = df_sample[df_sample['anomaly_iso_forest_tuning'] == 1].shape[0]
# num_normais = df_sample[df_sample['anomaly_iso_forest_tuning'] == 0].shape[0]

# print(f"Número de anomalias detectadas: {num_anomalias}")
# print(f"Número de amostras normais: {num_normais}")


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Depois, para tornar possível e mais compreensível a comparação entre dados anômalos e normais, foi criado um gráfico de barras com as quantidades dos dados, no qual é possível entender que, apesar de o número de anomalias ter dobrado, a quantidade de dados anômalos ainda é pequena e concentrada em comparação com o total de dados normais.

# # %%
# import seaborn as sns
# import matplotlib.pyplot as plt

# # Plotando a contagem de amostras normais vs anomalias
# sns.countplot(x='anomaly_iso_forest_tuning', hue='anomaly_iso_forest_tuning', data=df_sample, palette='coolwarm', dodge=False)
# plt.title('Contagem de Amostras: Normais vs Anomalias')
# plt.ylabel('Contagem')
# plt.legend(title='Classificação', loc='upper right', labels=['Normal', 'Anomalia'])
# plt.show()


# # %% [markdown]
# # #### 10.4.2 Anomalias entre o consumo horarizado e o consumo total em metros cúbicos

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para entender como as anomalias detectadas se relacionam com o consumo de gás total e diluído entre as medições enviadas pelo medidor, foi criado o gráfico abaixo. Nessa relação visual, é possível entender que o modelo identificou como anomalias todos os dados que saíram da concentração em azul (dados normais) e que apesar de parecer ser a minoria de dados, a concentração em azul possui a maioria dos dados do Dataframe. 

# # %%
# # Definindo o tamanho da figura
# plt.figure(figsize=(8, 6))

# # Criando o gráfico de dispersão com cores para as anomalias
# sns.scatterplot(x='consumo_horarizado', y='consumo em m^3', hue='anomaly_iso_forest_tuning', data=df_sample, palette='coolwarm')

# # Ajustando o título e os rótulos dos eixos
# plt.title('Consumo horarizado vs Consumo em m³ (Normais vs Anomalias)')
# plt.xlabel('Consumo horarizado')
# plt.ylabel('Consumo em m³')

# # Garantindo que ambas as categorias apareçam na legenda, manualmente
# handles, labels = plt.gca().get_legend_handles_labels()
# # Mapeando 0 para "Normal" e 1 para "Anomalia"
# plt.legend(handles=handles, labels=['Normal', 'Anomalia'], title='Classificação')

# # Exibindo o gráfico
# plt.show()

# # %% [markdown]
# # #### 10.4.3 Quantidade de anomalias e dados normais entre os perfis de consumo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Entendendo que o conjunto de anomalias pode ser afetado pelo desbalanceamento entre as classes de perfil de consumo de cada cliente, foram criados dois gráficos: um gráfico de barras que mostra a quantidade total de anomalias por perfil de consumo e que permite uma análise geral de como as anomalias estão distribuídas; e um gráfico de dispersão de cada perfil de consumo que permite investigações mais profundas sobre a distribuição de dados anômalos e normais em cada uma das classes.

# # %%
# # Criando o DataFrame para perfis de consumo e anomalias
# df_perfis = df_sample.melt(id_vars=['anomaly_iso_forest_tuning'], 
#                            value_vars=['perfil_consumo_Aquecedor', 'perfil_consumo_Caldeira', 'perfil_consumo_Cocção', 'perfil_consumo_Cocção + Aquecedor', 'perfil_consumo_Cocção + Caldeira'],
#                            var_name='Perfil de Consumo', 
#                            value_name='Valor do Perfil')

# # Plotando o gráfico de barras empilhadas
# plt.figure(figsize=(17, 6))
# sns.barplot(x='Perfil de Consumo', y='Valor do Perfil', hue='anomaly_iso_forest_tuning', data=df_perfis, palette='coolwarm')

# # Customizando o título da legenda para indicar o que 0 e 1 significam
# leg = plt.legend(title='Anomalia')
# leg.texts[0].set_text('0 = Normal')
# leg.texts[1].set_text('1 = Anomalia')

# plt.title('Gráfico de Barras Empilhadas: Perfis de Consumo vs Anomalias')
# plt.ylabel('Valor do Perfil')
# plt.xlabel('Perfil de Consumo')
# plt.show()


# # %%
# plt.figure(figsize=(18, 14))
# plt.title('Gráficos de Dispersão: Perfis de Consumo vs Consumo em m³ (Normais vs Anomalias)', fontsize = 16, pad = 30)

# # Gráfico 1: Aquecedor
# plt.subplot(3, 2, 1)
# plt.plot(df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['perfil_consumo_Aquecedor'], 
#          label='Aquecedor - Normal', color='blue', marker='o', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['perfil_consumo_Aquecedor'], 
#             label='Aquecedor - Anomalia', color='red', s=100, marker='x')
# plt.title('Aquecedor')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Gráfico 2: Caldeira
# plt.subplot(3, 2, 2)
# plt.plot(df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['perfil_consumo_Caldeira'], 
#          label='Caldeira - Normal', color='green', marker='s', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['perfil_consumo_Caldeira'], 
#             label='Caldeira - Anomalia', color='red', s=100, marker='x')
# plt.title('Caldeira')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Gráfico 3: Cocção
# plt.subplot(3, 2, 3)
# plt.plot(df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['perfil_consumo_Cocção'], 
#          label='Cocção - Normal', color='orange', marker='^', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['perfil_consumo_Cocção'], 
#             label='Cocção - Anomalia', color='red', s=100, marker='x')
# plt.title('Cocção')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Gráfico 4: Cocção + Aquecedor
# plt.subplot(3, 2, 4)
# plt.plot(df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['perfil_consumo_Cocção + Aquecedor'], 
#          label='Cocção + Aquecedor - Normal', color='purple', marker='x', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['perfil_consumo_Cocção + Aquecedor'], 
#             label='Cocção + Aquecedor - Anomalia', color='red', s=100, marker='x')
# plt.title('Cocção + Aquecedor')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# # Gráfico 5: Cocção + Caldeira
# plt.subplot(3, 2, 5)
# plt.plot(df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['consumo em m^3'], 
#          df_sample[df_sample['anomaly_iso_forest_tuning'] == 0]['perfil_consumo_Cocção + Caldeira'], 
#          label='Cocção + Caldeira - Normal', color='black', marker='d', linewidth=2)
# plt.scatter(df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['consumo em m^3'], 
#             df_sample[df_sample['anomaly_iso_forest_tuning'] == 1]['perfil_consumo_Cocção + Caldeira'], 
#             label='Cocção + Caldeira - Anomalia', color='red', s=100, marker='x')
# plt.title('Cocção + Caldeira')
# plt.xlabel('Consumo em m³')
# plt.ylabel('Perfil de Consumo')
# plt.legend()
# plt.grid(True)

# plt.tight_layout()
# plt.show()


# # %% [markdown]
# # #### 10.4.4 Quantidade de anomalias de acordo com o tempo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Também foi identificado como a quantidade de anomalias se comporta com o passar do tempo nos quais os dados foram gerados. Para isso, o seguinte gráfico foi criado e permitiu identificar que, com o passar do tempo, as anomalias crescem. Entretanto, possíveis causas são o número crescente de clientes que não possuem consumo nos meses iniciais dos dados.

# # %%
# # Agrupar por mês e contar as anomalias
# anomalias_tempo = df_sample[df_sample['anomaly_iso_forest_tuning'] == True].groupby(df_sample['datetime'].dt.to_period('M')).size()

# # Plotar as anomalias ao longo do tempo
# plt.figure(figsize=(10, 6))
# anomalias_tempo.plot(kind='line', marker='o', color='red')
# plt.title('Anomalias ao longo do tempo')
# plt.xlabel('Data (Ano-Mês)')
# plt.ylabel('Número de anomalias')
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.show()

# # %% [markdown]
# # #### 10.4.5 Anomalias pela diferença de tempo em horas entre medições

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Por fim, foram identificadas as anomalias com base no tempo entre duas medições consecutivas de um mesmo cliente. Nesse sentido, o modelo identificou como anomalias os casos extremos de registros de consumo negativo e muitas horas de gap entre as medições de um mesmo cliente, mas a maioria das anomalias também se encontram entre os dados considerados normais, o que identifica a necessidade de investigações mais aprofundadas entre os dados na concentração azul.

# # %%
# # Plotar scatterplot de anomalias vs delta_time
# plt.figure(figsize=(10, 6))
# sns.scatterplot(x='delta_time', y='consumo_horarizado', hue='anomaly_iso_forest_tuning', data=df_sample, palette='coolwarm', alpha=0.7)
# plt.title('Anomalias vs Delta Time')
# plt.xlabel('Delta Time (horas)')
# plt.ylabel('Variação de consumo por hora')
# # Garantindo que ambas as categorias apareçam na legenda, manualmente
# handles, labels = plt.gca().get_legend_handles_labels()
# # Mapeando 0 para "Normal" e 1 para "Anomalia"
# plt.legend(handles=handles, labels=['Normal', 'Anomalia'], title='Classificação')
# plt.grid(True)
# plt.show()

# # %% [markdown]
# # # 11. One-Class SVM

# # %% [markdown]
# #  &nbsp;&nbsp;&nbsp;&nbsp;One-Class SVM é uma variante do SVM projetada para a detecção de anomalias. Ele busca definir uma fronteira que envolva a maioria das amostras normais no espaço de características, separando-as de possíveis anomalias. Durante o treinamento, o algoritmo ajusta um hiperplano que encapsula as amostras normais, enquanto na fase de teste, amostras que caem fora dessa margem são classificadas como anômalas. Esse método é amplamente utilizado em tarefas como detecção de outliers, fraudes e em sistemas com informações limitadas sobre a distribuição de dados anômalos (Bando, 2024).

# # %% [markdown]
# # ## 11.1. Criação do Modelo e Ultilização das Métricas 

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A seguir, está o desenvolvimento do modelo One-Class SVM utilizando as colunas selecionadas. Além disso, incluímos as métricas Davies-Bouldin Index (DBI), Calinski-Harabasz Index (CH Index) e Silhouette Score, que têm como objetivo avaliar o desempenho do modelo preditivo.

# # %%
# df_amostra = df_merged.sample(frac=0.01, random_state=42)
# colunas_selecionadas = [
#     'temp_scaled',
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'perfil_consumo_Cocção + Caldeira',
#     'consumo em m^3',
#     'consumo_horarizado',
#     'delta_time',
#     'variação_consumo',
    
# ]
# df_amostra = df_amostra[colunas_selecionadas]
# df_amostra.head()

# # %%
# # Importação das bibliotecas 
# from sklearn.preprocessing import StandardScaler
# from sklearn.svm import OneClassSVM
# from sklearn.metrics import davies_bouldin_score, silhouette_score, calinski_harabasz_score


# # Normalização das colunas selecionadas
# scaler = StandardScaler()
# X_train_scaled = scaler.fit_transform(df_amostra[colunas_selecionadas])


# # Modelo One-Class SVM
# model = OneClassSVM(kernel='rbf', gamma=0.1, nu=0.05)
# model.fit(X_train_scaled)


# # -1 são anomalias, 1 são normais
# labels = model.predict(X_train_scaled)


# # Calculando o Índice de Davies-Bouldin (DBI)
# dbi = davies_bouldin_score(X_train_scaled, labels)
# print(f'Davies-Bouldin Index: {dbi}')


# # Calculando o Índice de Calinski-Harabasz (CH Index)
# ch_index = calinski_harabasz_score(X_train_scaled, labels)
# print(f'Calinski-Harabasz Index: {ch_index}')

# # Calculando o Silhouette Score
# silhouette_avg = silhouette_score(X_train_scaled, labels)
# print(f'Silhouette Score: {silhouette_avg}')

# # %% [markdown]
# # ## 11.2. Análise dos Resultados das Métricas

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Nesta seção, serão apresentadas a análise dos resultados das métricas Índice de Silhueta, Índice de Davies-Bouldin (DBI) e Índice de Calinski-Harabasz Index (CH Index). Essas métricas desempenham um papel fundamental na avaliação da capacidade do modelo em distinguir padrões normais de consumo de comportamentos anômalos. Dessa maneira, para complementar e validar os resultados obtidos por essas métricas, foram desenvolvidas visualizações gráficas que proporcionam uma interpretação mais clara dos dados e ajudam a identificar possíveis melhorias no modelo, se necessário.

# # %% [markdown]
# # ### 11.2.1 Resultados das Métricas

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após a execução do modelo preditivo não-supervisionado One-Class SVM, obtivemos os primeiros resultados das métricas utilizadas:
# # - Davies-Bouldin Index (DBI): = 3,19
# # - Calinski-Harabasz Index (CH Index): = 1002,66 
# # - Silhouette Score = 0,70
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Em uma análise inicial, mesmo sem a definição dos hiperparâmetros ideais, os resultados foram razoáveis. O valor do DBI, de 3,19, poderia ser menor, uma vez que valores mais baixos indicam uma melhor separação entre os clusters. Por outro lado, os valores do CH Index e do Silhouette Score foram considerados satisfatórios. O CH Index de 1002,66 sugere uma boa definição dos clusters, já que valores mais altos indicam uma melhor separação entre os grupos. Da mesma forma, o Silhouette Score de 0,70 mostra que os pontos estão relativamente bem agrupados dentro de cada cluster, sendo que valores mais próximos de 1 indicam uma maior coesão e melhor separação entre os clusters. Sendo assim, mesmo sem ajustes nos hiperparâmetros, os resultados iniciais foram aceitáveis.
# # 

# # %% [markdown]
# # ### 11.2.2. Clusters Identificados pelo One-Class SVM

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O objetivo deste gráfico é visualizar a distribuição entre padrões de consumo normais e possíveis anomalias detectadas pelo modelo. Ao gerar clusters, após realizar a redução para duas dimensões utilizando a Análise de Componentes Principais (PCA) com as colunas selecionadas, o gráfico apresenta as amostras consideradas anômalas, representadas por pontos vermelhos, e as amostras consideradas normais, representadas por pontos azuis. Dessa forma, é possível observar de maneira mais clara a separação entre comportamentos normais e anômalos, ajudando na validação e na capacidade do modelo em detectar anomalias no consumo de gás natural.

# # %%
# from sklearn.decomposition import PCA
# import matplotlib.patches as mpatches
# import matplotlib.pyplot as plt

# # Reduzindo para 2 componentes para visualização (PCA)
# pca = PCA(n_components=2)
# X_pca = pca.fit_transform(X_train_scaled)

# # Contando quantos pontos são normais (1) e quantos são anomalias (-1)
# num_normais = sum(labels == 1)
# num_anomalias = sum(labels == -1)

# # Gráfico de Silhouette Score
# plt.figure(figsize=(10, 5))
# sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=labels, palette={1: 'blue', -1: 'red'})
# plt.title('Clusters Identificados pelo One-Class SVM')
# plt.xlabel('PCA1')
# plt.ylabel('PCA2')

# # Criando a legenda personalizada com a contagem
# anomalia_patch = mpatches.Patch(color='red', label=f'Anomalia ({num_anomalias})')
# normal_patch = mpatches.Patch(color='blue', label=f'Normal ({num_normais})')

# # Adicionando a legenda no gráfico
# plt.legend(handles=[anomalia_patch, normal_patch], loc='lower right')

# plt.show()


# # %% [markdown]
# # ### 11.2.3. Temperatura Escalada vs Consumo Horarizado

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Este gráfico tem como objetivo analisar a relação entre a temperatura escalada e o consumo horarizado de gás natural, permitindo a identificação de padrões de consumo e anomalias. A dispersão dos pontos ilustra como o consumo varia em função da temperatura, possibilitando a detecção de comportamentos atípicos que podem indicar anomalias. É provável que o gráfico tenha considerado como anomalias os valores de consumo horarizado negativos, uma vez que não faz sentido ter um consumo de gás negativo por hora, assim como pontos que excedem a média de consumo esperado. Essa análise é essencial para entender a influência da temperatura nas variações de consumo, e dessa forma ajustar se necessário a eficiência do modelo.

# # %%


# # Configurando o tamanho do gráfico
# plt.figure(figsize=(10, 6))

# # Contando quantos pontos são normais (1) e quantos são anomalias (-1)
# num_normais = sum(labels == 1)
# num_anomalias = sum(labels == -1)

# # Criando o gráfico de dispersão
# sns.scatterplot(
#     x=df_amostra['temp_scaled'], 
#     y=df_amostra['consumo_horarizado'], 
#     hue=labels,  
#     palette={1: 'blue', -1: 'red'},  
#     alpha=0.7  
# )

# # Ajuste dos limites do eixo X e Y
# plt.xlim(left=0)  # Eixo X começando em 0
# plt.ylim(bottom=-100, top=df_amostra['consumo_horarizado'].max())  # Definir os limites do eixo Y

# # Títulos e rótulos
# plt.title('Temperatura Escalada X Consumo Horarizado')
# plt.xlabel('Temp Escalada')
# plt.ylabel('Consumo Horarizado')

# # Criando a legenda personalizada
# anomalia_patch = mpatches.Patch(color='red', label=f'Anomalia ({num_anomalias})')
# normal_patch = mpatches.Patch(color='blue', label=f'Normal ({num_normais})')

# # Adicionando a legenda no gráfico
# plt.legend(handles=[anomalia_patch, normal_patch])

# # Exibir o gráfico
# plt.show()


# # %% [markdown]
# # ### 11.2.4. Consumo acumulado em m³ vs Delta Time por tipo de perfil

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Este conjunto de gráficos tem como objetivo apresentar uma análise do consumo acumulado de gás em m³ em relação à diferença, em horas, entre medições, para diferentes tipos de perfis de consumo. Dessa forma, é possível comparar o comportamento de consumo entre perfis como aquecedor, caldeira, cocção e suas combinações, permitindo identificar padrões e desvios no consumo de cada perfil. Essa análise ajuda a melhorar a eficácia do modelo, uma vez que facilita a detecção de perfis que apresentam comportamentos anômalos, contribuindo para ajustes mais precisos no modelo.

# # %%
# # Definindo o número de perfis
# perfil_consumo = [
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'perfil_consumo_Cocção + Caldeira'
# ]

# # Definindo o limiar para anomalias
# limiar_anomalia = 50  # Defina o limite que considera anomalia

# plt.figure(figsize=(15, 10))

# # Loop para criar gráficos de dispersão para cada perfil de consumo
# for i, perfil in enumerate(perfil_consumo):
#     plt.subplot(2, 3, i + 1)  # Subplots em 2 linhas e 3 colunas
    
#     # Filtrando dados para o perfil específico
#     cluster_data = df_sample_positive[df_sample_positive[perfil] == 1]  # Considerando que o perfil ativo seja 1

#     # Identificando anomalias
#     anomalias = cluster_data[cluster_data['consumo em m^3'] > limiar_anomalia]
#     normais = cluster_data[cluster_data['consumo em m^3'] <= limiar_anomalia]
    
#     # Plotando os dados normais
#     plt.scatter(normais['delta_time'], 
#                 normais['consumo em m^3'], 
#                 label=f'Normal ({len(normais)})', color='blue')
    
#     # Plotando os dados anômalos
#     plt.scatter(anomalias['delta_time'], 
#                 anomalias['consumo em m^3'], 
#                 label=f'Anomalia ({len(anomalias)})', color='red')  

#     # Definindo título e rótulos
#     plt.title(f'{perfil}')

#     plt.xlabel('delta_time')
#     plt.ylabel('Consumo acumulado em m³')
    
#     plt.grid(True)
    
#     # Ajustando a legenda para cada subplot com as contagens
#     plt.legend()

# # Ajustando o layout para evitar sobreposição
# plt.tight_layout()

# # Exibindo os gráficos
# plt.show()


# # %% [markdown]
# # ### 11.2.5. Média do consumo horarizado de cada tipo de perfil

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Este gráfico tem como objetivo apresentar o consumo médio por hora (m³/hora) para os diferentes tipos de perfis. Cada ponto no gráfico representa a média de consumo horarizado para um determinado perfil, permitindo uma visualização clara das diferenças de consumo entre eles. Dessa forma, ao identificar quais perfis têm um consumo médio mais elevado, é possível ajustar o modelo preditivo para detectar anomalias, uma vez que desvios em relação a esses padrões médios podem indicar comportamentos de consumo atípicos ou anômalos.

# # %%
# # Definindo o número de perfis
# perfil_consumo = [
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'perfil_consumo_Cocção + Caldeira'
# ]

# # Criando um DataFrame para calcular a média do consumo horarizado por perfil
# medias_consumo = []

# # Loop para calcular a média de consumo_horarizado para cada perfil
# for perfil in perfil_consumo:  # Usando 'perfil_consumo' no lugar de 'perfis'
#     media = df_amostra[perfil].mean()
#     medias_consumo.append({'Perfil': perfil, 'Media_Consumo': media})

# # Convertendo a lista para um DataFrame
# df_medias = pd.DataFrame(medias_consumo)

# # Criando o gráfico de dispersão
# plt.figure(figsize=(12, 7))
# sns.scatterplot(data=df_medias, x='Perfil', y='Media_Consumo', hue='Media_Consumo', palette='coolwarm', s=100)

# # Ajustando o título e os rótulos
# plt.xticks(rotation=45, ha='right')  # Rotacionar o eixo X para melhor leitura
# plt.title('Média do Consumo Horarizado por Tipo de Perfil', fontsize=14)
# plt.xlabel('Tipo de Perfil')
# plt.ylabel('Média do Consumo Horarizado')

# # Exibindo o gráfico com layout ajustado
# plt.tight_layout()
# plt.show()


# # %% [markdown]
# # ### 11.2.6. Variação do consumo vs Consumo total

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Este gráfico permite visualizar como as variações de consumo se comportam em relação aos níveis de consumo total, ajudando a identificar padrões que podem não ser imediatamente evidentes. Além disso, a visualização facilita a detecção de relações entre o consumo total e suas flutuações, permitindo uma análise mais aprofundada dos hábitos de consumo dos clientes e a identificação de potenciais anomalias que poderiam ser relevantes para ajustes no modelo preditivo.

# # %%
# plt.figure(figsize=(10, 6))
# num_normais = sum(labels == 1)
# num_anomalias = sum(labels == -1)
# sns.scatterplot(x='consumo em m^3', y='variação_consumo', hue=labels, data=df_amostra, palette={1: 'blue', -1: 'red'})
# plt.title('Variação de Consumo vs Consumo Total')
# plt.xlabel('Consumo Total (m³)')
# plt.ylabel('Variação de Consumo')
# anomalia_patch = mpatches.Patch(color='red', label=f'Anomalia ({num_anomalias})')
# normal_patch = mpatches.Patch(color='blue', label=f'Normal ({num_normais})')
# plt.legend(handles=[normal_patch, anomalia_patch])
# plt.show()


# # %% [markdown]
# # ## 11.3. Fine tuning de hiperparâmetros do One-Class SVM

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Hiperparâmetros em um modelo preditivo são valores definidos antes do treinamento, controlando como o algoritmo será ajustado aos dados. Nesse contexto, tecnicas de busca podem ser aplicadas para os encontrar, como o GridSearchCV e RandomizedSearchCV, ambos com suas características e métodos de busca específicos.

# # %% [markdown]
# # ### 11.3.1. GridSearchCV

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O GridSearchCV é uma técnica que busca os melhores hiperparâmetros, testando todas as combinações possíveis em uma grade pré-definida para otimizar o modelo de aprendizado de máquina. Abaixo, estamos aplicando o método para encontrar os hiperparâmetros do modelo OneClassSVM.

# # %%
# from sklearn.model_selection import GridSearchCV
# from sklearn.pipeline import Pipeline
# import numpy as np

# # Definindo os parâmetros a serem testados
# param_grid = {
#     'oneclasssvm__gamma': [0.001, 0.01, 0.1, 1, 10],
#     'oneclasssvm__nu': [0.01, 0.05, 0.1, 0.5]
# }

# # Criando o pipeline com o modelo
# pipeline = Pipeline([
#     ('scaler', StandardScaler()),
#     ('oneclasssvm', OneClassSVM(kernel='rbf'))
# ])

# # Usando GridSearchCV para otimizar os hiperparâmetros
# grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
# grid_search.fit(df_amostra)

# # Imprimindo os melhores hiperparâmetros e a pontuação
# print(f"Melhores hiperparâmetros encontrados pelo GridSearchCV: {grid_search.best_params_}")
# print(f"Melhor pontuação: {grid_search.best_score_}")

# # %% [markdown]
# # ### 11.3.2. RandomizedSearchCV

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O RandomizedSearchCV é uma técnica que também é utilizada para fins de encontrar os melhores hiperparâmetros. Em vez de testar todas as combinações possíveis, este método irá escolher aleatoriamente um número limitado de combinações da grade de hiperparâmetros fornecida.

# # %%
# from sklearn.model_selection import RandomizedSearchCV

# # Definindo o espaço de busca para RandomizedSearchCV
# param_dist = {
#     'oneclasssvm__gamma': [0.001, 0.01, 0.1, 1, 10],
#     'oneclasssvm__nu': [0.01, 0.05, 0.1, 0.5]
# }

# # Criando o pipeline com o modelo
# pipeline_random = Pipeline([
#     ('scaler', StandardScaler()),
#     ('oneclasssvm', OneClassSVM(kernel='rbf'))
# ])

# # Usando RandomizedSearchCV para otimizar os hiperparâmetros
# random_search = RandomizedSearchCV(pipeline_random, param_distributions=param_dist, n_iter=10, cv=3, scoring='accuracy', n_jobs=-1, random_state=42)
# random_search.fit(df_amostra)

# # Imprimindo os melhores hiperparâmetros e a pontuação
# print(f"Melhores hiperparâmetros encontrados pelo RandomizedSearchCV: {random_search.best_params_}")
# print(f"Melhor pontuação: {random_search.best_score_}")

# # %% [markdown]
# # ### 11.3.3. Descoberta dos melhores hiperparâmetros

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após a execução dos dois modelos, identificamos que os hiperparâmetros ideais para o modelo preditivo são: `'oneclasssvm__nu': 0.01` e `'oneclasssvm__gamma': 0.001`. Com esses parâmetros ajustados, podemos aplicar o modelo para alcançarmos as métricas finais de desempenho.

# # %%
# from sklearn.preprocessing import StandardScaler
# from sklearn.svm import OneClassSVM
# from sklearn.metrics import davies_bouldin_score, silhouette_score, calinski_harabasz_score


# # Normalização das colunas selecionadas
# scaler = StandardScaler()
# X_train_scaled = scaler.fit_transform(df_amostra[colunas_selecionadas])

# # Modelo One-Clas SVM
# model = OneClassSVM(kernel='rbf', gamma=0.001, nu=0.01)
# model.fit(X_train_scaled)


# # -1 são anomalias, 1 são normais
# labels = model.predict(X_train_scaled)


# # Calculando o Índice de Davies-Bouldin (DBI)
# dbi = davies_bouldin_score(X_train_scaled, labels)
# print(f'Davies-Bouldin Index: {dbi}')


# # Calculando o Índice de Calinski-Harabasz (CH Index)
# ch_index = calinski_harabasz_score(X_train_scaled, labels)
# print(f'Calinski-Harabasz Index: {ch_index}')

# # Calculando o Silhouette Score
# silhouette_avg = silhouette_score(X_train_scaled, labels)
# print(f'Silhouette Score: {silhouette_avg}')

# # %% [markdown]
# # ## 11.4. Análise dos resultados do modelo One-Class SVM após fine tuning de hiperparâmetros

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após definir os melhores hiperparâmetros para o modelo One-Class SVM, é fundamental realizar uma nova análise dos resultados para comparar o desempenho antes e depois do fine tuning. Essa análise permitirá avaliar as melhorias no modelo, identificando variações na precisão da detecção de anomalias e verificando se os ajustes de hiperparâmetros resultaram em um aumento na eficácia do modelo.

# # %% [markdown]
# # ### 11.4.1 Comparando os resultados das Métricas

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Após o ajuste dos hiperparâmetros do nosso modelo preditivo, observamos melhorias nos valores das métricas utilizadas para avaliação. Antes do fine tuning dos hiperparâmetros, os valores obtidos foram:
# # - DBI = 3,19, 
# # - CH Index = 1002,66 
# # - Silhouette Score = 0,70
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Após o ajuste, os valores das métricas passaram para: 
# # - DBI = 2,74
# # - CH Index = 1890,22
# # - Silhouette Score = 0,89.
# # 
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Ao analisar esses resultados, é possível observar o seguinte:
# # 
# # - Davies-Bouldin Index (DBI): O valor reduziu de 3,19 para 2,74. Como o DBI é uma métrica onde valores menores indicam melhor separação entre os clusters e menor dispersão dentro de cada grupo, essa redução é um sinal positivo.
# # 
# # - Calinski-Harabasz Index (CH Index): O CH Index aumentou significativamente de 1002,66 para 1890,22. Valores mais altos nessa métrica indicam uma melhor definição dos clusters, ou seja, maior separação entre as observações normais e anômalas.
# # 
# # - Silhouette Score: O Silhouette Score passou de 0,70 para 0,89. Valores mais próximos de 1 nessa métrica indicam que os clusters estão bem compactos e separados. Esse aumento demonstra que os dados estão sendo agrupados de forma mais coesa, com os pontos dentro de cada cluster estando mais próximos entre si.
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Portando, após o fine tuning dos hiperparâmetros, o desempenho do modelo melhorou de forma consistente em todas as métricas.
# # 

# # %% [markdown]
# # ### 11.4.2. Clusters Identificados pelo One-Class SVM

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Neste gráfico, que ilustra a distribuição e a quantidade de dados classificados como anômalos e não anômalos, observa-se uma diferença significativa nas contagens após o ajuste. O número de anomalias, que inicialmente era de 1.476, reduziu drasticamente para 296, enquanto a quantidade de dados classificados como normais aumentou de 28.036 para 29.216. 

# # %%
# # Reduzindo para 2 componentes para visualização (PCA)
# pca = PCA(n_components=2)
# X_pca = pca.fit_transform(X_train_scaled)

# # Contando quantos pontos são normais (1) e quantos são anomalias (-1)
# num_normais = sum(labels == 1)
# num_anomalias = sum(labels == -1)

# # Gráfico de Silhouette Score
# plt.figure(figsize=(10, 5))
# sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=labels, palette={1: 'blue', -1: 'red'})
# plt.title('Clusters Identificados pelo One-Class SVM')
# plt.xlabel('PCA1')
# plt.ylabel('PCA2')

# # Criando a legenda personalizada com a contagem
# anomalia_patch = mpatches.Patch(color='red', label=f'Anomalia ({num_anomalias})')
# normal_patch = mpatches.Patch(color='blue', label=f'Normal ({num_normais})')

# # Adicionando a legenda no gráfico
# plt.legend(handles=[anomalia_patch, normal_patch], loc='lower right')

# plt.show()

# # %% [markdown]
# # ### 11.4.3. Temperatura Escalada vs Consumo Horarizado

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Este gráfico apresenta as anomalias no consumo por hora em relação ao consumo em m³. Essa análise permite identificar irregularidades como valores de consumo horarizado negativos, que indicam possíveis erros de medição ou fraudes, e dessa forma são consideradas dados anômalos. Além disso, compreender o consumo ao longo do tempo ajuda a otimizar a gestão de recursos, prevenir desperdícios e garantir a precisão das leituras. 

# # %%


# # Configurando o tamanho do gráfico
# plt.figure(figsize=(10, 6))

# # Contando quantos pontos são normais (1) e quantos são anomalias (-1)
# num_normais = sum(labels == 1)
# num_anomalias = sum(labels == -1)

# # Criando o gráfico de dispersão
# sns.scatterplot(
#     x=df_amostra['consumo em m^3'], 
#     y=df_amostra['consumo_horarizado'], 
#     hue=labels,  
#     palette={1: 'blue', -1: 'red'},  
#     alpha=0.7  
# )

# # Ajuste dos limites do eixo X e Y
# plt.xlim(left=0)  # Eixo X começando em 0
# plt.ylim(bottom=-100, top=df_amostra['consumo_horarizado'].max())  # Definir os limites do eixo Y

# # Títulos e rótulos
# plt.title('consumo em m^3 X Consumo Horarizado')
# plt.xlabel('consumo em m^3')
# plt.ylabel('Consumo Horarizado')

# # Criando a legenda personalizada
# anomalia_patch = mpatches.Patch(color='red', label=f'Anomalia ({num_anomalias})')
# normal_patch = mpatches.Patch(color='blue', label=f'Normal ({num_normais})')

# # Adicionando a legenda no gráfico
# plt.legend(handles=[anomalia_patch, normal_patch])

# # Exibir o gráfico
# plt.show()


# # %% [markdown]
# # ### 11.4.4. Consumo de Gás (m³) vs Delta Time (durante um mês)

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Este gráfico apresenta a relação entre o consumo médio de gás em metros cúbicos (m³) ao longo de uma semana, para clientes com o perfil de cocção + aquecedor. Dessa maneira, a linha principal representa o consumo médio para cada dia da semana, e área sombreada ao redor da linha principal representa o desvio-padrão. Desse modo, uma sombra estreita sugere que os valores estão mais concentrados em torno da média, enquanto uma sombra mais ampla indica uma maior irregularidade nos consumos individuais em relação à média. Com isso, podemos analisar que nos finais de semana o consumo individual de cada cliente nesses dois dias é mais fiel a média comaprado na quarta-feira, onde apresenta maior dispersão na sombra. A análise revela que, nos finais de semana, o consumo individual de cada cliente tende a se alinhar mais com a média, evidenciado por uma sombra mais estreita. Em contrapartida, na quarta-feira, observa-se uma maior dispersão na sombra, indicando que os consumos individuais apresentam uma variabilidade mais significativa.

# # %%
# # Definir o período de uma semana em horas (7 dias = 168 horas)
# limite_semana = 168  # Aproximadamente uma semana

# # Filtrando os dados para um delta_time dentro de uma semana e para o perfil específico
# df_semana = df_amostra[(df_amostra['delta_time'] <= limite_semana) & (df_amostra['perfil_consumo_Cocção + Aquecedor'] == 1)]

# # Convertendo delta_time para dias da semana (segunda, terça, etc.)
# df_semana['dia_semana'] = (df_semana['delta_time'] // 24) % 7  # Dividindo por 24 para converter em dias e usando % 7 para obter o dia da semana

# # Mapeando os números de 0 a 6 para os dias da semana (segunda a domingo)
# dias_semana_map = {0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'}
# df_semana['dia_semana'] = df_semana['dia_semana'].map(dias_semana_map)

# # Criando o gráfico de consumo em m³ por dia da semana
# plt.figure(figsize=(12, 6))

# # Plotando o consumo em m³ ao longo dos dias da semana
# sns.lineplot(x='dia_semana', y='consumo em m^3', data=df_semana)

# # Ajustando o título e rótulos dos eixos
# plt.title('Consumo de Gás (m³) por Dia da Semana para o Perfil "Cocção + Aquecedor"', fontsize=14)
# plt.xlabel('Dia da Semana', fontsize=12)
# plt.ylabel('Consumo em m³', fontsize=12)

# # Ajustando o layout para evitar sobreposição
# plt.grid(True)
# plt.tight_layout()

# # Exibindo o gráfico
# plt.show()


# # %% [markdown]
# # ### 11.4.5. Média do consumo horarizado de cada tipo de perfil

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp; Este gráfico mostra o consumo médio por hora de cada tipo de perfil. Mesmo após os ajustes nos hiperparâmetros, a média continua a mesma. A análise do gráfico revela que o perfil que combina cocção e aquecedor apresenta um consumo significativamente maior em relação aos outros perfis. Essa informação é importante para futuras análises, pois esse perfil pode apresentar consumos que, à primeira vista, parecem ser anomalias, mas que, na verdade, refletem um padrão de consumo mais elevado do que os demais. Compreender essa diferença é essencial para evitar interpretações erradas dos dados.

# # %%
# # Definindo o número de perfis
# perfil_consumo = [
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'perfil_consumo_Cocção + Caldeira'
# ]

# # Criando um DataFrame para calcular a média do consumo horarizado por perfil
# medias_consumo = []

# # Loop para calcular a média de consumo_horarizado para cada perfil
# for perfil in perfil_consumo:  # Usando 'perfil_consumo' no lugar de 'perfis'
#     media = df_amostra[perfil].mean()
#     medias_consumo.append({'Perfil': perfil, 'Media_Consumo': media})

# # Convertendo a lista para um DataFrame
# df_medias = pd.DataFrame(medias_consumo)

# # Criando o gráfico de dispersão
# plt.figure(figsize=(12, 7))
# sns.scatterplot(data=df_medias, x='Perfil', y='Media_Consumo', hue='Media_Consumo', palette='coolwarm', s=100)

# # Ajustando o título e os rótulos
# plt.xticks(rotation=45, ha='right')  # Rotacionar o eixo X para melhor leitura
# plt.title('Média do Consumo Horarizado por Tipo de Perfil', fontsize=14)
# plt.xlabel('Tipo de Perfil')
# plt.ylabel('Média do Consumo Horarizado')

# # Exibindo o gráfico com layout ajustado
# plt.tight_layout()
# plt.show()


# # %% [markdown]
# # ### 11.4.6. Variação do consumo vs Consumo total

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Neste gráfico, é possível observar uma mudança significativa não apenas na quantidade de dados classificados como anomalias e na quantidade de dados considerados normais, conforme discutido no gráfico "Clusters Identificados pelo One-Class SVM", mas também na visualização geral. Os pontos em azul, que representam os dados normais, estão agora mais destacados, tornando-se mais perceptíveis na representação gráfica. Essa melhoria visual ressalta a diferença entre os dados normais e anômalos, facilitando a interpretação e análise dos resultados.

# # %%
# # Tamanho do gráfico
# plt.figure(figsize=(10, 6))

# # Contando quantos pontos são normais (1) e quantos são anomalias (-1)
# num_normais = sum(labels == 1)
# num_anomalias = sum(labels == -1)

# sns.scatterplot(x='consumo em m^3', y='variação_consumo', hue=labels, data=df_amostra, palette={1: 'blue', -1: 'red'})
# plt.title('Variação de Consumo vs Consumo Total')
# plt.xlabel('Consumo Total (m³)')
# plt.ylabel('Variação de Consumo')
# anomalia_patch = mpatches.Patch(color='red', label=f'Anomalia ({num_anomalias})')
# normal_patch = mpatches.Patch(color='blue', label=f'Normal ({num_normais})')
# plt.legend(handles=[normal_patch, anomalia_patch])
# plt.show()


# # %% [markdown]
# # # 12. DBScan

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Segundo Gabriel Monteiro (2020), o modelo DBSCAN utiliza uma abordagem que agrupa pontos com base na densidade. A formação dos clusters ocorre a partir da densidade de pontos em uma determinada área. Se um ponto não atender aos critérios de densidade ou aos limites de distância estabelecidos, ele não será classificado em um cluster.
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Desse modo, a definição dos parâmetros é fundamental para o funcionamento adequado do algoritmo. O parâmetro Eps define a distância máxima em que dois pontos podem estar para serem considerados parte do mesmo cluster. Já o parâmetro Min Samples estabelece a quantidade mínima de pontos em uma região necessária para garantir que haja densidade suficiente para formar um cluster. O DBSCAN não requer a definição prévia do número de clusters e é mais rápido que o k-means. Ele identifica padrões não lineares e lida com outliers, mas pode enfrentar dificuldades em datasets com alta variabilidade de densidade e em dados de alta dimensionalidade, a escolha dos parâmetros é crítica, e a ordem dos dados pode afetar os resultados.

# # %% [markdown]
# # ### 12.1 Modelagem

# # %% [markdown]
# # ##### 12.1.1 Redução do dataframe *df_merged* em outro dataset, contendo as novas features de consumo_horarizado e delta_time

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Considerando os últimos ajustes de pré-processamento, configurando a variação de consumo de forma horarizada, ou seja, calculada de horário em horário, a lista de features selecionadas para a construção do modelo DBScan foi refeita, fazendo a inclusão das novas colunas *consumo_horarizado* e *delta_time*.

# # %%
# colunas_selecionadas2 = [
#     'temp_scaled',
#     'perfil_consumo_Aquecedor',
#     'perfil_consumo_Caldeira',
#     'perfil_consumo_Cocção',
#     'perfil_consumo_Cocção + Aquecedor',
#     'perfil_consumo_Cocção + Aquecedor + Piscina',
#     'perfil_consumo_Cocção + Caldeira',
#     'consumo em m^3',
#     'consumo_horarizado',
#     'delta_time'
# ]

# # %% [markdown]
# # ##### 12.1.2 Cópia do df_merged com colunas selecionadas para o dataframe df_sample2

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para uma testagem eficiente do modelo, o DataFrame foi copiado e reduzido para um novo *dataset*, denominado de *df_sample2*, o qual será utilizado nas próximas utilizações. Ao ser alterado, o valor de "frac" definirá a porcentagem do conjunto de dados a ser coletada, possuindo o valor inicial de 8% dos dados.

# # %%
# # Redução do modelo na variável df_sample2 para testagem do DBScan
# df_sample2 = df_merged[colunas_selecionadas2].sample(frac=0.008, random_state=42).astype(int).copy() # 8% dos dados

# # %% [markdown]
# # ##### 12.1.3 Programação do modelo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Abaixo, segue a programação do modelo preditivo DBScan, a qual começa com a escalonagem das features selecionadas para implementar uma normalização, auxiliando nas operações lógicas. Então, o DBScan é implementado, configurando-se um valor determinado de *eps* (para cada ponto, o raio máximo para a detecção de pontos vizinhos) e do *min_samples* (quantidade mínimas de pontos de um agrupamento para ser considerado um cluster). Então, para auxiliar na plotagem do gráfico, fez-se a redução de dimensionalidade com PCA para apenas 2 componentes, e plotou-se o gráfico.

# # %%
# ## Importação das bibliotecas
# from sklearn.decomposition import PCA
# from sklearn.cluster import DBSCAN

# # Normalização das colunas selecionadas com o Standart Scaler
# scaler = StandardScaler()
# features_scaled = scaler.fit_transform(df_sample2)

# # Modelo DBSCAN. Eps = distância mínima para 2 pontos serem considerados vizinhos. Min_samples = número mínimo de pontos em uma vizinhança para ser considerado um cluster
# dbscan = DBSCAN(eps=0.6, min_samples=100) # Parâmetros iniciais, os quais serão aprimorados com o futuro fine tuning
# clusters = dbscan.fit_predict(features_scaled)

# # Redução de dimensionalidade para visualização do gráfico
# pca = PCA(n_components=2)
# features_pca = pca.fit_transform(features_scaled)

# # Fit dos clusters no DataFrame df_sample2
# df_sample2['cluster'] = clusters

# # Gráfico de visualização dos clusters em 2D com PCA
# plt.figure(figsize=(10, 7))
# sns.scatterplot(x=features_pca[:, 0], y=features_pca[:, 1], hue=clusters, palette='tab10', s=20, edgecolor='k')
# plt.title('Clusters DBSCAN - Sample DataFrame')
# plt.xlabel('Componente Principal 1')
# plt.ylabel('Componente Principal 2')
# plt.show()

# # Contagem os pontos em cada cluster
# print(df_sample2['cluster'].value_counts())


# # %% [markdown]
# # ##### Contagem do número de clusters gerados

# # %%
# # Contagem dos clusters gerados pelo DBSCAN
# df_sample2['cluster'].nunique()

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Com base no algoritmo, com um eps de 0.6 e um min_samples de 100, foram gerados cerca de 8 clusters, sendo os clusters com valor -1 considerados como "ruídos", ou anomalias.

# # %% [markdown]
# # ##### 12.1.4 Fine Tuning de hiperparâmetros com cálculo de Silhueta

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Considerando-se que a alteração dos hiperparâmetros eps e min_samples interfere no sucesso do modelo, implementou-se um Fine Tuning para realizar várias combinações de valores, avaliando os melhores com o cálculo da Silhueta. Devido ao seu tempo de execução de cerca de 15 minutos, o código foi comentado para maior eficiência do notebook, mas caso deseje-se executá-lo, basta remover os comentários.

# # %%
# """

# # Definição de intervalos de eps e min_samples para testagem
# eps_values = np.arange(0.2, 1.0, 0.1)  # Testando valores entre 0.4 e 1.0, pulando de 0.1 em 0.1
# min_samples_values = range(50, 150, 25)  # Testando valores de 50 a 150, pulando de 25 em 25

# # Variáveis para guardar os melhores parâmetros
# best_eps = None
# best_min_samples = None
# best_silhouette_score = -1 # menor valor possível para o best_silhouette_score
# best_clusters = None

# # Loop para testar todas as combinações de eps e min_samples
# for eps in eps_values:
#     for min_samples in min_samples_values:
#         # Modelo DBSCAN com os parâmetros de cada instância
#         dbscan = DBSCAN(eps=eps, min_samples=min_samples)
#         clusters = dbscan.fit_predict(features_scaled)
        
#         if len(set(clusters)) > 1:  # Garante que há mais de um cluster
#             score = silhouette_score(features_scaled, clusters)
            
#             # Verificação se o score atual é o melhor
#             if score > best_silhouette_score:
#                 best_silhouette_score = score
#                 best_eps = eps
#                 best_min_samples = min_samples
#                 best_clusters = clusters

# # Aplicar os melhores parâmetros encontrados ao DataFrame original
# df_sample2['cluster'] = best_clusters

# # Redução de dimensionalidade para visualização do gráfico
# pca = PCA(n_components=2)
# features_pca = pca.fit_transform(features_scaled)

# # Gráfico de visualização dos clusters em 2D com PCA
# plt.figure(figsize=(10, 7))
# sns.scatterplot(x=features_pca[:, 0], y=features_pca[:, 1], hue=df_sample2['cluster'], palette='tab10', s=20, edgecolor='k')
# plt.title(f'Clusters DBSCAN - eps: {best_eps}, min_samples: {best_min_samples}')
# plt.xlabel('Componente Principal 1')
# plt.ylabel('Componente Principal 2')
# plt.show()

# # Contagem dos pontos em cada cluster
# print(df_sample2['cluster'].value_counts())
# print(f'Melhor eps: {best_eps}, Melhor min_samples: {best_min_samples}, Melhor Silhouette Score: {best_silhouette_score}')

# """


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Testando de valores de eps entre 0.2 e 1.0, e de min_samples entre 50 e 150, obteve-se o seguinte output:
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;*Melhor eps: 0.5000000000000001, Melhor min_samples: 50, Melhor Silhouette Score: 0.7629696140135187*

# # %% [markdown]
# # ##### 12.1.5 Execução do modelo adicionando métricas Davies-Bouldin Index (DBI) e Calinski-Harabasz Index (CH Index)

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Assim como decidido pela equipe, mais duas métricas serão utilizadas para a conferência do modelo preditivo, o DBI e CH Index. Abaixo, segue o cálculo de hiperparâmetros e a implementação do cálculo da silhueta, DBI e CH Index. Devido ao seu tempo de execução, o código foi comentado para maior eficiência do notebook, mas caso deseje-se executá-lo, basta remover os comentários.

# # %%
# """

# from sklearn.metrics import davies_bouldin_score, calinski_harabasz_score

# # Definição de intervalos de eps e min_samples para testagem
# eps_values = np.arange(0.2, 1.0, 0.1)  # Testar valores entre 0.2 e 1.0, variando de 0.1 a 0.1
# min_samples_values = range(50, 150, 25)  # Testar valores de 50 a 150, variando de 25 a 25

# # Variáveis para guardar os melhores parâmetros
# best_eps = None
# best_min_samples = None
# best_silhouette_score = -1
# best_dbi = float('inf')  # Para DBI, menor é melhor, então inicializamos com infinito
# best_ch = -1  # Para CH, maior é melhor, então inicializamos com -1
# best_clusters = None

# # Loop para testar todas as combinações de eps e min_samples
# for eps in eps_values:
#     for min_samples in min_samples_values:
#         # Modelo DBSCAN com os parâmetros atuais
#         dbscan = DBSCAN(eps=eps, min_samples=min_samples)
#         clusters = dbscan.fit_predict(features_scaled)
        
#         if len(set(clusters)) > 1:  # Garantir que há mais de um cluster
            
#             # Silhouette Score
#             sil_score = silhouette_score(features_scaled, clusters)
            
#             # Davies-Bouldin Index (DBI)
#             dbi = davies_bouldin_score(features_scaled, clusters)
            
#             # Calinski-Harabasz Index (CH Index)
#             ch = calinski_harabasz_score(features_scaled, clusters)
            
#             # Verifica se este é o melhor conjunto de métricas até agora
#             if (sil_score > best_silhouette_score and dbi < best_dbi and ch > best_ch):
#                 best_silhouette_score = sil_score
#                 best_dbi = dbi
#                 best_ch = ch
#                 best_eps = eps
#                 best_min_samples = min_samples
#                 best_clusters = clusters

# # Aplica os melhores parâmetros encontrados ao DataFrame df_sample2
# df_sample2['cluster'] = best_clusters

# # Redução de dimensionalidade para visualização do gráfico
# pca = PCA(n_components=2)
# features_pca = pca.fit_transform(features_scaled)

# # Gráfico de visualização dos clusters em 2D com PCA
# plt.figure(figsize=(10, 7))
# sns.scatterplot(x=features_pca[:, 0], y=features_pca[:, 1], hue=df_sample2['cluster'], palette='tab10', s=20, edgecolor='k')
# plt.title(f'Clusters DBSCAN - eps: {best_eps}, min_samples: {best_min_samples}')
# plt.xlabel('Componente Principal 1')
# plt.ylabel('Componente Principal 2')
# plt.show()

# # Contagem dos pontos em cada cluster
# print(df_sample2['cluster'].value_counts())
# print(f'Melhor eps: {best_eps}, Melhor min_samples: {best_min_samples}, Melhor Silhouette Score: {best_silhouette_score}')
# print(f'Melhor Davies-Bouldin Index (DBI): {best_dbi}')
# print(f'Melhor Calinski-Harabasz Index (CH Index): {best_ch}')

# """


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Calculando-se as 3 métricas, obteve-se o seguinte output:
# # 
# # cluster<br>
# #  0    12883<br>
# #  1     3547<br>
# #  4     3489<br>
# #  2     1428<br>
# # -1     1021<br>
# #  3      590<br>
# #  5      282<br>
# #  7      257<br>
# #  8       59<br>
# #  6       54<br><br>
# # Name: count, dtype: int64<br><br>
# # **Melhor eps**: 0.2, Melhor min_samples: 50, Melhor Silhouette Score: 0.7482794489545446<br><br>
# # **Melhor Davies-Bouldin Index (DBI)**: 1.7877124152854893<br><br>
# # **Melhor Calinski-Harabasz Index (CH Index)**: 1383.0505542992075

# # %% [markdown]
# # ### 12.2 Análise de resultados do DBScan

# # %% [markdown]
# # **Análise de Consistência dos Clusters**

# # %%
# # Estatísticas descritivas dos clusters
# cluster_analysis = df_sample2.groupby('cluster')['consumo em m^3'].describe()
# print(cluster_analysis)


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Os clusters definidos com -1, representa os outliers, os quais são possíveis de serem identificados por sua dispersão em relação aos demais clusters. o consumo médio é muito alto, com 544,58 m³, e o desvio padrão também é elevado, em 793,06 m³, o que nos mostra que os outliers apresentam uma variação ampla. Já os clusters definidos com 0, tem o maior número de pontos e um consumo médio parecidos e possuem consumo moderadamente baixo e uma dispersão moderada. 
# # &nbsp;&nbsp;&nbsp;&nbsp;Os clusters menores (1, 2, 3, 4, etc.) apresentam padrões de consumo bem variados, com médias que vão de 7,24 m³ até 53,81 m³. Isso indica que perfis de consumo diferentes foram agrupados em categorias distintas, ou seja, o DBSCAN conseguiu identificar diferentes grupos de perfis de consumo e separar aqueles que estão fora do padrão, considerados anômalos.

# # %% [markdown]
# # **Identificação de Outliers**

# # %%
# # Visualizar as primeiras entradas do cluster de ruído (-1)
# outliers = df_sample2[df_sample2['cluster'] == -1]
# print(outliers.head())

# # Visualizar distribuição dos outliers
# plt.figure(figsize=(10, 6))
# sns.histplot(outliers['consumo em m^3'], bins=30, kde=True)
# plt.title('Distribuição de Consumo - Outliers (ruído)')
# plt.show()


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A visualização dos outliers com histogramas demonstra que a maioria dos pontos classificados como "ruído" está concentrada em consumos baixos. Mais da metade dos outliers tem níveis de consumo abaixo de 500 m³, enquanto alguns apresentam valores muito elevados, ultrapassando 5000 m³, conforme mostrado nos dados descritivos.
# # &nbsp;&nbsp;&nbsp;&nbsp;A tabela gerada pelo código mostra uma amostra dos pontos classificados como outliers (ou seja, pontos com rótulo -1), que não foram agrupados em nenhum dos clusters do modelo DBSCAN. A tabela mostra que cada outlier possui diferentes combinações de consumo nos diversos perfis, o que provavelmente levou à sua classificação como ponto anômalo (ou "ruído"), pois não se encaixaram nos padrões identificados pelos clusters principais. Esses pontos podem representar comportamentos fora do comum, que devem ser investigados mais a fundo.

# # %% [markdown]
# # **Proporção de Pontos Classificados como Ruído**

# # %%
# # Porcentagem de pontos classificados como ruído
# noise_points = (df_sample2['cluster'] == -1).sum()
# total_points = len(df_sample2)
# noise_percentage = (noise_points / total_points) * 100
# print(f'Porcentagem de pontos classificados como ruído: {noise_percentage:.2f}%')


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Com o resultado acima, é possível identificar que, em média, aproximadamente 4,32% dos pontos não estavam em nenhum cluster. Esse valor é relativamente moderado, o que significa que a maior parte dos dados foi agrupada nos clusters, mas uma boa parte foi classificada como "ruído" ou anomalias.

# # %% [markdown]
# # **Análise de Clusters**

# # %%
# # Contar quantos pontos estão em cada cluster
# cluster_counts = df_sample2['cluster'].value_counts()
# print("Contagem dos pontos em cada cluster:")
# print(cluster_counts)


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A contagem de pontos por cluster mostra que o cluster 0 é o maior, concentrando a maior parte dos dados, com um total de 12.883 pontos. Já os clusters menores variam entre 54 e 3.547 pontos. Isso é algo comum em problemas onde o DBSCAN agrupa a maioria dos dados em um cluster principal e distribui os demais em clusters menores, dependendo da densidade dos dados.

# # %% [markdown]
# # **Conclusão**
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;O modelo DBSCAN foi capaz de identificar clusters importantes de consumo, distinguindo com sucesso os principais grupos de usuários e padrões de consumo, além de detectar comportamentos mais incomuns. A análise revelou uma estrutura clara, onde a maior parte dos dados foi agrupada em clusters significativos, permitindo a identificação de diferentes perfis de consumo. Além disso, foi possível identificar a existência de 1021 outliers, que representam consumos fora do padrão esperado. Esses outliers podem indicar anomalias ou situações que merecem uma investigação mais detalhada, como erros de medição ou casos atípicos que fogem da norma. De maneira geral, o DBSCAN se mostrou eficiente para segmentar os dados e destacar áreas críticas, oferecendo uma base sólida para ações corretivas e otimizações futuras.

# # %% [markdown]
# # # 13. Optics

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O modelo OPTICS (Ordering Points To Identify the Clustering Structure) é uma técnica de clustering muito utilizada para identificar outliers e anomalias. É similiar ao DBScan, porém fornece uma fexibilidade maior na detecção de clusters com densidades variadas, algo que pode ser útil ao analisar dados de consumo de gás, uma vez que podem existir padrões de consumo muito variados. <br>
# # &nbsp;&nbsp;&nbsp;&nbsp;Para rodar o OPTICS, as features escolhidas foram: ```consumo_horarizado```, ```temp```, ```variação_consumo```, ```delta_time```.

# # %%
# features = ['consumo_horarizado', 'temp', 'variação_consumo', 'delta_time']

# # %% [markdown]
# # ## 13.1. Aplicação do modelo

# # %%
# from sklearn.cluster import OPTICS

# df_amostral = df_merged.sample(frac=0.01, random_state=42)

# X = df_amostral[features]

# optics_model = OPTICS(min_samples=20, xi=0.01, min_cluster_size=0.05)

# optics_model.fit(X)

# df_amostral['cluster'] = optics_model.labels_

# df_amostral['is_anomaly'] = df_amostral['cluster'] == -1

# anomalias = df_amostral[df_amostral['is_anomaly'] == True]
# print(f"Anomalias detectadas: {len(anomalias)}")


# # %% [markdown]
# # ## 13.2. Visualização de clusters gerados

# # %%
# df_amostral['is_anomaly'].value_counts()

# # %%
# plt.figure(figsize=(10, 6))
# sns.scatterplot(x='consumo_horarizado', y='variação_consumo', hue='cluster', data=df_amostral, palette='Set1')

# # Destacar as anomalias
# anomalias = df_amostral[df_amostral['is_anomaly'] == True]
# plt.scatter(anomalias['consumo_horarizado'], anomalias['variação_consumo'], color='red', label='Anomalias', marker='x')

# plt.title("Clusters de Consumo e Anomalias Detectadas")
# plt.legend()
# plt.show()


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A princípio, é possível perceber que a clusterização feita pelo modelo OPTICS não parece fazer sentido, uma vez que praticamente todos os dados foram colocados como anomalias. Ora, se todos os dados são anormais, então nenhum é anormal. A partir disso, entendemos que o modelo precisava passar por um ajuste fino de hiperparâmetros a fim de nos conceder resultados mais satisfatórios.

# # %% [markdown]
# # ## 13.3. Finetuning de hiperparâmetros

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para o modelo OPTICS, os principais hiperparâmetros a serem ajustados são: <br>
# #  - ```min_samples```: O número mínimo de pontos em uma região para que essa região seja considerada um cluster; <br>
# #  - ```xi```: Parâmetro de densidade que controla a sensibilidade do modelo em relação a mudanças de densidade nos dados; <br>
# #  - ```min_cluster_size```: Tamanho mínimo de um cluster em termos da fração total dos pontos 

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para esta abordagem, utilizaremos o método de GridSearch para encontrar a melhor combinação de valores de hiperparâmetros. O GridSearch é um algoritmo que testa todas as combinações de hiperparâmetros e retorna aquela que possua melhores resultados. Para esta análise, será utilizado como métrica de eficiência do modelo e comparação entre hiperparâmetros o Davies-Bouldin Score, que mede a qualidade dos clusters gerados pelo modelo, baseando-se na similaridade média entre os clusters e na sua separação.

# # %%
# # #from sklearn.metrics import davies_bouldin_score

# # # Defina a grade de hiperparâmetros
# # # param_grid = {
# #     'min_samples': [5, 10, 20, 50],
# #     'xi': [0.05, 0.1, 0.2],
# #     'min_cluster_size': [0.05, 0.1, 0.2]
# # }

# # best_score = np.inf  # Comece com um valor alto para o Davies-Bouldin, já que menor é melhor
# # best_params = {}

# # # Loop manual pelos hiperparâmetros
# # for min_samples in param_grid['min_samples']:
# #     for xi in param_grid['xi']:
# #         for min_cluster_size in param_grid['min_cluster_size']:
# #             # Treina o modelo OPTICS com cada combinação de hiperparâmetros
# #             optics = OPTICS(min_samples=min_samples, xi=xi, min_cluster_size=min_cluster_size)
# #             optics.fit(X)

# #             # Apenas avalie se há mais de um cluster identificado
# #             if len(np.unique(optics.labels_)) > 1:
# #                 score = davies_bouldin_score(X, optics.labels_)
# #                 print(f"Parâmetros: min_samples={min_samples}, xi={xi}, min_cluster_size={min_cluster_size}, Score: {score}")

# #                 # Atualiza se o score for melhor
# #                 if score < best_score:
# #                     best_score = score
# #                     best_params = {'min_samples': min_samples, 'xi': xi, 'min_cluster_size': min_cluster_size}

# # # Exibe os melhores parâmetros e o melhor score
# # print("Melhores hiperparâmetros:", best_params)
# # print("Melhor Davies-Bouldin Score:", best_score)


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Aqui, o código foi comentado por conta do tempo de execução. Caso queira rodar novamente para outros dados ou semelhante, basta descomentar toda a célular e rodar novamente.

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Ao rodar o algoritmo de GridSearch acima, foi retornada a seguinte melhor combinação de hiperparâmetros: 
# # - Melhores hiperparâmetros: {'min_samples': 5, 'xi': 0.2, 'min_cluster_size': 0.1}
# # 
# # &nbsp;&nbsp;&nbsp;&nbsp;Com o seguinte Davies-Bouldin Score: <br>
# # 
# # - Melhor Davies-Bouldin Score: 0.6797220500482788

# # %%
# best_params = {'min_samples': 5, 'xi': 0.2, 'min_cluster_size': 0.1}

# # %% [markdown]
# # ## 13.4. Teste após ajuste de hiperparâmetros

# # %%
# optics_model = OPTICS(min_samples=best_params['min_samples'], xi=best_params['xi'], min_cluster_size=best_params['min_cluster_size'])
# optics_model.fit(X)

# df_amostral['cluster'] = optics_model.labels_

# # Consideramos anomalias os pontos em que o consumo horarizado é negativo também
# df_amostral['is_anomaly'] = (df_amostral['cluster'] == -1) | (df_amostral['consumo_horarizado'] < 0)

# anomalias = df_amostral[df_amostral['is_anomaly'] == True]

# print(f"Anomalias detectadas: {len(anomalias)}")


# # %% [markdown]
# # ### 13.4.1. Cálculo de percentual de anomalias encontradas

# # %%
# (len((df_amostral[df_amostral['is_anomaly'] == True])) / len(df_amostral)) * 100

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Aqui, o percentual de anomalias encontrado foi de 0,12%

# # %% [markdown]
# # ## 13.5. Visualização de clusters após ajuste

# # %%
# plt.figure(figsize=(10, 6))
# sns.scatterplot(x='delta_time', y='consumo_horarizado', hue='cluster', data=df_amostral, palette='Set1')

# # Destacar as anomalias
# anomalias = df_amostral[df_amostral['is_anomaly'] == True]
# plt.scatter(anomalias['delta_time'], anomalias['consumo_horarizado'], color='red', label='Anomalias', marker='x')

# plt.title("Clusters de Consumo e Anomalias Detectadas")
# plt.xlabel('Variação de tempo entre medições (horas)')
# plt.ylabel('Consumo horarizado (m³/h)')
# plt.legend()
# plt.show()


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Avaliando o resultado final do modelo, é possível perceber que:
# # 1. A quantidade de anomalias identificadas caiu **muito**, passando para apenas 0,12% do dataframe amostral, o que corresponde a 36 linhas de dados. Isso reflete que o modelo considerou a maior parte dos dados como normais, e apenas uma pequena parcela como anomalia, como é o esperado, uma vez que as anomalias são exceções. Além disso, é importante ressaltar que pontos com valor de consumo horarizado negativo foram manualmente considerados anomalias. 
# # 2. A distribuição dos dois clusters (normal e anormal) ficou muito mais claro na segunda visualização. Agora, é possível entender que o modelo considerou como anomalia apenas os dados que possuíam consumo horarizado extremamente baixo ou negativos. 

# # %% [markdown]
# # ### 13.5.1. Cálculo do coeficiente de silhueta para o modelo 

# # %%
# labels_with_noise = df_amostral['cluster'].copy()

# silhouette_avg = silhouette_score(X, labels_with_noise)

# print(f"Coeficiente de Silhueta (incluindo ruídos) para OPTICS: {silhouette_avg}")

# # %% [markdown]
# # ## 13.6. Conclusão do modelo OPTICS

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Em conclusão, é possível perceber através da análise dos dados e clusterização com o modelo OPTICS que dados que possuem consumo horarizado negativos são considerados anômalos. algo que faz sentido no contexto do projeto atual, que analisa dados de consumo de gás. Além disso, o modelo classificou os dados com variação de tempo entre medições muito alta também como anomalia, algo que também faz sentido de acordo com informações que foram passadas pela empresa parceira. Dessa forma, a utilização de tal modelo aplicado a todos os dados de consumo que possuímos se faz de extrema utilidade para identificar ao menos estes dois tipos de anomalia que, por mais que não sejam as únicas, são significativas. 

# # %% [markdown]
# # # 14. Comparação entre todos os modelos

# # %% [markdown]
# # # 15. Previsão de consumo com modelo supervisionado

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Um modelo de aprendizagem supervisionada consegue aprender a partir de dados com resultados pré-definidos, ou seja, já rotulados. Esse tipo de modelo se faz muito útil quando já possuímos dados que estão rotulados ou classificados e queremos classificar novos dados. No contexto do projeto, utilizaremos um modelo supervisionado em conjunto com uma base de dados sintética disponibilizada pela Compass para construir um modelo preditivo que consiga dizer quantos metros cúbicos de gás um cliente irá consumir no próximo mês.

# # %% [markdown]
# # ## 15.1. Carregamento dos dados sintéticos

# # %%
# df_sintetico = pd.read_csv('../data_inteli/consumo_diario_sintetico.csv')

# # %%
# df_sintetico.head(3)

# # %% [markdown]
# # ## 15.2. Verificação da existência de valores nulos e duplicados

# # %%
# df_sintetico.isna().sum()

# # %%
# df_nulos = df_sintetico[df_sintetico.isna().any(axis=1)]
# df_nulos

# # %% [markdown]
# # ### 15.2.1. Tratamento de valores faltantes

# # %%
# ## Converter de colunas de data para datetime e criar uma coluna de ano e mês
# df_sintetico['data_hora'] = pd.to_datetime(df_sintetico['data_hora'])
# df_sintetico['ano_mes'] = df_sintetico['data_hora'].dt.to_period('M')

# # %%
# ## Calculo da média de consumo diário para cada instalação (clientCode + clientIndex)
# df_sintetico['media_consumo_instalacao'] = df_sintetico.groupby(['clientCode', 'clientIndex'])['consumo_dia'].transform('mean')

# ## Substituição os valores NaN na coluna consumo_dia pela média da instalação correspondente
# df_sintetico['consumo_dia'] = df_sintetico['consumo_dia'].fillna(df_sintetico['media_consumo_instalacao'])

# print(f"Restam {df_sintetico['consumo_dia'].isnull().sum()} valores NaN após preencher com a média da instalação.")

# # %% [markdown]
# # ### 15.2.2. Tratamento de valores duplicados

# # %%
# df_sintetico.duplicated().sum()

# # %%
# ## Substui os valores duplicados pelo valor médio da instalação correspondente
# df_sintetico = df_sintetico.groupby(['clientCode', 'clientIndex', 'data_hora']).agg({
#     'consumo_dia': 'mean',  
# }).reset_index()


# # %%
# df_sintetico.duplicated().sum()

# # %% [markdown]
# # ## 15.3. Enriquecimento de dataset

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O enriquecimento do dataset é uma medida tomada para acrescentar mais dados que podem ser úteis para um modelo preditivo. Um exemplo de enriquecimento foi feito durante a seção de pré-processamento dos dados para encontro de anomalias, onde foi realizada uma consulta em uma API de temperatura a fim de saber a temperatura média de cada dia em cada medição. 
# # &nbsp;&nbsp;&nbsp;&nbsp;Para o dataset sintético, o enriquecimento será feito apenas por meio de cálculos com os dados já existentes (consumo diário e dia).

# # %% [markdown]
# # Criação de colunas para dia, mês e ano

# # %%
# df_sintetico['ano'] = df_sintetico['data_hora'].dt.year
# df_sintetico['mes'] = df_sintetico['data_hora'].dt.month
# df_sintetico['dia'] = df_sintetico['data_hora'].dt.day


# # %% [markdown]
# # Criação de coluna para dia da semana

# # %% [markdown]
# # 0: Segunda-feira <br>
# # 1: Terça-feira<br>
# # 2: Quarta-feira<br>
# # 3: Quinta-feira<br>
# # 4: Sexta-feira<br>
# # 5: Sábado<br>
# # 6: Domingo<br>

# # %%
# df_sintetico['dia_da_semana'] = df_sintetico['data_hora'].dt.dayofweek

# # %% [markdown]
# # Calculo de médias móveis do consumo diário em diferentes janelas (7 e 30 dias) para capturar tendências

# # %%
# df_sintetico['ano_mes'] = df_sintetico['data_hora'].dt.to_period('M')

# # %%
# df_sintetico['media_movel_7_dias'] = df_sintetico['consumo_dia'].rolling(window=7).mean()
# df_sintetico['media_movel_30_dias'] = df_sintetico['consumo_dia'].rolling(window=30).mean()
# df_sintetico['media_movel_30_dias'] = df_sintetico['media_movel_30_dias'].fillna(0) ## Dados que não possuem uma janela de 30 dias
# df_sintetico['media_movel_7_dias'] = df_sintetico['media_movel_7_dias'].fillna(0) ## Dados que não possuem uma janela de 7 dias

# # %% [markdown]
# # Cálculo de consumo mensal dos clientes

# # %%
# df_sintetico['consumo_mensal'] = df_sintetico.groupby(['clientCode', 'clientIndex', 'ano_mes'])['consumo_dia'].transform('sum')

# # %% [markdown]
# # Adição de estação do ano ao dataset

# # %%
# def obter_estacao(data):
#     """
#     Função para obter a estação do ano com base na data.
#     No Brasil, as estações são:
#     - Verão: 21 de dezembro a 20 de março
#     - Outono: 21 de março a 20 de junho
#     - Inverno: 21 de junho a 20 de setembro
#     - Primavera: 21 de setembro a 20 de dezembro
#     """
#     mes = data.month
#     dia = data.day
    
#     if (mes == 12 and dia >= 21) or (mes == 1) or (mes == 2) or (mes == 3 and dia <= 20):
#         return 'Verão'
#     elif (mes == 3 and dia >= 21) or (mes == 4) or (mes == 5) or (mes == 6 and dia <= 20):
#         return 'Outono'
#     elif (mes == 6 and dia >= 21) or (mes == 7) or (mes == 8) or (mes == 9 and dia <= 20):
#         return 'Inverno'
#     else: # (mes == 9 and dia >= 21) or (mes == 10) or (mes == 11) or (mes == 12 and dia <= 20)
#         return 'Primavera'

# # %% [markdown]
# # Converte a estação em ângulo e retorna as coordenadas no círculo trigonométrico. <br>
# # Isso é feito para que as estações sejam representadas de forma cíclica.

# # %%

# def estacao_para_trig(estacao):
#     """
#     Converte a estação em ângulo e retorna as coordenadas no círculo trigonométrico.
#     Isso é feito para que as estações sejam representadas de forma cíclica.
#     """
#     estacoes = {'Verão': 0, 'Outono': 1, 'Inverno': 2, 'Primavera': 3}
#     angulo = (estacoes[estacao] / 4) * 2 * np.pi  # Converter a estação para um ângulo em radianos
#     epsilon = 1e-10
#     valores = (np.cos(angulo), np.sin(angulo))
#     valores_ajustados = tuple(0.0 if abs(v) < epsilon else float(v) for v in valores)
    
#     return valores_ajustados

# # %%
# estacao_para_trig('Verão')

# # %%
# estacao_para_trig('Outono')

# # %%
# estacao_para_trig('Inverno')

# # %%
# estacao_para_trig('Primavera')

# # %%
# df_sintetico['estacao'] = df_sintetico['data_hora'].apply(obter_estacao)

# # %%
# df_sintetico['estacao'].value_counts()

# # %% [markdown]
# # Calculo de média de consumo por estação do ano

# # %%
# media_consumo_por_estacao = df_sintetico.groupby('estacao')['consumo_dia'].mean().sort_index()

# print(media_consumo_por_estacao)

# # %%
# # Resetar o índice para o seaborn
# df_media = media_consumo_por_estacao.reset_index()
# df_media.columns = ['Estacao', 'Media_Consumo']

# # Plotar o gráfico com seaborn
# plt.figure(figsize=(10, 6))
# sns.barplot(x='Estacao', y='Media_Consumo', data=df_media, palette='viridis', legend=False, hue='Estacao')
# plt.title('Média de Consumo por Estação do Ano')
# plt.xlabel('Estação do ano')
# plt.ylabel('Média de Consumo')
# plt.xticks(rotation=45)
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.tight_layout()
# plt.show()

# # %% [markdown]
# # Calculo de mudanças percentuais no consumo entre períodos para detectar tendências de aumento ou diminuição. Além disso, pode ser úteis para identificar tendências sazonais

# # %%
# df_sintetico['mudanca_percentual'] = df_sintetico.groupby(['clientCode'])['consumo_dia'].pct_change()

# # %%
# df_sintetico['mudanca_percentual']

# # %%
# df_sintetico.fillna(0, inplace=True)

# # %% [markdown]
# # Transformação logarítmica a fim de estabilizar a variância da coluna consumo_dia 

# # %%
# df_sintetico['consumo_log'] = np.log1p(df_sintetico['consumo_dia'])

# # %%
# df_sintetico.info()

# # %% [markdown]
# # ## 15.4. Modelo Holt-Winters

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O método de Holt-Winters é uma técnica de previsão de séries temporais que incorpora a tendência e a sazonalidade dos dados. É um modelo que se mostra particularmente eficaz quando os dados apresentam padrões sazonais definidos ao longo do tempo. Dessa forma, o modelo Holt-Winters se faz ideal para analisar, por exemplo, o consumo de gás de um cliente ao longo dos anos, uma vez que este consumo é sazonal e aumenta ou diminui em determinadas épocas. 

# # %% [markdown]
# # ### 15.4.1. Definição de um dataframe com uma instalação

# # %%
# client_code = 'f7f9c17fabf5aec8cbe5a8dfe918f1d0195d9571969d0f2370790ec6e7cb6731'
# client_index = 1
# instalacao_df = df_sintetico[(df_sintetico['clientCode'] == client_code) & (df_sintetico['clientIndex'] == client_index)].copy()

# # %%
# instalacao_df['ano_mes'].value_counts()

# # %% [markdown]
# # ### 15.4.2. Agrupamento de dados por mês

# # %%
# # Agrupar os dados por instalação e por mês, somando o consumo diário
# instalacao_mensal_df = instalacao_df.groupby('ano_mes')['consumo_dia'].sum().reset_index()

# # Garantir que o índice seja o ano e mês
# instalacao_mensal_df.set_index('ano_mes', inplace=True)

# # Verificar o resultado
# print(instalacao_mensal_df.tail())


# # %% [markdown]
# # ### 15.4.3. Primeira previsão com Holt-Winters

# # %%
# from statsmodels.tsa.holtwinters import ExponentialSmoothing


# modelo_mensal = ExponentialSmoothing(
#     instalacao_mensal_df['consumo_dia'], 
#     trend='add',      
#     seasonal='add',   
#     seasonal_periods=12  ## Sazonalidade anual (12 meses)
# )

# ## Fit do modelo
# ajuste_mensal = modelo_mensal.fit()

# previsao_mensal = ajuste_mensal.forecast(1)  ## Prever apenas o próximo mês

# print(previsao_mensal)


# # %% [markdown]
# # #### 15.4.3.1. Ajusta previsão para o mês após o último mês do dataframe

# # %%
# proximo_mes = instalacao_mensal_df.index[-1] + 1  ## Próximo mês após o último disponível

# previsao_mensal.index = [proximo_mes]

# print(previsao_mensal)


# # %% [markdown]
# # #### 15.4.3.1. Gráfico de consumo mensal do cliente e ponto de previsão para o mês seguinte

# # %%
# instalacao_mensal_df['consumo_dia'].plot(label='Consumo Mensal Real', figsize=(20, 6))
# previsao_mensal.plot(label='Previsão Próximo Mês', linestyle='--', color='red')

# ## Adicionar o ponto de previsão ao gráfico
# plt.scatter(previsao_mensal.index, previsao_mensal, color='red', zorder=5)

# for i, value in enumerate(previsao_mensal):
#     plt.text(previsao_mensal.index[i], value + 0.02 * value, f'{value:.2f}', 
#              color='red', fontsize=12, ha='center')

# plt.title(f"Previsão de Consumo Mensal para {client_code} - {client_index}")
# plt.xlabel('Ano e Mês')
# plt.ylabel('Consumo Mensal')
# plt.legend()

# plt.show()


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Aqui, o modelo previu que, no mês de Agosto de 2024, tal cliente consumiria 1,45 metros cúbicos de gás.

# # %% [markdown]
# # Tendo apenas esta previsão, não é possível ter um ideia do quão correto o valor está. Por conta disso, aplicaremos uma separação dos dados em um dataframe para treinamento e outro para testes.

# # %% [markdown]
# # ### 15.4.4. Segunda versão com Holt-Winters, medindo precisão

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Como dito anteriormente, para esta versão, treinaremos o modelo com 80% dos dados, e então o testaremos com os 20% restantes.

# # %% [markdown]
# # #### 15.4.4.1. Divisão do dataframe em treinamento e teste (80/20)

# # %%
# # Dividir os dados em 80% treino e 20% teste
# train_size = int(len(instalacao_mensal_df) * 0.8)
# train, test = instalacao_mensal_df.iloc[:train_size], instalacao_mensal_df.iloc[train_size:]

# # Verificar os tamanhos dos conjuntos de treino e teste
# print(f"Tamanho do conjunto de treino: {len(train)} meses")
# print(f"Tamanho do conjunto de teste: {len(test)} meses")


# # %% [markdown]
# # #### 15.4.4.2. Treinamento do modelo com dados de treino

# # %%
# # Definir e ajustar o modelo Holt-Winters com os dados de treino
# modelo_treino = ExponentialSmoothing(
#     train['consumo_dia'], 
#     trend='add',      # Pode-se tentar 'mul' se necessário
#     seasonal='add',   # Ou 'mul', dependendo da característica dos dados
#     seasonal_periods=7  # Sazonalidade anual (7 dias)
# )

# ajuste_treino = modelo_treino.fit()

# # Fazer a previsão para o número de meses no conjunto de teste
# previsao_teste = ajuste_treino.forecast(len(test))

# # Verificar as previsões
# print(previsao_teste)


# # %% [markdown]
# # #### 15.4.4.2. Cálculo das métricas de erro para o modelo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Como principais três métricas para avaliar o modelo, escolhemos o Erro Médio Absoluto, o Erro Médio Quadrático e o Erro Médio Percentual. Cada uma dessas métricas tem como objetivo avaliar o quanto o modelo erra as previsões. <br>
# # &nbsp;&nbsp;&nbsp;&nbsp; O erro absoluto médio calcula a média das diferenças absolutas entre os valores reais e os valores que foram previstos pelo modelo. Um erro médio absoluto de 1, por exemplo, quer dizer que, quando o modelo erra, ele erra por cerca de 1 unidade (metro cúbico, no nosso caso). Já o erro médio quadrático calcula a mesma média que a métrica anterior, porém elevando os erros ao quadrado, o que resulta em uma penalização maior para erros maiores. Ademais, o erro médio percentual mede a média dos erros absolutos divididos pelos valores reais, multiplicados por 100%. Por exemplo, um erro percentual de 0.05 quer dizer que o modelo tem um erro de 5% em relação aos valores reais. <br>
# # &nbsp;&nbsp;&nbsp;&nbsp;Por fim, o cálculo dessas métricas é de extrema importância para avaliar o modelo. Uma vez que o ideal é que todas essas métricas sejam as menores possíveis, podemos ajustar o modelo e verificar se ele melhorou ou piorou com base nos valores destas métricas.

# # %%
# from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error

# ## Erro Absoluto Médio
# mae = mean_absolute_error(test['consumo_dia'], previsao_teste)

# ## Erro Quadrático Médio
# mse = mean_squared_error(test['consumo_dia'], previsao_teste)

# ## Erro Percentual Absoluto Médio
# mape = mean_absolute_percentage_error(test['consumo_dia'], previsao_teste)

# # Exibir os resultados
# print(f"Erro Médio Absoluto: {mae}")
# print(f"Erro Médio Quadrático: {mse}")
# print(f"Erro Médio Percentual: {mape}")


# # %% [markdown]
# # #### 15.4.4.2. Definir limite superior para considerar previsão correta

# # %% [markdown]
# # Aqui, definimos que valores previstos que estejam num range de +10% a -10% do valor real serão considerados como previsões corretas.

# # %%
# # Calcular o intervalo de +10% e -10% do consumo mensal no conjunto de teste
# limite_superior = test['consumo_dia'] * 1.10
# limite_inferior = test['consumo_dia'] * 0.90


# # %% [markdown]
# # #### 15.4.4.2. Plotagem de gráfico de consumo, comparando Treino, Teste e Previsão

# # %%
# plt.figure(figsize=(14, 6))
# train['consumo_dia'].plot(label='Consumo Mensal - Treino', color='blue')
# test['consumo_dia'].plot(label='Consumo Mensal - Teste', color='green')

# previsao_teste.plot(label='Previsão', linestyle='--', color='red')

# ## Adiciona faixa de +10% e -10% no gráfico
# plt.fill_between(test.index, limite_inferior, limite_superior, color='gray', alpha=0.3, label='Faixa de ±10%')

# plt.title(f"Previsão de Consumo Mensal para {client_code} - {client_index}")
# plt.xlabel('Ano e Mês')
# plt.ylabel('Consumo Mensal (m³)')
# plt.legend()
# plt.show()


# # %% [markdown]
# # Novamente, consideramos corretas aquelas previsões que se encontram dentro do limite de 10% para cima ou para baixo. No gráfico acima, são corretas todas as previsões (linha tracejada vermelha) que se encontram dentro da área cinza.

# # %%
# previsoes_corretas = (previsao_teste >= limite_inferior) & (previsao_teste <= limite_superior)

# # %%
# # Contar quantas previsões estão corretas
# total_previsoes = len(previsao_teste)
# previsoes_corretas_count = previsoes_corretas.sum()

# percentual_previsoes_corretas = (previsoes_corretas_count / total_previsoes) * 100

# print(f"{percentual_previsoes_corretas:.2f}% das previsões estão dentro da faixa de ±10% para este cliente.")


# # %% [markdown]
# # ### 15.4.5. Ajuste de hiperparâmetros dos modelos

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Os hiperparâmetros de um modelo são os valores ou configurações que passamos para um modelo de maneira manual. Tais hiperparâmetros causam um impacto significante no desempenho do modelo, e são responsáveis por controlar o processo de treinamento e definir a estrutura do modelo. Por conta disso, é muito importante encontrar uma combinação ideal de hiperparâmetros para que o modelo performe da melhor maneira possível.

# # %% [markdown]
# # #### 15.4.5.1. Parâmetros do modelo a serem ajustados

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Para o modelo Holt-Winters, foram identificados 4 hiperparâmetros a serem ajustados:
# # - trend: Define o tipo de componente de tendência que será utilizado nos cálculos do modelo. Sendo do tipo 'add', o modelo utilizará uma tendência aditiva, onde a tendência é somada na série temporal. Sendo do tipo 'mul', o modelo utilizará uma tendência multiplicativa, sendo mais adequado quando a taxa de crescimento é proporcional ao nível da série temporal. Tendo este parâmetro como 'None', temos que o modelo não inclui componente de tendência.
# # - seasonal: Define o tipo de componente sazonal que o modelo utilizará em seus cálculos, capturando padrões repetitivos intervalos de tempo, como, por exemplo, um consumo de gás que aumenta em meses de férias escolares. Os valores para esse parâmetro são os mesmos do parâmetro 'trend'.
# # - seasonal_periods: Define o número de períodos que um ciclo sazonal completo deve ter. Para um ciclo de um ano, por exemplo, o valor deveria ser de 12. 
# # - damped_trend: Define se a tendência deve ser amortecida ao longo do tempo. Se verdadeiro, aplica o amortecimento, fazendo com que a tendência seja menos pronunciada com o passar do tempo. Se falso, não aplica amortecimento e a tendência pode continuar indefinidamente. 

# # %%
# # Parâmetros a serem testados
# trend_options = ['add', 'mul', None]
# seasonal_options = ['add', 'mul', None]
# seasonal_periods = [i for i in range(2, 31)]  
# damped_trend_options = [True, False]

# # %%

# # Variáveis para armazenar os melhores resultados
# best_mae = np.inf
# best_mse = np.inf
# best_mape = np.inf
# best_params = {}

# # %% [markdown]
# # #### 15.4.5.2. Grid Search Manual para encontrar melhores parâmetros

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;O algoritmo de Grid Search é utilizado na análise de dados para encontrar a melhor combinação possível de hiperparâmetros para um modelo. Acima, definimos a nossa "grade" de parâmetros, e, abaixo, iremos testar todas essas combinações e calcular as métricas de erro para cada uma. Vale ressaltar que o algoritmo de Grid Search possui um custo computacional **alto**, e só é viável utilizá-lo aqui porque a quantidade de parâmetros é pequena. 

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Aqui, rodamos vários loops para testar todas as combinações possíveis de parâmetros. A cada iteração, é calculado o erro médio, quadrático e percentual. Ao final, é recomendada a combinação de valores que resultou nos menores erros.

# # %%
# for trend in trend_options:
#     for seasonal in seasonal_options:
#         for period in seasonal_periods:
#             for damped in damped_trend_options:
#                 try:
#                     ## Apenas testar damped_trend se houver uma tendência
#                     if trend is None and damped:
#                         continue
                    
#                     ## Definir e ajustar o modelo Holt-Winters com os dados de treino
#                     modelo_treino = ExponentialSmoothing(
#                         train['consumo_dia'], 
#                         trend=trend, 
#                         seasonal=seasonal,
#                         seasonal_periods=period,
#                         damped_trend=damped
#                     )

#                     ajuste_treino = modelo_treino.fit()

#                     ## Fazer a previsão para o número de meses no conjunto de teste
#                     previsao_teste = ajuste_treino.forecast(len(test))

#                     ## Calcular as métricas
#                     mae = mean_absolute_error(test['consumo_dia'], previsao_teste)
#                     mse = mean_squared_error(test['consumo_dia'], previsao_teste)
#                     mape = mean_absolute_percentage_error(test['consumo_dia'], previsao_teste)

#                     ## Comparar o erro e armazenar o melhor modelo (baseado no MAE)
#                     if mae < best_mae:
#                         best_mae = mae
#                         best_mse = mse
#                         best_mape = mape
#                         best_params = {
#                             'trend': trend,
#                             'seasonal': seasonal,
#                             'seasonal_periods': period,
#                             'damped_trend': damped
#                         }

#                 except Exception as e:
#                     print(f"Erro com a configuração {trend}, {seasonal}, {period}, damped={damped}: {e}")

# # %%
# ## Exibir os melhores parâmetros e métricas
# print(f"Melhores parâmetros: {best_params}")
# print(f"MAE: {best_mae}")
# print(f"MSE: {best_mse}")
# print(f"MAPE: {best_mape}")

# # %% [markdown]
# # ### 15.4.6. Modelagem com hiperparâmetros ajustados

# # %%
# modelo_treino = ExponentialSmoothing(
#     train['consumo_dia'], 
#     trend=best_params['trend'],      
#     seasonal=best_params['seasonal'],   
#     seasonal_periods=best_params['seasonal_periods'],
#     damped_trend=best_params['damped_trend']  
# )

# ajuste_treino = modelo_treino.fit()

# # Fazer a previsão para o número de meses no conjunto de teste
# previsao_teste = ajuste_treino.forecast(len(test))

# # Verificar as previsões
# print(previsao_teste)


# # %%
# limite_inferior = test['consumo_dia'] * 0.90
# limite_superior = test['consumo_dia'] * 1.10

# # %%
# plt.figure(figsize=(14, 6))
# train['consumo_dia'].plot(label='Consumo Mensal - Treino', color='blue')
# test['consumo_dia'].plot(label='Consumo Mensal - Teste', color='green')

# previsao_teste.plot(label='Previsão', linestyle='--', color='red')

# ## Adiciona faixa de +10% e -10% no gráfico
# plt.fill_between(test.index, limite_inferior, limite_superior, color='gray', alpha=0.3, label='Faixa de ±10%')

# plt.title(f"Previsão de Consumo Mensal para {client_code} - {client_index}")
# plt.xlabel('Ano e Mês')
# plt.ylabel('Consumo Mensal (m³)')
# plt.legend()
# plt.show()


# # %%
# # Calcular o MAE (Erro Absoluto Médio)
# mae = mean_absolute_error(test['consumo_dia'], previsao_teste)

# # Calcular o MSE (Erro Quadrático Médio)
# mse = mean_squared_error(test['consumo_dia'], previsao_teste)

# # Calcular o MAPE (Erro Percentual Absoluto Médio)
# mape = mean_absolute_percentage_error(test['consumo_dia'], previsao_teste)

# # Exibir os resultados
# print(f"MAE: {mae}")
# print(f"MSE: {mse}")
# print(f"MAPE: {mape}")


# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;Acima, podemos perceber que as métricas de erro diminuíram após o ajuste dos hiperparâmetros. Além disso, é possível ver, abaixo, que a porcentagem de previsões corretas também aumentou!

# # %%
# previsoes_corretas = (previsao_teste >= limite_inferior) & (previsao_teste <= limite_superior)

# # %%
# # Contar quantas previsões estão corretas
# total_previsoes = len(previsao_teste)
# previsoes_corretas_count = previsoes_corretas.sum()

# percentual_previsoes_corretas = (previsoes_corretas_count / total_previsoes) * 100

# print(f"{percentual_previsoes_corretas:.2f}% das previsões estão dentro da faixa de ±10% para este cliente.")

# # %% [markdown]
# # ### 15.4.7. Explicabilidade do modelo

# # %% [markdown]
# # &nbsp;&nbsp;&nbsp;&nbsp;A explicabilidade do modelo consiste em analisar quais componentes influenciaram a previsão que o modelo fez. Diferentemente de alguns modelos, o Holt-Winters não possui uma maneira de se demonstrar a explicabilidade de maneira tão didática. Entretanto, podemos visualizar como que cada componente do modelo (nivel, tendência, sazonalidade e amortecimento) contribuiu para a previsão. Abaixo, temos a visualização gráfica: 

# # %%
# train.index = train.index.to_timestamp()

# # %%
# plt.figure(figsize=(10, 6))

# plt.plot(train.index, train['consumo_dia'], label='Consumo Mensal Real')
# plt.plot(train.index, ajuste_treino.fittedvalues, label='Valores Ajustados pelo Modelo')

# plt.title(f'Consumo Diário Real vs. Previsão do Modelo para determinado cliente')
# plt.xlabel('Data')
# plt.ylabel('Consumo Diário (m³)')

# plt.legend()
# plt.show()


# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Aqui, é possível perceber que o modelo performa uma média próxima à real na maior parte dos casos. Entretanto, é difícil que o modelo acerte valores mais extremos como consumos muito mais altos ou baixos do que o normal. Além disso, é possível perceber, a partir do gráfico, que o modelo captura bem os padrões de sazonalidade. Apesar de não acertar o valor exato, ele consegue entender quando o consumo deve subir ou descer. 

# %% [markdown]
# ## 15.5. Finalização do modelo

# %% [markdown]
# &nbsp;&nbsp;&nbsp;&nbsp;Dessa forma, esta seção implementou completamente um modelo preditivo a parte de todo o escopo inicial (de encontrar anomalias em dados reais). Foi feito o pré-processamento dos dados sintéticos entregues pela empresa parceira, ajuste em dados de treino e teste, treinamento de modelo, ajuste de hiperparâmetros e validação de resultados a partir de métricas que calculam a taxa de erro do modelo. De acordo com a própria empresa parceira, uma previsão de consumo de gás para um cliente agrega muito valor às operações da Compass, uma vez que esta previsão pode estar presente, por exemplo, na conta de gás de determinado cliente, que já poderá estar ciente de quanto ele terá que pagar, em média, pelo gás no mês que vem. 

# %% [markdown]
# # 16. Decisão do modelo final

# %%
colunas_selecionadas = [
    'temp_scaled',
    'perfil_consumo_Aquecedor',
    'perfil_consumo_Caldeira',
    'perfil_consumo_Cocção',
    'perfil_consumo_Cocção + Aquecedor',
    'perfil_consumo_Cocção + Aquecedor + Piscina',
    'perfil_consumo_Cocção + Caldeira',
    'consumo em m^3',
    'variação_consumo',
    'consumo_horarizado',
    'delta_time'
]

# %%
# def validar_dados(df, colunas):
#     if df.empty:
#         raise ValueError("O DataFrame está vazio.")
#     if not all(col in df.columns for col in colunas):
#         raise ValueError("Uma ou mais colunas selecionadas não estão presentes no DataFrame.")
#     return True

# # Validação dos dados
# validar_dados(df_merged, colunas_selecionadas)

# # Pré-processamento dos dados
# scaler = StandardScaler()
# df_scaled = scaler.fit_transform(df_merged[colunas_selecionadas])

# # Definindo a grade de hiperparâmetros
# param_grid = {
#     'n_estimators': [100, 150, 200],
#     'max_samples': [0.8, 1.0],
#     'max_features': [0.8, 1.0],
#     'contamination': [0.05, 0.1, 'auto'],
#     'bootstrap': [False, True]
# }

# # Definindo o Isolation Forest
# iso_forest = IsolationForest(random_state=42)

# # Função customizada de pontuação usando o Silhouette Score
# def custom_scorer(estimator, X):
#     # Prevendo rótulos de anomalias (-1 para anomalia, 1 para normal)
#     labels = estimator.fit_predict(X)
#     labels = np.where(labels == 1, 0, 1)  # Convertendo para 0 (normal) e 1 (anomalia)
    
#     # Calculando Silhouette Score (usando labels como clusters)
#     if len(np.unique(labels)) > 1:  # Garantindo que há mais de um cluster
#         return silhouette_score(X, labels)
#     else:
#         return -1  # Retornando valor negativo para não penalizar quando não houver separação

# # Criando o scorer
# scorer = make_scorer(custom_scorer, greater_is_better=True, needs_proba=False)

# # Configurando o GridSearchCV
# grid_search = GridSearchCV(iso_forest, param_grid, cv=3, verbose=3, scoring=scorer)

# try:
#     # Executando o GridSearchCV para encontrar os melhores hiperparâmetros
#     grid_search.fit(df_scaled)

#     # Extraindo os melhores hiperparâmetros
#     best_params = grid_search.best_params_
#     print(f"Melhores parâmetros: {grid_search.best_params_}")
#     print(f"Melhor score: {grid_search.best_score_}")
    
#     # Treinando o modelo final com os melhores hiperparâmetros
#     best_iso_forest = grid_search.best_estimator_
    
#     # Detectando anomalias
#     df_merged['anomaly_isoforest'] = best_iso_forest.fit_predict(df_scaled)
#     df_merged['anomaly_isoforest'] = df_merged['anomaly_isoforest'].map({1: 0, -1: 1})  # 0 para normal, 1 para anomalia
    
#     # Informando a quantidade de anomalias detectadas
#     num_anomalias = df_merged['anomaly_isoforest'].sum()
#     print(f"Número de anomalias detectadas: {num_anomalias} de {len(df_merged)} amostras.")
    
#     # Calculando o Davies-Bouldin Index (DBI)
#     dbi_isoforest = davies_bouldin_score(df_scaled, df_merged['anomaly_isoforest'])
#     print(f"Davies-Bouldin Index (DBI) Isolation Forest: {dbi_isoforest:.4f}")
    
#     # Calculando o Calinski-Harabasz Index (CH Index)
#     ch_index_isoforest = calinski_harabasz_score(df_scaled, df_merged['anomaly_isoforest'])
#     print(f"Calinski-Harabasz Index (CH Index) Isolation Forest: {ch_index_isoforest:.4f}")
    
#     # Verificação condicional para o Silhouette Score
#     if num_anomalias > 0 and num_anomalias < len(df_merged):
#         silhouette_isoforest = silhouette_score(df_scaled, df_merged['anomaly_isoforest'])
#         print(f"Silhouette Score Isolation Forest (amostragem): {silhouette_isoforest:.4f}")
#     else:
#         print("Não foi possível calcular o Silhouette Score, pois não há uma separação adequada entre anomalias e normais.")
    
#     # Exportando o melhor modelo treinado
#     joblib.dump(best_iso_forest, 'best_isolation_forest_model.joblib')
#     print("Melhor modelo Isolation Forest salvo com sucesso!")
    
# except Exception as e:
#     print(f"Erro ao aplicar Isolation Forest: {e}")
#     raise

# %%
def validar_dados(df, colunas):
    if df.empty:
        raise ValueError("O DataFrame está vazio.")
    if not all(col in df.columns for col in colunas):
        raise ValueError("Uma ou mais colunas selecionadas não estão presentes no DataFrame.")
    return True

# Validação dos dados
validar_dados(df_merged, colunas_selecionadas)

# Pré-processamento dos dados
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df_merged[colunas_selecionadas])


# %%
params = {
    'bootstrap': False,
    'contamination': 0.05,  # Proporção de anomalias
    'max_features': 0.8,    # Proporção de features usadas em cada split
    'max_samples': 0.8,     # Proporção de amostras usadas para construir cada árvore
    'n_estimators': 100     # Número de árvores
}

# Criando o modelo Isolation Forest
iso_forest_final = IsolationForest(**params, random_state=42)

# Treinando e fazendo a previsão ao mesmo tempo com fit_predict
df_merged['anomaly_isoforest'] = iso_forest_final.fit_predict(df_scaled)

# Mapeando 1 para normal e -1 para anomalia
df_merged['anomaly_isoforest'] = df_merged['anomaly_isoforest'].map({1: 0, -1: 1})  # 0 para normal, 1 para anomalia

# Informando a quantidade de anomalias detectadas
num_anomalias = df_merged['anomaly_isoforest'].sum()
print(f"Número de anomalias detectadas: {num_anomalias} de {len(df_merged)} amostras.")

# %%
import seaborn as sns
import matplotlib.pyplot as plt

# Contagem de normais vs anomalias 
sns.countplot(x='anomaly_isoforest', hue='anomaly_isoforest', data=df_sample, palette='coolwarm', legend=False)
plt.title('Contagem de Amostras: Normais vs Anomalias')
plt.xlabel('0: Normal, 1: Anomalia')
plt.ylabel('Contagem')
plt.show()

# %% [markdown]
# # 17. Correlação de consumo anômalo e clientes

# %% [markdown]
# # 18. Exportação do modelo

# %%
import joblib

# iso_forest = joblib.load('best_isolation_forest_model.joblib')

# %% [markdown]
# # 19. Referências

# %% [markdown]
# # 20. Créditos

# %% [markdown]
# ---
# 
# Este notebook foi desenvolvido utilizando **Python** e as seguintes bibliotecas: `pandas`, `NumPy`, `Matplotlib`, `Seaborn`, entre outras. Caso seja necessário, ajuste os parâmetros ou execute as células conforme indicado ao longo do notebook.
# 
# ---
# 
# *Autores: Caio de Alcantara Santos, Cecília Beatriz Melo Galvão, Eduardo Faris Libutti Salles, Kethlen Martins da Silva, Lucas Cozzolino Tort, Mariella Sayumi Mercado Kamezawa, Nataly de Souza Cunha e Pablo de Azevedo*  
# *Data: 19/08/2024*


