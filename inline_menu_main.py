from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

inline_menu_buy_main = InlineKeyboardMarkup(row_width=2,
                                inline_keyboard=
                                [
                                    [
                                        InlineKeyboardButton(text='📢 Купить запросы ', callback_data='buy')
                                    ]
                                ]
                                )


inline_menu_main = InlineKeyboardMarkup(row_width=2,
                                inline_keyboard=
                                [

                                    [
                                        InlineKeyboardButton(text='➕ Добавить карту ', callback_data='add_card')
                                        
                                    ],
                                    [
                                        InlineKeyboardButton(text='📒 Мои карты ', callback_data='my_cards')
                                    ],
                                    [
                                        InlineKeyboardButton(text='🗣 Поддержка ', callback_data='ask')
                                    ],
                                    [
                                        InlineKeyboardButton(text='📢 Купить запросы ', callback_data='buy')
                                    ],
                                    [
                                        InlineKeyboardButton(text='🙏 Помощь ', callback_data='help'),
                                        InlineKeyboardButton(text='👤 Профиль ', callback_data='profile')
                                    ]

                                ]
                                )