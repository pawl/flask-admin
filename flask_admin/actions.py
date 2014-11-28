from flask import request, redirect


from flask.ext.admin import tools
from flask.ext.admin._compat import text_type


def action(name, text, confirmation=None, dropdown=True):
    """
        Use this decorator to expose actions that span more than one
        entity (model, file, etc)

        :param name:
            Action name
        :param text:
            Action text.
        :param confirmation:
            Confirmation text. If not provided, action will be executed
            unconditionally.
        :param dropdown:
            Determines whether the action appears in the dropdown.
            If not provided, the action will appear in the dropdown.
    """
    def wrap(f):
        f._action = (name, text, confirmation, dropdown)
        return f

    return wrap


class ActionsMixin(object):
    """
        Actions mixin.

        In some cases, you might work with more than one "entity" (model, file, etc) in
        your admin view and will want to perform actions on a group of entities simultaneously.

        In this case, you can add this functionality by doing this:
        1. Add this mixin to your administrative view class
        2. Call `init_actions` in your class constructor
        3. Expose actions view
        4. Import `actions.html` library and add call library macros in your template
    """

    def __init__(self):
        """
            Default constructor.
        """
        self._actions = []
        self._actions_data = {}

    def init_actions(self):
        """
            Initialize list of actions for the current administrative view.
        """
        self._actions = []
        self._actions_data = {}

        for p in dir(self):
            attr = tools.get_dict_attr(self, p)

            if hasattr(attr, '_action'):
                name, text, desc, dropdown = attr._action

                self._actions.append((name, text, dropdown))

                # TODO: Use namedtuple
                # Reason why we need getattr here - what's in attr is not
                # bound to the object.
                self._actions_data[name] = (getattr(self, p), text, desc, dropdown)

    def is_action_allowed(self, name):
        """
            Verify if action with `name` is allowed.

            :param name:
                Action name
        """
        return True

    def get_actions_list(self):
        """
            Return a list and a dictionary of allowed actions.
        """
        actions = []
        actions_confirmation = {}

        for act in self._actions:
            name, text, dropdown = act

            if self.is_action_allowed(name):
                actions.append((name, text_type(text), dropdown))

                confirmation = self._actions_data[name][2]
                if confirmation:
                    actions_confirmation[name] = text_type(confirmation)

        return actions, actions_confirmation

    def handle_action(self, return_view=None):
        """
            Handle action request.

            :param return_view:
                Name of the view to return to after the request.
                If not provided, will return user to the index view.
        """
        action = request.form.get('action')
        ids = request.form.getlist('rowid')

        handler = self._actions_data.get(action)

        if handler and self.is_action_allowed(action):
            response = handler[0](ids)

            if response is not None:
                return response

        if not return_view:
            url = self.get_url('.' + self._default_view)
        else:
            url = self.get_url('.' + return_view)

        return redirect(url)
