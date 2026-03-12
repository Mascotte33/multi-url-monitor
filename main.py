from collections import defaultdict
import time
import datetime
import requests
import re

url_list = ["https://google.com",
            "https://httpstat.us/200",
            "https://httpstat.us/500",
            "https://10.255.255.1"]


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
    if response["status"] == 200 and response["duration"] <= 1:
        return "INFO"
    elif response["status"] == 200 and response["duration"] >= 1:
        return "WARNING"
    elif response["status"] != 200 or "Exception" in response["error"]:
        return "ERROR"


def log_result(response, level, url):
    with open("health_check.log", "a") as log_file:
        if response["status"] == None:
            log_file.write(
                f"{datetime.datetime.now():%Y-%m-%d_%H:%M:%S} {level} {url} Status: {response["error"]} \n")
        else:
            log_file.write(
                f"{datetime.datetime.now():%Y-%m-%d_%H:%M:%S} {level} {url} Status: {response["status"]} Response time: {response["duration"]:.2f}s \n")


def run_monitor(url_list):
    log_data = defaultdict(list)
    for url in url_list:
        i = 0
        while i < 3:
            response = check_url(url)
            level = log_level(response)
            log_result(response, level, url)
            i += 1
            time.sleep(5)
            log_data[url].append({
                "level": level,
                "duration": response["duration"]
            })

    return log_data


def generate_summary(log_data):
    for url, results in log_data.items():
        info_count = 0
        warning_count = 0
        error_count = 0
        total_duration = 0
        duration_count = 0

        for result in results:
            level = result["level"]
            duration = result["duration"]

            if level == "INFO":
                info_count += 1
            elif level == "WARNING":
                warning_count += 1
            elif level == "ERROR":
                error_count += 1

            if duration != None:
                total_duration = total_duration + duration
                duration_count += 1

        with open("summary_report.txt", "a") as summary_file:
            if total_duration != 0:
                summary_file.write(
                    f"URL: {url} \n INFO: {info_count} \n WARNING: {warning_count} \n ERROR {error_count} \n Avarage response time: {(total_duration / duration_count):.2f}s \n\n"
                )
            else:
                summary_file.write(
                    f"URL: {url} \n INFO: {info_count} \n WARNING: {warning_count} \n ERROR {error_count} \n Avarage response time: None \n\n"
                )

            if error_count >= 1:
                summary_file.write(
                    f"ALERT: Too many errors on {url} \n\n"
                )


if __name__ == "__main__":
    log_data = run_monitor(url_list)
    generate_summary(log_data)
