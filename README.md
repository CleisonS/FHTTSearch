# UNM Inspector

Ferramenta gráfica passiva, em Python/PySide6, para diagnosticar como o FiberHome UNM2000 v5.0.3 expõe janelas e controles ao Windows por Win32 e Microsoft UI Automation (UIA).

## Objetivo e escopo
O UNM Inspector lista janelas, detecta backends, percorre árvores de controles, mostra propriedades, captura screenshots, exporta TXT/CSV/JSON e gera um relatório ZIP para análise técnica. Esta fase **não** pesquisa FHTTs, não abre OLTs automaticamente, não clica em comandos operacionais, não usa OCR e não altera o UNM2000.

## Requisitos e compatibilidade
- Windows 10/11 64 bits.
- Python 3.11 ou 3.12 para execução em desenvolvimento.
- Dependências: PySide6, pywinauto, pywin32, psutil e Pillow. Testes usam pytest e pytest-qt. PyInstaller é usado somente no build.

## Instalação
```bat
scripts\install.bat
```

## Execução
```bat
scripts\run.bat
```
Ou:
```bat
python main.py
```

## Execução como administrador
A aplicação não exige administrador. Se o UNM2000 estiver elevado, algumas propriedades podem retornar acesso negado; nesse caso, feche o Inspector e execute `run.bat` como administrador para comparar os resultados.

## Fluxo recomendado
1. Abra o UNM2000.
2. Faça login manualmente.
3. Abra a janela principal.
4. Abra uma OLT.
5. Deixe aberta a janela NE Manager.
6. Abra o UNM Inspector.
7. Clique em **Atualizar janelas**.
8. Selecione a janela NE Manager.
9. Execute **Detectar backends**.
10. Execute **Inspecionar controles**.
11. Abra o **Live Inspector**.
12. Posicione o cursor sobre Search, ONU List, Device Tree, ONU Status, Device Name e Physical Address.
13. Congele e copie cada elemento relevante.
14. Gere o relatório completo.
15. Compartilhe o ZIP gerado em `output/reports/`.

## Como usar
- **Lista de janelas:** use filtros por título/processo, “Somente UNM2000” e “Somente visíveis”.
- **Backends:** Win32 e UIA são testados separadamente; falha em um backend não encerra a aplicação.
- **Inspeção:** a árvore central mostra nome, tipo, classe, Automation ID, handle e backend; o painel direito mostra propriedades completas.
- **Live Inspector:** janela separada que lê o controle sob o cursor sem alterar foco. F8 congela; Ctrl+C copia quando a janela está ativa.
- **Screenshots:** tela inteira, janela selecionada e região de controle são salvas em `output/screenshots/`.
- **Exportação:** TXT, CSV com BOM e separador `;`, JSON indentado e relatório completo ZIP.

## Arquivos gerados
- Logs: `logs/unm_inspector.log`.
- Screenshots: `output/screenshots/`.
- Relatórios: `output/reports/YYYYMMDD_HHMMSS_UNM_Inspection.zip`.
- Configuração local: `config.json`, criada na primeira execução com base em `config.example.json`.

## Erros comuns
- **Backend UIA não acessou a janela:** tente Win32 ou execute com privilégios iguais ao UNM2000.
- **Janela minimizada:** screenshots podem não representar o conteúdo atual.
- **Controle desapareceu:** a inspeção continua e registra erro parcial.
- **Configuração corrompida:** o arquivo é salvo como `.corrupted.bak` e os padrões são restaurados.

## Segurança e limitações
A ferramenta é passiva: não envia dados à internet, não abre portas, não registra teclas, não injeta DLL, não acessa memória do processo e não modifica arquivos do UNM2000. Não usa OCR, OpenCV, Selenium nem automação por coordenadas fixas. A leitura depende do que Win32/UIA disponibilizam.

## Testes
```bat
pytest -q
```

## Build do executável
```bat
scripts\build_exe.bat
```
O build onedir gera `dist\UNMInspector\UNMInspector.exe` e inclui recursos QSS, README e configuração exemplo.
