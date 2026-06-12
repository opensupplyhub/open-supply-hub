import React from 'react';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ContributeFormSelectListToReplace from '../../components/ContributeFormSelectListToReplace';
import { contributeReplacesNoneSelectionID } from '../../util/constants';

const makeList = (overrides = {}) => ({
    id: 1,
    name: 'Active List',
    description: 'An active list',
    file_name: 'active.csv',
    is_active: true,
    is_public: true,
    status: 'APPROVED',
    item_count: 5,
    items_url: '/api/facility-lists/1/items/',
    created_at: '2024-01-01T00:00:00Z',
    statuses: [],
    parsing_errors: [],
    status_counts: {
        UPLOADED: 0,
        PARSED: 0,
        GEOCODED: 0,
        GEOCODED_NO_RESULTS: 0,
        MATCHED: 5,
        POTENTIAL_MATCH: 0,
        CONFIRMED_MATCH: 0,
        ERROR: 0,
        ERROR_PARSING: 0,
        ERROR_GEOCODING: 0,
        ERROR_MATCHING: 0,
        DELETED: 0,
        DUPLICATE: 0,
        ITEM_REMOVED: 0,
    },
    ...overrides,
});

// Renders with the given list pre-selected so the selected item's label is
// visible in the collapsed trigger (MUI v4 Select renders selected item text
// in the trigger; portal-based menu items are not accessible in jsdom tests).
const renderWithSelection = (list, overrides = {}) =>
    renderWithProviders(
        <ContributeFormSelectListToReplace
            lists={[list]}
            replaces={list.id}
            handleChange={() => {}}
            {...overrides}
        />,
    );

const renderNoneSelected = lists =>
    renderWithProviders(
        <ContributeFormSelectListToReplace
            lists={lists}
            replaces={contributeReplacesNoneSelectionID}
            handleChange={() => {}}
        />,
    );

describe('ContributeFormSelectListToReplace', () => {
    it('shows "None" label when no list is selected', () => {
        renderNoneSelected([makeList()]);
        expect(
            screen.getByText('None (do not replace a list)'),
        ).toBeInTheDocument();
    });

    it('shows list name in the trigger when that list is selected', () => {
        renderWithSelection(makeList({ id: 42, name: 'My Active List' }));
        expect(screen.getByText('My Active List')).toBeInTheDocument();
    });

    it('falls back to file_name when name is absent', () => {
        renderWithSelection(
            makeList({ id: 42, name: null, file_name: 'upload.csv' }),
        );
        expect(screen.getByText('upload.csv')).toBeInTheDocument();
    });

    it('does not display "(inactive)" in any rendered text', () => {
        renderNoneSelected([
            makeList({ id: 1, name: 'List One' }),
            makeList({ id: 2, name: 'List Two' }),
        ]);
        expect(screen.queryByText(/\(inactive\)/)).not.toBeInTheDocument();
    });

    it('shows description in the trigger when that list is selected', () => {
        renderWithSelection(
            makeList({
                id: 42,
                name: 'My List',
                description: 'A helpful description',
            }),
        );
        expect(screen.getByText('A helpful description')).toBeInTheDocument();
    });
});
