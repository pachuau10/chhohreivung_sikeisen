from django import forms
from .models import Note, Post


class NoteUploadForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'description', 'file', 'subject', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Biology Chapter 5 - Cell Division', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Brief description of what this note covers...', 'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be 10 MB or less.')
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'docx']:
                raise forms.ValidationError('Only PDF and DOCX files are allowed.')
        return file


class NoteSearchForm(forms.Form):
    q = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search notes...',
        'class': 'form-control',
    }))
    subject = forms.ChoiceField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Subject
        subjects = Subject.objects.all()
        self.fields['subject'].choices = [('', 'All Subjects')] + [(s.slug, s.name) for s in subjects]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'shared_note']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': "What's on your mind?", 'class': 'form-control border-0 bg-light rounded-3', 'style': 'resize:none;font-size:.9rem'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'shared_note': forms.Select(attrs={'class': 'form-select form-select-sm border-0 bg-light rounded-3', 'style': 'font-size:.85rem;color:var(--text-muted)'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['shared_note'].queryset = user.notes.all().order_by('-created_at')
            self.fields['shared_note'].empty_label = '-- Attach a note (optional) --'
            self.fields['shared_note'].label = ''
