from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class ReminderManagementKeyboards:

    def get_reminder_management_keyboard_by_status(
        reminder_id: int, reminder_status: bool
    ) -> InlineKeyboardMarkup:
        if reminder_status:
            button_text = "Отключить"
            cb_data = f"disable_reminder:{reminder_id}:{reminder_status}"
        else:
            button_text = "Включить"
            cb_data = f"enable_reminder:{reminder_id}:{reminder_status}"

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Сбросить время запуска",
                        callback_data=f"reset_reminder_start_time:{reminder_id}:{reminder_status}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=button_text,
                        callback_data=cb_data,
                    ),
                    InlineKeyboardButton(
                        text="Удалить", callback_data=f"delete_reminder:{reminder_id}"
                    ),
                ],
            ]
        )
