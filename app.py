
# Importação das Bibliotecas
import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import matplotlib.pyplot as plt
import os

# Criação do App
app = Flask(__name__)
app.secret_key = "Nes123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dados_saude.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Rotas (Páginas)
@app.route("/")
def home():
    return render_template("home.html")  

@app.route("/funcionalidade")
def funcionalidade():
    return render_template("funcionalidade.html")

@app.route("/apresentacao")
def apresentacao():
    return render_template("apresentacao.html")  

# Gráfico Estabelecimentos de Saúde por Região
@app.route("/funcionalidade_estabelecimentos")
def funcionalidade_estabelecimentos():

    csv_path = os.path.join("data", "Estabelecimentos de Saude por Região.csv")
    df = pd.read_csv(csv_path)
    regioes = df.groupby("no_reg_geo")["valor"].sum()
    plt.figure(figsize=(8, 8))
    regioes.plot.pie(autopct="%1.1f%%", startangle=90, colors=["#2864ec", "#2050bd", "#183c8e", "#10285e", "#0a1e4a"])
    plt.title("Distribuição de Estabelecimentos de Saúde por Região")
    plt.ylabel("")  
    grafico_path = os.path.join("static", "img", "grafico_pizza.png")
    plt.savefig(grafico_path)
    plt.close()
    return render_template("funcionalidade_estabelecimentos.html", grafico_url="img/grafico_pizza.png")

# Profissionais de Saúde por Região 
@app.route("/funcionalidade_profissionais", methods=["GET", "POST"])
def funcionalidade_profissionais():

    csv_prof_path = os.path.join("data", "Profissionais da Saúde por Região.csv")
    df = pd.read_csv(csv_prof_path)

    regiao = request.form.get("regiao", "Todas")
    ano = request.form.get("ano", "Todos")
    categoria = request.form.get("categoria", "Todas")
    
    if regiao != "Todas":
        df = df[df["no_reg_geo"] == regiao]
    if ano != "Todos":
        df = df[df["ano"] == int(ano)]
    if categoria != "Todas":
        df = df[df["saude_categoria"] == categoria]

    # Gráfico 1 - Distribuição por Região
    regioes = df.groupby("no_reg_geo")["valor"].sum()
    plt.figure(figsize=(8, 8))
    regioes.plot.pie(autopct="%1.1f%%", startangle=90, colors=["#e07404", "#ca6804", "#b35d03", "#9d5103", "#864602"])
    plt.title("Distribuição Total de Profissionais por Região")
    plt.xticks(rotation=0)
    grafico_pizza_path = os.path.join("static", "img", "grafico_pizza_profissionais.png")
    plt.savefig(grafico_pizza_path)
    plt.close()

    # Gráfico 2 - Barras Empilhadas
    categorias_por_regiao = df.groupby(["no_reg_geo", "saude_categoria"])["valor"].sum().unstack()
    cores = ['#e07404', "#ca6804", "#b35d03", "#9d5103", "#864602"]
    categorias_por_regiao.plot(kind="bar", stacked=True, figsize=(10, 6), color = cores)
    plt.title("Profissionais por Categoria e Região")
    plt.xlabel("Região")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=0)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    grafico_barras_path = os.path.join("static", "img", "grafico_barras_profissionais.png")
    plt.savefig(grafico_barras_path, bbox_inches="tight") 
    plt.close()
    
    # Gráfico 3 - Evolução temporal de uma categoria
    if categoria != "Todas":
        df_categoria = df[df["saude_categoria"] == categoria]
        evolucao_temporal = df_categoria.groupby("ano")["valor"].sum()
        plt.figure(figsize=(10, 6))
        evolucao_temporal.plot(kind="line", marker="o")
        plt.title(f"Evolução Temporal: {categoria}")
        plt.xlabel("Ano")
        plt.ylabel("Quantidade")
        plt.xticks(rotation=0)
        grafico_linhas_path = os.path.join("static", "img", "grafico_linhas.png")
        plt.savefig(grafico_linhas_path)
        plt.close()
    else:
        grafico_linhas_path = None

    # Gráfico 4 - Correlação entre duas categorias
    categorias = df["saude_categoria"].unique()
    if len(categorias) >= 2:
        categoria_1 = categorias[0]
        categoria_2 = categorias[1]
        df_corr = df[df["saude_categoria"].isin([categoria_1, categoria_2])]
        pivot_corr = df_corr.pivot_table(values="valor", index="no_reg_geo", columns="saude_categoria", aggfunc="sum").dropna()
        plt.figure(figsize=(8, 6))
        plt.scatter(pivot_corr[categoria_1], pivot_corr[categoria_2], color = "#ca6804")
        plt.title(f"Correlação: {categoria_1} vs {categoria_2}")
        plt.xlabel(categoria_1)
        plt.ylabel(categoria_2)
        grafico_dispersao_path = os.path.join("static", "img", "grafico_dispersao.png")
        plt.savefig(grafico_dispersao_path)
        plt.close()

    else:
        grafico_dispersao_path = None
    
    anos = df["ano"].drop_duplicates().sort_values().tolist()
    regioes = df["no_reg_geo"].drop_duplicates().sort_values().tolist()
    categorias = df["saude_categoria"].drop_duplicates().sort_values().tolist()
    
    return render_template(
        "funcionalidade_profissionais.html",
        grafico_pizza_url="img/grafico_pizza_profissionais.png",
        grafico_barras_empilhadas_url="img/grafico_barras_profissionais.png",
        grafico_linhas_url="img/grafico_linhas.png" if grafico_linhas_path else "",
        grafico_dispersao_url="img/grafico_dispersao.png" if grafico_dispersao_path else "",
        regiao_selecionada=regiao,
        ano_selecionado=ano,
        categoria_selecionada=categoria,
        anos=anos,
        regioes=regioes,
        categorias=categorias
    )

@app.route("/funcionalidade_leitos", methods=["GET", "POST"])
def funcionalidade_leitos():

    csv_leitos_path = os.path.join("data", "Leitos por Região.csv")
    df = pd.read_csv(csv_leitos_path)
    
    regiao = request.form.get("regiao", "Todas")
    ano = request.form.get("ano", "Todos")
    categoria = request.form.get("categoria", "Todas")

    if regiao != "Todas":
        df = df[df["no_reg_geo"] == regiao]
    if ano != "Todos":
        df = df[df["ano"] == int(ano)]
    if categoria != "Todas":
        df = df[df["saude_categoria"] == categoria]
    
    # Gráfico 1 - Distribuição por Categoria em uma Região/Tempo
    categorias = df.groupby("saude_categoria")["valor"].sum()
    plt.figure(figsize=(10, 6))
    categorias.plot(kind="bar", color="#2864ec")
    plt.title("Distribuição de Leitos por Categoria")
    plt.xlabel("Categoria")
    plt.ylabel("Quantidade")
    plt.xticks(rotation=0)
    grafico_barras_categorias_path = os.path.join("static", "img", "grafico_barras_categorias.png")
    plt.savefig(grafico_barras_categorias_path)
    plt.close()
    
    # Gráfico 2 - Evolução Temporal de Leitos por Categoria
    if categoria == "Todas":
        cores = ["#2864ec", "#08142f", "#183c8e", "#10285e", "#0c1e47", "#2050bd"]
        evolucao = df.groupby(["ano", "saude_categoria"])["valor"].sum().unstack()
        evolucao.plot(kind="line", marker="o", figsize=(12, 6), color=cores[:len(evolucao.columns)])
        plt.title("Evolução Temporal de Leitos por Categoria")
        plt.xlabel("Ano")
        plt.ylabel("Quantidade")
        plt.legend()
        grafico_linhas_leitos_path = os.path.join("static", "img", "grafico_linhas_leitos.png")
        plt.savefig(grafico_linhas_leitos_path)
        plt.close()
    else:
        grafico_linhas_leitos_path = ""

    # Gráfico 3 - Comparação Regional de Leitos em uma Categoria
    grafico_comparacao_regional_path = None
    if True:  
        regiao_comparacao = df.groupby("no_reg_geo")["valor"].sum()
        plt.figure(figsize=(10, 6))
        regiao_comparacao.plot(kind="bar", color="#2050bd")
        plt.title(f"Comparação Regional de Leitos ({categoria})")
        plt.xlabel("Região")
        plt.ylabel("Quantidade")
        plt.xticks(rotation=0)
        grafico_comparacao_regional_path = os.path.join("static", "img", "grafico_comparacao_regional.png")
        print(f"Caminho do gráfico de comparação regional: {grafico_comparacao_regional_path}")
        plt.savefig(grafico_comparacao_regional_path)
        plt.close()

    anos = df["ano"].drop_duplicates().sort_values().tolist()
    regioes = df["no_reg_geo"].drop_duplicates().sort_values().tolist()
    categorias = df["saude_categoria"].drop_duplicates().sort_values().tolist()
    
    grafico_linhas_leitos_url = "img/grafico_linhas_leitos.png" if grafico_linhas_leitos_path else ""
    grafico_comparacao_regional_url = "img/grafico_comparacao_regional.png" if grafico_comparacao_regional_path else ""

    return render_template(
        "funcionalidade_leitos.html",
        grafico_barras_categorias_url="img/grafico_barras_categorias.png",
        grafico_linhas_leitos_url="img/grafico_linhas_leitos.png",
        grafico_comparacao_regional_url="img/grafico_comparacao_regional.png",
        regiao_selecionada=regiao,
        ano_selecionado=ano,
        categoria_selecionada=categoria,
        anos=anos,
        regioes=regioes,
        categorias=categorias
    )

@app.route("/funcionalidade_dengue", methods=["GET", "POST"])
def funcionalidade_dengue():

    csv_dengue_path = os.path.join("data", "Casos de Dengue por Região.csv")
    df = pd.read_csv(csv_dengue_path)

    regiao = request.form.get("regiao", "Todas")
    ano = request.form.get("ano", "Todos")

    if regiao != "Todas":
        df = df[df["no_reg_geo"] == regiao]
    if ano != "Todos":
        df = df[df["ano"] == int(ano)]

    # Gráfico 1 - Casos de Dengue por Ano em uma Região
    casos_ano = df.groupby("ano")["valor"].sum()
    plt.figure(figsize=(10, 6))
    casos_ano.plot(kind="line", marker="o", color="#08946c")
    plt.title("Evolução de Casos de Dengue por Ano")
    plt.xlabel("Ano")
    plt.ylabel("Casos")
    grafico_evolucao_casos_path = os.path.join("static", "img", "grafico_evolucao_casos.png")
    plt.savefig(grafico_evolucao_casos_path)
    plt.close()

    # Gráfico 2 - Comparação Regional de Casos de Dengue
    casos_regiao = df.groupby("no_reg_geo")["valor"].sum()
    plt.figure(figsize=(10, 6))
    casos_regiao.plot(kind="bar", color="#08946c")
    plt.title("Casos de Dengue por Região")
    plt.xlabel("Região")
    plt.ylabel("Casos")
    grafico_comparacao_regional_casos_path = os.path.join("static", "img", "grafico_comparacao_regional_casos.png")
    plt.savefig(grafico_comparacao_regional_casos_path)
    plt.close()

    anos = df["ano"].drop_duplicates().sort_values().tolist()
    regioes = df["no_reg_geo"].drop_duplicates().sort_values().tolist()

    return render_template(
        "funcionalidade_dengue.html",
        grafico_evolucao_casos_url="img/grafico_evolucao_casos.png",
        grafico_comparacao_regional_casos_url="img/grafico_comparacao_regional_casos.png",
        regiao_selecionada=regiao,
        ano_selecionado=ano,
        anos=anos,
        regioes=regioes
    )

@app.route("/funcionalidade_mortalidade", methods=["GET", "POST"])
def funcionalidade_mortalidade():
    csv_path = os.path.join("data", "Taxa de Mortalidade por Região.csv")
    df = pd.read_csv(csv_path)

    regiao = request.form.get("regiao", "Todas")
    ano = request.form.get("ano", "Todos")
    categoria = request.form.get("categoria", "Todas")

    if regiao != "Todas":
        df = df[df["no_reg_geo"] == regiao]
    if ano != "Todos":
        df = df[df["ano"] == int(ano)]
    if categoria != "Todas":
        df = df[df["saude_categoria"] == categoria]

    # Gráfico 1 - Taxa média por Região
    taxa_regiao = df.groupby("no_reg_geo")["valor"].mean()
    plt.figure(figsize=(10, 6))
    taxa_regiao.plot(kind="bar", color="#ff9999")
    plt.title("Taxa Média de Mortalidade por Região")
    plt.xlabel("Região")
    plt.ylabel("Taxa Média")
    plt.xticks(rotation=0)
    grafico_barra_path = os.path.join("static", "img", "grafico_barra_mortalidade.png")
    plt.savefig(grafico_barra_path)
    plt.close()

    # Gráfico 2 - Evolução Temporal
    grafico_linhas_path = None
    if regiao != "Todas":
        evolucao = df.groupby("ano")["valor"].mean()
        plt.figure(figsize=(12, 6))
        evolucao.plot(kind="line", marker="o", color="#ff9999")
        plt.title(f"Evolução da Mortalidade em {regiao}")
        plt.xlabel("Ano")
        plt.ylabel("Taxa")
        plt.xticks(rotation=0)
        grafico_linhas_path = os.path.join("static", "img", "grafico_linhas_mortalidade.png")
        plt.savefig(grafico_linhas_path)
        plt.close()

    # Gráfico 3 - Comparação de Categorias
    grafico_categorias_path = None
    if categoria == "Todas":
        categorias = df.groupby("saude_categoria")["valor"].mean()
        plt.figure(figsize=(10, 6))
        categorias.plot(kind="bar", color="#ff9999")
        plt.title("Comparação de Taxas por Categoria")
        plt.xlabel("Categoria")
        plt.ylabel("Taxa Média")
        plt.xticks(rotation=0)
        grafico_categorias_path = os.path.join("static", "img", "grafico_categorias_mortalidade.png")
        plt.savefig(grafico_categorias_path)
        plt.close()

    anos = df["ano"].drop_duplicates().sort_values().tolist()
    regioes = df["no_reg_geo"].drop_duplicates().sort_values().tolist()
    categorias = df["saude_categoria"].drop_duplicates().sort_values().tolist()

    grafico_linhasmort_url = "img/grafico_linhas_mortalidade.png" if grafico_linhas_path else ""
    grafico_categoriasmort_url = "img/grafico_categorias_mortalidade.png" if grafico_categorias_path else ""

    return render_template(
        "funcionalidade_mortalidade.html",
        grafico_barramort_url="img/grafico_barra_mortalidade.png",
        grafico_linhasmort_url=grafico_linhasmort_url,
        grafico_categoriasmort_url=grafico_categoriasmort_url,
        regiao_selecionada=regiao,
        ano_selecionado=ano,
        categoria_selecionada=categoria,
        anos=anos,
        regioes=regioes,
        categorias=categorias
    )

if __name__ == "__main__":
    app.run(debug=True)
    