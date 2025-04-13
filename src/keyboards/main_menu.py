from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class MainMenuButtons:

    create_reminder = InlineKeyboardButton(
        text="Создать напоминание", callback_data="create_reminder"
    )

    show_created_reminders = InlineKeyboardButton(
        text="Мои напоминания", callback_data="show_created_reminders"
    )

    show_active_reminders = InlineKeyboardButton(
        text="Активные", callback_data="show_active_reminders"
    )

    show_disabled_reminders = InlineKeyboardButton(
        text="Неактивные", callback_data="show_disabled_reminders"
    )

    to_main_menu = InlineKeyboardButton(
        text="В главное меню", callback_data="to_main_menu"
    )


class MainMenuKeyboards:

    main_window = InlineKeyboardMarkup(
        inline_keyboard=[
            [MainMenuButtons.create_reminder],
            [MainMenuButtons.show_created_reminders],
        ]
    )

    created_reminders = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                MainMenuButtons.show_active_reminders,
                MainMenuButtons.show_disabled_reminders
            ],
            [
                MainMenuButtons.to_main_menu
            ],
        ],
    )
