import re
import time
import datetime
import requests
from matplotlib import pyplot as plt
from pathlib import Path
from collections import defaultdict
from dominate import document
from dominate.tags import *


url_list = ["https://google.com",
            "https://youtube.com",
            "https://facebook.com",
            "https://twitter.com",]


def check_url(url):

    try:
        start_time = time.time()
        response = requests.get(url, timeout=3.00)
        duration = time.time() - start_time
        return {
            "status": response.status_code,
            "duration": duration,
            "error": "None"
        }

    except requests.exceptions.Timeout as timeout_exception:
        return {
            "status": None,
            "duration": None,
            "error": "Timeout Exception"
        }

    except requests.exceptions.ConnectionError as connection_exception:
        return {
            "status": None,
            "duration": None,
            "error": "Connection Exception"
        }

    except requests.exceptions.RequestException as request_exception:
        return {
            "status": None,
            "duration": None,
            "error": "Request Exception"
        }


def log_level(response):
    if response['status'] == 200 and response['duration'] <= 1:
        return "INFO"
    elif response['status'] == 200 and response['duration'] >= 1:
        return "WARNING"
    elif response["status"] != 200 or 'Exception' in response['error']:
        return "ERROR"


def log_result(response, level, url):
    with open("health_check.log", "a") as log_file:
        if response['status'] == None:
            log_file.write(
                f"{datetime.datetime.now():%Y-%m-%d_%H:%M:%S} {level} {url} Status: {response['error']} \n")
        else:
            log_file.write(
                f"{datetime.datetime.now():%Y-%m-%d_%H:%M:%S} {level} {url} Status: {response['status']} Response time: {response["duration"]:.2f}s \n")


def run_monitor(url_list):
    log_data = defaultdict(list)
    for url in url_list:
        i = 0
        while i < 3:
            response = check_url(url)
            level = log_level(response)
            log_result(response, level, url)
            i += 1
            # time.sleep(5)    #THIS IS COMMENTED FOR TESTING
            log_data[url].append({
                "level": level,
                "duration": response['duration']
            })

    return log_data


def generate_summary(log_data):

    for url, results in log_data.items():
        stats = calculate_stats(results)

        with open("summary_report.txt", "a") as summary_file:
            if stats['average_duration'] != 0:
                summary_file.write(
                    f"URL: {url} \n INFO: {stats['info']} \n WARNING: {stats['warning']} \n ERROR {stats['error']} \n Average response time: {(stats['average_duration']):.2f}s \n\n"
                )
            else:
                summary_file.write(
                    f"URL: {url} \n INFO: {stats['info']} \n WARNING: {stats['warning']} \n ERROR {stats['error']} \n Average response time: None \n\n"
                )

            if stats['error'] >= 1:
                summary_file.write(
                    f"ALERT: Too many errors on {url} \n\n"
                )


def plot_response_times(log_data):

    fig = plt.figure()
    x_tries = []
    y_duration = []

    for url, results in log_data.items():
        i = 1
        for result in results:
            x_tries.append(i)
            if result['duration'] == None:
                y_duration.append(0)
            else:
                y_duration.append(round(result['duration'], 2))
            i += 1

        file_name = re.sub(r'[^a-zA-Z0-9\s]', '', url).strip()
        file_name = file_name[5:]
        folder = Path("plots")
        folder.mkdir(parents=True, exist_ok=True)

        plt.bar(x_tries, y_duration, color='steelblue',
                edgecolor='black', linewidth=1.2)
        plt.xticks(x_tries)
        plt.xlabel("Number of tries")
        plt.ylabel("Time to respond in s")
        plt.title(f"Response time for {url}")
        plt.savefig(f'plots/{file_name}.png', dpi=fig.dpi)
        plt.clf()
        plt.close()

        x_tries.clear()
        y_duration.clear()


def clear_files():
    open("health_check.log", "w").close()
    open("summary_report.txt", "w").close()
    open("summary_report.html", "w").close()


def calculate_stats(results):
    info_count = 0
    warning_count = 0
    error_count = 0
    total_duration = 0
    duration_count = 0

    for result in results:
        level = result['level']
        duration = result['duration']

        if level == 'INFO':
            info_count += 1
        elif level == 'WARNING':
            warning_count += 1
        elif level == 'ERROR':
            error_count += 1

        if duration != None:
            total_duration = total_duration + duration
            duration_count += 1

    average_duration = (
        total_duration / duration_count) if duration_count > 0 else None
    return {
        "info": info_count,
        "warning": warning_count,
        "error": error_count,
        "average_duration": average_duration
    }


def generate_html_report(log_data):
    charts_iterator = 0

    with document(title='summary_report') as doc:
        h1('URL Monitoring Report')

        for url, results in log_data.items():
            stats = calculate_stats(results)

            file_name = re.sub(r'[^a-zA-Z0-9\s]', '', url).strip()
            file_name = file_name[5:]
            chart_path = f'{file_name}.png'

            with div(_class='report'):
                p(f'URL: {url}')
                p(f'INFO: {stats['info']}')
                p(f'WARNING: {stats['warning']}')
                p(f'ERROR: {stats['error']}')
                p(f'Average response time {(stats['average_duration']):.2f}')

                if chart_path:
                    h2('Response Time Chart')
                    img(src=chart_path)
                    charts_iterator += 1

    with open('summary_report.html', 'a') as summary_report:
        summary_report.write(doc.render())


if __name__ == "__main__":
    clear_files()
    log_data = run_monitor(url_list)
    generate_summary(log_data)
    plot_response_times(log_data)
    generate_html_report(log_data)
