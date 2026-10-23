import json


def generate_json(taxonomy: dict) -> bytes:
    '''Serialize taxonomy tree to JSON bytes for S3 upload.'''
    return json.dumps(
        {'sections': taxonomy['sections']},
        ensure_ascii=False,
    ).encode('utf-8')
