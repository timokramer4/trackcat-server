from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


SERVER = "smtp.strato.de"
FROM = "info@trackcat.de"
TO = ["finnjoana56@gmail.com"] # must be a list

TEXT = "Verify your Email by clicking the link safe-harbour.de:4242."




def sendVmail(reciever):

  #TO.append(reciever)

  html = """\
    <!DOCTYPE html><html lang=3Dde><head><meta content=3D"email=3Dno" name=3D"f=
ormat-detection"><meta content=3D"date=3Dno" name=3D"format-detection"><sty=
le>.awl a {color: #FFFFFF; text-decoration: none;} .abml a {color: #000000;=
 font-family: Roboto-Medium,Helvetica,Arial,sans-serif; font-weight: bold; =
text-decoration: none;} .adgl a {color: rgba(0, 0, 0, 0.87); text-decoratio=
n: none;} .afal a {color: #b0b0b0; text-decoration: none;} @media screen an=
d (min-width: 600px) {.v2sp {padding: 6px 30px 0px;} .v2rsp {padding: 0px 1=
0px;}} @media screen and (min-width: 600px) {.mdv2rw {padding: 40px 40px;}}=
 </style><link href=3D"//fonts.googleapis.com/css?family=3DGoogle+Sans" rel=
=3Dstylesheet type=3D"text/css"></head><body bgcolor=3D"#FFFFFF" style=3D"m=
argin: 0; padding: 0;"><table border=3D0 cellpadding=3D0 cellspacing=3D0 he=
ight=3D"100%" lang=3Dde style=3D"min-width: 348px;" width=3D"100%"><Tbody><=
tr height=3D32 style=3D"height: 32px;"><td></td></tr><tr align=3Dcenter><td=
><div itemscope itemtype=3D"//schema.org/EmailMessage"><div itemprop=3Dacti=
on itemscope itemtype=3D"//schema.org/ViewAction"><link href=3D"https://acc=
ounts.google.com/AccountChooser?Email=3Dfinnjoana56@gmail.com&amp;continue=
=3Dhttps://myaccount.google.com/alert/nt/1553096407704?rfn%3D31%26rfnc%3D1%=
26eid%3D3227118939799603214%26et%3D0%26anexp%3Dgivab-fa--mdv2-fa--hsc-contr=
ol_b--ivab-fa" itemprop=3Durl><meta content=3D"Aktivit=C3=A4t =C3=BCberpr=
=C3=BCfen" itemprop=3Dname></div></div><table border=3D0 cellpadding=3D0 ce=
llspacing=3D0 style=3D"padding-bottom: 20px;max-width: 516px;min-width: 220=
px;"><Tbody><tr><td style=3D"width: 8px;" width=3D8></td><td><div align=3Dc=
enter class=3Dmdv2rw style=3D"border-style: solid; border-width: thin; bord=
er-color:#dadce0; border-radius: 8px; padding: 40px 20px;"><img height=3D24=
 src=3D"https://www.gstatic.com/accountalerts/email/googlelogo_color_188x64=
dp.png" style=3D"width: 75px; height: 24px; margin-bottom: 16px;" width=3D7=
5><div style=3D"font-family: &#39;Google Sans&#39;,Roboto,RobotoDraft,Helve=
tica,Arial,sans-serif;border-bottom: thin solid #dadce0; color: rgba(0,0,0,=
0.87); line-height: 32px; padding-bottom: 24px;text-align: center; word-bre=
ak: break-word;"><div style=3D"font-size: 24px;">Neues Ger=C3=A4t angemelde=
t</div><table align=3Dcenter style=3D"margin-top:8px;"><Tbody><tr style=3D"=
line-height: normal;"><td align=3Dright style=3D"padding-right:8px;"><img h=
eight=3D20 src=3D"https://www.gstatic.com/accountalerts/email/anonymous_pro=
file_photo.png" style=3D"width: 20px; height: 20px; vertical-align: sub; bo=
rder-radius: 50%;;" width=3D20></td><td><a style=3D"font-family: &#39;Googl=
e Sans&#39;,Roboto,RobotoDraft,Helvetica,Arial,sans-serif;color: rgba(0,0,0=
,0.87); font-size: 14px; line-height: 20px;">finnjoana56@gmail.com</a></td>=
</tr></Tbody></table></div><div style=3D"font-family: Roboto-Regular,Helvet=
ica,Arial,sans-serif; font-size: 14px; color: rgba(0,0,0,0.87); line-height=
: 20px;padding-top: 20px; text-align: center;">Jemand hat sich =C3=BCber ei=
n neues Windows-Ger=C3=A4t in Ihrem Google-Konto angemeldet. Sie haben dies=
e E-Mail erhalten, weil wir uns vergewissern m=C3=B6chten, dass es sich hie=
rbei um Sie handelt.<div style=3D"padding-top: 32px;text-align: center;"><a=
 href=3D"https://accounts.google.com/AccountChooser?Email=3Dfinnjoana56@gma=
il.com&amp;continue=3Dhttps://myaccount.google.com/alert/nt/1553096407704?r=
fn%3D31%26rfnc%3D1%26eid%3D3227118939799603214%26et%3D0%26anexp%3Dgivab-fa-=
-mdv2-fa--hsc-control_b--ivab-fa" link-id=3D"main-button-link" style=3D"fon=
t-family: &#39;Google Sans&#39;,Roboto,RobotoDraft,Helvetica,Arial,sans-ser=
if; line-height: 16px; color: #ffffff; font-weight: 400; text-decoration: n=
one;font-size: 14px;display:inline-block;padding: 10px 24px;background-colo=
r: #4184F3; border-radius: 5px; min-width: 90px;" target=3D"_blank">Aktivit=
=C3=A4t pr=C3=BCfen</a></div></div></div><div style=3D"text-align: left;"><=
div style=3D"font-family: Roboto-Regular,Helvetica,Arial,sans-serif;color: =
rgba(0,0,0,0.54);font-size: 11px; line-height: 18px; padding-top: 12px; tex=
t-align: center;"><div>Wir haben Ihnen diese E-Mail gesendet, um Sie =C3=BC=
ber wichtige =C3=84nderungen zu Ihrem Google-Konto und den Diensten von Goo=
gle zu informieren.</div><div style=3D"direction: ltr;">&copy; 2019 Google =
LLC, <a class=3Dafal style=3D"font-family: Roboto-Regular,Helvetica,Arial,s=
ans-serif;color: rgba(0,0,0,0.54);font-size: 11px; line-height: 18px; paddi=
ng-top: 12px; text-align: center;">1600 Amphitheatre Parkway, Mountain View=
, CA 94043, USA</a></div></div></div></td><td style=3D"width: 8px;" width=
=3D8></td></tr></Tbody></table></td></tr><tr height=3D32 style=3D"height: 3=
2px;"><td></td></tr></Tbody></table><img height=3D1 src=3D"https://notifica=
tions.googleapis.com/email/t/AFG8qyUrgFL9GTL3SHfwtWP3iooa97lTJHVTqCpNQRJHq4=
xGq_HPsW0zH35WeJCtYfdlo3Vzs4CLNlOZz6UxCUsz10fmihCI_mO4CfxdVmkjNT2j9hXo6MgM9=
etncwyrpAb8fmkegbyLIG1DMECpVI5BbGFJJVVnNHsZ2mMlfPmv8wdeQGYsAsCUAjfiBi6nnj-B=
tssEd5aPIDw-csLqUbiMKGLBDArxeeg_gI3tMZ1aZ72JGREOuKwYO00M/a.gif" width=3D1><=
/body></html>



  """



  # <html>
  #   <head>

  #   </head>
  #   <body>
    
  #     <h2>Email Verification</h2>

  #       <p>verify EMail """ + reciever + """</p>

  #       <a href="http://safe-harbour.de:4242">verify</a>
  #     </p>
  #   </body>
  # </html>



  msg = MIMEMultipart('alternative')
  msg['Subject'] = "TrackCat Email Verification"
  msg['From'] = FROM
  #msg['To'] = "finnjoana56@gmail.com"#TO

  # Prepare actual message
  # message = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

  # %s
  # """ % (FROM, ", ".join(TO), SUBJECT, TEXT)


  part1 = MIMEText(TEXT, 'plain')
  part2 = MIMEText(html, 'html')

  msg.attach(part1)
  msg.attach(part2)

  # Send the mail

  server = smtplib.SMTP(SERVER, 587)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login(FROM, "@track_c[]t2019")
  server.sendmail(FROM, TO, msg.as_string())
  server.quit()
  
  print("DONE SENDING------------------------")


sendVmail(TO[0])