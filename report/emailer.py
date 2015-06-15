# check if all imports are needed
import smtplib, email, email.mime.multipart, email.mime.text

def send_email(html, mail_settings):
    # create html email
    emailMsg = email.mime.multipart.MIMEMultipart('alternative')
    emailMsg['Subject'] = "Report"
    emailMsg['From'] = "kkostenkov@gmail.com"
    emailMsg['To'] = ', '.join(mail_settings["address"])
    emailMsg.attach(email.mime.text.MIMEText(html,'html')) # ,"UTF-8" as additional arg
    body = email.mime.text.MIMEText("""HTML report here""")
    emailMsg.attach(body)
    #_send_gmail(emailMsg)
    _send(emailMsg, mail_settings)

def _send(emailMsg, mail_settings):
    smtp = smtplib.SMTP(mail_settings["server"], mail_settings["port"])
    smtp.starttls()
    smtp.login(mail_settings["login"], mail_settings["password"])
    try:
        print("Sending...\n")
        smtp.sendmail('kkostenkov@gmail.com', mail_settings["address"], \
                      emailMsg.as_string())
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused) as ErrorMsg:
        sys.stderr.write("Проблема с отправкой письма. Причина: %s" % ErrorMsg)
        print("Error\n")
        s.quit()
        return
    smtp.quit()
    print("Done")

def _send_gmail(emailMsg, mail_settings):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login('kkostenkov@gmail.com','SECRET')
    try:
        print("sending...\n")
        s.sendmail('kkostenkov@gmail.com',['kiparis87@mail.ru'], emailMsg.as_string())
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused) as ErrorMsg:
        sys.stderr.write("Проблема с отправкой письма. Причина: %s" % ErrorMsg)
        print("Error\n")
        s.quit()
        return
    print("Done.\n")
    s.quit()

def _attach_file(emailMsg):
    filename='table.html'
    fp=open(filename,'rb')
    att = email.mime.application.MIMEApplication(fp.read(),_subtype="html")
    fp.close()
    att.add_header('Content-Disposition','attachment',filename=filename)
    msg.attach(att)
