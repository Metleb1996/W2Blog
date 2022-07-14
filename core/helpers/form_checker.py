from core.helpers.is_email import is_email

def form_checker(form, rules:dict):
    keys = rules.keys()
    for key in keys:
        if not key in form:
            return False, "{} required!".format(rules[key])
        if len(form[key]) > rules[key]['max']:
            return False, "{} is to long!".format(rules[key])
        if len(form[key]) < rules[key]['min']:
            return False, "{} is to short!".format(rules[key])
        if rules[key]['type'] == "email":
            if not is_email(form[key]):
                return False, "{} not email!".format(form[key])
    return True, None