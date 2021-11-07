import requests
import os
from statistics import mean 
from dotenv import load_dotenv
from terminaltables import AsciiTable

load_dotenv()
token = os.getenv('SUPERJOB_TOKEN')


def predict_rub_salary(salary_from, salary_to):
    if salary_from and not salary_to:
        salary = salary_from*1.2
    elif not salary_from and salary_to:
        salary = salary_to*0.8
    else:
        salary = (salary_from + salary_to) / 2
    return salary
    

def predict_rub_salary_hh(vacancy):
    salary_delta = vacancy['salary']  #salary_delta = {'from': None, 'to': 160000, 'currency': 'RUR', 'gross': False}
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
    #headers = {'User-Agent: MyApp/1.0 (annfike@gmail.com)'} #headers=headers
    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'accept': '*/*'
    }
    payload = {'text': f'Программист {language}',
               'area': area,
               'period': period,
               'page': page, 
               } #params=payload
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    response = response.json()
    #vacancies = response['items']
    return response



#print(get_vacancies('Программист Python', 1, 30, 10))
#get_vacancies('Программист Python', 1, 30)


languages = ['Python', 'JavaScript', 'Java', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go']
#languages = ['Python', 'JavaScript']

def get_language_vacancies_statistics_hh(languages):
    result = {}
    for language in languages:
        language_vacancies_details = {}
        vacancies_one_page = get_vacancies(language, 1, 30, 0)
        vacancies_number = vacancies_one_page['found']
        pages_number = vacancies_one_page['pages']
        language_vacancies_details['vacancies_found'] = vacancies_number
        pages = [] #вакансии со всех страниц, каждая страница - отдельный список (в общем)
        for page in range(0, pages_number):
            vacancies = get_vacancies(language, 1, 30, page)
            pages.append(vacancies['items'])
        vacancies_all_pages = []
        for page in pages: # вытаскивам вакансии из списков каждого дня, добавляем в один общий список
            for vacancy in page:
                vacancies_all_pages.append(vacancy)
        salaries = [predict_rub_salary_hh(vacancy) for vacancy in vacancies_all_pages]
        salaries = [int(salary) for salary in salaries if salary != None]
        average_salary = int(mean(salaries))
        language_vacancies_details['average_salary'] = average_salary
        language_vacancies_details['vacancies_processed'] = len(salaries)
        result[language] = language_vacancies_details
    return result


def get_vacancies_sj(language, area, period, page):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {
        'X-Api-App-Id': 'v3.r.12470833.549ffb13b4b982fe0e79f1e177cecfce4caff978.74a2abe65baf34f5c0e6d1c242de9262f71d7288'
        }
    payload = {'keyword': f'Программист {language}',
                'town': area,
                'period': period, 
                'page': page, 
                'count': 100, 
                } #params=payload
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    response = response.json()
    #vacancies = response['objects']
    return response

#print(get_vacancies_sj('PHP', 'Moscow', 0, 0))


def get_language_vacancies_statistics_sj(languages):
    result = {}
    for language in languages:
        language_vacancies_details = {}
        vacancies_one_page = get_vacancies_sj(language, 'Москва', 0, 0)
        vacancies_number = vacancies_one_page['total']
        pages_number = round(vacancies_number/100)
        if pages_number != 0:
            language_vacancies_details['vacancies_found'] = vacancies_number
            pages = [] #вакансии со всех страниц, каждая страница - отдельный список (в общем)
            for page in range(0, pages_number):
                vacancies = get_vacancies_sj(language, 'Москва', 0, page)
                pages.append(vacancies['objects'])
            vacancies_all_pages = []
            for page in pages: # вытаскивам вакансии из списков каждого дня, добавляем в один общий список
                for vacancy in page:
                    vacancies_all_pages.append(vacancy)
            salaries = [predict_rub_salary_sj(vacancy) for vacancy in vacancies_all_pages]
            salaries = [int(salary) for salary in salaries if salary != None]
            average_salary = int(mean(salaries))
            language_vacancies_details['average_salary'] = average_salary
            language_vacancies_details['vacancies_processed'] = len(salaries)
            result[language] = language_vacancies_details
    return result

sj_result = get_language_vacancies_statistics_sj(languages)
hh_result = get_language_vacancies_statistics_hh(languages)

print(sj_result)
print(hh_result)

table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
for k,v in sj_result.items():
    row = [k, v['vacancies_found'], v['vacancies_processed'], v['average_salary']]
    table_data.append(row)
    row = []

print(table_data)

table = AsciiTable(table_data)
table.title = 'SuperJob Moscow'
print(table.table)

table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
for k,v in hh_result.items():
    row = [k, v['vacancies_found'], v['vacancies_processed'], v['average_salary']]
    table_data.append(row)
    row = []

table = AsciiTable(table_data)
table.title = 'HeadHunter Moscow'
print(table.table)

if __name__ == '__main__':
    main()