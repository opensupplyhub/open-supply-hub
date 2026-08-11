import json


def generate_json(taxonomy: dict) -> bytes:
    '''Serialize taxonomy tree to JSON bytes for S3 upload.'''
    return json.dumps(
        {'sections': taxonomy['sections']},
        ensure_ascii=False,
    ).encode('utf-8')


def generate_js_bundle(taxonomy: dict) -> bytes:
    '''Generate the ES module bundle consumed by the React search UI.'''
    taxonomy_json = json.dumps(
        {'sections': taxonomy['sections']},
        ensure_ascii=False,
        indent=4,
    )
    body = (
        'export const ISIC_REV4_TAXONOMY = Object.freeze(\n'
        f'    {taxonomy_json}\n'
        ');\n'
    )
    return body.encode('utf-8')
