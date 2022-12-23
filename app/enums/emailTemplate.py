from enum import Enum


class EmailTemplate(str, Enum):
    ResetPassword = 'ResetPassword'
    ConfirmAccount = 'ConfirmAccount'
