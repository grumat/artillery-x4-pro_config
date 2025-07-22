import gettext
import os
import locale
import sys

SUPPORTED_LANGUAGES = ["en_US", "pt_BR"]
#SUPPORTED_LANGUAGES = ["pt"]
DEFAULT_LANGUAGE = "en_US"
#DEFAULT_LANGUAGE = "pt_BR"
APP_NAME = "messages"


def GetUserPreferredLocales():
	"""
	Attempts to get the user's preferred locales from the system.
	Returns a list of language codes (e.g., ['en_US', 'en', 'fr_FR', 'fr']).
	"""
	try:
		# locale.getdefaultlocale() is a good cross-platform starting point.
		user_locale, _ = locale.getdefaultlocale()
		if user_locale:
			# Normalize to include both "en_US" and "en" forms for matching
			return [user_locale, user_locale.split('_')[0]]
		return []
	except Exception as e:
		return []


def SelectBestLanguage(preferred_locales, supported_languages, default_language):
	"""
	Selects the best language from supported_languages based on preferred_locales.
	"""
	for user_lang in preferred_locales:
		if user_lang in supported_languages:
			return user_lang
	flex = {}
	for l in supported_languages:
		flex[l.split('_')[0]] = l
	for user_lang in preferred_locales:
		l = user_lang.split('_')[0]
		if l in flex:
			return flex[l]
	return default_language


def GetLocalePath():
	if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
		bundle_dir = sys._MEIPASS
	else:
		bundle_dir = os.path.dirname(os.path.abspath(__file__))
	return os.path.join(bundle_dir, "locale")


def SetupI18nAuto():
	"""
	Sets up the gettext environment by auto-detecting the best language.
	"""
	# 1. Determine user's preferred locales
	preferred_locales = GetUserPreferredLocales()

	# 2. Select the best language from our supported list
	selected_lang = SelectBestLanguage(preferred_locales, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE)

	# 3. Determine the base path for resources (PyInstaller compatibility)
	locale_path = GetLocalePath()

	try:
		# Set the locale for the current process/thread. This is crucial for gettext.
		# LC_ALL sets all locale categories.
		locale.setlocale(locale.LC_ALL, selected_lang)

		translator = gettext.translation(APP_NAME, locale_path, languages=[selected_lang])
		# Install the translator globally if you want to use '_' or 'gettext'
		# without explicitly calling translator.gettext
		translator.install()		# Bind the domain to the locale directory and set the text domain
		
	except FileNotFoundError as e:
		# Fallback if setting locale fails (e.g., system doesn't have it installed)
		gettext.NullTranslations().install()
	except gettext.Error as e:
		# Fallback if gettext binding fails
		gettext.NullTranslations().install()


def SetupI18nManual(lang_code):
	"""
	A fallback function to manually set up i18n for a given language code.
	"""
	locale_path = GetLocalePath()

	try:
		locale.setlocale(locale.LC_ALL, lang_code)
		gettext.bindtextdomain(APP_NAME, locale_path)
		gettext.textdomain(APP_NAME)
		_ = gettext.gettext
		return _
	except Exception as e:
		return lambda x: x

