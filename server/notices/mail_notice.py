import smtplib
import yaml

with open("notices/smtp_config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def send_email(host, status, check_dict):
    smtp_host = config['smtp_host']
    to_addr = "me@emptylips.ru"
    from_addr = "Mornlight <me@emptylips.ru>"
    subject = "Host {}, event {}".format(host, status)
    message_body = "Hey, admin! Host {}, status {} \n".format(host, status)
    for item in check_dict:
        message_body += item + ' - ' + check_dict[item]['status'] + ' - ' + \
                        str(check_dict[item]['value']) + '\n'
    BODY = "\r\n".join((
        "From: %s" % from_addr,
        "To: %s" % to_addr,
        "Subject: %s" % subject,
        "",
        message_body
    ))

    server = smtplib.SMTP_SSL(smtp_host, 465)
    server.login('me@emptylips.ru', config['smtp_pass'])
    server.sendmail(from_addr, [to_addr], BODY)
    server.quit()


if __name__ == "__main__":
    pass
