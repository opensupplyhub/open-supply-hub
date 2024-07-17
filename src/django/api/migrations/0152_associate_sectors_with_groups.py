from django.db import migrations, models

from api.models import (
    Sector,
    SectorGroup,
)


def associate_sectors_with_groups(apps, schema_editor):
    sector_groups = {
        "Apparel, Footwear, Textiles": [
            "Apparel",
            "Apparel Accessories",
            "Footwear",
            "Home Accessories",
            "Home Textiles",
            "Leather",
            "Textiles",
            "Jewelry",
        ],
        "Agriculture, Food & Beverage": [
            "Agriculture",
            "Animal Production",
            "Aquaculture",
            "Beverages",
            "Biotechnology",
            "Crop Production",
            "Farming",
            "Food",
            "Food & Beverage",
            "Food Industry",
            "Food Manufacturing",
        ],
        "Technology": [
            "Computers",
            "Computing Infrastructure",
            "Information",
            "Technology",
            "Telecommunications",
            "Manufacturing",
        ],
        "Automotive": [
            "Automotive",
            "Automotive Parts",
            "Parts Dealers",
            "Manufacturing",
            "Trucking",
            "Components",
            "Repair",
        ],
        "Electronics": [
            "Electronics",
            "Electrical Devices",
            "Consumer Electronics",
            "Electronic Product Manufacturing",
            "Components",
            "Repair",
            "Manufacturing",
        ],
        "Energy": [
            "Electricity",
            "Energy",
            "Energy Production & Utilities",
            "Gas",
            "Oil & Gas",
            "Renewable Energy",
            "Solar Energy",
            "Utilities",
        ],
        "Utilities": ["Utilities", "Water Utilities"],
        "Mining": [
            "Coal",
            "Commodities",
            "Gas",
            "Jewelry",
            "Manufacturing",
            "Material Production",
            "Metal Manufacturing",
            "Mining",
            "Oil & Gas",
            "Pipeline Transportation",
            "Quarrying",
        ],
        "Construction": [
            "Building Construction",
            "Building Materials",
            "Civil Engineering Construction",
            "Components",
            "Construction",
            "Equipment",
            "Maintenance",
            "Pipeline Transportation",
            "Specialty Trade Contractors",
            "Transportation Equipment",
            "Trucking",
        ],
        "Cosmetics": [
            "Beauty Products",
            "Chemicals",
            "Personal Care Products",
        ],
        "Durable Goods": [
            "Appliances",
            "Durable Goods",
            "Hard Goods",
            "Home",
            "Machinery Manufacturing",
            "Maintenance",
            "Manufacturing",
            "Repair",
            "Technical Services",
        ],
        "Transportation": [
            "Air Transportation",
            "Equipment",
            "Ground Passenger Transportation",
            "Pipeline Transportation",
            "Rail Transportation",
            "Transportation Equipment",
            "Trucking",
            "Maritime Transportation",
        ],
        "Aerospace": ["Aerospace", "Air Transportation"],
        "Forestry": [
            "Forestry",
            "Furniture",
            "Home Accessories",
            "Home Furnishings",
            "Logging",
            "Manufacturing",
            "Material Production",
            "Paper Products",
            "Wood Products",
        ],
        "Press": ["Books", "Paper Products", "Printing"],
        "Health": [
            "Healthcare",
            "Hospitals",
            "Medical Equipment & Services",
            "Nursing",
            "Pharmaceuticals",
        ],
        "Entertainment": [
            "Arts",
            "Arts & Entertainment",
            "Entertainment",
            "Recreation",
        ],
        "Accommodation": ["Accommodation", "Renting"],
        "Finance": ["Banking", "Finance", "Financial Services"],
        "General Merchandise": [
            "Commodities",
            "Consumer Products",
            "Garden Tools",
            "General Merchandise",
            "Hobby",
            "Merchant Wholesalers",
            "Multi-Category",
            "Musical Instruments",
            "Nondurable Goods",
            "Plastics",
            "Rubber Products",
            "Supplies Dealers",
            "Toys",
            "Wholesale Trade",
        ],
        "Storage": ["Storage", "Warehousing"],
        "Sporting Goods": ["Sporting Goods", "Sports Equipment"],
        "Education, Research, Services": [
            "Archives",
            "Educational Services",
            "International Affairs",
            "Professional Services",
            "Research",
            "Technical and Scientific Activities",
        ],
        "Other": [
            "Allied Products",
            "Hunting",
            "Tobacco Products",
            "Unspecified",
        ],
    }

    sectors = Sector.objects.all()
    print('sectors >>>', sectors)

    for sector in sectors:
        print('sector >>>', sector)
        for group_name, sector_names in sector_groups.items():
            if sector.name in sector_names:
                group_instance, created = SectorGroup.objects.get_or_create(
                    name=group_name
                )
                sector.groups.add(group_instance)


def revert_changes(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0151_add_sector_group_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='sector',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                related_name='sectors',
                to='api.SectorGroup',
                help_text='The sector groups to which this sector belongs.',
            ),
        ),
        migrations.RunPython(associate_sectors_with_groups, revert_changes),
    ]
