import os
from statistics import mean 

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_rub_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        salary = salary_from*1.2
    elif not salary_from and salary_to:
        salary = salary_to*0.8
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
    if vacancy['payment_from'] == 0 and vacancy['payment_to'] == 0 or vacancy['currency'] != 'rub':
        salary = None
    else:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        salary = predict_rub_salary(salary_from, salary_to)
    return salary


def get_vacancies(language, area, period, page):
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
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
        language_vacancies_details = {}
        vacancies_one_page = get_vacancies(language, 1, 30, 0)
        vacancies_number = vacancies_one_page['found']
        pages_number = vacancies_one_page['pages']
        language_vacancies_details['vacancies_found'] = vacancies_number
        pages = [] 
        for page in range(0, pages_number):
            vacancies = get_vacancies(language, 1, 30, page)
            pages.append(vacancies['items'])
        vacancies_all_pages = []
        for page in pages: 
            for vacancy in page:
                vacancies_all_pages.append(vacancy)
        salaries = [predict_rub_salary_hh(vacancy) for vacancy in vacancies_all_pages]
        salaries = [int(salary) for salary in salaries if salary is not None]
        average_salary = int(mean(salaries))
        language_vacancies_details['average_salary'] = average_salary
        language_vacancies_details['vacancies_processed'] = len(salaries)
        result[language] = language_vacancies_details
    return result


def get_vacancies_sj(language, area, period, page, token):
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
        language_vacancies_details = {}
        vacancies_one_page = get_vacancies_sj(language, 'Москва', 0, 0, token)
        vacancies_number = vacancies_one_page['total']
        pages_number = round(vacancies_number/100)
        if pages_number != 0:
            language_vacancies_details['vacancies_found'] = vacancies_number
            pages = [] 
            for page in range(0, pages_number):
                vacancies = get_vacancies_sj(language, 'Москва', 0, page, token)
                pages.append(vacancies['objects'])
            vacancies_all_pages = []
            for page in pages: 
                for vacancy in page:
                    vacancies_all_pages.append(vacancy)
            salaries = [predict_rub_salary_sj(vacancy) for vacancy in vacancies_all_pages]
            salaries = [int(salary) for salary in salaries if salary is not None]
            average_salary = int(mean(salaries))
            language_vacancies_details['average_salary'] = average_salary
            language_vacancies_details['vacancies_processed'] = len(salaries)
            result[language] = language_vacancies_details
    return result


def main():
    load_dotenv()
    token = os.getenv('SUPERJOB_TOKEN')
    languages = ['Python', 'JavaScript', 'Java', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']
    sj_result = get_language_vacancies_statistics_sj(languages, token)
    hh_result = get_language_vacancies_statistics_hh(languages)

    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, details in sj_result.items():
        row = [language, details['vacancies_found'], details['vacancies_processed'], details['average_salary']]
        table_data.append(row)
        row = []
    table = AsciiTable(table_data)
    table.title = 'SuperJob Moscow'
    print(table.table)
    print()

    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language, details in hh_result.items():
        row = [language, details['vacancies_found'], details['vacancies_processed'], details['average_salary']]
        table_data.append(row)
        row = []
    table = AsciiTable(table_data)
    table.title = 'HeadHunter Moscow'
    print(table.table)

if __name__ == '__main__':
    main()