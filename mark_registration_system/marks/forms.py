from django import forms

class MarkEntryForm(forms.Form):
    module_code = forms.CharField(max_length=20, label="Module Code")
    module_name = forms.CharField(max_length=100, label="Module Name")
    cw1_marks = forms.IntegerField(label="Coursework 1 Marks")
    cw2_marks = forms.IntegerField(label="Coursework 2 Marks")
    cw3_marks = forms.IntegerField(label="Coursework 3 Marks")
    student_id = forms.CharField(max_length=20, label="Student ID")
    student_name = forms.CharField(max_length=100, label="Student Name")
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')], label="Gender")
    date_of_entry = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Date of Entry")

#Ensure that coursework marks are within a valid range (e.g., 0–100).
    def clean_cw1_marks(self):
        cw1 = self.cleaned_data.get('cw1_marks')
        if cw1 < 0 or cw1 > 100:
            raise forms.ValidationError("Coursework 1 Marks must be between 0 and 100.")
        return cw1

    def clean_cw2_marks(self):
        cw2 = self.cleaned_data.get('cw2_marks')
        if cw2 < 0 or cw2 > 100:
            raise forms.ValidationError("Coursework 2 Marks must be between 0 and 100.")
        return cw2

    def clean_cw3_marks(self):
        cw3 = self.cleaned_data.get('cw3_marks')
        if cw3 < 0 or cw3 > 100:
            raise forms.ValidationError("Coursework 3 Marks must be between 0 and 100.")
        return cw3