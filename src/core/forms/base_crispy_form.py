from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class BaseCrispyForm(forms.Form):
    SUBMIT_BUTTON_VALUE = "Submit"
    SUBMIT_BUTTON_CSS_CLASSES = "btn-no-bg btn-outline-primary"

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = "post"
        if self.SUBMIT_BUTTON_VALUE:
            self.helper.add_input(
                Submit(
                    name="action",
                    value=self.SUBMIT_BUTTON_VALUE,
                    css_class=self.SUBMIT_BUTTON_CSS_CLASSES,
                )
            )
        self.extra_init()

        super().__init__(*args, **kwargs)

    def extra_init(self):
        return
