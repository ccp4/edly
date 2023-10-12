# Import smtplib for the actual sending function
import smtplib,ssl,sys,os,re
import argparse
from subprocess import Popen
from email.message import EmailMessage
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

parser = argparse.ArgumentParser()
parser.add_argument('-l','--local'  ,action='store_true',default=False)
parser.add_argument('-f','--folder' ,default='')
args = parser.parse_args()

test=args.local
folder=args.folder


#### get email info
with open('mail.txt','r') as f:
    mail_info = dict([tuple(re.sub(' +',' ',l.strip()).split(' = ')) for l in f.readlines() if '=' in l])
    password       = mail_info['password']
    sender_email   = mail_info['sender_email']
    receiver_email = mail_info['receiver_email']



#### Create email
msg = MIMEMultipart()
msg['Subject'] = f'test report '
msg['From'] = sender_email
msg['To']   = receiver_email

#### Body
body="Please find the test reports attached : \n\n"
with open(os.path.join(folder,'run_tests.log'),'r') as f:
    body+=''.join(f.readlines())
msg.attach(MIMEText(body, "plain"))

#### attachments
for filename in ['server.log','pytest.log','report.html','console.log']:
    with open(os.path.join(folder,filename), "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    msg.attach(part)



try:
    if test:
        #####local server
        #python -m smtpd -c DebuggingServer -n localhost:1025
        # p = Popen("python -m smtpd -c DebuggingServer -n localhost:1025",sell=True)
        # p.communicate()
        server = smtplib.SMTP('localhost:1025')
        server.send_message(msg)
    else:
        # Try to log in to server and send email
        smtp_server = "smtp.gmail.com"
        port = 587  # For starttls
        context = ssl.create_default_context()
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        # password+=' '
        # print("pwd = '%s'" %password)
        server.login(sender_email, password)
        out = server.sendmail(sender_email, receiver_email, msg.as_string())
        if out:print(out)


    # TODO: Send email here
except Exception as e:
    # Print any error messages to stdout
    print(e)
finally:
    if 'quit' in server.__dict__:
        server.quit()
