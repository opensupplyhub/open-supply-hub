import React from 'react';
import DashboardFacilityCard from '../../components/DashboardFacilityCard';
import COLOURS from '../../util/COLOURS';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {
    dashboardFacilityCardTitles,
} from '../../util/constants';


describe('DashboardFacilityCard component', () => {
    const defaultProps = {
        updateOSID: jest.fn(),
        fetchFacility: jest.fn(),
        clearFacility: jest.fn(),
        osID:'BD2021113R7R87P',
        data: {
            "id": "BD2021113R7R87P",
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    90.418952,
                    23.896051
                ]
            },
            "properties": {
                "name": "Zaber & Zubair Fabrics Ltd",
                "address": "Pagar, Tongi, Gazipur Tongi, Gazipur Dhaka Gazipur 1710 Dhaka",
                "country_code": "BD",
                "os_id": "BD2021113R7R87P",
                "other_names": [
                    "Zaber & Zubair Fabric Ltd.",
                ],
                "other_addresses": [
                    "Pagar Tongi 1710 | GAZIPUR",
                ],
                "contributors": [
                    {
                        "id": 97,
                        "name": "Fair Factories Clearinghouse (FFC Factory List Oct 2022)",
                        "is_verified": false,
                        "contributor_name": "Fair Factories Clearinghouse",
                        "list_name": "FFC Factory List Oct 2022"
                    },
                ],
                "country_name": "Bangladesh",
                "claim_info": {
                    "id": 498,
                    "office": null,
                    "contact": null,
                    "facility": {
                        "sector": null,
                        "address": null,
                        "website": null,
                        "location": null,
                        "description": "Home textile",
                        "affiliations": null,
                        "name_english": null,
                        "phone_number": null,
                        "facility_type": null,
                        "minimum_order": null,
                        "product_types": null,
                        "workers_count": null,
                        "certifications": null,
                        "parent_company": {
                            "id": "Noman Group",
                            "name": "Noman Group"
                        },
                        "production_types": null,
                        "average_lead_time": null,
                        "other_facility_type": null,
                        "name_native_language": null,
                        "female_workers_percentage": null
                    },
                    "contributor": "Zaber and Zubair Fabrics Ltd"
                },
                "is_claimed": false,
                "other_locations": [
                    {
                        "lat": 23.8952576,
                        "lng": 90.42012659999999,
                        "contributor_id": 2238,
                        "contributor_name": "International Accord Foundation",
                        "notes": null
                    },
                ],
                "is_closed": null,
                "activity_reports": [],
                "contributor_fields": [],
                "new_os_id": null,
                "has_inexact_coordinates": false,
                "extended_fields": {
                    "name": [
                        {
                            "value": "Zaber & Zubair Fabrics Ltd",
                            "field_name": "name",
                            "contributor_id": 2238,
                            "contributor_name": "International Accord Foundation",
                            "updated_at": "2024-06-04T04:28:08.091814Z"
                        },
                    ],
                    "address": [                      {
                        "value": "Pagar, Tongi, Gazipur Tongi, Gazipur Dhaka",
                        "field_name": "address",
                        "contributor_id": 2238,
                        "contributor_name": "International Accord Foundation",
                        "updated_at": "2024-06-04T04:28:08.091814Z",
                        "is_from_claim": false
                    },],
                    "number_of_workers": [        {
                        "id": 2170641,
                        "is_verified": false,
                        "value": {
                            "max": 4001,
                            "min": 4001
                        },
                        "updated_at": "2024-08-12T08:25:58.725752Z",
                        "contributor_name": "H&M Group",
                        "contributor_id": 5993,
                        "value_count": 3,
                        "is_from_claim": false,
                        "field_name": "number_of_workers",
                        "verified_count": 0
                    },],
                    "native_language_name": [],
                    "facility_type": [                       {
                        "id": 2218875,
                        "is_verified": false,
                        "value": {
                            "raw_values": "Final Product Assembly",
                            "matched_values": [
                                [
                                    "PROCESSING_TYPE",
                                    "SKIPPED_MATCHING",
                                    null,
                                    "Final Product Assembly"
                                ]
                            ]
                        },
                        "updated_at": "2024-08-18T00:47:16.158542Z",
                        "contributor_name": "Marks & Spencer",
                        "contributor_id": 10104,
                        "value_count": 6,
                        "is_from_claim": false,
                        "field_name": "facility_type",
                        "verified_count": 0
                    },],
                    "processing_type": [{
                        "id": 2218876,
                        "is_verified": false,
                        "value": {
                            "raw_values": "Final Product Assembly",
                            "matched_values": [
                                [
                                    "PROCESSING_TYPE",
                                    "SKIPPED_MATCHING",
                                    null,
                                    "Final Product Assembly"
                                ]
                            ]
                        },
                        "updated_at": "2024-08-18T00:47:16.199354Z",
                        "contributor_name": "Marks & Spencer",
                        "contributor_id": 10104,
                        "value_count": 6,
                        "is_from_claim": false,
                        "field_name": "processing_type",
                        "verified_count": 0
                    },],
                    "product_type": [       {
                        "id": 2141616,
                        "is_verified": false,
                        "value": {
                            "raw_values": [
                                "Leisure",
                                "Tech"
                            ]
                        },
                        "updated_at": "2024-08-02T14:30:18.426821Z",
                        "contributor_name": "JD Williams and Company LTD trading as N Brown ",
                        "contributor_id": 1610,
                        "value_count": 4,
                        "is_from_claim": false,
                        "field_name": "product_type",
                        "verified_count": 0
                    },],
                    "parent_company": [
                        {
                        "id": 262674,
                        "is_verified": false,
                        "value": {
                            "name": "Noman Group",
                            "raw_value": "Noman Group"
                        },
                        "updated_at": "2022-11-14T00:45:27.294312Z",
                        "contributor_name": "Zaber and Zubair Fabrics Ltd",
                        "contributor_id": 3922,
                        "value_count": 2,
                        "is_from_claim": true,
                        "field_name": "parent_company",
                        "verified_count": 0
                    },]
                },
                "created_from": {
                    "created_at": "2020-03-06T09:31:31.443253Z",
                    "contributor": "a Multi-Stakeholder Initiative"
                },
                "sector": [                    {
                    "updated_at": "2024-08-18T00:46:41.082596Z",
                    "contributor_id": 10104,
                    "contributor_name": "Marks & Spencer",
                    "values": [
                        "Home"
                    ],
                    "is_from_claim": false
                },]
            }
        },
        fetching: false,
        error: null,
        handleEnterKeyPress: jest.fn(),
        title: dashboardFacilityCardTitles.targetFacilityToMerge,
        highlightBackground: false,
    };

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <DashboardFacilityCard {...{...defaultProps, ...props}}/>
        );

    it('renders without crashing', () => {
        renderComponent();
    });

    it('renders the facility title', () => {
        const { getByText } = renderComponent();

        expect(getByText(dashboardFacilityCardTitles.targetFacilityToMerge)).toBeInTheDocument();
    });


    it('renders the NOT claimed facility card without green background', () => {
        const { container } = renderComponent();

        expect(container.firstChild).not.toHaveStyle(`background:${COLOURS.GREEN}`)
    });

    it('renders the claimed facility card with green background', () => {
        const { container } = renderComponent({highlightBackground: true,
            data: {
                ...defaultProps.data,
                properties: {
                    ...defaultProps.data.properties,
                    is_claimed: true,
                },
            },});

        expect(container.firstChild).toHaveStyle(`background:${COLOURS.GREEN}`)
    });
});
