import json
import random
from django.views.generic import DetailView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from notes.models import Note
from ai_engine.models import GeneratedQuestion
from .models import PracticeTest, PracticeAttempt, UsageLog
from .forms import PracticeTestForm


class CreateTestView(LoginRequiredMixin, View):
    def get(self, request):
        note_id = request.GET.get('note')
        if not note_id:
            messages.error(request, 'Select a note first to create a test.')
            return redirect('note_list')
        note = get_object_or_404(Note, pk=note_id, user=request.user)
        mcqs = list(GeneratedQuestion.objects.filter(note=note, user=request.user, question_type='mcq'))
        if not mcqs:
            messages.error(request, 'No MCQs generated for this note yet.')
            return redirect('note_detail', pk=note.pk)
        form = PracticeTestForm(initial={
            'title': f'{note.title} Quiz',
            'question_count': min(10, len(mcqs)),
            'duration_minutes': 30,
        })
        return render(request, 'tests/create_test.html', {'form': form, 'note': note, 'mcq_count': len(mcqs)})

    def post(self, request):
        note_id = request.GET.get('note')
        if not note_id:
            messages.error(request, 'Select a note first.')
            return redirect('note_list')
        note = get_object_or_404(Note, pk=note_id, user=request.user)
        mcqs = list(GeneratedQuestion.objects.filter(note=note, user=request.user, question_type='mcq'))
        if not mcqs:
            messages.error(request, 'No MCQs generated for this note yet.')
            return redirect('note_detail', pk=note.pk)
        form = PracticeTestForm(request.POST)
        if form.is_valid():
            count = min(form.cleaned_data['question_count'], len(mcqs))
            random.shuffle(mcqs)
            selected = mcqs[:count]
            test = form.save(commit=False)
            test.user = request.user
            test.note = note
            test.save()
            test.questions.set(selected)
            UsageLog.objects.create(user=request.user, action='test_created', detail={'test_id': test.id, 'note_id': note.id, 'count': count})
            messages.success(request, f'Test created with {count} questions!')
            return redirect('take_test', pk=test.pk)
        return render(request, 'tests/create_test.html', {'form': form, 'note': note, 'mcq_count': len(mcqs)})


class TakeTestView(LoginRequiredMixin, DetailView):
    model = PracticeTest
    template_name = 'tests/take_test.html'
    context_object_name = 'test'

    def get_queryset(self):
        return PracticeTest.objects.filter(user=self.request.user).prefetch_related('questions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        context['duration_seconds'] = self.object.duration_minutes * 60
        return context


class SubmitTestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        test = get_object_or_404(PracticeTest, pk=pk, user=request.user)
        answers = json.loads(request.POST.get('answers', '{}'))
        time_taken = int(request.POST.get('time_taken', 0))
        questions = test.questions.all()
        correct_count = 0
        total = questions.count()
        for q in questions:
            user_answer = answers.get(str(q.id))
            if user_answer is not None:
                if q.question_type == 'mcq':
                    if str(user_answer) == str(q.correct_answer):
                        correct_count += 1
                else:
                    if user_answer.strip().lower() == q.correct_answer.strip().lower():
                        correct_count += 1
        score = correct_count
        percentage = (correct_count / total * 100) if total > 0 else 0
        attempt = PracticeAttempt.objects.create(
            user=request.user,
            test=test,
            answers=answers,
            score=score,
            total_questions=total,
            correct_count=correct_count,
            percentage=round(percentage, 2),
            time_taken_seconds=time_taken,
            completed_at=timezone.now(),
            is_completed=True,
        )
        UsageLog.objects.create(
            user=request.user,
            action='test_attempt',
            detail={'test_id': test.id, 'score': score, 'total': total}
        )
        return redirect('test_result', pk=attempt.id)


class TestResultView(LoginRequiredMixin, DetailView):
    model = PracticeAttempt
    template_name = 'tests/test_result.html'
    context_object_name = 'attempt'

    def get_queryset(self):
        return PracticeAttempt.objects.filter(user=self.request.user).select_related('test')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.test.questions.all()
        return context


class TestHistoryView(LoginRequiredMixin, ListView):
    model = PracticeAttempt
    template_name = 'tests/test_history.html'
    context_object_name = 'attempts'
    paginate_by = 10

    def get_queryset(self):
        return PracticeAttempt.objects.filter(
            user=self.request.user, is_completed=True
        ).select_related('test').order_by('-completed_at')
