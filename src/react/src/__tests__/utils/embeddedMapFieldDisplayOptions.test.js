import {
    combineEmbedAndNonstandardFields,
    formatEmbedConfigForServer,
    formatExistingFields,
} from '../../util/embeddedMap';

describe('embedded map field display options', () => {
    const base = { width: '600', fullWidth: false, height: '400' };

    it('reads the display options saved on a field', () => {
        const [field] = formatExistingFields([
            {
                column_name: 'brand_note',
                display_name: 'Brand note',
                visible: true,
                order: 0,
                searchable: false,
                show_in_list: true,
                display_as: 'blurb',
            },
        ]);

        expect(field.showInList).toBe(true);
        expect(field.displayAs).toBe('blurb');
    });

    it('falls back to "not in the list, shown as text" for older fields', () => {
        const [field] = formatExistingFields([
            {
                column_name: 'parent_company',
                display_name: 'Parent Company',
                visible: true,
                order: 0,
                searchable: true,
            },
        ]);

        expect(field.showInList).toBe(false);
        expect(field.displayAs).toBe('text');
    });

    describe('fields with data', () => {
        const saved = [
            {
                column_name: 'processing_type',
                display_name: 'Processing Type',
                visible: true,
                order: 0,
                searchable: false,
            },
            {
                column_name: 'project',
                display_name: 'Initiatives',
                visible: true,
                order: 1,
                searchable: true,
            },
        ];
        const all = ['processing_type', 'project', 'parent_company', 'tier'];

        it('keeps every field and flags the ones with data', () => {
            const fields = combineEmbedAndNonstandardFields(saved, all, [
                'project',
                'tier',
            ]);
            const flags = Object.fromEntries(
                fields.map(f => [f.columnName, f.hasData]),
            );

            expect(flags).toEqual({
                project: true,
                tier: true,
                processing_type: false,
                parent_company: false,
            });
        });

        it('lists the fields with data first, in a gapless order', () => {
            const fields = combineEmbedAndNonstandardFields(saved, all, [
                'project',
                'tier',
            ]);

            expect(fields.slice(0, 2).map(f => f.hasData)).toEqual([
                true,
                true,
            ]);
            expect(fields[0].columnName).toBe('project');
            expect(fields.map(f => f.order)).toEqual([0, 1, 2, 3]);
        });

        it('does not flag fields when no data information is given', () => {
            const fields = combineEmbedAndNonstandardFields(saved, all);

            expect(fields.map(f => f.columnName)).toContain('processing_type');
            expect(fields.every(f => f.hasData === undefined)).toBe(true);
        });
    });

    it('gives new nonstandard fields the default display options', () => {
        const fields = combineEmbedAndNonstandardFields([], ['my_column']);

        expect(fields[0].showInList).toBe(false);
        expect(fields[0].displayAs).toBe('text');
    });

    it('sends the display options to the server', () => {
        const payload = formatEmbedConfigForServer(base, [
            {
                columnName: 'project',
                displayName: 'Initiatives',
                visible: true,
                searchable: true,
                order: 0,
                showInList: true,
                displayAs: 'tags',
            },
        ]);

        expect(payload.embed_fields[0].show_in_list).toBe(true);
        expect(payload.embed_fields[0].display_as).toBe('tags');
    });

    it('sends the defaults when a field has no display options', () => {
        const payload = formatEmbedConfigForServer(base, [
            {
                columnName: 'project',
                displayName: 'Initiatives',
                visible: true,
                searchable: true,
                order: 0,
            },
        ]);

        expect(payload.embed_fields[0].show_in_list).toBe(false);
        expect(payload.embed_fields[0].display_as).toBe('text');
    });
});
