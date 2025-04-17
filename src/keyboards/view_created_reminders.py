from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class ViewCreatedRemindersButtons:

    show_active_reminders = InlineKeyboardButton(
        text="Активные", callback_data="show_active_reminders"
    )

    show_disabled_reminders = InlineKeyboardButton(
        text="Неактивные", callback_data="show_disabled_reminders"
    )

    to_main_menu = InlineKeyboardButton(
        text="В главное меню", callback_data="to_main_menu"
    )


class ViewCreatedRemindersKeyboards:

    show_created_reminders = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                ViewCreatedRemindersButtons.show_active_reminders,
                ViewCreatedRemindersButtons.show_disabled_reminders,
            ],
            [ViewCreatedRemindersButtons.to_main_menu],
        ],
    )
