# Zip-Bruteforce

Script simples em Python para **descobrir a senha** de um arquivo `.zip` usando uma **wordlist externa** (`TOP500.txt` por padrão). O programa **imprime somente a senha encontrada** (útil para correção automática).

> ⚠️ Use apenas em arquivos para os quais você tem autorização. A quebra de senhas de arquivos alheios sem permissão é ilegal.


## Requisitos
- Python 3.8 ou superior.
- (Opcional) `pyzipper` para suporte a ZIPs com criptografia AES:
```bash
pip install pyzipper
```

## Instalação rápida

```bash
# 1) Copiar / copiar a pasta zip-bruteforce para seu computador
cd zip-bruteforce

# 2) (Opcional) criar e ativar venv
python3 -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 3) (Opcional) instalar pyzipper se souber que o ZIP usa AES
pip install --upgrade pip
pip install pyzipper
```

## Uso

```bash
# Sintaxe mínima (usa TOP500.txt da pasta atual)
python3 brute_zip.py -z caminho/para/arquivo.zip

# Exemplo
python3 brute_zip.py -z trabalho.zip
```

- Se a senha for encontrada: o programa **imprime somente** a senha no terminal e sai com código `0`.
- Se a senha não estiver na wordlist: não imprime nada e sai com código `1`.
- Em caso de erro (zip não encontrado / zip inválido / wordlist ausente): mensagens aparecem no `stderr` e o programa sai com código `2`.

### Opções
```
-z, --zip       Caminho para o arquivo .zip alvo (obrigatório)
-w, --wordlist  Caminho para a wordlist (padrão: ./TOP500.txt)
-v, --verbose   Mostra progresso/erros em stderr (stdout permanece limpo)
```

### Exemplo com verbose (debug)
```bash
python3 brute_zip.py -z trabalho.zip --verbose
# Progressos e erros aparecerão em stderr; a senha, se encontrada, aparecerá em stdout.
```

## Observações técnicas
- O script tenta abrir o **primeiro arquivo** contido no ZIP e ler 1 byte para validar a senha sem extrair conteúdo.
- Para lidar com variações de encoding, cada candidato de senha é testado em `utf-8` e `latin-1`.
- Se o ZIP usar criptografia AES, instale `pyzipper` para maior compatibilidade (veja seção Requisitos).

## Sugestão para testar localmente (criar um zip protegido)
No Linux com `zip` instalado:
```bash
# cria arquivo protegido por senha (será solicitado a senha)
zip -e exemplo.zip arquivo_para_incluir.txt
```
Ou usando 7-Zip (7z):
```bash
7z a -pMINHASENHA exemplo.zip arquivo_para_incluir.txt
```

## Saída / integração com correção automática
- Por projetar saída limpa, a ferramenta é adequada para scripts de avaliação automática. 
- Códigos de saída:
  - `0` = senha encontrada
  - `1` = senha não encontrada
  - `2` = erro (arquivo não encontrado / zip inválido / wordlist ausente / etc)

## Licença
MIT
