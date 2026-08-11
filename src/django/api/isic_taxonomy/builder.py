def display_label(code: str, label: str) -> str:
    return f'{code} - {label}'


def build_taxonomy(rows: list[dict[str, str]]) -> dict:
    '''
    Build the nested ISIC Rev 4 taxonomy tree from validated row dicts.

    Output matches the schema used by isicRev4Taxonomy.js and isic_rev4.json.
    '''
    sections: dict[str, dict] = {}

    for row in rows:
        section_code = row['section'].strip().upper()
        section_label = row['section_label'].strip()
        class_code = row['4-digits'].strip().zfill(4)
        division_code = class_code[:2]
        group_code = class_code[:3]
        division_label = row['division_label'].strip()
        group_label = row['group_label'].strip()
        class_label = row['description'].strip()

        section = sections.setdefault(section_code, {
            'code': section_code,
            'label': section_label,
            'displayLabel': display_label(section_code, section_label),
            'kind': 'section',
            'divisions': {},
        })
        divisions = section['divisions']
        division = divisions.setdefault(division_code, {
            'code': division_code,
            'label': division_label,
            'displayLabel': display_label(division_code, division_label),
            'kind': 'division',
            'sectionCode': section_code,
            'groups': {},
        })
        groups = division['groups']
        group = groups.setdefault(group_code, {
            'code': group_code,
            'label': group_label,
            'displayLabel': display_label(group_code, group_label),
            'kind': 'group',
            'sectionCode': section_code,
            'divisionCode': division_code,
            'classes': {},
        })
        classes = group['classes']
        classes[class_code] = {
            'code': class_code,
            'label': class_label,
            'displayLabel': display_label(class_code, class_label),
            'kind': 'class',
            'sectionCode': section_code,
            'divisionCode': division_code,
            'groupCode': group_code,
        }

    section_list = []
    for section_code in sorted(sections.keys()):
        section = sections[section_code]
        division_list = []
        for division_code in sorted(section['divisions'].keys()):
            division = section['divisions'][division_code]
            group_list = []
            for group_code in sorted(division['groups'].keys()):
                group = division['groups'][group_code]
                class_list = [
                    group['classes'][class_code]
                    for class_code in sorted(group['classes'].keys())
                ]
                group_list.append({
                    'code': group['code'],
                    'label': group['label'],
                    'displayLabel': group['displayLabel'],
                    'kind': group['kind'],
                    'sectionCode': group['sectionCode'],
                    'divisionCode': group['divisionCode'],
                    'classes': class_list,
                })
            division_list.append({
                'code': division['code'],
                'label': division['label'],
                'displayLabel': division['displayLabel'],
                'kind': division['kind'],
                'sectionCode': division['sectionCode'],
                'groups': group_list,
            })
        section_list.append({
            'code': section['code'],
            'label': section['label'],
            'displayLabel': section['displayLabel'],
            'kind': section['kind'],
            'divisions': division_list,
        })

    return {'sections': section_list}


def count_taxonomy_levels(taxonomy: dict) -> dict[str, int]:
    sections = taxonomy.get('sections', [])
    division_count = 0
    group_count = 0
    class_count = 0

    for section in sections:
        for division in section.get('divisions', []):
            division_count += 1
            for group in division.get('groups', []):
                group_count += 1
                class_count += len(group.get('classes', []))

    return {
        'section_count': len(sections),
        'division_count': division_count,
        'group_count': group_count,
        'class_count': class_count,
    }
