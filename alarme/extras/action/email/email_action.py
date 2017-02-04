import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from jinja2 import Environment, PackageLoader, Template

from alarme import Action


class EmailAction(Action):

    def __init__(self, app, id_, host, port, login, password, sender, recipient, subject, env={}, text=None, template=None):
        super().__init__(app, id_)
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.env = env
        self.text = text
        self.template = template

    async def run(self):
        self.logger.info('send_email')
        smtp = aiosmtplib.SMTP(hostname=self.host, port=self.port)
        await smtp.connect()
        await smtp.ehlo()
        await smtp.starttls()
        await smtp.ehlo()
        await smtp.login(self.login, self.password)
        env = self.env.copy()
        env.update(dict(
            app=self.app,
        ))
        package_name = sys.modules[__name__].__package__
        jinja_env = Environment(loader=PackageLoader(package_name))
        try:
            plain_template = jinja_env.get_template(
                '{}.txt'.format(self.template)
            )
        except:
            plain_template = Template(self.text)
        part1 = MIMEText(plain_template.render(**env), 'plain')
        try:
            html_template = jinja_env.get_template(
                '{}.html'.format(self.template)
            )
        except:
            msg = part1
        else:
            part2 = MIMEText(html_template.render(**env), 'html')
            msg = MIMEMultipart('alternative')
            msg.attach(part1)
            msg.attach(part2)
        msg['Subject'] = Template(self.subject).render(**env)
        await smtp.sendmail(self.sender, [self.recipient], msg.as_string())
