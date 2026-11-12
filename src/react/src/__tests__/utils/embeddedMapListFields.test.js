import {
    getListFields,
    MAX_BLURB_LENGTH,
    splitTagValues,
    truncateBlurb,
} from '../../util/embeddedMap';

describe('embedded map fields in the search results list', () => {
    const embedFields = [
        {
            column_name: 'brand_note',
            display_name: 'Brand note',
            visible: true,
            show_in_list: true,
            display_as: 'blurb',
            order: 2,
        },
        {
            column_name: 'project',
            display_name: 'Initiatives',
            visible: true,
            show_in_list: true,
            display_as: 'tags',
            order: 0,
        },
        {
            column_name: 'parent_company',
            display_name: 'Parent Company',
            visible: true,
            show_in_list: false,
            order: 1,
        },
        {
            column_name: 'hidden_column',
            display_name: 'Hidden',
            visible: false,
            show_in_list: true,
            order: 3,
        },
    ];
    const contributorFields = [
        { fieldName: 'project', label: 'Initiatives', value: 'HERhealth|RISE' },
        { fieldName: 'parent_company', label: 'Parent', value: 'Acme' },
        { fieldName: 'brand_note', label: 'Brand note', value: 'A note.' },
        { fieldName: 'hidden_column', label: 'Hidden', value: 'secret' },
    ];

    it('returns "In list" fields with a value, in the chosen order', () => {
        expect(getListFields(embedFields, contributorFields)).toEqual([
            {
                columnName: 'project',
                label: 'Initiatives',
                value: 'HERhealth|RISE',
                displayAs: 'tags',
            },
            {
                columnName: 'brand_note',
                label: 'Brand note',
                value: 'A note.',
                displayAs: 'blurb',
            },
        ]);
    });

    it('never returns a field that is not visible', () => {
        const columns = getListFields(embedFields, contributorFields).map(
            f => f.columnName,
        );

        expect(columns).not.toContain('hidden_column');
    });

    it('leaves out fields this facility has no value for', () => {
        const fields = getListFields(embedFields, [
            { fieldName: 'project', value: null },
            { fieldName: 'brand_note', value: '   ' },
        ]);

        expect(fields).toEqual([]);
    });

    it('returns nothing when there is no config or no data', () => {
        expect(getListFields(undefined, contributorFields)).toEqual([]);
        expect(getListFields(embedFields, undefined)).toEqual([]);
        expect(getListFields([], [])).toEqual([]);
    });

    it('defaults to text when a field has no display choice', () => {
        const fields = getListFields(
            [
                {
                    column_name: 'csc_brand',
                    display_name: 'Brand',
                    visible: true,
                    show_in_list: true,
                    order: 0,
                },
            ],
            [{ fieldName: 'csc_brand', value: 'Sorel' }],
        );

        expect(fields[0].displayAs).toBe('text');
    });
});

describe('splitTagValues', () => {
    it('splits on pipes, semicolons and commas and trims', () => {
        expect(splitTagValues('HERhealth| RISE ;Clean by Design, X')).toEqual([
            'HERhealth',
            'RISE',
            'Clean by Design',
            'X',
        ]);
    });

    it('drops empty parts', () => {
        expect(splitTagValues('A||B, ,')).toEqual(['A', 'B']);
    });
});

describe('truncateBlurb', () => {
    it('leaves a short blurb alone, trimmed', () => {
        expect(truncateBlurb('  A short note.  ')).toBe('A short note.');
    });

    it('caps a long blurb and marks it as cut', () => {
        const blurb = truncateBlurb('x'.repeat(MAX_BLURB_LENGTH + 50));

        expect(blurb.length).toBe(MAX_BLURB_LENGTH + 1);
        expect(blurb.endsWith('…')).toBe(true);
    });
});
