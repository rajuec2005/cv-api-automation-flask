from config import *
from json import loads
import smtplib
from email.message import EmailMessage
from jinja2 import Template, Environment, FileSystemLoader, BaseLoader
import os
from main.utils.reporter_util.report_helper import ReportHelper

class EmailHelper:

    def __init__(self, uid):
        self.uuid = uid

    def sendMail(self):

        msg = EmailMessage()
        msg['From'] = SENDER_ADDR
        msg['To'] = RECEIVER_ADDR
        msg['Subject'] = "API Test Report for execution id: {}".format(self.uuid)

        # initialize reportHelperObj to use it's methods to generate report_stats and render
        reportHelperObj = ReportHelper(self.uuid)
        report_stats = reportHelperObj.get_report_stats(reportHelperObj.results)

        # using this template to make a html table in mail itself
        template_path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'template.html'))

        # template rendering
        html_table = reportHelperObj.render(template_path, reportHelperObj.results, report_stats)
        msg.add_alternative(html_table, subtype='html')

        # attach the html report
        doc = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output', self.uuid+'.html'))
        with open(doc, 'rb') as f:
            doc_data = f.read()
            doc_name = self.uuid+".html"
            msg.add_attachment(doc_data, maintype='application', subtype='octet-stream', filename=doc_name)

        # connect to server and send mail
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.connect(EMAIL_HOST, EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        text = msg.as_string()
        server.sendmail(SENDER_ADDR, RECEIVER_ADDR, text)
        server.quit()
        print("email sent")