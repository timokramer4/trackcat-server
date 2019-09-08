import smtplib

from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid

SERVER = "smtp.strato.de"
FROM = "no-reply@trackcat.de"

# Send verification mail
def sendVmail(reciever, firstName, verificationLink):

    # Create the base text message.
    msg = EmailMessage()
    msg['Subject'] = "TrackCat Email Bestätigung"
    msg['From'] = FROM

    msg['To'] = [reciever]

    msg.set_content("""\
    Hallo """+firstName+""",

    um den vollen Umfang von TrackCat nutzen zu können, müssen Sie ihre Email Adresse über den Link bestätigen.

    """+verificationLink+"""\

    Vielen Dank,
    Ihr Trackcat Team""")

    # Add the html version.  This converts the message into a multipart/alternative
    # container, with the original text message as the first part and the new html
    # message as the second part.
    asparagus_cid = make_msgid()

    string = """\
      <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <meta name="x-apple-disable-message-reformatting" />
            <title>Trackcat E-Mail bestätigung</title>
        </head>
        <body style="padding:0;margin:0;">
            <table align="center" style="background-color:#e9ebee;width:100%;max-width:100%;min-width:100%;" border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr align="center">
                  <td style="width:100%;height:32px"></td>
              </tr>
              <tr align="center">
                  <td align="center">
                    <table border="0" cellpadding="0" cellspacing="0" style="background-color:#e9ebee;min-width:360px;max-width:600px;width:100%;" width="100%">
                        <table align="center" style="max-width:600px;width:100%;" cellpadding="0" cellspacing="0" border="0">
                          <tr align="center">
                              <td style="max-width:600px;padding:2em 40px 0em;width:100%;background-color:white;border-radius:5px 5px 0 0 ;overflow:hidden;"><a href="http://trackcat.de" style="color:#3b5998;text-decoration:none;"><img src="cid:{asparagus_cid}" style="border:0;max-width:50%;" title="Trackcat Logo" /></a></td>
                          </tr>
                        </table>
                        <table align="center" style="max-width:600px;width:100%;" cellpadding="0" cellspacing="0" border="0">
                          <tr align="center">
                              <td style="max-width:600px;padding:50px 40px 40px 40px;width:100%;background-color:#fbfbfc;background-color:#ffffff;background-image:linear-gradient(#ffffff,#edf2fa);border-radius:0 0 5px 5px;">
                                <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                    <tr align="center">
                                      <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;text-align:center;color:#333333;font-size:27px;font-family:ArialMT, Arial, sans-serif;font-weight:light;line-height:36px;">Bitte bestätigen Sie Ihre Email-Adresse</td>
                                    </tr>
                                    <tr align="center">
                                      <td style="width:100%;height:30px;"></td>
                                    </tr>
                                </table>
                                <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                    <tr align="center">
                                      <td style="text-align:left;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;line-height:24px;">
                                          <p>Hallo """+firstName+""",</p><p>  um den vollen Umfang von TrackCat nutzen zu können, müssen Sie ihre Email Adresse über den Button bestätigen.</p>
                                          <br>
                                          <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                                  <tr align="center">
                                                    <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;width:100%;min-width:360px">
                                                        <table align="center" style="background-color:#407fff;border-radius:3.6px;padding:10px 30px;-webkit-border-radius:3.6px;-moz-border-radius:3.6px;">
                                                          <tr align="center">
                                                              <td><a href='"""+verificationLink+"""' style="display:inline-block;text-decoration:none;color:#ffffff;font-size:15px;font-family:ArialMT, Arial, sans-serif;font-weight:bold;text-align:center;width:100%;">Verifzieren</a></td>
                                                          </tr>
                                                        </table>
                                                    </td>
                                                  </tr>
                                                  <tr align="center">
                                                    <td style="width:100%;height:0px;"></td>
                                                  </tr>
                                              </table>
                                          <p> Vielen Dank,<br /> Ihr Trackcat Team </p>
                                      </td>
                                    </tr>
                                    <tr align="center">
                                      <td style="width:100%;height:30px;"></td>
                                    </tr>
                                </table>
                              </td>
                          </tr>
                          <tr align="center">
                              <td style="width:100%;height:5px;"></td>
                          </tr>
                        </table>
                        <table style="width:100%;" align="center">
                          <tr align="center">
                              <td>
                                <table align="center" style="max-width:600px;width:100%;" cellpadding="0" cellspacing="0" border="0">
                                    <tr align="center">
                                      <td style="max-width:600px;padding:50px 40px 40px 40px;width:100%;background-color:#fbfbfc;padding:20px 0px 0px 0px;background-color:#e9ebee;">
                                          <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                            <tr align="center">
                                                <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;color:#8f949b;font-size:12px;padding:0 20px;">This from Trackcat auto generated message was send to <a style="color:#3b5998;text-decoration:none;">"""+reciever+"""</a>. There is no active e-mail subscription that could be terminated.
                                            </tr>
                                            <tr align="center">
                                                <td style="width:100%;height:15px;"></td>
                                            </tr>
                                          </table>
                                          <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                            <tr align="center">
                                                <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;background-color:#979797;width:100%;height:1px;"></td>
                                            </tr>
                                            <tr align="center">
                                                <td style="width:100%;height:15px;"></td>
                                            </tr>
                                          </table>
                                          <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                            <tr align="center">
                                                <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;color:#8f949b;font-size:12px;padding:0 64px;">Copyright &copy; Trackcat <script>document.write(new Date().getFullYear())</script><br>All rights reserved.</td>
                                            </tr>
                                            <tr align="center">
                                                <td style="width:100%;height:0;"></td>
                                            </tr>
                                          </table>
                                      </td>
                                    </tr>
                                    <tr align="center">
                                      <td style="width:100%;height:5px;"></td>
                                    </tr>
                                </table>
                              </td>
                          </tr>
                        </table>
                    </table>
                  </td>
              </tr>
              <tr align="center">
                  <td style="width:100%;height:32px"></td>
              </tr>
            </table>
        </body>
      </html>"""

    msg.add_alternative(string.format(asparagus_cid=asparagus_cid[1:-1]), subtype='html')
    # note that we needed to peel the <> off the msgid for use in the html.

    try:
      # Now add the related image to the html part.
      with open("/var/www/application/static/img/logo.png", 'rb') as img:
          msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=asparagus_cid)
      pass
    except Exception as identifier:
      # Now add the related image to the html part.
      with open("./static/img/logo.png", 'rb') as img:
          msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=asparagus_cid)
      pass

  

    # Make a local copy of what we are going to send.
    # with open('outgoing.msg', 'wb') as f:
    #     f.write(bytes(msg))

    # Send the message via local SMTP server.
    server = smtplib.SMTP(SERVER, 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(FROM, "@track_c[]t2019")
    server.send_message(msg)  # sendmail(FROM, TO, msg.as_string())
    server.quit()

# Send reset password mail
def sendResetMail(reciever, firstName, resetLink, deleteLink):

      # Create the base text message.
      msg = EmailMessage()
      msg['Subject'] = "TrackCat Password zurücksetzen"
      msg['From'] = FROM
  
      # TODO remove MAils on release
      msg['To'] = ["finnjoana56@gmail.com", "timokramer1@me.com", reciever]
  
      msg.set_content("""\
      Hallo """+firstName+""",

      Sie möchten Ihr Passwort zurücksetzen? Im Folgenden haben Sie die Möglichkeit, Ihr Passwort zurückzusetzen. Wenn Sie Ihr Passwort nicht zurücksetzen möchten, können Sie den Vorgang abbrechen:

     
      Passwort zurücksetzen: """+resetLink+"""\
      Zurücksetzen abbrechen: """+ deleteLink +"""\

      Vielen Dank,
      Ihr Trackcat Team""")
  
      # Add the html version.  This converts the message into a multipart/alternative
      # container, with the original text message as the first part and the new html
      # message as the second part.
      asparagus_cid = make_msgid()
  
      string = """\
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <meta name="x-apple-disable-message-reformatting" />
            <title>TrackCat Passwort zurücksetzen</title>
        </head>
        <body style="padding:0;margin:0;">
            <table align="center" style="background-color:#e9ebee;width:100%;max-width:100%;min-width:100%;" border="0" cellpadding="0" cellspacing="0" width="100%">
              <tr align="center">
                  <td style="width:100%;height:32px"></td>
              </tr>
              <tr align="center">
                  <td align="center">
                    <table border="0" cellpadding="0" cellspacing="0" style="background-color:#e9ebee;min-width:360px;max-width:600px;width:100%;" width="100%">
                        <table align="center" style="max-width:600px;width:100%;" cellpadding="0" cellspacing="0" border="0">
                          <tr align="center">
                              <td style="max-width:600px;padding:2em 40px 0em;width:100%;background-color:white;border-radius:5px 5px 0 0 ;overflow:hidden;"><a href="http://trackcat.de" style="color:#3b5998;text-decoration:none;"><img src="cid:{asparagus_cid}" style="border:0;max-width:50%;" title="Trackcat Logo" /></a></td>
                          </tr>
                        </table>
                        <table align="center" style="max-width:600px;width:100%;" cellpadding="0" cellspacing="0" border="0">
                          <tr align="center">
                              <td style="max-width:600px;padding:50px 40px 40px 40px;width:100%;background-color:#fbfbfc;background-color:#ffffff;background-image:linear-gradient(#ffffff,#edf2fa);border-radius:0 0 5px 5px;">
                                <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                    <tr align="center">
                                      <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;text-align:center;color:#333333;font-size:27px;font-family:ArialMT, Arial, sans-serif;font-weight:light;line-height:36px;">Password zurücksetzen</td>
                                    </tr>
                                    <tr align="center">
                                      <td style="width:100%;height:30px;"></td>
                                    </tr>
                                </table>
                                <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                    <tr align="center">
                                      <td style="text-align:left;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;line-height:24px;">
                                          <p>Hallo """+firstName+""",</p><p>  Sie möchten Ihr Passwort zurücksetzen?. Im Folgenden haben Sie die Möglichkeit, Ihr Passwort zurückzusetzen. Wenn Sie Ihr Passwort nicht zurücksetzen möchten, können Sie den Vorgang abbrechen:</p>
                                          <br>
                                          <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                                  <tr align="center">
                                                    <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;width:100%;min-width:360px">
                                                        <table align="center" style="background-color:#407fff;border-radius:3.6px;padding:10px 30px;-webkit-border-radius:3.6px;-moz-border-radius:3.6px;">
                                                          <tr align="center">
                                                              <td><a href='"""+resetLink+"""' style="display:inline-block;text-decoration:none;color:#ffffff;font-size:15px;font-family:ArialMT, Arial, sans-serif;font-weight:bold;text-align:center;width:100%;">Passwort zurücksetzen</a></td>
                                                          </tr>
                                                        </table>
                                                        <br>
                                                        <table align="center" style="border-style:solid;border-color:#407fff;border-radius:3.6px;padding:8.5px 30px;-webkit-border-radius:3.6px;-moz-border-radius:3.6px;">
                                                            <tr align="center">
                                                                <td><a href='"""+ deleteLink +"""' style="display:inline-block;text-decoration:none;color:#407fff;font-size:15px;font-family:ArialMT, Arial, sans-serif;font-weight:bold;text-align:center;width:100%;">Abbrechen</a></td>
                                                            </tr>
                                                          </table>
                                                    </td>
                                                  </tr>
                                                  <tr align="center">
                                                    <td style="width:100%;height:0px;"></td>
                                                  </tr>
                                              </table>
                                          <p> Vielen Dank,<br /> Ihr Trackcat Team </p>
                                      </td>
                                    </tr>
                                    <tr align="center">
                                      <td style="width:100%;height:30px;"></td>
                                    </tr>
                                </table>
                              </td>
                          </tr>
                          <tr align="center">
                              <td style="width:100%;height:5px;"></td>
                          </tr>
                        </table>
                        <table style="width:100%;" align="center">
                          <tr align="center">
                              <td>
                                <table align="center" style="max-width:600px;width:100%;" cellpadding="0" cellspacing="0" border="0">
                                    <tr align="center">
                                      <td style="max-width:600px;padding:50px 40px 40px 40px;width:100%;background-color:#fbfbfc;padding:20px 0px 0px 0px;background-color:#e9ebee;">
                                          <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                            <tr align="center">
                                                <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;color:#8f949b;font-size:12px;padding:0 20px;">This from Trackcat auto generated message was send to <a style="color:#3b5998;text-decoration:none;">"""+reciever+"""</a>. There is no active e-mail subscription that could be terminated.
                                            </tr>
                                            <tr align="center">
                                                <td style="width:100%;height:15px;"></td>
                                            </tr>
                                          </table>
                                          <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                            <tr align="center">
                                                <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;background-color:#979797;width:100%;height:1px;"></td>
                                            </tr>
                                            <tr align="center">
                                                <td style="width:100%;height:15px;"></td>
                                            </tr>
                                          </table>
                                          <table align="center" border="0" cellpadding="0" cellspacing="0" style="width:100%;">
                                            <tr align="center">
                                                <td style="text-align:center;border-spacing:0;color:#4c4c4c;font-family:ArialMT, Arial, sans-serif;font-size:15px;width:100%;color:#8f949b;font-size:12px;padding:0 64px;">Copyright &copy; Trackcat <script>document.write(new Date().getFullYear())</script><br>All rights reserved.</td>
                                            </tr>
                                            <tr align="center">
                                                <td style="width:100%;height:0;"></td>
                                            </tr>
                                          </table>
                                      </td>
                                    </tr>
                                    <tr align="center">
                                      <td style="width:100%;height:5px;"></td>
                                    </tr>
                                </table>
                              </td>
                          </tr>
                        </table>
                    </table>
                  </td>
              </tr>
              <tr align="center">
                  <td style="width:100%;height:32px"></td>
              </tr>
            </table>
        </body>
      </html>"""
  
      msg.add_alternative(string.format(asparagus_cid=asparagus_cid[1:-1]), subtype='html')
      # note that we needed to peel the <> off the msgid for use in the html.
  
      try:
        # Now add the related image to the html part.
        with open("/var/www/application/static/img/logo.png", 'rb') as img:
            msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=asparagus_cid)
        pass
      except Exception as identifier:
        # Now add the related image to the html part.
        with open("./static/img/logo.png", 'rb') as img:
            msg.get_payload()[1].add_related(img.read(), 'image', 'png', cid=asparagus_cid)
        pass
  
    
  
      # Make a local copy of what we are going to send.
      # with open('outgoing.msg', 'wb') as f:
      #     f.write(bytes(msg))
  
      # Send the message via local SMTP server.
      server = smtplib.SMTP(SERVER, 587)
      server.ehlo()
      server.starttls()
      server.ehlo()
      server.login(FROM, "@track_c[]t2019")
      server.send_message(msg)  # sendmail(FROM, TO, msg.as_string())
      server.quit()

# Testing this script
# sendResetMail("finnjoana56@gmail.com", "Finn", "http://safe-harbour.de:4242", "")
# sendVmail("finnjoana56@gmail.com", "Finn", "http://safe-harbour.de:4242")
# print("Done test Sending")