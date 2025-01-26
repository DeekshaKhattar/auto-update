import psutil
import platform
import os
import time
import subprocess
import re
import statistics
import win32serviceutil
import win32service
import requests
import json
import base64
import socket
import ssl

class SystemHealthChecker:
    def __init__(self, api_url, data_to_encrypt, key):
        self.api_url = api_url
        self.data_to_encrypt = data_to_encrypt
        self.key = key

    def xor_encrypt(self, data, key):
        encrypted = ''
        for i in range(len(data)):
            encrypted += chr(ord(data[i]) ^ ord(key[i % len(key)]))
        return base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')

    def check_service_status(self, service_name):
        try:
            # Check if the service is running
            status = win32serviceutil.QueryServiceStatus(service_name)[1]
            return status == win32service.SERVICE_RUNNING
        except Exception:
            return False  # Service is not running or an error occurred

    def check_critical_services(self):
        services = [
            "autoUpdateService", "Spooler"
        ]
        total_services = len(services)
        service_lis=[]
        service_dic={}
        for service in services:
            try:
                service_lis.append(self.check_service_status(service))
                service_dic[service]=self.check_service_status(service)
            except Exception as e:
                service_lis.append(False)
                service_dic[service]=False
                print(f"Error checking status for {service}: {e}")

        services_up = sum(service_lis)
        percentage_up = round((services_up / total_services) * 100, 2)
        return round(percentage_up, 2),service_dic

    def check_disk_space(self):
        disk_usage = psutil.disk_usage('/')
        return disk_usage.percent

    def check_memory_usage(self):
        memory = psutil.virtual_memory()
        return memory.percent

    def check_cpu_usage(self):
        cpu_percent = psutil.cpu_percent(interval=1)
        return cpu_percent

    # def check_system_uptime(self):
    #     uptime_seconds = time.time() - psutil.boot_time()
    #     uptime_hours = round((uptime_seconds / 3600), 2)
    #     return uptime_hours

    def check_page_memory(self):
        try:
            virtual_memory_info = subprocess.run('systeminfo | find "Virtual Memory"', stdout=subprocess.PIPE, text=True, shell=True)
            vmi = virtual_memory_info.stdout.strip()

            # Extract values from virtual memory information
            values = self.extract_values(vmi)
            if values:
                max_size, _, in_use_size = values

                # Calculate consolidated percentage
                percentage_used = self.calculate_percentage(max_size, in_use_size)

                return round(percentage_used, 2)
            else:
                return "Error: Unable to extract values from virtual memory information."
        except Exception as e:
            return f"Error checking page memory: {str(e)}"

    def extract_values(self, data):
        max_size_match = re.search(r'Max Size:\s+(\d+)', data)
        available_size_match = re.search(r'Available:\s+(\d+)', data)
        in_use_size_match = re.search(r'In Use:\s+(\d+)', data)

        if max_size_match and available_size_match and in_use_size_match:
            max_size = int(max_size_match.group(1))
            available_size = int(available_size_match.group(1))
            in_use_size = int(in_use_size_match.group(1))

            return max_size, available_size, in_use_size

        return None

    def calculate_percentage(self, max_size, in_use_size):
        if max_size > 0:
            percentage_used = (in_use_size / max_size) * 100
            return percentage_used
        return None

    def check_hardware_health(self):
        try:
            if platform.system() == "Windows":
                result = subprocess.run(["wmic", "diskdrive", "get", "status"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout_lines = result.stdout.split('\n')
                status_line = stdout_lines[2].strip()
                return f"{status_line}"
            else:
                return "Hardware health check not supported on this platform."
        except Exception as e:
            return f"Error checking hardware health: {str(e)}"

    def make_sentiment_entry(self, cpu, page_mem, ciritical_service,ciritical_services_details ,latncy):
        try:
            auth_key = self.xor_encrypt(self.data_to_encrypt, self.key)
            payload = json.dumps({
                "hostname": socket.gethostname(),
                # "mac_address": gma(),
                # "ram": float(ram),
                "cpu": float(cpu),
                # "hardisk": float(hardisk),
                "page_memory": float(page_mem),
                "critical_services": float(ciritical_service),
                "critical_services_details":ciritical_services_details,
                "latency": float(latncy),
                # "uptime": float(uptm)
            })
            headers = {
                'Authorization': auth_key,
                'Content-Type': 'application/json'
            }
            response = requests.post(self.api_url, headers=headers, data=payload, verify=ssl.CERT_NONE)
            print(response.text)
        except Exception as e:
            print(f"Can not make a sentiment entry due to: {e}")
        return True

    def run_health_check(self):
        print("System Health Check on", platform.system(), platform.release())

        disk_space = self.check_disk_space()
        memory_usage = self.check_memory_usage()
        cpu_usage = self.check_cpu_usage()
        # uptime = self.check_system_uptime()
        hardware_health = self.check_hardware_health()  # Check hardware health
        page_memory = self.check_page_memory()
        latency = self.check_latency()
        ciritical_services,ciritical_services_details = self.check_critical_services()

        create_sentiment_entry = self.make_sentiment_entry(memory_usage, cpu_usage,
                disk_space, ciritical_services,ciritical_services_details, latency)

        # print("RAM:", memory_usage, "%")
        print("CPU:", cpu_usage, "%")
        print("HDD:", disk_space, "%")
        print("Page Memory:", page_memory)
        # print("Event Logs:", event_logs) # extra data
        # print("Hardware Health:", hardware_health) # extra data
        print("Critical Services", ciritical_services)
        print("Latency", latency)
        # print("Uptime:", uptime, "hours")

if __name__ == '__main__':
    api_url = "http://10.9.1.68:8000/portal/api/v1/sentiment/"
    data_to_encrypt = "PCGC1bUF9XsZmYS5Zg1tGJVSrevQi5xtfeR4hnsCeR6U3GS95K"
    key = ".Gq0JGP`l&W`t+iLy4Td%-6v6%]tw*bnvn[-`&2kz5Be~2SnI"

    health_checker = SystemHealthChecker(api_url, data_to_encrypt, key)
    health_checker.run_health_check()