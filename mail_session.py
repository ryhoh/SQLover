from datetime import datetime, timedelta
import random
import requests
import string
from typing import Dict

import db


MAILGUN_API_KEY = db.read_mailgun_api_key()
# APP_DOMAIN = 'https://localhost:8000'
APP_DOMAIN = 'https://sqlabo.herokuapp.com'

# clean old inactivated users
db.delete_inactivated_users()


class MailSession:
    """
    Base class for session with an user using email.

    """
    EXPIRE_MINUTES = 30
    sessions: Dict[str, 'MailSession'] = dict()

    def __init__(self, user_name: str):
        self.user_name = user_name
        while True:  # Identification for signup session. Used for account activation.
            self.id = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
            if self.id not in self.sessions:
                break
        self.created_datetime = datetime.now()
        self.sessions[self.id] = self

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other: 'MailSession'):
        return self.id == other.id

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.id, self.user_name)

    def is_expired(self) -> bool:
        return self.created_datetime - datetime.now() > timedelta(minutes=self.EXPIRE_MINUTES)

    def send_mail(self, language: str, email: str):
        raise NotImplementedError

    @staticmethod
    def _call_api_for_send_mail(sender_name: str, to: str, subject: str, text: str):
        return requests.post(  # use mailgun api
            "https://api.mailgun.net/v3/sandbox8b306743e1324385b99e843fac6f002b.mailgun.org/messages",
            auth=("api", MAILGUN_API_KEY),
            data={
                "from": sender_name,
                "to": [to],
                "subject": subject,
                "text": text
            }
        )


class SignupMailSession(MailSession):
    def send_mail(self, language: str, email: str):
        contents_dict = {
            'en': """
Hello %s!

Thank you for your signup at SQLabo.
To activate your account, please access below url.
(This url is available for %s minutes)

%s/activate?param=%s

This email address is for sending only.
Please do not reply to this email.

If this email is unexpected, please ignore this email.

--
SQLabo Service
Maintainer: https://github.com/ryhoh

""",
            'ja': """
こんにちは %s さん！

SQLabo にご登録いただきありがとうございます。
以下の URL を開いて、アカウントをアクティベートしましょう。
（この URL は %s 分間有効です）

%s/activate?param=%s

このメールアドレスは送信専用です。
返信しないでください。

もしこのメールが身に覚えのないものだった場合は、恐れ入りますがお読み捨てください。

--
SQLabo Service
Maintainer: https://github.com/ryhoh

"""
        }

        subject_dict = {
            'en': 'SQLabo: Please activate your account',
            'ja': 'SQLabo アカウントをアクティベートしてください',
        }

        if language not in ('en', 'ja'):
            raise ValueError('invalid language:', language)

        return self._call_api_for_send_mail(
            sender_name="SQLabo Account Activation <activation@sqlabo.herokuapp.com>",
            to=email,
            subject=subject_dict[language],
            text=contents_dict[language] % (self.user_name, self.EXPIRE_MINUTES, APP_DOMAIN, self.id)
        )


class ResetPasswordMailSession(MailSession):
    def send_mail(self, language: str, email: str):
        contents_dict = {
            'en': """
Hello %s!

To reset your password, please access below url.
(This url is available for %s minutes)

%s/reset_password?param=%s

This email address is for sending only.
Please do not reply to this email.

If this email is unexpected, please ignore this email.
Thank you!

--
SQLabo Service
Maintainer: https://github.com/ryhoh

""",
            'ja': """
こんにちは %s さん！

以下の URL を開いて、パスワードをリセットしましょう。
（この URL は %s 分間有効です）

%s/reset_password?param=%s

このメールアドレスは送信専用です。
返信しないでください。

もしこのメールが身に覚えのないものだった場合は、恐れ入りますがお読み捨てください。

--
SQLabo Service
Maintainer: https://github.com/ryhoh

"""
        }

        subject_dict = {
            'en': 'SQLabo: Please reset your password',
            'ja': 'SQLabo パスワードを再設定してください',
        }

        if language not in ('en', 'ja'):
            raise ValueError('invalid language:', language)

        return self._call_api_for_send_mail(
            sender_name="SQLabo Password Recovery <password_recovery@sqlabo.herokuapp.com>",
            to=email,
            subject=subject_dict[language],
            text=contents_dict[language] % (self.user_name, self.EXPIRE_MINUTES, APP_DOMAIN, self.id)
        )
