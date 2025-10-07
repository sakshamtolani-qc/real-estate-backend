from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class LeadSourcesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Dummy data, replace with real aggregation logic
        lead_sources = [
            {"source": "Email", "percentage": 50, "color": "#212121"},
            {"source": "Website", "percentage": 43, "color": "#E7C873"},
            {"source": "Phone", "percentage": 37, "color": "#D4AF37"},
            {"source": "Physical", "percentage": 37, "color": "#B794D6"},
            {"source": "Other", "percentage": 37, "color": "#7DD3E8"}
        ]
        return Response({"lead_sources": lead_sources})