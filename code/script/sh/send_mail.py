# 邮件发送
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

import configparser

#  实例化configParser对象
config = configparser.ConfigParser()
# -read读取ini文件
config.read('../../email_config.ini')
# -options(section)得到该section的所有option
email_config=dict(config.items('email'))
smtp_config=dict(config.items('smtp'))

fromaddr = email_config['sender']
username=email_config['username']
password = email_config['password']
toaddrs = email_config['receiver'].split(';')


content = '请解压附件查看报表'
textApart = MIMEText(content)

zipFile = 'report_'+sys.argv[1] +'.zip'
zipApart = MIMEApplication(open(zipFile, 'rb').read())
zipApart.add_header('Content-Disposition', 'attachment', filename=zipFile)

m = MIMEMultipart()
m.attach(textApart)
m.attach(zipApart)
m['Subject'] = sys.argv[1]+'联通周报表'

try:
    server = smtplib.SMTP(smtp_config['host'],port=smtp_config['port'])
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, m.as_string())
    server.quit()
except smtplib.SMTPException as e:
    print('error:',e) #打印错误
    exit(1)


print('success')