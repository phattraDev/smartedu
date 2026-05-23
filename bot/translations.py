"""
Translations for the School Telegram Bot.
Supported languages: English (en), Khmer (km)
"""

STRINGS = {
    # ── Language picker ──────────────────────────────────────────────────────
    "lang_pick_title": {
        "en": "🌐 *Choose Your Language*\n\n────────────────────────────\nPlease select your preferred language:",
        "km": "🌐 *ជ្រើសរើសភាសា*\n\n────────────────────────────\nសូមជ្រើសរើសភាសាដែលអ្នកចូលចិត្ត:",
    },
    "lang_btn_en": {
        "en": "🇬🇧  English",
        "km": "🇬🇧  English",
    },
    "lang_btn_km": {
        "en": "🇰🇭  ភាសាខ្មែរ",
        "km": "🇰🇭  ភាសាខ្មែរ",
    },
    "lang_saved": {
        "en": "✅ Language set to *English*.",
        "km": "✅ បានកំណត់ភាសា *ខ្មែរ*។",
    },

    # ── Class picker ─────────────────────────────────────────────────────────
    "class_pick_welcome": {
        "en": "👋 *Welcome, {name}!*\n\n────────────────────────────\nTo get started, please select your\nchild's class from the list below:\n\n_You only need to do this once._",
        "km": "👋 *សូមស្វាគមន៍, {name}!*\n\n────────────────────────────\nដើម្បីចាប់ផ្តើម សូមជ្រើសរើស\nថ្នាក់រៀនរបស់កូនអ្នកពីបញ្ជីខាងក្រោម:\n\n_អ្នកត្រូវធ្វើវាតែម្តងប៉ុណ្ណោះ។_",
    },
    "class_pick_change": {
        "en": "✏️ *Change Class*\n\n────────────────────────────\nSelect your child's new class:",
        "km": "✏️ *ប្តូរថ្នាក់រៀន*\n\n────────────────────────────\nជ្រើសរើសថ្នាក់រៀនថ្មីរបស់កូនអ្នក:",
    },
    "class_none_available": {
        "en": "⚠️ *No Classes Available*\n\n────────────────────────────\nNo classes have been set up yet.\nPlease contact the school office for assistance.",
        "km": "⚠️ *មិនមានថ្នាក់រៀន*\n\n────────────────────────────\nមិនទាន់មានថ្នាក់រៀនណាមួយទេ។\nសូមទាក់ទងការិយាល័យសាលា។",
    },
    "class_registered": {
        "en": "✅ *Class Registered*\n\n────────────────────────────\n🏫  Your child's class:  *{code}*\n────────────────────────────\n\nAll set! I'll remember this for next time.\nYou can change it anytime from the menu.",
        "km": "✅ *បានចុះឈ្មោះថ្នាក់រៀន*\n\n────────────────────────────\n🏫  ថ្នាក់រៀនរបស់កូន:  *{code}*\n────────────────────────────\n\nរួចរាល់ហើយ! ខ្ញុំនឹងចងចាំសម្រាប់ពេលក្រោយ។\nអ្នកអាចប្តូរវាបានគ្រប់ពេលពីម៉ឺនុយ។",
    },
    "class_save_error": {
        "en": "⚠️ *Error*\n\nCould not save your class. Please try /start again.",
        "km": "⚠️ *កំហុស*\n\nមិនអាចរក្សាទុកថ្នាក់រៀនបានទេ។ សូមសាកល្បង /start ម្តងទៀត។",
    },

    # ── Main menu ────────────────────────────────────────────────────────────
    "menu_welcome_back": {
        "en": "👋 *Welcome back, {name}!*\n\n────────────────────────────\n🏫  Class:  *{code}*\n📅  Today:  {date}\n────────────────────────────\n\nHow can I help you today?",
        "km": "👋 *សូមស្វាគមន៍មកវិញ, {name}!*\n\n────────────────────────────\n🏫  ថ្នាក់:  *{code}*\n📅  ថ្ងៃនេះ:  {date}\n────────────────────────────\n\nខ្ញុំអាចជួយអ្នកអ្វីបានថ្ងៃនេះ?",
    },
    "menu_main": {
        "en": "🏠 *Main Menu*\n\n────────────────────────────\n{class_line}📅  Today:  {date}\n────────────────────────────\n\nHow can I help you today?",
        "km": "🏠 *ម៉ឺនុយចម្បង*\n\n────────────────────────────\n{class_line}📅  ថ្ងៃនេះ:  {date}\n────────────────────────────\n\nខ្ញុំអាចជួយអ្នកអ្វីបានថ្ងៃនេះ?",
    },
    "menu_class_line": {
        "en": "🏫  Class:  *{code}*\n",
        "km": "🏫  ថ្នាក់:  *{code}*\n",
    },

    # ── Menu buttons ─────────────────────────────────────────────────────────
    "btn_homework": {
        "en": "📚  Homework",
        "km": "📚  កិច្ចការផ្ទះ",
    },
    "btn_holidays": {
        "en": "🗓  Upcoming Holidays",
        "km": "🗓  វិស្សមកាលខាងមុខ",
    },
    "btn_change_class": {
        "en": "✏️  Change Class",
        "km": "✏️  ប្តូរថ្នាក់រៀន",
    },
    "btn_about": {
        "en": "ℹ️  About",
        "km": "ℹ️  អំពី",
    },
    "btn_back": {
        "en": "‹  Back to Menu",
        "km": "‹  ត្រឡប់ទៅម៉ឺនុយ",
    },
    "btn_change_lang": {
        "en": "🌐  Change Language",
        "km": "🌐  ប្តូរភាសា",
    },

    # ── Homework ─────────────────────────────────────────────────────────────
    "hw_fetching": {
        "en": "⏳ Fetching homework, please wait…",
        "km": "⏳ កំពុងទាញយកកិច្ចការផ្ទះ សូមរង់ចាំ…",
    },
    "hw_class_not_found": {
        "en": "❌ *Class Not Found*\n\nYour class could not be found in the system.\nPlease tap *Change Class* from the menu to update it.",
        "km": "❌ *រកមិនឃើញថ្នាក់រៀន*\n\nថ្នាក់រៀនរបស់អ្នករកមិនឃើញក្នុងប្រព័ន្ធ។\nសូមចុច *ប្តូរថ្នាក់រៀន* ពីម៉ឺនុយ។",
    },
    "hw_none_today": {
        "en": "📚 *Homework — Class {code}*\n\n────────────────────────────\n📅  {date}\n────────────────────────────\n\n✅  No homework has been assigned yet today.\n\n_Check back later or contact your teacher._",
        "km": "📚 *កិច្ចការផ្ទះ — ថ្នាក់ {code}*\n\n────────────────────────────\n📅  {date}\n────────────────────────────\n\n✅  មិនទាន់មានកិច្ចការផ្ទះថ្ងៃនេះទេ។\n\n_សូមពិនិត្យម្តងទៀតនៅពេលក្រោយ ឬទាក់ទងគ្រូ។_",
    },
    "hw_header": {
        "en": "📚 *Homework — Class {code}*\n────────────────────────────\n📅  {date}\n📋  {count} assignment{plural} found\n────────────────────────────\n",
        "km": "📚 *កិច្ចការផ្ទះ — ថ្នាក់ {code}*\n────────────────────────────\n📅  {date}\n📋  រកឃើញ {count} កិច្ចការ\n────────────────────────────\n",
    },
    "hw_due": {
        "en": "📅  Due: *{date}*",
        "km": "📅  កំណត់ថ្ងៃ: *{date}*",
    },
    "hw_teacher": {
        "en": "👩‍🏫  Teacher: {name}",
        "km": "👩‍🏫  គ្រូ: {name}",
    },
    "hw_attachment": {
        "en": "📎  Attachment included ↓",
        "km": "📎  មានឯកសារភ្ជាប់ ↓",
    },
    "hw_footer": {
        "en": "────────────────────────────\n_Tap any attachment below to download it._",
        "km": "────────────────────────────\n_ចុចលើឯកសារភ្ជាប់ខាងក្រោមដើម្បីទាញយក។_",
    },

    # ── Holidays ─────────────────────────────────────────────────────────────
    "hol_none": {
        "en": "🗓 *Upcoming Holidays*\n\n────────────────────────────\n\nNo upcoming holidays are scheduled at this time.\n\n_Check back later for updates._",
        "km": "🗓 *វិស្សមកាលខាងមុខ*\n\n────────────────────────────\n\nមិនមានវិស្សមកាលខាងមុខណាមួយទេ។\n\n_សូមពិនិត្យម្តងទៀតនៅពេលក្រោយ។_",
    },
    "hol_header": {
        "en": "🗓 *Upcoming Holidays*\n────────────────────────────\n📅  {date}\n────────────────────────────\n",
        "km": "🗓 *វិស្សមកាលខាងមុខ*\n────────────────────────────\n📅  {date}\n────────────────────────────\n",
    },
    "hol_date_single": {
        "en": "📅  Date: *{date}*",
        "km": "📅  ថ្ងៃ: *{date}*",
    },
    "hol_date_from": {
        "en": "📅  From: *{date}*",
        "km": "📅  ចាប់ពី: *{date}*",
    },
    "hol_date_to": {
        "en": "📅  To:      *{date}*",
        "km": "📅  ដល់:      *{date}*",
    },
    "hol_footer": {
        "en": "────────────────────────────\n_All dates are subject to change._",
        "km": "────────────────────────────\n_កាលបរិច្ឆេទទាំងអស់អាចផ្លាស់ប្តូរបាន។_",
    },

    # ── About ────────────────────────────────────────────────────────────────
    "about": {
        "en": "ℹ️ *About This Bot*\n\n────────────────────────────\n🏫  *{school}*\n────────────────────────────\n\nThis bot helps parents stay informed about:\n\n📚  Daily homework assignments\n🗓  Upcoming school holidays\n📢  Important school announcements\n\n────────────────────────────\nFor support, please contact the school office.",
        "km": "ℹ️ *អំពីបូតនេះ*\n\n────────────────────────────\n🏫  *{school}*\n────────────────────────────\n\nបូតនេះជួយឪពុកម្តាយឱ្យដឹងអំពី:\n\n📚  កិច្ចការផ្ទះប្រចាំថ្ងៃ\n🗓  វិស្សមកាលសាលាខាងមុខ\n📢  សេចក្តីប្រកាសសាលាសំខាន់ៗ\n\n────────────────────────────\nសម្រាប់ជំនួយ សូមទាក់ទងការិយាល័យសាលា។",
    },

    # ── Misc ─────────────────────────────────────────────────────────────────
    "cancelled": {
        "en": "Cancelled. Use the menu below:",
        "km": "បានបោះបង់។ ប្រើម៉ឺនុយខាងក្រោម:",
    },
    "use_menu": {
        "en": "Please use the menu below to navigate:",
        "km": "សូមប្រើម៉ឺនុយខាងក្រោមដើម្បីរុករក:",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Return the translated string for key in lang, with optional format args."""
    lang = lang if lang in ("en", "km") else "en"
    text = STRINGS.get(key, {}).get(lang, STRINGS.get(key, {}).get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text
