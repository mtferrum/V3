from telebot import TeleBot, apihelper, types
import logging
import numpy as np

log = logging.getLogger('spyspace')


class Telegram(TeleBot):

    def __init__(self, token, proxy=None):
        if proxy is not None:
            apihelper.proxy = proxy
        self.subscribers = []
        self.msg_templates = {}
        super().__init__(token)

    def listen(self, **kwargs):
        super().polling(**kwargs)

    def add_handlers(self, action, callback=False, **kwargs):
        if callback:
            handler_dict = super()._build_handler_dict(action, func=lambda call: True,
                                                       **kwargs)
            super().add_callback_query_handler(handler_dict)
        else:
            handler_dict = super()._build_handler_dict(action, func=lambda message: True,
                                                       **kwargs)
            super().add_message_handler(handler_dict)

    def inline_keyboard(self, keys):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(*[types.InlineKeyboardButton(text=name, callback_data=call) for
                       name, call in keys])
        return keyboard

    def add_mailing_template(self, name, text):
        self.msg_templates[name] = text

    def send_mailing(self, name, *args, **kwargs):
        msg = self.msg_templates[name].format(*args)
        media_group = []
        for key, value in kwargs.items():
            if isinstance(value, np.ndarray):
                if len(value.shape) == 2:
                    media_group.append(types.InputMediaPhoto(value, caption=str(key),
                                                             parse_mode='HTML'))
        for user_id in self.subscribers:
            try:
                self.send_message(user_id, text=msg, disable_web_page_preview='false',
                                  parse_mode="html")
                self.send_media_group(user_id, media_group)
                res = 200
            except apihelper.ApiException as e:
                res = e.result.status_code
            yield res, user_id


class MultiTelegram(Telegram):

    def __init__(self, proxy=None, **tokens):
        if proxy is not None:
            apihelper.proxy = proxy
        assert len(tokens) > 0
        self.tokens = tokens
        super().__init__(self.tokens[list(self.tokens.keys())[0]])

    def add_token(self, name, token):
        self.tokens[name] = token

    def remove_token(self, name):
        if len(self.tokens) > 1:
            self.tokens.pop(name, None)
        else:
            log.debug('last token')

    def change_token(self, name):
        if self.tokens.get(name):
            self.token = self.tokens[name]
        else:
            log.debug('token not found')

    def add_mailing_template(self, name, text, token=None):
        self.msg_templates[name] = text
        if token is not None:
            self.add_token(name, token)

    def send_mailing(self, name, *args, **kwargs):
        if name in self.tokens.keys():
            self.change_token(name)
        sending = super().send_mailing(name, *args, **kwargs)
        while True:
            res, user_id = next(sending)
            yield res, user_id
