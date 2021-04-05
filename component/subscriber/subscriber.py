from scope import config, log, messenger, executor
from lib.queries.mysql_queries import mysql_queries as queries


class Subscriber:

    def __init__(self, password=None):
        if password is None:
            self.password = config.find('telebot_password')
        self.subscriber_bot = config.find('telebot_subscriber')
        self.temp_states = {}
        executor.execute_query(queries, 'create_telegram_subscribers_table', commit=True)
        try:
            executor.execute_query(queries, 'alter_bot_telegram_subscribers_table',
                                   commit=True)
        except Exception as e:
            log.debug(e)
        messenger.change_token(self.subscriber_bot)
        messenger.add_handlers(self.start, commands=['start'])
        messenger.add_handlers(self.stop, commands=['stop'])
        messenger.add_handlers(self.input_password, content_types=['text'])
        messenger.add_handlers(self.confirm, callback=True)
        messenger.listen()

    def start(self, message):
        user_id = message.from_user.id
        subscribers = [sub[0] for sub in executor.execute_query(queries,
                                                                'select_telegram_subscribers',
                                                                bot=self.subscriber_bot)]
        if user_id not in subscribers:
            msg = 'Введите пароль.'
            messenger.send_message(user_id, msg, parse_mode='html')
            self.temp_states[user_id] = 'input_password'
        else:
            msg = 'Вы уже подписаны.'
            messenger.send_message(user_id, msg, parse_mode='html')

    def stop(self, message):
        user_id = message.from_user.id
        subscribers = [sub[0] for sub in executor.execute_query(queries,
                                                                'select_telegram_subscribers',
                                                                bot=self.subscriber_bot)]
        if user_id in subscribers:
            keys = [('Да', 'yes'), ('Нет', 'no')]
            msg = 'Вы уверены, что хотите отписаться?'
            messenger.send_message(user_id, msg, parse_mode='html',
                                   reply_markup=messenger.inline_keyboard(keys))
            self.temp_states[user_id] = 'confirm_stop'
        else:
            msg = 'Вы не подписаны.'
            messenger.send_message(user_id, msg, parse_mode='html')

    def confirm(self, call):
        user_id = call.from_user.id
        user_state = self.temp_states.pop(user_id, None)
        if user_state == 'confirm_stop':
            if call.data == 'yes':
                msg = 'Вы отписались'
                executor.execute_query(queries, 'delete_telegram_subscriber', user_id=user_id,
                                       bot=self.subscriber_bot, commit=True)
                messenger.send_message(user_id, msg, parse_mode='html')
                messenger.answer_callback_query(callback_query_id=call.id,
                                                show_alert=False)
            else:
                msg = 'Отписка отменена.'
                messenger.send_message(user_id, msg, parse_mode='html')
                messenger.answer_callback_query(callback_query_id=call.id,
                                                show_alert=False)

    def input_password(self, message):
        user_id = message.from_user.id
        input_text = message.text
        user_state = self.temp_states.pop(user_id, None)
        if user_state == 'input_password':
            if input_text == self.password:
                msg = 'Доступ разрешен, подписка оформлена.'
                executor.execute_query(queries, 'insert_telegram_subscriber', user_id=user_id,
                                       bot=self.subscriber_bot, commit=True)
                messenger.send_message(user_id, msg, parse_mode='html')
            else:
                msg = 'В доступе отказано.'
                messenger.send_message(user_id, msg, parse_mode='html')
