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
        return None
    else:
        salary_from = salary_delta['from']
        salary_to = salary_delta['to']
        salary = predict_rub_salary(salary_from, salary_to)
    return salary


def predict_rub_salary_sj(vacancy):
    if not vacancy['payment_from'] and not vacancy['payment_to'] \
                                   or vacancy['currency'] != 'rub':
        return None
    else:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        salary = predict_rub_salary(salary_from, salary_to)
    return salary


def get_vacancies_hh(language, page, area, period):
    url = 'https://api.hh.ru/vacancies'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
        AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/80.0.3987.149 Safari/537.36',
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


def get_language_vacancies_statistics_hh(language):
    language_vacancies = []
    page = 0
    while True:
        vacancies = get_vacancies_hh(language, page, area=1, period=3)
        if vacancies:
            pages_number = vacancies['pages']
            language_vacancies.extend(vacancies['items'])
            page += 1
            if page > pages_number:
                break
    vacancies_number = vacancies['found']
    salaries = [predict_rub_salary_hh(vacancy) for vacancy in language_vacancies]
    salaries = [int(salary) for salary in salaries if salary]
    average_salary = int(mean(salaries))
    vacancies_processed = len(salaries)
    return vacancies_number, average_salary, vacancies_processed


def get_languages_vacancies_statistics_hh(languages):
    languages_vacancies_statistics = {}
    for language in languages:
        (vacancies_number,
        average_salary,
        vacancies_processed) = get_language_vacancies_statistics_hh(language)
        language_vacancies_details = {
            'vacancies_found': vacancies_number,
            'average_salary': average_salary,
            'vacancies_processed': vacancies_processed,
        }
        languages_vacancies_statistics[language] = language_vacancies_details
    return languages_vacancies_statistics


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


def get_language_vacancies_statistics_sj(language, token):
    language_vacancies = []
    page = 0
    while True:
        vacancies = get_vacancies_sj(language, page, token, area='Москва', period=0)
        if vacancies:
            language_vacancies.extend(vacancies['objects'])
            page += 1
            if not vacancies['more']:
                break
    vacancies_number = vacancies['total']
    salaries = [predict_rub_salary_sj(vacancy) for vacancy in language_vacancies]
    salaries = [int(salary) for salary in salaries if salary]
    average_salary = int(mean(salaries))
    vacancies_processed = len(salaries)
    return vacancies_number, average_salary, vacancies_processed


def get_languages_vacancies_statistics_sj(languages, token):
    languages_vacancies_statistics = {}
    for language in languages:
        (vacancies_number,
        average_salary,
        vacancies_processed) = get_language_vacancies_statistics_sj(language, token)
        language_vacancies_details = {
            'vacancies_found': vacancies_number,
            'average_salary': average_salary,
            'vacancies_processed': vacancies_processed,
        }
        languages_vacancies_statistics[language] = language_vacancies_details
    return languages_vacancies_statistics


def get_table(result, title):
    table = [
        ['Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата']
        ]
    for language, details in result.items():
        row = [language,
            details['vacancies_found'],
            details['vacancies_processed'],
            details['average_salary']
            ]
        table.append(row)
        row = []
    table = AsciiTable(table)
    table.title = title
    return table.table


def main():
    load_dotenv()
    token = os.getenv('SUPERJOB_TOKEN')
    languages = ['Python',
        'JavaScript',
        'Java', 'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go']
    sj_result = get_languages_vacancies_statistics_sj(languages, token)
    hh_result = get_languages_vacancies_statistics_hh(languages)
    print(get_table(sj_result, 'SuperJob Moscow'))
    print(get_table(hh_result, 'HeadHunter Moscow'))


if __name__ == '__main__':
    main()