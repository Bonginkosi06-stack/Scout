from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core.auth_utils import get_student_id, get_student_profile
from documents.models import Document
from opportunities.models import Opportunity
from django.utils import timezone

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def review_application(request):
    """
    Prepare an assisted application for review.

    Nothing is submitted here. The endpoint retrieves information already
    stored for the authenticated student so the frontend can display a
    review screen before explicit confirmation.
    """
    opportunity_id = request.data.get("opportunity_id")

    if not opportunity_id:
        return Response(
           {"error": "opportunity_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Never trust a student ID supplied by the frontend.
    student_id = get_student_id(request.user)

    try:
         opportunity=Opportunity.objects.get(
            opportunity_id=opportunity_id,
            is_active=True,
            is_verified=True,
            closing_date__gte=timezone.now(),
        )
    except Opportunity.DoesNotExist:
        return Response(
            {"error": "Opportunity not found or unavailable."},
            status=status.HTTP_404_NOT_FOUND 
        )

    #Retrieve the student's existing profile.
    profile = get_student_profile(request.user)

    #Retrieve documents already uploaded by this student
    documents = Document.objects.filter(
        student_id=student_id,
        is_active=True,
    )

    document_data = [
        {
            "document_id": document.document_id,
            "document_type": document.document_type,
            "file_name": document.file_name,
        }
        for document in documents
    ]

    return Response(
        {
            "can_submit": True,
            "student": {
                "student_id": student_id,
                "profile": profile,
            },
            "opportunity": {
                "opportunity_id": opportunity.opportunity_id,
                "title": opportunity.title,
                "opportunity_type": opportunity.opportunity_type,
                "provider_id": opportunity.provider_id,
                "closing_date": opportunity.closing_date,
            },
            "documents": document_data,
            "message": (
                "Review the application details before confirming submission."
            ),
        },
        status=status.HTTP_200_OK,
    )