try:
    from flask_babelex import Domain

except ImportError:
    def gettext(string, **variables):
        return string % variables

    def ngettext(singular, plural, num, **variables):
        return (singular if num == 1 else plural) % variables

    def lazy_gettext(string, **variables):
        return gettext(string, **variables)

else:
    from flask_admin import translations
    from flask import _request_ctx_stack
    from flask_babelex import get_locale, support, NullTranslations

    try:
        from wtforms.i18n import messages_path
    except ImportError:
        from wtforms.ext.i18n.utils import messages_path

    class CustomDomain(Domain):
        def __init__(self):
            super(CustomDomain, self).__init__(translations.__path__[0], domain='admin')

        def get_translations_path(self, ctx):
            view = get_current_view()

            if view is not None:
                dirname = view.admin.translations_path
                if dirname is not None:
                    return dirname

            return super(CustomDomain, self).get_translations_path(ctx)

        def get_translations(self):
            ''' Override to merge wtforms translations with flask-admin
            '''
            ctx = _request_ctx_stack.top
            if ctx is None:
                return NullTranslations()

            locale = get_locale()

            cache = self.get_translations_cache(ctx)

            translations = cache.get(str(locale))
            if translations is None:
                dirname = self.get_translations_path(ctx)
                translations = support.Translations.load(dirname,
                                                         locale,
                                                         domain=self.domain)

                # start of overridden section - merging wtforms translations
                wtf_translations = support.Translations.load(messages_path(),
                                                             locale,
                                                             domain='wtforms')
                translations.merge(wtf_translations)

                cache[str(locale)] = translations

            return translations

    domain = CustomDomain()

    gettext = domain.gettext
    ngettext = domain.ngettext
    lazy_gettext = domain.lazy_gettext

# lazy imports
from .helpers import get_current_view
