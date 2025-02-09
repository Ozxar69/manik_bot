from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers.bot_handlers import (
    add_date_handler,
    ask_date,
    book_date,
    cancel_handler,
    cancel_record,
    confirm_booking,
    confirm_cancel_record,
    delete_dates,
    deny_booking,
    get_dates_for_deleting,
    handle_admin_cancel_date,
    handle_admin_cancel_record,
    handle_booking,
    handle_date_input,
    handle_service_choice,
    request_confirm_admin_cancel_record,
    view_free_records,
    view_info,
    view_personal_records,
    view_records,
    wake_up,
send_handler,
)


def setup_handlers(application) -> None:
    """Настраивает обработчики команд и сообщений для бота."""
    application.add_handler(
        CommandHandler("start", wake_up)
    )

    application.add_handler(
        CallbackQueryHandler(add_date_handler, pattern="^add_date$")
    )

    application.add_handler(
        CallbackQueryHandler(view_records, pattern="^view_records$")
    )

    application.add_handler(
        CallbackQueryHandler(cancel_handler, pattern="^cancel$")
    )

    application.add_handler(
        CallbackQueryHandler(view_free_records, pattern="^view_free_records$")
    )

    application.add_handler(
        CallbackQueryHandler(book_date, pattern="^book_date$")
    )
    application.add_handler(
        CallbackQueryHandler(handle_booking, pattern="^book_")
    )

    application.add_handler(
        CallbackQueryHandler(confirm_booking, pattern="^confirm\\|")
    )
    application.add_handler(
        CallbackQueryHandler(deny_booking, pattern="^deny\\|")
    )

    application.add_handler(
        CallbackQueryHandler(view_personal_records, pattern="my_records")
    )

    application.add_handler(
        CallbackQueryHandler(cancel_record, pattern="^cancel_record$")
    )

    application.add_handler(
        CallbackQueryHandler(confirm_cancel_record, pattern=r"^confirm_cancel_")
    )

    application.add_handler(
        CallbackQueryHandler(handle_service_choice, pattern="^service_")
    )

    application.add_handler(
        CallbackQueryHandler(
            handle_admin_cancel_date, pattern="^admin_cancel_date$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            request_confirm_admin_cancel_record, pattern="^cancel\\|"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            handle_admin_cancel_record, pattern="handle_admin_cancel_record\\|"
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            get_dates_for_deleting, pattern="get_dates_for_deleting"
        )
    )
    application.add_handler(
        CallbackQueryHandler(delete_dates, pattern="delete\\|")
    )

    application.add_handler(
        CallbackQueryHandler(view_info, pattern="full_info")
    )
    application.add_handler(
        CallbackQueryHandler(send_handler, pattern="send_handler"))
    application.add_handler(
        CallbackQueryHandler(ask_date, pattern="^ask_date$"))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_input))
