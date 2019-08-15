import json

from flask import Flask, request, Response
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
prefix = "/api/psd2/"

err_resp = Response(status=401)
url = "localhost:5002"
api_path = "/api/psd2"s
api_url = url + api_path

consent = "1432-psd2-consent"
auth = "123auth567"

consent_create = False
current_req_id = "req_id"

headers = {
    "Content-Type": "application/json"
}


@app.route(api_path + "/v1/consents", methods=["POST"])
def post():
    global consent_created, current_req_id
    x_req_id = request.headers.get("X-Request-ID")
    accounts = json.loads(request.data).get("access")
    # validating consent
    with open("./res/first_consent.json") as f:
        js = json.load(f)
        if not accounts == js:
            return err_resp
    consent_created = True
    current_req_id = x_req_id
    return Response(
        json.dumps(
            {
                "consentStatus": "received",
                "consentId": consent,
                "_links":
                    {
                        "scaRedirect": {"href": api_url},
                        "status": {"href": f"/v1/consents/{consent}/status"},
                        "scaStatus": {"href": f"/v1/consents/{consent}/authorisations/{auth}"}
                    }
            }),
        status=201,
        headers={
            "X-Request-ID": x_req_id,
            "Content-Type": "application/json",
            "ASPSP-SCA-Approach": "REDIRECT"
        },
    )


@app.route(f"{api_path}/v1/consents/{consent}/status", methods=["GET"])
def consent_status():
    if request.headers.get("X-Request-ID") != current_req_id or not consent_created:
        return err_resp
    return Response(
        json.dumps({"consentStatus": "valid"}),
        headers={
            "X-Request-ID": current_req_id,
            "Content-Type": "application/json"
        },
        status=201
    )


@app.route(f"{api_path}/v1/consents/{consent}/authorisations/{auth}", methods=["GET"])
def get_authorization():
    if request.headers.get("X-Request-ID") != current_req_id and not consent_create:
        return err_resp
    return Response(
        json.dumps({
            "access":
                {
                    "balances":
                        [
                            {"iban": "LV95LATB000222PSD2001"}
                        ],
                    "transactions":
                        [
                            {"iban": "LV68LATB000222PSD2002"},
                            {"pan": "123456xxxxxx3457"}
                        ]
                },
            "recurringIndicator": False,
            "validUntil": "2017-11-01",
            "frequencyPerDay": "4",
            "consentStatus": "valid",
            "_links": {"account": {"href": "/api/psd2/v1/accounts"}}
        }),
        status=200,
        headers={
            "X-Request-ID": current_req_id,
            "Content-Type": "application/json"
        }
    )


@app.route(api_path + "/v1/accounts", methods=["GET"])
def get_accounts():
    header = request.headers
    if header.get("X-Request-ID") == current_req_id and header.get("Consent-ID") == consent:
        headers["X-Request-ID"] = current_req_id
        return Response(
            json.dumps(
                {
                    "accounts":
                        [
                            {
                                "resourceId": "3dc3d5b3-7023-4848-9853-f5400a64e80f",
                                "iban": "LV95LATB000222PSD2001",
                                "currency": "EUR",
                                "product": "Girokonto",
                                "cashAccountType": "CurrentAccount",
                                "name": "Main Account",
                                "_links": {
                                    "balances": {"href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e80f/balances"},
                                    "transactions": {
                                        "href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e80f/transactions"}}
                            },
                            {
                                "resourceId": "3dc3d5b3-7023-4848-9853-f5400a64e81g",
                                "iban": "LV68LATB000222PSD2002",
                                "currency": "EUR",
                                "product": "Fremdwährungskonto",
                                "cashAccountType": "CurrentAccount",
                                "name": "US Dollar Account",
                                "_links": {
                                    "balances": {"href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e81g/balances"},
                                    "transactions": {
                                        "href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e81g/transactions"}}
                            }
                        ]
                }),
            status=200,
            headers=headers
        )
    return err_resp

# TODO accounts
# TODO sepa-credit-payments
# TODO funds-confirmation


if __name__ == '__main__':
    app.run(port=5002)
