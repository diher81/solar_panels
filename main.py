import os
import smtplib
from email.message import EmailMessage

import requests
from statistics import median
from dotenv import load_dotenv

load_dotenv()

SITE_ID = os.getenv("SE_SITE_ID")
API_KEY = os.getenv("SE_API_KEY")

print("SITE_ID =", SITE_ID)
print("API_KEY present =", API_KEY is not None)

SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_TO = os.environ["MAIL_TO"]

# def send_mail(subject, body):
#     msg = EmailMessage()
#     msg["Subject"] = subject
#     msg["From"] = MAIL_FROM
#     msg["To"] = MAIL_TO
#     msg.set_content(body)
#
#     with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
#         smtp.starttls()
#         smtp.login(SMTP_USER, SMTP_PASSWORD)
#         smtp.send_message(msg)

def get_optimizer_data():
    url = (
        f"https://monitoringapi.solaredge.com/"
        f"site/{SITE_ID}/equipment/optimizers"
        f"?api_key={API_KEY}"
    )

    response = requests.get(url, timeout = 30)
    response.raise_for_status()

    return response.json()


def find_anomalies(data):
    """
    Pas dit aan op basis van jouw daadwerkelijke JSON.
    """

    optimizers = []

    for item in data["reporters"]:
        power = item["lastReportedPower"]

        optimizers.append(
            {
                "id": item["serialNumber"],
                "power": power,
            }
        )

    powers = [x["power"] for x in optimizers if x["power"] > 0]

    if len(powers) < 3:
        return []

    baseline = median(powers)

    anomalies = []

    for opt in optimizers:
        if opt["power"] < baseline * 0.2:
            anomalies.append(opt)

    return anomalies


def main():
    data = get_optimizer_data()

    anomalies = find_anomalies(data)

    if anomalies:
        body = "\n".join(
            f"{a['id']} -> {a['power']} W"
            for a in anomalies
        )

        # send_mail(
        #     "SolarEdge afwijking gedetecteerd",
        #     body,
        # )


if __name__ == "__main__":
    main()