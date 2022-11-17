#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
  Esse arquivo faz a geração 

  Modificado em 04 de dezembro de 2016
  por Vitor Mazuco (vitor.mazuco@gmail.com)
"""

import sys
from collections import namedtuple
import string
import argparse
import os
try:
    import xlrd
except:
    sys.exit("[!] Por favor, intale a biblioteca xlrd com o comando: pip install xlrd")

def unique_list(list_sort, verbose):
    noted = []
    if verbose > 0:
        print("[*] Removendo duplicatas enquanto mantém a ordem")
    [noted.append(item) for item in list_sort if not noted.count(item)] # Compreensão da lista
    return noted


def census_parser(filename, verbose):
    # Criar a tupla nomeada
    CensusTuple = namedtuple('Census', 'name, rank, count, prop100k, cum_prop100k, pctwhite, pctblack, pctapi, pctaian, pct2prace, pcthispanic')

    # Defina a localização do arquivo e da planilha até que os argumentos sejam desenvolvidos
    worksheet_name = "top1000"

    # Definir as variáveis da folha de trabalho e folha de trabalho
    workbook = xlrd.open_workbook(filename)
    spreadsheet = workbook.sheet_by_name(worksheet_name)
    total_rows = spreadsheet.nrows - 1
    current_row = -1

    # Definir as variaveis para obter os detalhes
    username_dict = {}
    surname_dict = {}
    alphabet = list(string.ascii_lowercase)

    while current_row < total_rows:
        row = spreadsheet.row(current_row)
        current_row += 1
        entry = CensusTuple(*tuple(row)) # Passando os valores da linha como uma tupla para o 'namedtuple'
        surname_dict[entry.rank] = entry
        cellname = entry.name
        cellrank = entry.rank
        for letter in alphabet:
            if "." not in str(cellrank.value):
                if verbose > 1:
                    print("[-] Eliminando os cabeçalhos da tabela")
                break
            username = letter + str(cellname.value.lower())
            rank = str(cellrank.value) # convertendo em strings
            username_dict[username] = rank
    username_list = sorted(username_dict, key=lambda key: username_dict[key])

    return(surname_dict, username_dict, username_list)

def username_file_parser(prepend_file, append_file, verbose):
    if prepend_file:
        put_where = "begin" # começo
        filename = prepend_file
    elif append_file:
        put_where = "end" # final
        filename = append_file
    else:
        sys.exit("[!] Ocorreu um erro ao processar a lista de sobrenome suplementar!")
    with open(filename) as file:
        lines = [line.rstrip('\n') for line in file]
    if verbose > 1:
        if "end" in put_where:
            print("[*] Adicionando %d entradas à lista de nomes de usuários") % (len(lines))
        else:
            print("[*] Adicionando %d entradas à lista de nomes de usuários") % (len(lines))
    return(lines, put_where)

def combine_usernames(supplemental_list, put_where, username_list, verbose):
    if "begin" in put_where:
        username_list[:0] = supplemental_list # Adicionar
    if "end" in put_where:
        username_list.extend(supplemental_list)
    username_list = unique_list(username_list, verbose)
    return(username_list)

def write_username_file(username_list, filename, domain, verbose):
    open(filename, 'w').close() # Exclui o conteúdo do nome do arquivo
    if domain:
        domain_filename = filename + "_" + domain
        email_list = []
        open(domain_filename, 'w').close()
    if verbose > 1:
        print("[*] Escrevendo para %s") % (filename)
    with open(filename, 'w') as file:
        file.write('\n'.join(username_list))
    if domain:
        if verbose > 1:
            print("[*] Escrevendo lista suportada por domínio para %s") % (domain_filename)
        for line in username_list:
            email_address = line + "@" + domain
            email_list.append(email_address)
        with open(domain_filename, 'w') as file:
            file.write('\n'.join(email_list))
    return


if __name__ == '__main__':
    # Se o script for executado no CLI
    usage = '''modo de usar: %(prog)s [-c census.xlsx] [-f output_filename] [-a append_filename] [-p prepend_filename] [-d domain_name] -q -v -vv -vvv'''
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument("-c", "--census", type=str, help="O arquivo do censo que será usado para criar nomes de usuários, pode ser recuperado:\n wget http://www2.census.gov/topics/genealogy/2000surnames/Top1000.xls", action="store", dest="census_file")
    parser.add_argument("-f", "--filename", type=str, help="Nome do arquivo para a saída dos nomes de usuário", action="store", dest="filename")
    parser.add_argument("-a","--append", type=str, action="store", help="Uma lista de nome de usuário para acrescentar à lista gerada a partir do censo", dest="append_file")
    parser.add_argument("-p","--prepend", type=str, action="store", help="Uma lista de nomes de usuários para antecipar à lista gerada a partir do censo", dest="prepend_file")
    parser.add_argument("-d","--domain", type=str, action="store", help="O domínio para acrescentar aos nomes de utilizador", dest="domain_name")
    parser.add_argument("-v", action="count", dest="verbose", default=1, help="Nível de verbosidade, padrão para um, este produz cada comando e resultado")
    parser.add_argument("-q", action="store_const", dest="verbose", const=0, help="Define os resultados como silenciosos")
    parser.add_argument('--version', action='version', version='%(prog)s 0.42b')
    args = parser.parse_args()

    # Definir Construtores
    census_file = args.census_file   # Census
    filename = args.filename         # Nome do arquivo para saídas
    verbose = args.verbose           # Nível de Verbosidade
    append_file = args.append_file   # Nome do arquivo para os nomes de usuário anexados ao arquivo de saída
    prepend_file = args.prepend_file # Nome do arquivo para os nomes de usuário adcionados ao arquivo de saída
    domain_name = args.domain_name   # O nome do domínio a ser anexado à lista de nome de usuário
    dir = os.getcwd()                # Obter diretório de trabalho atual
		
    # Validator Argumento
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    if append_file and prepend_file:
        sys.exit("[!] Selecione antes ou anexar para um arquivo não ambos")
	
    if not filename:
        if os.name != "nt":
             filename = dir + "/census_username_list"
        else:
             filename = dir + "\\census_username_list"
    else:
        if filename:
            if "\\" or "/" in filename:
                if verbose > 1:
                    print("[*] Usando o nome do arquivo: %s") % (filename)
        else:
            if os.name != "nt":
                filename = dir + "/" + filename
            else:
                filename = dir + "\\" + filename
                if verbose > 1:
                    print("[*] Usando o nome do arquivo: %s") % (filename)

    # Definir variáveis de trabalho
    sur_dict = {}
    user_dict = {}
    user_list = []
    sup_username = []
    target = []
    combined_users = []

    # Processar arquivo censo
    if not census_file:
        sys.exit("[!] Você não forneceu um arquivo do census!")
    else:
        sur_dict, user_dict, user_list = census_parser(census_file, verbose)

    # Processar arquivo de nome de usuário suplementar
    if append_file or prepend_file:
        sup_username, target = username_file_parser(prepend_file, append_file, verbose)
        combined_users = combine_usernames(sup_username, target, user_list, verbose)
    else:
        combined_users = user_list

    write_username_file(combined_users, filename, domain_name, verbose)
