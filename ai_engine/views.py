import json
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from notes.models import Note
from .models import GeneratedQuestion, Flashcard, Summary
from .services import AIService
from tests.models import UsageLog


class GenerateMCQView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user)
        if not note.extracted_text:
            return JsonResponse({'error': 'No text content found. The document may not have been processed correctly. Try re-uploading.'}, status=400)
        profile = request.user.profile
        if not request.user.is_staff and profile.generations_remaining <= 0:
            return JsonResponse({
                'error': 'Limit reached', 'message': 'You\'ve used all your free AI generations for today. Upgrade to Premium for unlimited access.',
                'plan': profile.plan, 'upgrade_url': reverse('pricing'),
            }, status=429)
        service = AIService()
        data = service.generate_mcqs(note.extracted_text)
        if not data:
            return JsonResponse({'error': 'Failed to generate questions.'}, status=500)
        for item in data:
            GeneratedQuestion.objects.create(
                note=note,
                user=request.user,
                question_type='mcq',
                question_text=item.get('question', ''),
                options=item.get('options', []),
                correct_answer=str(item.get('correct', 0)),
                explanation=item.get('explanation', ''),
            )
        profile.ai_generations_used += 1
        profile.save()
        UsageLog.objects.create(user=request.user, action='ai_generation', detail={'type': 'mcq', 'note_id': note.id})
        return JsonResponse({'success': True, 'count': len(data)})


class GenerateShortQuestionsView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user)
        if not note.extracted_text:
            return JsonResponse({'error': 'No text content found. The document may not have been processed correctly. Try re-uploading.'}, status=400)
        profile = request.user.profile
        if not request.user.is_staff and profile.generations_remaining <= 0:
            return JsonResponse({
                'error': 'Limit reached', 'message': 'You\'ve used all your free AI generations for today. Upgrade to Premium for unlimited access.',
                'plan': profile.plan, 'upgrade_url': reverse('pricing'),
            }, status=429)
        service = AIService()
        data = service.generate_short_questions(note.extracted_text)
        if not data:
            return JsonResponse({'error': 'Failed to generate questions.'}, status=500)
        for item in data:
            GeneratedQuestion.objects.create(
                note=note,
                user=request.user,
                question_type='short',
                question_text=item.get('question', ''),
                correct_answer=item.get('answer', ''),
                explanation=item.get('explanation', ''),
            )
        profile.ai_generations_used += 1
        profile.save()
        UsageLog.objects.create(user=request.user, action='ai_generation', detail={'type': 'short', 'note_id': note.id})
        return JsonResponse({'success': True, 'count': len(data)})


class GenerateLongQuestionsView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user)
        if not note.extracted_text:
            return JsonResponse({'error': 'No text content found. The document may not have been processed correctly. Try re-uploading.'}, status=400)
        profile = request.user.profile
        if not request.user.is_staff and profile.generations_remaining <= 0:
            return JsonResponse({
                'error': 'Limit reached', 'message': 'You\'ve used all your free AI generations for today. Upgrade to Premium for unlimited access.',
                'plan': profile.plan, 'upgrade_url': reverse('pricing'),
            }, status=429)
        service = AIService()
        data = service.generate_long_questions(note.extracted_text)
        if not data:
            return JsonResponse({'error': 'Failed to generate questions.'}, status=500)
        for item in data:
            GeneratedQuestion.objects.create(
                note=note,
                user=request.user,
                question_type='long',
                question_text=item.get('question', ''),
                correct_answer=item.get('answer', ''),
                explanation=item.get('explanation', ''),
            )
        profile.ai_generations_used += 1
        profile.save()
        UsageLog.objects.create(user=request.user, action='ai_generation', detail={'type': 'long', 'note_id': note.id})
        return JsonResponse({'success': True, 'count': len(data)})


class GenerateFlashcardsView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user)
        if not note.extracted_text:
            return JsonResponse({'error': 'No text content found. The document may not have been processed correctly. Try re-uploading.'}, status=400)
        profile = request.user.profile
        if not request.user.is_staff and profile.generations_remaining <= 0:
            return JsonResponse({
                'error': 'Limit reached', 'message': 'You\'ve used all your free AI generations for today. Upgrade to Premium for unlimited access.',
                'plan': profile.plan, 'upgrade_url': reverse('pricing'),
            }, status=429)
        service = AIService()
        data = service.generate_flashcards(note.extracted_text)
        if not data:
            return JsonResponse({'error': 'Failed to generate flashcards.'}, status=500)
        for item in data:
            Flashcard.objects.create(
                note=note,
                user=request.user,
                front=item.get('front', ''),
                back=item.get('back', ''),
            )
        profile.ai_generations_used += 1
        profile.save()
        UsageLog.objects.create(user=request.user, action='ai_generation', detail={'type': 'flashcard', 'note_id': note.id})
        return JsonResponse({'success': True, 'count': len(data)})


class GenerateSummaryView(LoginRequiredMixin, View):
    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user)
        if not note.extracted_text:
            return JsonResponse({'error': 'No text content found. The document may not have been processed correctly. Try re-uploading.'}, status=400)
        profile = request.user.profile
        if not request.user.is_staff and profile.generations_remaining <= 0:
            return JsonResponse({
                'error': 'Limit reached', 'message': 'You\'ve used all your free AI generations for today. Upgrade to Premium for unlimited access.',
                'plan': profile.plan, 'upgrade_url': reverse('pricing'),
            }, status=429)
        service = AIService()
        content = service.generate_summary(note.extracted_text)
        if not content:
            return JsonResponse({'error': 'Failed to generate summary.'}, status=500)
        Summary.objects.create(
            note=note,
            user=request.user,
            content=content,
        )
        profile.ai_generations_used += 1
        profile.save()
        UsageLog.objects.create(user=request.user, action='ai_generation', detail={'type': 'summary', 'note_id': note.id})
        return JsonResponse({'success': True})


class AIGeneratedContentView(LoginRequiredMixin, View):
    def get(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user)
        mcqs = GeneratedQuestion.objects.filter(note=note, question_type='mcq')
        shorts = GeneratedQuestion.objects.filter(note=note, question_type='short')
        longs = GeneratedQuestion.objects.filter(note=note, question_type='long')
        flashcards = Flashcard.objects.filter(note=note)
        summaries = Summary.objects.filter(note=note)
        data = {
            'mcqs': [{'id': q.id, 'question': q.question_text, 'options': q.options, 'correct': q.correct_answer, 'explanation': q.explanation} for q in mcqs],
            'shorts': [{'id': q.id, 'question': q.question_text, 'answer': q.correct_answer, 'explanation': q.explanation} for q in shorts],
            'longs': [{'id': q.id, 'question': q.question_text, 'answer': q.correct_answer, 'explanation': q.explanation} for q in longs],
            'flashcards': [{'id': f.id, 'front': f.front, 'back': f.back, 'learned': f.is_learned} for f in flashcards],
            'summaries': [{'id': s.id, 'content': s.content} for s in summaries],
        }
        return JsonResponse(data)


class FlashcardStudyView(LoginRequiredMixin, View):
    def get(self, request, pk):
        from django.shortcuts import render
        note = get_object_or_404(Note, pk=pk, user=request.user)
        flashcards = list(Flashcard.objects.filter(note=note, user=request.user))
        return render(request, 'ai_engine/flashcard_study.html', {
            'note': note,
            'flashcards': flashcards,
        })


class MarkFlashcardLearnedView(LoginRequiredMixin, View):
    def post(self, request, pk):
        card = get_object_or_404(Flashcard, pk=pk, user=request.user)
        card.is_learned = request.POST.get('learned') == 'true'
        card.save()
        return JsonResponse({'success': True})


class ExportFlashcardsPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        note = get_object_or_404(Note, pk=pk, user=request.user)
        cards = list(Flashcard.objects.filter(note=note, user=request.user))

        if not cards:
            messages.error(request, 'No flashcards to export.')
            return redirect('note_detail', pk=note.pk)

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm, leftMargin=15*mm, rightMargin=15*mm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CardTitle', parent=styles['Heading4'], spaceAfter=4*mm, alignment=TA_CENTER, fontSize=14, textColor=colors.HexColor('#7C3AED'))
        front_style = ParagraphStyle('Front', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, leading=14, spaceBefore=2*mm, spaceAfter=2*mm)
        back_style = ParagraphStyle('Back', parent=styles['Normal'], fontSize=9, alignment=TA_LEFT, leading=12, textColor=colors.HexColor('#555555'))

        elements = []
        elements.append(Paragraph(f'{note.title} — Flashcards', title_style))
        elements.append(Spacer(1, 6*mm))

        for i, card in enumerate(cards):
            data = [
                [Paragraph(f'<b>Question:</b> {card.front}', front_style)],
                [Paragraph(f'<b>Answer:</b> {card.back}', back_style)],
            ]
            t = Table(data, colWidths=[170*mm])
            t.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('BACKGROUND', (0,0), (0,0), colors.HexColor('#F3EEFF')),
                ('BACKGROUND', (0,1), (0,1), colors.HexColor('#FAFAFA')),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,-1), 4*mm),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4*mm),
                ('LEFTPADDING', (0,0), (-1,-1), 4*mm),
                ('RIGHTPADDING', (0,0), (-1,-1), 4*mm),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 4*mm))

        doc.build(elements)
        buf.seek(0)

        from django.http import HttpResponse
        response = HttpResponse(buf.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{note.title}_flashcards.pdf"'
        return response
