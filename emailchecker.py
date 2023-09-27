import argparse
import sys
import os
from dns import resolver
from validate_email import validate_email
import concurrent.futures
from tqdm import tqdm

def create_parser():
    parser = argparse.ArgumentParser(description="Email validation from a file")
    parser.add_argument('-m', '--mail', help="Single email address to validate")
    parser.add_argument('-f', '--file', help="File containing a list of email addresses to validate")
    parser.add_argument('-t', '--threads', type=int, default=4, help="Number of threads for concurrent validation")
    return parser

def validate_single_email(mail):
    # Разделите email-адрес на имя пользователя и домен
    username, domain = mail.split('@')

    try:
        # Получите MX (Mail Exchanger) записи для домена
        mx_records = resolver.resolve(domain, 'MX')
        return bool(mx_records)
    except Exception as e:
        # Ничего не выводим в случае ошибки
        return False

def validate_emails_from_file(file_path, num_threads):
    try:
        with open(file_path, 'r') as file:
            email_list = file.read().splitlines()
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                results = list(tqdm(executor.map(validate_single_email, email_list), total=len(email_list)))
            
            for email, is_valid in zip(email_list, results):
                if is_valid:
                    print(f'\033[32m[+] Email "{email}" существует!\033[0m')
                else:
                    print(f'\033[31m[-] Email "{email}" не существует!\033[0m')
    except FileNotFoundError:
        print(f"Файл '{file_path}' не найден.")
    except Exception as e:
        # Ничего не выводим в случае ошибки при чтении файла
        pass

if __name__ == '__main__':
    parser = create_parser()

    # Если не указаны аргументы командной строки, выведите справку и завершите выполнение
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    namespace = parser.parse_args(sys.argv[1:])
    
    if namespace.mail:
        mail = namespace.mail
        is_valid = validate_single_email(mail)
        if is_valid:
            print('\033[32m[+] Email существует!\033[0m')
        else:
            print('\033[31m[-] Email не существует!\033[0m')
    
    if namespace.file:
        file_path = namespace.file
        validate_emails_from_file(file_path, namespace.threads)
