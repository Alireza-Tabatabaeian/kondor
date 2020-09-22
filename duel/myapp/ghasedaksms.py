import ghasedak

API_KEY = "50287c9af67a248bbd0a703b6438fbb88a23263fb80cef041505236b15352c65"


def send_verification(mob, template, code):
    sms = ghasedak.Ghasedak(API_KEY)
    sms.verification({"receptor": mob, "type": 1, "template": template, "param1": code.__str__()})
