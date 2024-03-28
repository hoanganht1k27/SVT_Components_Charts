import smtplib
import sys
if sys.version_info[0] == 3:
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.utils import formatdate, COMMASPACE
    from email import encoders as Encoders 
else:
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email.Utils import COMMASPACE , formatdate
    from email import Encoders
import logging
import os

def sendMail ( to , fro , subject , text , files = [ ] , server = "localhost" ) :
    #assert type ( to ) == list
    #assert type ( files ) == list
    try:
       logging.info("Building email content")
       msg = MIMEMultipart ( )
       msg [ 'From' ] = fro
       msg [ 'To' ] = COMMASPACE.join ( to )
       msg [ 'Date' ] = formatdate ( localtime = True )
       msg [ 'Subject' ] = subject

       msg.attach ( MIMEText ( text ) )
    except Exception as e:
        msg = ("Generation of email failed due to {}".format(e))
        logging.error(msg)
        return msg

    try:
        if files != None:
            for file in files :
                logging.info ( '\tAttaching file ' + file )
                part = MIMEBase ( 'application' , "octet-stream" )
                part.set_payload ( open ( file , "rb" ).read ( ) )
                Encoders.encode_base64 ( part )
                part.add_header ( 'Content-Disposition' , 'attachment; filename="%s"'
                                  % os.path.basename ( file ) )
                msg.attach ( part )
    except Exception as e:
        msg = ("Generation of email attachment failed due to {}".format(e))
        logging.error(msg)
        return msg

    try:
        logging.info("sending emai to server {}".format(server))
        logging.info ( '\tSending email from {}'.format(fro ))
        logging.info ( '\tSending email to {}'.format(to))
        smtp = smtplib.SMTP ( server )
        smtp.sendmail ( fro , to , msg.as_string ( ) )
        smtp.close ( )
    except Exception as e:
        msg = ("Sending of email failed due to {}".format(e))
        logging.error(msg)
        return msg
