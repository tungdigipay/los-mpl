import smtplib, configparser, ssl
import email
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate, formataddr

config = configparser.ConfigParser()
config.read('configs.ini')
config = config['SMTP']

port = 465  # For SSL 
smtp_server = config['smtp_host']
sender_email = config['smtp_user']
password = config['smtp_pass']


def process(receiver_email, name, file):
   context = ssl.create_default_context()
   message = __body({
      "name": name
   })

   msg = MIMEMultipart()
   msg['From'] = formataddr(('MFast Pay Later', 'no-reply@mfast.vn'))
   msg['To'] = receiver_email
   msg['Date'] = formatdate(localtime=True)
   msg['Subject'] = "Thông báo về hợp đồng mua hàng trả sau"
   msg.attach(MIMEText(message, 'html'))

   with open(file, "rb") as fil:
      part = MIMEApplication(
            fil.read(),
            Name=basename(file)
      )
      # After the file is closed
      part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file)
      msg.attach(part)
   with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
      server.login(sender_email, password)
      server.sendmail("no-reply@mfast.vn", receiver_email, msg.as_string())

def __body(data):
   return """\
<html>
  <head></head>
  <body>
    <style>
      body{
         margin: 0; padding: 0;
         font-family: "Helvetica", sans-serif;
         background-color:  #ffffff;

      }
      a:hover{
         text-decoration: none;
      }
   </style>

   <div style="padding-left: 20px; margin-top: 20px">
      <p>Xin chào <strong>%s</strong>, </p>
      <p>Chúng tôi thông báo hợp đồng trả góp của bạn như sau</p>

      %s
   </div>
  </body>
</html>
""" % (data['name'], __footer())

def __footer():
   return """
<p>
    ———————
    <br>
    <strong>MFast CS Team</strong>
    <br>
    <strong>Hotline:</strong> <a href=\"tel:0899909789\">08999 09789</a>  ||  <strong>Email:</strong> <a href=\"mailto:hotro@mfast.vn\">hotro@mfast.vn</a>
</p>

<div style="color:#000;padding:5px 0px;">
    <p class="MsoNormal" style="font-family:&quot;Segoe UI Emoji&quot;,sans-serif;align-items:center;display:flex;"><span style="font-size:10pt;font-family:&quot;Segoe UI Emoji&quot;,sans-serif;color:#222222;margin-right:10px"><img data-emoji="💌" style="height:1.4em;width:1.4em;vertical-align:middle;transform:rotate(-25deg);" alt="💌" aria-label="💌" src="https://fonts.gstatic.com/s/e/notoemoji/13.1.1/1f48c/72.png" loading="lazy"></span><span style="font-size:10pt;font-family:&quot;Tahoma&quot;,sans-serif;color:#e32400">Phản ánh, góp ý về dịch vụ/Feedback:</span><span style="font-family:&quot;Tahoma&quot;,sans-serif;color:#222222">&nbsp;</span><span style="font-size:10pt;font-family:&quot;Tahoma&quot;,sans-serif"><a href="https://docs.google.com/forms/d/e/1FAIpQLScFweITCFy9vHAQQj2VgGrr2lA-kQoxZlj5ZtYkZU2-pj-Waw/viewform" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://docs.google.com/forms/d/e/1FAIpQLScFweITCFy9vHAQQj2VgGrr2lA-kQoxZlj5ZtYkZU2-pj-Waw/viewform&amp;source=gmail&amp;ust=1629256022775000&amp;usg=AFQjCNFqtpykcREydmBfORwz6m91u85KYQ" style="color:#15c;">Tại đây/Here</a></span></p>
    <p style="font-size:small; line-height:1.5;font-family:&quot;Segoe UI Emoji&quot;,sans-serif;">
        <strong style="color: #31960f">DigiPay J.S.C.</strong>
        <br>
        <strong>Add:</strong> 2nd Floor, Athena building, 146 Cong Hoa St., Ward 12, Tan Binh, HCMC, Vietnam
        <br>
        <strong>Tel:</strong> (028) 730 52015 || <strong>F:</strong> (028) 730 52015 || <strong>W:</strong>&nbsp;<a href="http://www.mfast.vn" style="color:#15c;">www.mfast.vn</a> || <strong>Fb:</strong> <a href="http://fb.me/mfast.vn" style="color:#15c;"> http://fb.me/mfast.vn</a>
    </p>
</div>
"""