import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import {
    ReadinessTracker,
    GroupTabs,
    ListFindings,
    Correction,
    Issue,
    Removal,
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
