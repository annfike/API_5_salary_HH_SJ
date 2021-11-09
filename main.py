import os
from statistics import mean 

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_rub_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        salary = salary_from * 1.2
    elif not salary_from and salary_to:
        salary = salary_to * 0.8
    else:
        salary = (salary_from + salary_to) / 2
    return salary
    

def predict_rub_salary_hh(vacancy):
    salary_delta = vacancy['salary'] 
    if not salary_delta or salary_delta['currency'] != 'RUR':
        salary = None
    else:
        salary_from = salary_delta['from']
        salary_to = salary_delta['to']
        salary = predict_rub_salary(salary_from, salary_to)
    return salary


def predict_rub_salary_sj(vacancy):
    if not vacancy['payment_from'] and not vacancy['payment_to'] or vacancy['currency'] != 'rub':
        salary = None
    else:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        salary = predict_rub_salary(salary_from, salary_to)
    return salary


def get_vacancies(language, page, area, period):
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'\
        '(KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'accept': '*/*'
        }
    payload = {
        'text': f'Программист {language}',
        'area': area,
        'period': period,
        'page': page, 
        } 
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    response = response.json()
    return response


def get_language_vacancies_statistics_hh(languages):
    result = {}
    for language in languages:
        vacancies_all_pages = []
        page = 0
        while True:
            vacancies = get_vacancies(language, page, area=1, period=3)
            pages_number = vacancies['pages']
            if page > pages_number:
                break
            vacancies_all_pages.extend(vacancies['items'])
            page += 1
        vacancies_number = vacancies['found']
        salaries = [predict_rub_salary_hh(vacancy) for vacancy in vacancies_all_pages]
        salaries = [int(salary) for salary in salaries if salary]
        average_salary = int(mean(salaries))
        language_vacancies_details = {
            'vacancies_found': vacancies_number,
            'average_salary': average_salary,
            'vacancies_processed': len(salaries),
        }
        result[language] = language_vacancies_details
    return result


def get_vacancies_sj(language, page, token, area, period):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {
        'X-Api-App-Id': token
        }
    payload = {
        'keyword': f'Программист {language}',
        'town': area,
        'period': period, 
        'page': page, 
        'count': 100, 
        } 
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    response = response.json()
    return response


def get_language_vacancies_statistics_sj(languages, token):
    result = {}
    for language in languages:
        vacancies_all_pages = [] 
        page = 0
        while True:
            vacancies = get_vacancies_sj(language, page, token, area='Москва', period=0)
            if vacancies:
                vacancies_all_pages.extend(vacancies['objects'])
                page += 1
                if not vacancies['more']:
                    break
        vacancies_number = vacancies['total']
        salaries = [predict_rub_salary_sj(vacancy) for vacancy in vacancies_all_pages]
        salaries = [int(salary) for salary in salaries if salary]
        average_salary = int(mean(salaries))
        language_vacancies_details = {
            'vacancies_found': vacancies_number,
            'average_salary': average_salary,
            'vacancies_processed': len(salaries),
        }
        result[language] = language_vacancies_details
    return result


def print_table(result, title):
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, details in result.items():
        row = [language, details['vacancies_found'], details['vacancies_processed'], details['average_salary']]
        table_data.append(row)
        row = []
    table = AsciiTable(table_data)
    table.title = title
    print(table.table)



def main():
    load_dotenv()
    token = os.getenv('SUPERJOB_TOKEN')
    languages = ['Python', 'JavaScript', 'Java', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']
    sj_result = get_language_vacancies_statistics_sj(languages, token)
    hh_result = get_language_vacancies_statistics_hh(languages)
    print_table(sj_result, 'SuperJob Moscow')
    print_table(hh_result, 'HeadHunter Moscow')


if __name__ == '__main__':
    main()