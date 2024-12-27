import gettext

gettext.bindtextdomain("messages", "vocabs/frontend/locales")
gettext.textdomain("messages")

language = ['es', 'en']

translations = gettext.translation("messages", localedir="vocabs/frontend/locales", languages=['en'])

translations.install()

_ = translations.gettext