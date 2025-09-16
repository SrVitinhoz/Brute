#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brute_zip.py
Tenta descobrir a senha de um arquivo .zip usando uma wordlist externa (TOP500.txt por padrão).
Comportamento:
 - Recebe somente o caminho do .zip alvo (-z / --zip).
 - Usa, por padrão, ./TOP500.txt (mas pode ser sobrescrito com -w).
 - Se encontrar a senha: imprime SOMENTE a senha no stdout (seguida de newline) e sai com código 0.
 - Se não encontrar: sai com código 1.
 - Em caso de erro (zip inválido / wordlist ausente / etc): mensagens em stderr e código 2.
 - Use --verbose para ver progresso/erros em stderr (stdout continua limpo).
Compatibilidade:
 - Python 3.8+
 - Se o ZIP usar criptografia AES e você instalar pyzipper (`pip install pyzipper`), o script tentará fallback.
"""
from __future__ import annotations
import argparse
import sys
import time
from zipfile import ZipFile, BadZipFile
from typing import Iterator

def iter_wordlist(path: str) -> Iterator[str]:
    """Lê a wordlist linha-a-linha (streaming) e retorna cada senha limpa."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                s = line.rstrip('\n\r')
                if s:
                    yield s
    except FileNotFoundError:
        raise
    except Exception as e:
        raise

def try_zipfile_open(z: ZipFile, member: str, pwd_bytes: bytes) -> bool:
    """Tenta abrir o membro do zip com zipfile builtin; retorna True se senha correta."""
    try:
        with z.open(member, 'r', pwd=pwd_bytes) as fh:
            # ler 1 byte para forçar validação da senha
            _ = fh.read(1)
        return True
    except RuntimeError:
        # geralmente senha incorreta
        return False
    except Exception:
        # outros erros também tratamos como falha para esse candidato
        return False

def try_pyzipper(zip_path: str, member: str, pwd_bytes: bytes, pyzipper_module) -> bool:
    """Se pyzipper estiver disponível, tenta abrir o zip com AES support."""
    try:
        with pyzipper_module.AESZipFile(zip_path, 'r') as z2:
            with z2.open(member, pwd=pwd_bytes) as fh:
                _ = fh.read(1)
        return True
    except RuntimeError:
        return False
    except Exception:
        return False

def find_password(zip_path: str, wordlist_path: str, verbose: bool=False) -> int:
    """
    Retorna:
     0 -> senha encontrada (imprimida em stdout)
     1 -> senha não encontrada
     2 -> erro (zip inválido, wordlist não encontrada, etc)
    """
    start = time.time()
    # Abrir zip
    try:
        z = ZipFile(zip_path)
    except FileNotFoundError:
        print(f"Erro: arquivo '{zip_path}' não encontrado.", file=sys.stderr)
        return 2
    except BadZipFile:
        print(f"Erro: '{zip_path}' não é um ZIP válido ou está corrompido.", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Erro abrindo zip: {e}", file=sys.stderr)
        return 2

    # Escolher primeiro arquivo (não diretório) interno para teste
    try:
        members = [m for m in z.namelist() if not m.endswith('/')]
    except Exception as e:
        print(f"Erro ao listar conteúdo do zip: {e}", file=sys.stderr)
        return 2

    if not members:
        print("Erro: ZIP não contém arquivos testáveis.", file=sys.stderr)
        return 2

    target_member = members[0]
    if verbose:
        print(f"[debug] membro interno para teste: {target_member}", file=sys.stderr)

    # tentar importar pyzipper (fallback AES) se estiver instalado
    pyzipper_module = None
    try:
        import pyzipper as _pz
        pyzipper_module = _pz
        if verbose:
            print("[debug] pyzipper encontrado — fallback AES habilitado.", file=sys.stderr)
    except Exception:
        if verbose:
            print("[debug] pyzipper NÃO instalado — AES fallback desabilitado.", file=sys.stderr)

    # iterar wordlist streaming
    try:
        total_tried = 0
        for candidate in iter_wordlist(wordlist_path):
            total_tried += 1
            # pular linhas vazias
            if not candidate:
                continue

            # tentar diferentes encodings comuns
            for enc in ('utf-8', 'latin-1'):
                try:
                    pwd_bytes = candidate.encode(enc)
                except Exception:
                    continue

                # primeiro zipfile builtin
                if try_zipfile_open(z, target_member, pwd_bytes):
                    # imprimir SOMENTE a senha no stdout
                    print(candidate)
                    return 0

                # fallback pyzipper (se disponível)
                if pyzipper_module and try_pyzipper(zip_path, target_member, pwd_bytes, pyzipper_module):
                    print(candidate)
                    return 0

            # progresso em stderr (cada 100 tentativas ou no fim)
            if verbose and total_tried % 100 == 0:
                elapsed = time.time() - start
                print(f"[debug] tentadas={total_tried} tempo={elapsed:.1f}s", file=sys.stderr)

        # terminou a wordlist sem sucesso
        return 1

    except FileNotFoundError:
        print(f"Erro: wordlist '{wordlist_path}' não encontrada.", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Erro lendo wordlist: {e}", file=sys.stderr)
        return 2

def main():
    ap = argparse.ArgumentParser(description="Descobre senha de arquivo .zip usando TOP500.txt (imprime APENAS a senha).")
    ap.add_argument('-z', '--zip', required=True, help='Caminho para o arquivo .zip alvo')
    ap.add_argument('-w', '--wordlist', default='TOP500.txt',
                    help='Caminho para wordlist (padrão: ./TOP500.txt)')
    ap.add_argument('-v', '--verbose', action='store_true', help='Imprime progresso/erros em stderr')
    args = ap.parse_args()

    rc = find_password(args.zip, args.wordlist, verbose=args.verbose)
    sys.exit(rc)

if __name__ == "__main__":
    main()
