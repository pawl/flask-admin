from wtforms import widgets
from flask.globals import _request_ctx_stack
from flask_admin.babel import gettext, ngettext
from flask_admin import helpers as h

__all__ = ['Select2Widget', 'DatePickerWidget', 'DateTimePickerWidget',
           'RenderTemplateWidget', 'Select2TagsWidget', 'UTCTimePickerWidget',
           'UTCDateTimePickerWidget', 'TimePickerWidget']


class Select2Widget(widgets.Select):
    """
        `Select2 <https://github.com/ivaynberg/select2>`_ styled select widget.

        You must include select2.js, form.js and select2 stylesheet for it to
        work.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'select2')

        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'

        return super(Select2Widget, self).__call__(field, **kwargs)


class Select2TagsWidget(widgets.TextInput):
    """`Select2 <http://ivaynberg.github.com/select2/#tags>`_ styled text widget.
    You must include select2.js, form.js and select2 stylesheet for it to work.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'select2')
        kwargs.setdefault('data-tags', u'1')
        return super(Select2TagsWidget, self).__call__(field, **kwargs)


class UTCWidget(widgets.TextInput):
    """ TextInput with a hidden input for UTC date/datetime/date values """
    def __call__(self, field, **kwargs):
        html = []

        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        kwargs.setdefault('data-role', u'datetimepicker')
        kwargs.setdefault('data-date-format', u'YYYY-MM-DD HH:mm:ss')

        # create id for hidden input (for UTC)
        utc_id = kwargs['id'] + '-utc'
        kwargs.setdefault('data-utc-input', utc_id)

        # remove "name" from 1st input field, so values aren't processed
        html.append('<input %s>' % self.html_params(**kwargs))

        # this input's value is set by form.js as UTC, it will be processed
        html.append('<input %s>' % self.html_params(id=utc_id,
                                                    name=field.name,
                                                    type="hidden"))

        return widgets.HTMLString(' '.join(html))


class DatePickerWidget(widgets.TextInput):
    """ Date picker widget. Requires: daterangepicker.js and form.js """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'datepicker')
        kwargs.setdefault('data-date-format', u'YYYY-MM-DD')
        return super(DatePickerWidget, self).__call__(field, **kwargs)


class DateTimePickerWidget(widgets.TextInput):
    """ Datetime picker widget. Requires: daterangepicker.js and form.js """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'datetimepicker')
        kwargs.setdefault('data-date-format', u'YYYY-MM-DD HH:mm:ss')
        return super(DateTimePickerWidget, self).__call__(field, **kwargs)


class UTCDateTimePickerWidget(DateTimePickerWidget, UTCWidget):
    """ DateTimePickerWidget with hidden field for UTC """
    pass


class TimePickerWidget(widgets.TextInput):
    """ Time picker widget. Requires: daterangepicker.js and form.js """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', u'timepicker')
        kwargs.setdefault('data-date-format', u'HH:mm:ss')
        return super(TimePickerWidget, self).__call__(field, **kwargs)


class UTCTimePickerWidget(TimePickerWidget, UTCWidget):
    """ TimePickerWidget with hidden field for UTC """
    pass


class RenderTemplateWidget(object):
    """
        WTForms widget that renders Jinja2 template
    """
    def __init__(self, template):
        """
            Constructor

            :param template:
                Template path
        """
        self.template = template

    def __call__(self, field, **kwargs):
        ctx = _request_ctx_stack.top
        jinja_env = ctx.app.jinja_env

        kwargs.update({
            'field': field,
            '_gettext': gettext,
            '_ngettext': ngettext,
            'h': h,
        })

        template = jinja_env.get_template(self.template)
        return template.render(kwargs)
