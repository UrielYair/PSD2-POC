import json

from flask import Flask, request, Response
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
prefix = "/api/psd2/"

err_resp = Response(status=401)
url = "localhost:5002"
api_path = "/api/psd2"
api_url = url + api_path

consent = "1432-psd2-consent"
auth = "123auth567"

consent_create = False
current_req_id = "req_id"
payment_id = 0

headers = {
    "Content-Type": "application/json"
}


@app.route(api_path + "/v1/consents", methods=["POST"])
def post():
    global consent_created, current_req_id, payment_id
    restart_jsons()
    x_req_id = request.headers.get("X-Request-ID")
    accounts = json.loads(request.data).get("access")
    # validating consent
    with open("./res/first_consent.json") as f:
        js = json.load(f)
        if not accounts == js:
            return err_resp
    consent_created = True
    current_req_id = x_req_id
    payment_id = 0
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
                                "name": "LV95LATB000222PSD2001",
                                "_links": {
                                    "balances": {"href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e80f/balances"},
                                    "transactions": {
                                        "href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e80f/transactions"}}
                            },
                            {
                                "resourceId": "3dc3d5b3-7023-4848-9853-f5400a64e81g",
                                "iban": "LV68LATB000222PSD2002",
                                "currency": "EUR",
                                "name": "LV68LATB000222PSD2002",
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


@app.route(api_path + "/v1/accounts/<account>", methods=["GET"])
def get_account(account):
    header = request.headers
    if header.get("X-Request-ID") == current_req_id and header.get("Consent-ID") == consent:
        if account == "LV95LATB000222PSD2001":
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
                                        "balances": {
                                            "href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e80f/balances"},
                                        "transactions": {
                                            "href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e80f/transactions"}}
                                }
                            ]
                    }),
                status=200,
                headers=headers
            )
        elif account == "LV68LATB000222PSD2002":
            headers["X-Request-ID"] = current_req_id
            return Response(
                json.dumps(
                    {
                        "accounts":
                            [
                                {
                                    "resourceId": "3dc3d5b3-7023-4848-9853-f5400a64e81g",
                                    "iban": "LV68LATB000222PSD2002",
                                    "currency": "EUR",
                                    "product": "Fremdwährungskonto",
                                    "cashAccountType": "CurrentAccount",
                                    "name": "US Dollar Account",
                                    "_links": {
                                        "balances": {
                                            "href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e81g/balances"},
                                        "transactions": {
                                            "href": "/v1/accounts/3dc3d5b3-7023-4848-9853-f5400a64e81g/transactions"}}
                                },
                            ]
                    }),
                status=200,
                headers=headers
            )
        else:
            return Response(
                json.dumps(
                    "No account with such iban was found"
                ),
                status=400
            )

    return err_resp


@app.route(api_path + "/v1/funds-confirmations", methods=["POST"])
def get_funds_confirmations():
    header = request.headers
    if header.get("X-Request-ID") == current_req_id and header.get("Consent-ID") == consent:
        headers["X-Request-ID"] = current_req_id
        headers["Content-Type"] = "application/json"
        account = json.loads(request.data).get("account")
        req_iban = account["iban"]
        instructed_amount = json.loads(request.data).get("instructedAmount")
        req_amount = instructed_amount["amount"]
        req_currency = instructed_amount["currency"]
        with open("./res/balances.json") as f:
            balances = json.load(f)
            if req_iban not in balances.keys():
                return err_resp
            cur_amount = balances[req_iban][req_currency]
        if req_amount > cur_amount:
            headers["X-Request-ID"] = current_req_id
            return Response(
                json.dumps(
                    {
                        "fundsAvailable": False
                    }),
                status=200,
                headers=headers
            )
        else:
            headers["X-Request-ID"] = current_req_id
            return Response(
                json.dumps(
                    {
                        "fundsAvailable": True
                    }),
                status=200,
                headers=headers
            )
    return err_resp


@app.route(api_path + "/v1/payments/sepa-credit-transfers", methods=["POST"])
def transfer_sepa_credit():
    header = request.headers
    if header.get("X-Request-ID") == current_req_id and header.get("Consent-ID") == consent \
            and header.get("TPP-Redirect-URI") == "site.com" and header.get("Content-Type") == "application/json":
        tpp_redirect_uri = header.get("TPP-Redirect-URI")
        instructed_amount = json.loads(request.data).get("instructedAmount")
        req_amount = instructed_amount["amount"]
        req_currency = instructed_amount["currency"]
        debtor_account = json.loads(request.data).get("debtorAccount")
        debtor_iban = debtor_account["iban"]
        creditor_name = json.loads(request.data).get("creditorName")
        creditor_account = json.loads(request.data).get("creditorAccount")
        creditor_iban = creditor_account["iban"]
        with open("./res/balances.json", "r+") as f1:
            balances = json.load(f1)
            if debtor_iban not in balances.keys() or creditor_iban not in balances.keys() \
                    or req_currency not in balances[debtor_iban]:
                return err_resp
            global payment_id
            last_payment = payment_id
            payment_id += 1
            cur_amount_debtor = balances[debtor_iban][req_currency]
            if req_amount > cur_amount_debtor:
                headers["X-Request-ID"] = current_req_id
                headers["TPP-Redirect-URI"] = tpp_redirect_uri
                headers["ASPSP-SCA-Approach"] = "REDIRECT"
                temp_payment_id = last_payment
                return Response(
                    json.dumps(
                        {
                            "paymentId": temp_payment_id,
                            "_links": {
                                "scaRedirect": tpp_redirect_uri,
                                "self": "/v1/payments/" + str(temp_payment_id),
                                "status": "Rejected",
                                "scaStatus": "Accepted"
                            }
                        }),
                    status=200,
                    headers=headers
                )
            else:
                temp_payment_id = last_payment
                headers["X-Request-ID"] = current_req_id
                headers["TPP-Redirect-URI"] = tpp_redirect_uri
                headers["ASPSP-SCA-Approach"] = "REDIRECT"
                balances[debtor_iban][req_currency] = cur_amount_debtor - req_amount
                if req_currency not in balances[creditor_iban]:
                    balances[creditor_iban][req_currency] = req_amount
                else:
                    balances[creditor_iban][req_currency] = balances[creditor_iban][req_currency] + req_amount
                with open("./res/payments.json", "r+") as f2:
                    payments = json.load(f2)
                    payments[temp_payment_id] = {
                        "creditor_iban": creditor_iban,
                        "debtor_iban": debtor_iban,
                        "currency": req_currency,
                        "amount": req_amount
                    }
                    f2.seek(0)
                    json.dump(payments, f2, indent=4)
                    f2.truncate()
                    f1.seek(0)
                    json.dump(balances, f1, indent=4)
                return Response(
                    json.dumps(
                        {
                            "paymentId": temp_payment_id,
                            "_links": {
                                "scaRedirect": tpp_redirect_uri,
                                "self": "/v1/payments/" + str(temp_payment_id),
                                "status": "Accepted",
                                "scaStatus": "Accepted"
                            }
                        }),
                    status=200,
                    headers=headers
                )
    return err_resp


def restart_jsons():
    """ Getting json back to default
    """
    with open("./res/payments.json", "w+") as f2:
        data = {}
        json.dump(data, f2, indent=4)

    with open("./res/balances.json", "w+") as f2:
        data = {
            "LV95LATB000222PSD2001": {"EUR": 500},
            "LV68LATB000222PSD2003": {"EUR": 200}
        }
        json.dump(data, f2, indent=4)


if __name__ == '__main__':
    app.run(port=5002)
