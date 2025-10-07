from django.core.management.base import BaseCommand
from properties.models import Property, PropertyType

MOCK_PROPERTIES = [
    {
        "title": "Luxury Family Home",
        "price": "395,000 INR",
        "location": "Lorem Ipsum",
        "bedrooms": 4,
        "bathrooms": 1,
        "area": "450 sqft",
        "status": "FOR SALE",
        "featured": True,
        "type": "3 BHK"
    },
    {
        "title": "Skyper Pool Apartment",
        "price": "280,000 INR",
        "location": "Lorem Ipsum",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": "450 sqft",
        "status": "FOR SALE",
        "type": "2 BHK"
    },
    {
        "title": "North Dillard Street",
        "price": "250 INR/month",
        "location": "Lorem Ipsum",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": "400 sqft",
        "status": "FOR RENT",
        "featured": True,
        "type": "Modern Villa"
    },
    {
        "title": "Eaton Garth Penthouse",
        "price": "280,000 INR",
        "location": "Lorem Ipsum",
        "bedrooms": 3,
        "bathrooms": 2,
        "area": "450 sqft",
        "status": "FOR SALE",
        "featured": True,
        "type": "3 BHK"
    },
    {
        "title": "New Apartment Nice View",
        "price": "200,000 INR",
        "location": "Lorem Ipsum",
        "bedrooms": 2,
        "bathrooms": 1,
        "area": "350 sqft",
        "status": "FOR SALE",
        "type": "Studio Apartment"
    },
]

class Command(BaseCommand):
    help = "Populate mock properties"

    def handle(self, *args, **kwargs):
        for prop in MOCK_PROPERTIES:
            ptype, _ = PropertyType.objects.get_or_create(name=prop["type"])
            Property.objects.get_or_create(
                title=prop["title"],
                defaults={
                    "property_type": ptype,
                    "price": prop["price"],
                    "location": prop["location"],
                    "bedrooms": prop["bedrooms"],
                    "bathrooms": prop["bathrooms"],
                    "area": prop["area"],
                    "status": "available" if prop["status"] == "FOR SALE" else "rented",
                    "listing_type": "sale" if prop["status"] == "FOR SALE" else "rent",
                    "featured": prop.get("featured", False),
                }
            )
        self.stdout.write(self.style.SUCCESS("Mock properties populated."))
