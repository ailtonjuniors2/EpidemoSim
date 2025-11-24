from vpython import *
from random import random, uniform

# ==========================================
# 1. CONFIGURAÇÃO VISUAL (CENA E GRÁFICO)
# ==========================================
scene.width = 1000
scene.height = 400
scene.title = "<b>Simulação de Epidemia SIR Dinâmica</b>\n"
scene.userzoom = False 
scene.center = vector(0, 0, 0)

# Caixa do ambiente (Mundo)
L = 20 
# Desenhamos uma caixa para delimitar visualmente
box(pos=vector(0,0,0), size=vector(L, L, 0.5), color=color.white, opacity=0.1)

# GRÁFICO: Criado uma vez, mas configurado dinamicamente depois
grafico = graph(title="<b>Evolução da Epidemia</b>", width=1000, height=300,
                xtitle="Tempo (t)", ytitle="Indivíduos",
                fast=False, scroll=True, xmin=0, xmax=200)

curva_S = gcurve(color=color.blue, label="Suscetíveis", width=2)
curva_I = gcurve(color=color.red, label="Infectados", width=2)
curva_R = gcurve(color=color.gray(0.5), label="Recuperados", width=2)

# ==========================================
# 2. VARIÁVEIS GLOBAIS
# ==========================================
agentes = []
running = False
tempo = 0
dt = 0  # Será incrementado no loop

# ==========================================
# 3. LÓGICA DA SIMULAÇÃO
# ==========================================

def setup_simulacao():
    global tempo, agentes, running
    
    # A. Para a simulação atual
    running = False
    botao_run.text = "Iniciar"
    botao_run.background = color.green
    
    # B. Limpa agentes 3D antigos da memória e da tela
    for a in agentes:
        a.visible = False
        del a
    agentes = []
    
    # C. RESETA O GRÁFICO (O Pulo do Gato)
    tempo = 0
    curva_S.delete()  # Apaga os dados da linha azul
    curva_I.delete()  # Apaga os dados da linha vermelha
    curva_R.delete()  # Apaga os dados da linha cinza
    
    # D. Lê os valores ATUAIS dos sliders
    N = int(sl_pop.value)
    I_inicial = int(sl_inf.value)
    
    # E. Ajusta a escala do Gráfico para os novos valores
    grafico.xmin = 0
    grafico.xmax = 400 # Valor padrão inicial
    grafico.ymax = N * 1.05 # Dá uma margem de 5% no topo
    
    # F. Cria a nova população
    for i in range(N):
        # Posição aleatória dentro da caixa L
        pos_x = uniform(-L/2 + 0.5, L/2 - 0.5)
        pos_y = uniform(-L/2 + 0.5, L/2 - 0.5)
        
        # Velocidade aleatória
        vel = vector(uniform(-1, 1), uniform(-1, 1), 0).norm() * 0.2
        
        # Cria esfera
        p = sphere(pos=vector(pos_x, pos_y, 0), radius=0.3, color=color.blue)
        p.vel = vel
        p.estado = 'S'
        
        # Infecta os primeiros
        if i < I_inicial:
            p.estado = 'I'
            p.color = color.red
            
        agentes.append(p)
    
    # Atualiza legenda inicial
    atualizar_legenda_stats(N - I_inicial, I_inicial, 0)

def step():
    global tempo
    
    # Parâmetros físicos
    beta = sl_beta.value
    gamma = sl_gamma.value
    raio_contagio = 1.0
    
    # Listas de transição
    novos_infectados = []
    novos_recuperados = []
    
    # Contadores do passo atual
    conta_S = 0
    conta_I = 0
    conta_R = 0
    
    for a in agentes:
        # 1. Movimento
        a.pos += a.vel
        
        # 2. Colisão com Paredes (Quicar)
        if abs(a.pos.x) > L/2: a.vel.x *= -1
        if abs(a.pos.y) > L/2: a.vel.y *= -1
        
        # 3. Contagem Estatística
        if a.estado == 'S': conta_S += 1
        elif a.estado == 'I': conta_I += 1
        elif a.estado == 'R': conta_R += 1
        
        # 4. Dinâmica da Doença (Só processa se for Infectado)
        if a.estado == 'I':
            # Tenta recuperar
            if random() < gamma:
                novos_recuperados.append(a)
            
            # Tenta infectar outros
            # (Otimização simples: checa todos, para N < 500 é ok)
            for b in agentes:
                if b.estado == 'S' and b != a:
                    dist = mag(a.pos - b.pos)
                    if dist < raio_contagio:
                        if random() < beta:
                            novos_infectados.append(b)

    # 5. Aplica as mudanças de estado
    for a in novos_infectados:
        if a.estado == 'S':
            a.estado = 'I'
            a.color = color.red
            
    for a in novos_recuperados:
        a.estado = 'R'
        a.color = color.gray(0.5)

    # 6. Atualiza o Gráfico
    curva_S.plot(tempo, conta_S)
    curva_I.plot(tempo, conta_I)
    curva_R.plot(tempo, conta_R)
    
    # Se o tempo passar do limite atual do gráfico, empurra a visão para frente
    if tempo >= grafico.xmax:
        grafico.xmin += 1
        grafico.xmax += 1

    atualizar_legenda_stats(conta_S, conta_I, conta_R)
    tempo += 1

def atualizar_legenda_stats(s, i, r):
    lbl_stats.text = f"<b>Tempo:</b> {tempo}  |  <b>Suscetíveis:</b> {s}  |  <b>Infectados:</b> {i}  |  <b>Recuperados:</b> {r}"

# ==========================================
# 4. INTERFACE DO USUÁRIO (CONTROLES)
# ==========================================

def click_run(b):
    global running
    running = not running
    if running:
        b.text = "Pausar"
        b.background = color.orange
    else:
        b.text = "Continuar"
        b.background = color.green

def click_reset(b):
    setup_simulacao()

scene.append_to_caption("\n")

# Botões Principais
botao_run = button(text="Iniciar", bind=click_run, background=color.green)
scene.append_to_caption("   ")
button(text="RESETAR / APLICAR", bind=click_reset, background=color.red, color=color.white)

scene.append_to_caption("\n\n")


# Mostrador de Estatísticas em Tempo Real
lbl_stats = wtext(text="Aguardando início...")
scene.append_to_caption("\n\n------------------------------------------------\n")

# Sliders
def upd_pop(s): wt_pop.text = f'{s.value}'
scene.append_to_caption("População Total (N): ")
wt_pop = wtext(text='150')
sl_pop = slider(min=10, max=500, value=150, length=250, bind=upd_pop)
scene.append_to_caption("\n\n")

def upd_inf(s): wt_inf.text = f'{s.value}'
scene.append_to_caption("Infectados Iniciais: ")
wt_inf = wtext(text='3')
sl_inf = slider(min=1, max=50, value=3, length=250, bind=upd_inf)
scene.append_to_caption("\n\n")

def upd_beta(s): wt_beta.text = f'{s.value:.2f}'
scene.append_to_caption("Taxa de Contágio (Beta): ")
wt_beta = wtext(text='0.80')
sl_beta = slider(min=0, max=1, value=0.8, step=0.01, length=250, bind=upd_beta)
scene.append_to_caption("\n\n")

def upd_gamma(s): wt_gamma.text = f'{s.value:.3f}'
scene.append_to_caption("Taxa de Recuperação (Gamma): ")
wt_gamma = wtext(text='0.010')
sl_gamma = slider(min=0, max=0.1, value=0.01, step=0.001, length=250, bind=upd_gamma)
scene.append_to_caption("\n\n")

# ==========================================
# 5. LOOP PRINCIPAL
# ==========================================

# Cria o estado inicial
setup_simulacao()

while True:
    rate(30) # Mantém a simulação em velocidade constante
    if running:
        step()