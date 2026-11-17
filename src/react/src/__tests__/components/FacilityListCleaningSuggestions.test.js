import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import {
    ReadinessTracker,
    GroupTabs,
    ListFindings,
    Correction,
    Issue,
    Removal,
    SuggestionRows,
    plural,
    describeCode,
    codeGuide,
    codeHelp,
    tierOf,
    visibleRows,
    isAuto,
    TIER,
} from '../../components/FacilityListCleaningSuggestions';
import {
    GROUPS,
    ROWS,
    SUGGESTIONS,
    SUMMARY,
} from '../../util/testUtils/listCleaningFixtures';

describe('helpers', () => {
    test('plural, describeCode and the guides', () => {
        expect(plural(1, 'row')).toBe('1 row');
        expect(plural(2, 'row')).toBe('2 rows');
        expect(plural(3, 'fix', 'fixes')).toBe('3 fixes');
        expect(describeCode('whitespace+casing')).toBe(
            'extra spaces removed, capitalisation fixed',
        );
        expect(describeCode('made_up_code')).toBe('made up code');
        expect(codeGuide('address_po_box+pii').title).toBe('PO Box in the address');
        expect(codeGuide('nothing')).toBeNull();
        expect(codeHelp('pii')).toMatch(/personal/);
        expect(codeHelp('')).toBe('');
    });

    test('every flag the pipeline emits has an explainer and a way out', () => {
        const issues = [
            'empty_row', 'missing_name', 'missing_address', 'missing_country',
            'unknown_country', 'address_po_box', 'pii', 'too_long',
            'address_too_few', 'address_too_many', 'multiple_addresses',
            'country_address_mismatch', 'name_incomplete', 'name_too_many',
            'multiple_names', 'repeated_names', 'non_roman_characters',
            'sector_unrecognized', 'column_swap', 'spelling_uncertain',
        ];
        issues.forEach(code => {
            expect(codeGuide(code)).not.toBeNull();
            expect(codeHelp(code, 'name')).not.toBe('');
        });
        expect(codeHelp('name_too_many', 'name')).toMatch(/only the facility name.*remove the row/);
        // A code nobody wrote advice for still says what to do.
        expect(codeHelp('something_new', 'address')).toBe(
            'Fix the value so it holds only the address, or remove the row.',
        );
    });


    test('tiers: flags block, fixes and advisory notes are recommended', () => {
        const byCode = Object.fromEntries(GROUPS.map(g => [g.code, g]));
        expect(tierOf(byCode.address_po_box)).toBe(TIER.BLOCKS);
        expect(tierOf(byCode.duplicate)).toBe(TIER.AUTO);
        expect(tierOf(byCode.workers_format)).toBe(TIER.RECOMMENDED);
        expect(tierOf(byCode.repeated_names)).toBe(TIER.RECOMMENDED);
        expect(isAuto(SUGGESTIONS.country)).toBe(true);
        expect(isAuto(SUGGESTIONS.workers)).toBe(false);
    });

    test('visibleRows keeps rows with at least one matching suggestion', () => {
        const flagged = visibleRows(ROWS, s => s.kind === 'ISSUE');
        expect(flagged.map(r => r.row_number)).toEqual([3, 5]);
        expect(flagged[0].suggestions).toHaveLength(1);
    });
});

describe('ReadinessTracker', () => {
    test('leads with the rows that still need the contributor', () => {
        const onViewFixes = jest.fn();
        render(
            <ReadinessTracker
                summary={SUMMARY}
                applied={false}
                onViewFixes={onViewFixes}
            />,
        );
        expect(screen.getByText('Your review is 0% done')).toBeInTheDocument();
        expect(
            screen.getByText(/1 with required fixes · 2 with recommended fixes/),
        ).toBeInTheDocument();
        expect(
            screen.getByText(/fixed automatically \(2 automatic fixes\)/),
        ).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /View automatic fixes/ }));
        expect(onViewFixes).toHaveBeenCalled();
        expect(screen.getByRole('progressbar')).toHaveAttribute('value', '0');
    });

    test('says what to do once every row is decided', () => {
        const { rerender } = render(
            <ReadinessTracker
                summary={{ ...SUMMARY, rows_pending_review: 0, changes_unapplied: 4 }}
                applied={false}
                showingAuto
                onViewFixes={() => {}}
            />,
        );
        expect(
            screen.getByText('Review done: submit your list for manual review'),
        ).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Hide automatic fixes/ })).toBeInTheDocument();
        rerender(
            <ReadinessTracker
                summary={{ ...SUMMARY, rows_pending_review: 0, changes_unapplied: 0 }}
                applied
            />,
        );
        expect(screen.getByText('Submitted for manual review')).toBeInTheDocument();
        expect(screen.getByText(/3 rows reviewed/)).toBeInTheDocument();
    });
});

describe('ListFindings', () => {
    test('shows header problems only', () => {
        const { container, rerender } = render(<ListFindings filePass={{}} />);
        expect(container).toBeEmptyDOMElement();
        rerender(
            <ListFindings
                filePass={{
                    header_issues: [{ column: 'country', note: 'Missing country column' }],
                    repeated_names: [{ name: 'x', rows: [2, 3] }],
                }}
            />,
        );
        expect(screen.getByText('Missing country column')).toBeInTheDocument();
        expect(screen.queryByText(/Findings about the whole file/)).toBeNull();
    });

    test('says when rows had only the formatting checks', () => {
        const { container, rerender } = render(
            <ListFindings filePass={{}} pipeline={{ model_error_rows: [], degraded: false }} />,
        );
        expect(container).toBeEmptyDOMElement();
        rerender(<ListFindings filePass={{}} pipeline={{ model_error_rows: [4] }} />);
        expect(
            screen.getByText(/could not run for 1 row, so that row shows only the formatting checks/),
        ).toBeInTheDocument();
        rerender(<ListFindings filePass={{}} pipeline={{ model_error_rows: [4, 5], degraded: true }} />);
        expect(screen.getByText(/most rows show only the formatting checks/)).toBeInTheDocument();
    });
});

describe('row components', () => {
    test('a correction can be accepted, kept or edited', () => {
        const onDecide = jest.fn();
        render(<Correction suggestion={SUGGESTIONS.workers} canAct busy={false} onDecide={onDecide} />);
        fireEvent.click(screen.getByRole('button', { name: 'Accept' }));
        expect(onDecide).toHaveBeenLastCalledWith('ACCEPTED');
        fireEvent.click(screen.getByRole('button', { name: 'Keep original' }));
        expect(onDecide).toHaveBeenLastCalledWith('REJECTED');
        fireEvent.click(screen.getByRole('button', { name: 'Edit' }));
        const input = screen.getByDisplayValue('1200');
        fireEvent.change(input, { target: { value: '1250' } });
        fireEvent.click(screen.getByRole('button', { name: 'Save' }));
        expect(onDecide).toHaveBeenLastCalledWith('EDITED', '1250');
    });

    test('a flagged row can be removed or fixed in place', () => {
        const onDecide = jest.fn();
        render(<Issue suggestion={SUGGESTIONS.poBox} canAct busy={false} onDecide={onDecide} />);
        fireEvent.click(screen.getByRole('button', { name: 'Remove row' }));
        expect(onDecide).toHaveBeenLastCalledWith('REMOVED');
        fireEvent.click(screen.getByRole('button', { name: 'Fix value' }));
        fireEvent.change(screen.getByDisplayValue('PO Box 41, Dhaka'), {
            target: { value: '12 Mirpur Road, Dhaka' },
        });
        fireEvent.click(screen.getByRole('button', { name: 'Save' }));
        expect(onDecide).toHaveBeenLastCalledWith('EDITED', '12 Mirpur Road, Dhaka');
    });

    test('an automatic removal can be kept', () => {
        const onDecide = jest.fn();
        render(<Removal suggestion={SUGGESTIONS.duplicate} canAct busy={false} onDecide={onDecide} />);
        fireEvent.click(screen.getByRole('button', { name: 'Keep row' }));
        expect(onDecide).toHaveBeenLastCalledWith('REJECTED');
    });

    test('an exact repeat the upload check dropped has no buttons', () => {
        const fixed = {
            ...SUGGESTIONS.duplicate,
            extra: { ...SUGGESTIONS.duplicate.extra, parser_removed: true },
        };
        render(<Removal suggestion={fixed} canAct busy={false} onDecide={jest.fn()} />);
        expect(screen.getByText('Removed: exact repeat')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Keep row' })).toBeNull();
        expect(screen.queryByRole('button', { name: 'Remove row' })).toBeNull();
    });

    test('undo on a flagged row puts it back to undecided', () => {
        const onDecide = jest.fn();
        const fixedRow = { ...SUGGESTIONS.poBox, decision: 'EDITED' };
        render(<Issue suggestion={fixedRow} canAct busy={false} onDecide={onDecide} />);
        fireEvent.click(screen.getByRole('button', { name: 'Undo' }));
        expect(onDecide).toHaveBeenLastCalledWith('PENDING');
        fireEvent.click(screen.getByRole('button', { name: 'Keep original' }));
        expect(onDecide).toHaveBeenLastCalledWith('REJECTED');
    });

    test('an undecided flagged row has nothing to undo', () => {
        render(<Issue suggestion={SUGGESTIONS.poBox} canAct busy={false} onDecide={jest.fn()} />);
        expect(screen.queryByRole('button', { name: 'Undo' })).toBeNull();
        expect(screen.getByRole('button', { name: 'Keep original' })).toBeInTheDocument();
    });
});

describe('GroupTabs', () => {
    const renderTabs = (props = {}) => {
        const decide = jest.fn();
        const decideGroup = jest.fn();
        const onShowAuto = jest.fn();
        const utils = render(
            <GroupTabs
                groups={GROUPS}
                rows={ROWS}
                canAct
                busy={false}
                decide={decide}
                decideGroup={decideGroup}
                onShowAuto={onShowAuto}
                {...props}
            />,
        );
        return { ...utils, decide, decideGroup, onShowAuto };
    };

    test('splits the chips into blockers and recommended fixes', () => {
        renderTabs();
        expect(screen.getByText('Needs review (3)')).toBeInTheDocument();
        expect(screen.getByText('Required fixes')).toBeInTheDocument();
        expect(screen.getByText('Recommended fixes')).toBeInTheDocument();
        expect(screen.queryByText('Automatic fixes')).toBeNull();
        // the Needs-you tab lists every row with something to decide
        expect(screen.getByText('Row 2')).toBeInTheDocument();
        expect(screen.getByText('Row 3')).toBeInTheDocument();
        expect(screen.queryByText('Row 4')).toBeNull();
    });

    test('a selected type shows its guidance and acts on the whole type', () => {
        const { decideGroup } = renderTabs();
        fireEvent.click(screen.getByRole('tab', { name: /Address is a PO Box/ }));
        expect(screen.getByText('Required fix', { selector: 'span[data-tier]' })).toBeInTheDocument();
        expect(screen.getByText(/PO Box in the address/)).toBeInTheDocument();
        expect(screen.getByText('Why this matters')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /^Remove 1 row$/ }));
        expect(decideGroup).toHaveBeenCalledWith('ISSUE:address_po_box:address', 'REMOVED', false);
        fireEvent.click(screen.getByRole('tab', { name: /same name at several addresses/ }));
        expect(screen.getByText('Recommended fix', { selector: 'span[data-tier]' })).toBeInTheDocument();
        fireEvent.click(screen.getByRole('tab', { name: /worker count formatted/ }));
        fireEvent.click(screen.getByRole('button', { name: /^Accept all 1$/ }));
        expect(decideGroup).toHaveBeenLastCalledWith(
            'CORRECTION:workers_format:number_of_workers', 'ACCEPTED', false,
        );
    });

    test('resolve everything accepts the fixes and removes the required rows in one go', () => {
        const { decideGroup } = renderTabs();
        fireEvent.click(
            screen.getByRole('button', {
                name: 'Resolve everything: accept 1 fix, remove 1 row, keep 1 row as uploaded',
            }),
        );
        expect(decideGroup).toHaveBeenCalledWith(
            [
                'ISSUE:address_po_box:address',
                'CORRECTION:workers_format:number_of_workers',
                'ISSUE:repeated_names:name',
            ],
            {
                'ISSUE:address_po_box:address': 'REMOVED',
                'CORRECTION:workers_format:number_of_workers': 'ACCEPTED',
                'ISSUE:repeated_names:name': 'REJECTED',
            },
            false,
        );
    });

    test('resolve everything leaves rows the contributor decided by hand alone', () => {
        const byHand = ROWS.map(r => ({
            ...r,
            suggestions: r.suggestions.map(s =>
                s.code === 'address_po_box'
                    ? { ...s, decision: 'EDITED', extra: { by_row: true } }
                    : s,
            ),
        }));
        renderTabs({ rows: byHand });
        expect(
            screen.getByRole('button', {
                name: 'Resolve everything: accept 1 fix, keep 1 row as uploaded',
            }),
        ).toBeInTheDocument();
    });

    test('repeated names are shown as copies with a keep-one action', () => {
        const flag = (id, rowNumber, group = { name: 'Same Name Ltd', rows: [5, 6] }) => ({
            ...SUGGESTIONS.repeated,
            id,
            row_number: rowNumber,
            extra: { group },
        });
        const rows = [
            { row_number: 5, name: 'Same Name Ltd', address: 'Zone 1', suggestions: [flag(50, 5)] },
            { row_number: 6, name: 'Same Name Ltd', address: 'Zone 2', suggestions: [flag(60, 6)] },
            { row_number: 7, name: 'Other', address: 'Zone 3', suggestions: [flag(70, 7, { name: 'Other', rows: [7] })] },
        ];
        const decide = jest.fn();
        render(
            <SuggestionRows rows={rows} canAct busy={false} decide={decide} filter={null} cluster />,
        );
        expect(screen.getByText(/“Same Name Ltd” on 2 rows/)).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Keep row 5, remove the other 1 copy' }));
        expect(decide).toHaveBeenCalledWith([
            { id: 50, decision: 'REJECTED' },
            { id: 60, decision: 'REMOVED' },
        ]);
        // One cluster only, so no "every name" button; row 7 stands alone.
        expect(screen.queryByRole('button', { name: /Keep one row per name/ })).toBeNull();
    });

    test('a moderator note still gets the explainer box', () => {
        const note = {
            ...GROUPS[0],
            key: 'ISSUE:name_too_many:name',
            code: 'name_too_many',
            field: 'name',
            severity: 'internal_note',
        };
        const noteRow = {
            row_number: 9,
            name: 'Example Ltd (formerly Other Ltd), Dhaka',
            address: 'Road 1',
            suggestions: [
                { ...SUGGESTIONS.poBox, id: 90, row_number: 9, field: 'name', code: 'name_too_many', severity: 'internal_note' },
            ],
        };
        renderTabs({ groups: [...GROUPS, note], rows: [...ROWS, noteRow] });
        fireEvent.click(screen.getByRole('tab', { name: /name has details that are not the name/ }));
        expect(screen.getByText(/Too much in the name/)).toBeInTheDocument();
        expect(screen.getByText('Moderator note', { selector: 'span[data-tier]' })).toBeInTheDocument();
        expect(screen.getByText(/only the facility name/)).toBeInTheDocument();
    });

    test('the Needs-you tab accepts every suggested fix or keeps everything', () => {
        const { decideGroup } = renderTabs();
        fireEvent.click(screen.getByRole('button', { name: /Accept all 1 fix/ }));
        expect(decideGroup).toHaveBeenCalledWith(
            ['CORRECTION:workers_format:number_of_workers'], 'ACCEPTED', false,
        );
        fireEvent.click(screen.getByRole('button', { name: /Keep all original values/ }));
        const [keys, decision] = decideGroup.mock.calls[1];
        expect(keys).toHaveLength(3);
        expect(decision).toBe('REJECTED');
    });

    test('rows can be ticked and decided in bulk', () => {
        const { decide } = renderTabs();
        fireEvent.click(screen.getByLabelText('Select all rows shown'));
        expect(screen.getByText('3 rows selected:')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: /^Keep original values$/ }));
        expect(decide).toHaveBeenCalledTimes(1);
        const sent = decide.mock.calls[0][0];
        expect(sent.map(d => d.decision)).toEqual(['REJECTED', 'REJECTED', 'REJECTED']);
        expect(screen.queryByText('3 rows selected:')).toBeNull();
        fireEvent.click(screen.getByLabelText('Select row 3'));
        fireEvent.click(screen.getByRole('button', { name: /Remove 1 row/ }));
        expect(decide.mock.calls[1][0]).toEqual([{ id: 3, decision: 'REMOVED' }]);
    });

    test('the automatic row opens from the tracker and can be hidden', () => {
        const { onShowAuto } = renderTabs({ showAuto: true });
        expect(screen.getByText('Automatic fixes')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('tab', { name: 'All automatic fixes (2)' }));
        expect(screen.getByText('Row 4')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('tab', { name: /country converted/ }));
        expect(screen.getByText('Automatic fix', { selector: 'span[data-tier]' })).toBeInTheDocument();
        expect(screen.getByText('What was done')).toBeInTheDocument();
        fireEvent.click(screen.getByRole('button', { name: 'Hide' }));
        expect(onShowAuto).toHaveBeenCalledWith(false);
    });

    test('a row decision goes through decide', () => {
        const { decide } = renderTabs();
        const row = screen.getByText('Row 2').closest('div[style]').parentElement;
        fireEvent.click(within(row).getByRole('button', { name: 'Accept' }));
        expect(decide).toHaveBeenCalledWith([{ id: 1, decision: 'ACCEPTED', value: undefined }]);
    });
});
