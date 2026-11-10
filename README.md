# SEL0337 – Prática 5 – Checkpoint 1

**Disciplina:** SEL0337 – Projetos em Sistemas Embarcados

**Integrantes:**
- Felipe Assis Bernardes Falvo — Nº USP: 15004433
- Kayke Malaquias Gregorio — Nº USP: 15651561

---

## 1. Objetivo

O objetivo desse checkpoint é fazer um programa em Python iniciar automaticamente no boot da Raspberry Pi, sem que ninguém precise executar ele manualmente. Para isso, o programa foi registrado como um **serviço do systemd** por meio de um *unit file* (`.service`).

## 2. Aplicação escolhida

Um **blink de LED** no **GPIO 18**, feito em Python com a biblioteca `RPi.GPIO`. O LED pisca a cada 0,2 s. Ao parar o serviço, um segundo script em Python é executado para garantir que o LED fique apagado.

**Montagem:** Foi utilizado um led no GPIO 18, um resistor, similar ao circuito da Fig. 7 do roteiro. É importante mencionar que durante o vídeo foi mostrado o circuito.

## 3. Arquivos do repositório

* **`blink_service.py`**: Código que pisca o LED. É o arquivo executado pelo systemd (`ExecStart`).
* **`parar_blink.py`**: Código executado ao interromper o serviço (`ExecStop`), responsável por apagar o LED e liberar o pino GPIO.
* **`blink_check1.service`**: *Unit file* que tem as configurações que descrevem o serviço para o systemd.
* **`video_prova.mp4`**: Vídeo mostrando a inicialização (`start`) e interrupção (`stop`) do serviço através do comando `systemctl`.
* **`video_reboot.mp4`**: Vídeo mostrando a habilitação do serviço (`enable`), a reinicialização da placa (`reboot`) e a execução automática do código com o LED piscando após o boot.

## 4. Conceitos

- **Boot da Raspberry Pi:** ao ligar, a GPU executa o código da ROM do SoC, que carrega o `bootcode.bin` e depois o `start.elf`. O `start.elf` le o `config.txt` e carrega o kernel Linux. Em seguida, o kernel monta o `rootfs` e passa ao *init system*.
- **Init system e systemd:** o init system é o primeiro processo do espaço de usuário. O systemd inicia, na ordem certa e em paralelo, os serviços do sistema e mantem eles até o desligamento. Cada serviço é feito por um arquivo `.service`.
- **systemctl:** ferramenta de linha de comando para controlar os serviços.
- **Unit file:** arquivo de configuração dividido em três blocos: `[Unit]`, `[Service]` e `[Install]`.
- **`start` × `enable`:** `start` inicia o serviço nessa sessão e o `enable` faz o serviço iniciar a cada boot.

## 5. Explicação dos códigos

### 5.1 `blink_service.py` (serviço principal)

```python
#!/usr/bin/env python3

import RPi.GPIO as GPIO #biblioteca dos pinos
import time #biblioteca para o tempo

GPIO.setmode(GPIO.BCM)

led = 18 #porta do led
GPIO.setup(led,GPIO.OUT) #colocando o led como saida

#funcao para ele ficar piscando
try:
    while True:
        GPIO.output(led,GPIO.HIGH) #ligando o led
        time.sleep(0.2)
        GPIO.output(led,GPIO.LOW) #desligando o led
        time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup() #limpando as portas
```
O `#!/usr/bin/env python3` indica que o arquivo deve ser interpretado pelo Python. O led foi ligado no GPIO 18 e configurado como saída. Dentro do while, a ideia é que o led pisque a cada 0,2 segundos até o programa parar. E ao usar o `try ... except KeyboardInterrupt`, o código para quando apertar Ctrl+C e o `GPIO.cleanup()` libera os pinos usados.


### 5.2 `parar_blink.py` (executado no `ExecStop`)

```python
#!/usr/bin/env python3

import RPi.GPIO as GPIO #biblioteca dos pinos

GPIO.setmode(GPIO.BCM)

led = 18 #porta do led

GPIO.setup(led,GPIO.OUT) #colocando led como saida
GPIO.output(led,GPIO.LOW) #desligando o led
GPIO.cleanup()
```

Esse código não tem while (laço), ou seja, ele vai rodar apenas uma vez. Após configurar o led no GPIO 18 e colocar ele como saída, ele desliga o pino (LOW) e libera o pino por meio da função `GPIO.cleanup()`. O systemd executa ele quando o serviço é parado (`systemctl stop`), garantindo que o LED fique apagado.

### 5.3 `blink_check1.service` (unit file)

```ini
[Unit]
Description= Blink LED (Python)
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/sel/3361/pratica5/blink_service.py
ExecStop=/usr/bin/python3 /home/sel/3361/pratica5/parar_blink.py
User=sel

[Install]
WantedBy=multi-user.target
```

No bloco do `[Unit]`, o Description indica o nome do do serviço mostrado pelo systemd. E o After=multi-user.target indica que o serviço só é iniciado depois que o sistema chega ao modo multiusuário, quando o sistema já está carregado.

No bloco do `[Service]`, a informação que está no ExecStart é o comando executado quando o serviço inicia. Já o que está no ExecStop é o comando executado quando o serviço é parado com systemctl stop, no qual nesse caso é chamado o `parar_blink.py`, que apaga o LED. E por fim, User=sel indica que o serviço roda com o usuário sel, e não como root. É importante mencionar que no ExecStart, o interpretador /usr/bin/python3 é chamado diretamente, pois o código depende do Python e da biblioteca RPi.GPIO para executar.

No bloco do `[Install]`, o WantedBy=multi-user.target indica que, ao executar systemctl enable, o serviço será ligado ao alvo `multi-user.target`, fazendo ele iniciar sozinho a cada boot. 

## 6. Como foi feito

1. Montagem do circuito do LED no GPIO 18 e criação dos códigos blink_service.py e parar_blink.py.
2. Teste do código, no terminal, encerrando com Ctrl+C:
   ```bash
   python3 blink_service.py
   ```
3. Criação do unit file `blink_check1.service`.
4. Instalação do serviço no systemd:
   ```bash
   sudo cp blink_check1.service /lib/systemd/system/
   sudo systemctl daemon-reload
   ```
5. Teste (`video_prova.mp4`):
   ```bash
   sudo systemctl start blink_check1.service
   systemctl status blink_check1.service
   sudo systemctl stop blink_check1.service    # executa o ExecStop (parar_blink.py)
   ```
6. Habilitação no boot e reinicialização (`video_reboot.mp4`):
   ```bash
   sudo systemctl enable blink_check1.service
   sudo reboot
   ```
7. Após o boot, o LED começou a piscar sozinho.

## 7. Resultados

- O serviço inicia automaticamente no boot e o LED pisca como mostra no vídeo `video_reboot.mp4`.
- `systemctl start` inicia o blink e `systemctl stop` encerra ele, executando o `parar_blink.py`, que apaga o LED, como mostra no vídeo `video_prova.mp4`.
- `systemctl disable blink_check1.service` remove a inicialização automática.
