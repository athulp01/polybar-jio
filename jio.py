#!/usr/bin/env python3
import requests, pickle, json, subprocess, os

class Jio:
    def __init__(self, number):
        self.number = number
        self.hdr = {"User-Agent": 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0','Accept': 'application/json, text/javascript, */*; q=0.01' , 'Accept-Language': 'en','Content-Type': 'application/json', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache ', 'Connection': 'keep-alive'}
        self.session = requests.Session()
    
    def send_otp(self):
        auth_url = "https://www.jio.com/api/jio-authenticate-service/authenticate/authJsonData"
        auth_req = self.session.get(auth_url, headers=self.hdr, timeout=2)
        
        otp_url = "https://www.jio.com/JioWebService/rest/loginService/sendOtp"
        otp_payload = {"mobileNumber":self.number,"loginFlowType":"MOBILE","alternateNumber":""}
        otp_req = self.session.post(otp_url, headers=self.hdr, timeout=2, json=otp_payload)
        try:
            otp_req.raise_for_status()
        except requests.exceptions.HTTPError:
            print("send otp error")
            exit(0)
    
    def verify_otp(self, otp):
        url = 'https://www.jio.com/JioWebService/rest/loginService/validateOtp'
        payload = {"otp":otp}
        req = self.session.post(url, headers=self.hdr, timeout=2, json=payload)
        if req.ok:
            self.session.get("https://www.jio.com/api/jio-authenticate-service/authenticate/authJsonData", headers=self.hdr, timeout=2)
            self.session.get("https://www.jio.com/dashboard/", headers=self.hdr)
            self.session.get("https://www.jio.com/api/jio-dashboard-service/dashboard/main", headers=self.hdr)
            self.session.get("https://www.jio.com/api/jio-authenticate-service/authenticate/authJsonData", headers=self.hdr, timeout=2)
        else:
            print("otp error")
            exit(1)
    
    def get_balance(self):
        url = "https://www.jio.com/api/jio-plan-service/plans/balance"
        req = self.session.get(url, headers=self.hdr, timeout=2)
        data = json.loads(req.text)
        print(data["dataBucket"]["balance"] + "/" + data["dataBucket"]["total"])
        return data

    def save_session(self, filename):
        with open(filename, "wb+") as f:
            pickle.dump(self.session.cookies, f)

    def load_session(self, filename):
        try:
            with open(filename, "rb") as f:
                self.session.cookies.update(pickle.load(f))
        except FileNotFoundError:
            return 


if __name__ == "__main__":
    jio = Jio("replace this with your number")
    jio.load_session("cookie")
    # jio.get_balance()
    try:
        jio.get_balance()
    except KeyError:
        jio.send_otp()
        proc = subprocess.Popen(["dmenu", "-p", "Enter OTP"], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
        jio.verify_otp(proc.stdout.read().decode('utf-8').strip())
        jio.get_balance()
        jio.save_session("cookie")
