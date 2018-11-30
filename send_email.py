from config import email_conf, contri_email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


def send_email(sent_conf, file_path=None):
    print('Start to send email...')
    server = smtplib.SMTP(email_conf['server'])
    # 判断是否存在 邮件抄送地址
    if sent_conf['cc_addrs']:
        email_list = sent_conf['to_addrs'].split(',') + sent_conf['cc_addrs'].split(',')
    else:
        email_list = sent_conf['to_addrs'].split(',')

    msg = MIMEMultipart()
    msg['From'] = email_conf['address']
    msg['To'] = sent_conf['to_addrs']
    msg['Cc'] = sent_conf['cc_addrs']
    msg['Subject'] = "[SensorsData] %s " % sent_conf['subject']
    msg.attach(MIMEText(sent_conf['body_content'], 'html'))

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(file_path, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename={}'.format(file_path.split('/')[-1]))
    msg.attach(part)
    
    server.login(email_conf['address'], email_conf['password'])
    server.sendmail(email_conf['address'], email_list, msg.as_string())
    
    server.quit()
    print('Email has sent, plz check.')
    

if __name__ == '__main__':
    send_email(contri_email, '/Users/GavinXue/Downloads/pandas_conditional.xlsx')