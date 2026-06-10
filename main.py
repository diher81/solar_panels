import os
import requests
from statistics import median

SITE_ID = os.environ["SE_SITE_ID"]
API_KEY = os.environ["SE_API_KEY"]

SMTP_HOST = os.environ["SMTP_HOST"]
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

MAIL_FROM = os.environ["MAIL_FROM"]
MAIL_TO = os.environ["MAIL_TO"]

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