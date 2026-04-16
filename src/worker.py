import logging
import re
import os
import sys
import time
import datetime
import requests
import boto3
from matplotlib import pyplot as plt
from pathlib import Path
from collections import defaultdict
from dominate import document
from dotenv import load_dotenv
from dominate.tags import *


def check_url(url):

    try:
        start_time = time.time()
        response = requests.get(url, timeout=3.00)
        duration = time.time() - start_time
        return {
            "status": response.status_code,
            "duration": duration,
            "error": None
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
    elif response['status'] != 200 or 'Exception' in response['error']:
        return "ERROR"


def log_result(response, level, url):
    with open(OUTPUT_DIR/"health_check.log", "a") as log_file:
        if response['status'] == None:
            message = f"{datetime.datetime.now():%Y-%m-%d_%H:%M:%S} {level} {url} Status: {response['error']} \n"
        else:
            message = f"{datetime.datetime.now():%Y-%m-%d_%H:%M:%S} {level} {url} Status: {response['status']} Response time: {response['duration']:.2f}s \n"           

        log_file.write(message)
        if level == 'ERROR':
            send_to_cloudwatch(message)


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
    with open(OUTPUT_DIR/'summary_report.txt', "w") as summary_file:

        for url, results in log_data.items():
            stats = calculate_stats(results)
        
            if stats['average_duration'] != None:
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
        folder = Path(OUTPUT_DIR/"plots")
        folder.mkdir(parents=True, exist_ok=True)

        plt.bar(x_tries, y_duration, color='steelblue',
                edgecolor='black', linewidth=1.2)
        plt.xticks(x_tries)
        plt.xlabel("Number of tries")
        plt.ylabel("Time to respond in s")
        plt.title(f"Response time for {url}")
        plt.savefig(OUTPUT_DIR/f'plots/{file_name}.png', dpi=fig.dpi)
        plt.clf()
        plt.close()

        x_tries.clear()
        y_duration.clear()


def clear_files():
    open(OUTPUT_DIR/"health_check.log", "w").close()
    open(OUTPUT_DIR/"summary_report.txt", "w").close()
    open(OUTPUT_DIR/"summary_report.html", "w").close()


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

    with document(title='summary_report') as doc:
        h1(f'URL Monitoring Report for {datetime.datetime.now():%Y-%m-%d_%H:%M:%S}')

        for url, results in log_data.items():
            stats = calculate_stats(results)

            file_name = re.sub(r'[^a-zA-Z0-9\s]', '', url).strip()
            file_name = file_name[5:]
            chart_path = f'plots/{file_name}.png'

            with div(_class='report'):
                p(f'URL: {url}')
                p(f'INFO: {stats['info']}')
                p(f'WARNING: {stats['warning']}')
                p(f'ERROR: {stats['error']}')
                if stats['average_duration'] != None:
                    p(f'Average response time {(stats['average_duration']):.2f}')
                else:
                    p(f'Did not connect')


                if os.path.exists(OUTPUT_DIR/f"{chart_path}"):
                    h2('Response Time Chart')
                    img(src=chart_path)

    with open(OUTPUT_DIR/"summary_report.html", 'w') as summary_report:
        summary_report.write(doc.render())


def upload_to_s3(local_path, s3_path):    
    try:
        s3_client.upload_file(str(local_path), bucket_name, s3_path)
        logging.info(f"Uploaded {local_path} to s3://{bucket_name}/{s3_path}")
    except Exception as e:
        logging.error(f"Failed to upload the file. {e}")

def send_to_cloudwatch(message):
    todaysDate = datetime.datetime.now().strftime("%Y-%m-%d")
    groupName = '/url-monitor/worker'

    try:
        logs_client.create_log_stream(
            logGroupName = groupName,
            logStreamName = todaysDate        
            )
    except logs_client.exceptions.ResourceAlreadyExistsException:
        pass

    logs_client.put_log_events(
        logGroupName= groupName,
        logStreamName= todaysDate,
        logEvents=[
            {
                'timestamp': int(time.time() * 1000),
                'message': message 
            }
        ]
    )
        


                


if __name__ == "__main__":   



    if os.path.exists('.env'):
        load_dotenv('.env') #dzieki temu moge sie dostac do zmiennych w .env


    logs_client = boto3.client(
        "logs",
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name = os.getenv("AWS_REGION")  
    )

    s3_client = boto3.client(
        "s3",
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name = os.getenv("AWS_REGION")        
    )
    bucket_name = os.getenv("S3_BUCKET_NAME")

    logging.basicConfig(level=logging.INFO)  #basicowa konfiguracja logging. bo z defaultu logging nie pokazuje"info"

    OUTPUT_DIR = Path("output")
    OUTPUT_DIR.mkdir(parents=True,exist_ok=True)


    env_interval = os.getenv("INTERVAL")
    if env_interval == None:
        logging.error("NO INTERVAL EXIT")
        sys.exit(1)
    else:
        interval = int(env_interval)

    urls = os.getenv("URLS")
    if urls:
        url_list = urls.split(",")
    elif not urls:   
        logging.error("No URLs provided!")
        sys.exit(1)

    clear_files()

    while True:
        try:
            logging.info("Starting monitoring cycle..")        
            log_data = run_monitor(url_list)
            generate_summary(log_data)
            plot_response_times(log_data)
            generate_html_report(log_data)

            for file_path in OUTPUT_DIR.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(OUTPUT_DIR)
                    upload_to_s3(file_path, str(relative_path))

            logging.info(f"Sleeping for {interval}s")
            time.sleep(interval)            
        except Exception as e:
            logging.error(f"Cycle failed {e}")

    
