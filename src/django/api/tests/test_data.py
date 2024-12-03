parsed_city_hall_data = {
    "geocoded_point": {
        "lat": 39.9525839,
        "lng": -75.1652215,
    },
    "geocoded_address": "Philadelphia, PA, USA",
    "full_response": {
        "results": [
            {
                "address_components": [
                    {
                        "long_name": "Philadelphia",
                        "short_name": "Philadelphia",
                        "types": [
                            "locality",
                            "political",
                        ],
                    },
                    {
                        "long_name": "Philadelphia County",
                        "short_name": "Philadelphia County",
                        "types": [
                            "administrative_area_level_2",
                            "political",
                        ],
                    },
                    {
                        "long_name": "Pennsylvania",
                        "short_name": "PA",
                        "types": [
                            "administrative_area_level_1",
                            "political",
                        ],
                    },
                    {
                        "long_name": "United States",
                        "short_name": "US",
                        "types": [
                            "country",
                            "political",
                        ],
                    },
                ],
                "formatted_address": "Philadelphia, PA, USA",
                "geometry": {
                    "bounds": {
                        "northeast": {
                            "lat": 40.1379919,
                            "lng": -74.9557629,
                        },
                        "southwest": {
                            "lat": 39.8670041,
                            "lng": -75.280303,
                        },
                    },
                    "location": {
                        "lat": 39.9525839,
                        "lng": -75.1652215,
                    },
                    "location_type": "APPROXIMATE",
                    "viewport": {
                        "northeast": {
                            "lat": 40.1379919,
                            "lng": -74.9557629,
                        },
                        "southwest": {
                            "lat": 39.8670041,
                            "lng": -75.280303,
                        },
                    },
                },
                "place_id": "ChIJ60u11Ni3xokRwVg-jNgU9Yk",
                "types": [
                    "locality",
                    "political",
                ],
            }
        ],
        "status": "OK",
    },
    "result_count": 1,
}

geocoding_data = {
    "results": [
        {
            "address_components": [
                {
                    "long_name": "990",
                    "short_name": "990",
                    "types": ["street_number"],
                },
                {
                    "long_name": "Spring Garden Street",
                    "short_name": "Spring Garden St",
                    "types": ["route"],
                },
                {
                    "long_name": "Center City",
                    "short_name": "Center City",
                    "types": ["neighborhood", "political"],
                },
                {
                    "long_name": "Philadelphia",
                    "short_name": "Philadelphia",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "Philadelphia County",
                    "short_name": "Philadelphia County",
                    "types": ["administrative_area_level_2", "political"],
                },
                {
                    "long_name": "Pennsylvania",
                    "short_name": "PA",
                    "types": ["administrative_area_level_1", "political"],
                },
                {
                    "long_name": "United States",
                    "short_name": "US",
                    "types": ["country", "political"],
                },
                {
                    "long_name": "19123",
                    "short_name": "19123",
                    "types": ["postal_code"],
                },
            ],
            "formatted_address": "990 Spring Garden St, "
            "Philadelphia, PA 19123, USA",
            "geometry": {
                "bounds": {
                    "northeast": {
                        "lat": 39.9614743,
                        "lng": -75.15379639999999,
                    },
                    "southwest": {"lat": 39.9611391, "lng": -75.1545269},
                },
                "location": {"lat": 39.961265, "lng": -75.15412760000001},
                "location_type": "ROOFTOP",
                "viewport": {
                    "northeast": {
                        "lat": 39.9626556802915,
                        "lng": -75.1528126697085,
                    },
                    "southwest": {
                        "lat": 39.9599577197085,
                        "lng": -75.1555106302915,
                    },
                },
            },
            "place_id": "ChIJ8cV_ZH_IxokRA_ETpdB5R3Y",
            "types": ["premise"],
        }
    ],
    "status": "OK",
}

geocoding_data_no_country = {
    "results": [
        {
            "address_components": [
                {
                    "long_name": "4WHM+QCX",
                    "short_name": "4WHM+QCX",
                    "types": ["plus_code"],
                },
                {
                    "long_name": "Famagusta",
                    "short_name": "Famagusta",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "99450",
                    "short_name": "99450",
                    "types": ["postal_code"],
                },
            ],
            "formatted_address": "4WHM+QCX, Famagusta 99450",
            "geometry": {
                "location": {"lat": 35.1294866, "lng": 33.9336133},
                "location_type": "GEOMETRIC_CENTER",
                "viewport": {
                    "northeast": {
                        "lat": 35.1308355802915,
                        "lng": 33.9349622802915,
                    },
                    "southwest": {
                        "lat": 35.1281376197085,
                        "lng": 33.9322643197085,
                    },
                },
            },
            "partial_match": True,
            "place_id": "ChIJDzTqezLI3xQRW5kjGEGLRzA",
            "types": ["establishment", "point_of_interest"],
        }
    ],
    "status": "OK",
}

geocoding_data_second_country = {
    "results": [
        {
            "address_components": [
                {
                    "long_name": "Noor Bagh",
                    "short_name": "Noor Bagh",
                    "types": [
                        "political",
                        "sublocality",
                        "sublocality_level_1",
                    ],
                },
                {
                    "long_name": "Srinagar",
                    "short_name": "Srinagar",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "190009",
                    "short_name": "190009",
                    "types": ["postal_code"],
                },
            ],
            "formatted_address": "Noor Bagh, Srinagar 190009",
            "geometry": {
                "bounds": {
                    "northeast": {"lat": 34.07490560000001, "lng": 74.8043599},
                    "southwest": {"lat": 34.0734423, "lng": 74.8023449},
                },
                "location": {"lat": 34.0742387, "lng": 74.8035549},
                "location_type": "APPROXIMATE",
                "viewport": {
                    "northeast": {
                        "lat": 34.07552293029151,
                        "lng": 74.8047013802915,
                    },
                    "southwest": {
                        "lat": 34.07282496970851,
                        "lng": 74.80200341970848,
                    },
                },
            },
            "partial_match": True,
            "place_id": "ChIJmQlkN-2P4TgR6u3glWeOMTE",
            "types": ["political", "sublocality", "sublocality_level_1"],
        },
        {
            "address_components": [
                {
                    "long_name": "Kaliakair",
                    "short_name": "Kaliakair",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "Gazipur District",
                    "short_name": "Gazipur District",
                    "types": ["administrative_area_level_2", "political"],
                },
                {
                    "long_name": "Dhaka Division",
                    "short_name": "Dhaka Division",
                    "types": ["administrative_area_level_1", "political"],
                },
                {
                    "long_name": "Bangladesh",
                    "short_name": "BD",
                    "types": ["country", "political"],
                },
            ],
            "formatted_address": "Kaliakair, Bangladesh",
            "geometry": {
                "bounds": {
                    "northeast": {"lat": 24.0840819, "lng": 90.2365494},
                    "southwest": {"lat": 24.0535966, "lng": 90.2030754},
                },
                "location": {"lat": 24.0694528, "lng": 90.2221213},
                "location_type": "APPROXIMATE",
                "viewport": {
                    "northeast": {"lat": 24.0840819, "lng": 90.2365494},
                    "southwest": {"lat": 24.0535966, "lng": 90.2030754},
                },
            },
            "partial_match": True,
            "place_id": "ChIJTfs3ierjVTcRysKYnbOKmZM",
            "types": ["locality", "political"],
        },
    ],
    "status": "OK",
}

listitem_geocode_data = {
    "results": [
        {
            "address_components": [
                {
                    "long_name": "Linjiacunzhen",
                    "short_name": "Linjiacunzhen",
                    "types": [
                        "political",
                        "sublocality",
                        "sublocality_level_2",
                    ],
                },
                {
                    "long_name": "Zhucheng",
                    "short_name": "Zhucheng",
                    "types": [
                        "political",
                        "sublocality",
                        "sublocality_level_1",
                    ],
                },
                {
                    "long_name": "Weifang",
                    "short_name": "Weifang",
                    "types": ["locality", "political"],
                },
                {
                    "long_name": "Shandong",
                    "short_name": "Shandong",
                    "types": ["administrative_area_level_1", "political"],
                },
                {
                    "long_name": "China",
                    "short_name": "CN",
                    "types": ["country", "political"],
                },
                {
                    "long_name": "262232",
                    "short_name": "262232",
                    "types": ["postal_code"],
                },
            ],
            "formatted_address": "Linjiacunzhen, Zhucheng, "
            + "Weifang, Shandong, China, 262232",
            "geometry": {
                "location": {"lat": 35.994813, "lng": 119.65418},
                "location_type": "APPROXIMATE",
                "viewport": {
                    "northeast": {"lat": 36.0038401, "lng": 119.6701874},
                    "southwest": {"lat": 35.9857849, "lng": 119.6381726},
                },
            },
            "partial_match": True,
            "place_id": "ChIJV5SPiTEkvjUR7ErhmnSRTR8",
            "types": ["political", "sublocality", "sublocality_level_2"],
        },
        {
            "address_components": [
                {
                    "long_name": "396210",
                    "short_name": "396210",
                    "types": ["postal_code"],
                },
                {
                    "long_name": "Daman",
                    "short_name": "Daman",
                    "types": ["administrative_area_level_2", "political"],
                },
                {
                    "long_name": "Dadra and Nagar Haveli and Daman and Diu",
                    "short_name": "DH",
                    "types": ["administrative_area_level_1", "political"],
                },
                {
                    "long_name": "India",
                    "short_name": "IN",
                    "types": ["country", "political"],
                },
            ],
            "formatted_address": "Dadra and Nagar Haveli and Daman and "
            + "Diu 396210, India",
            "geometry": {
                "bounds": {
                    "northeast": {"lat": 20.4696847, "lng": 72.8751228},
                    "southwest": {"lat": 20.4051972, "lng": 72.82805549999999},
                },
                "location": {"lat": 20.4346424, "lng": 72.8456399},
                "location_type": "APPROXIMATE",
                "viewport": {
                    "northeast": {"lat": 20.4696847, "lng": 72.8751228},
                    "southwest": {"lat": 20.4051972, "lng": 72.82805549999999},
                },
            },
            "partial_match": True,
            "place_id": "ChIJ8d4EeIra4DsR3xkUSZh_-ng",
            "types": ["postal_code"],
        },
    ],
    "status": "OK",
}

geocoding_no_results = {
    'results': [],
    'status': 'ZERO_RESULTS'
}
