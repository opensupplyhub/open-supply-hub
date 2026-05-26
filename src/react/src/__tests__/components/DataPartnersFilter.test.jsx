import React from 'react';
import { fireEvent } from '@testing-library/react';

import DataPartnersFilter from '../../components/Filters/DataPartnersFilter/DataPartnersFilter';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import {
    setPartnerContributorFilter,
    updateCombinePartnerContributorsFilterOption,
} from '../../actions/filters';
import { fetchPartnerGroupContributorsIfNeeded } from '../../actions/partnerGroupContributors';
import { getPartnerGroupsWithContributors } from '../../selectors/partnerFieldGroupsSelectors';

jest.mock('../../components/Filters/NestedSelect', () => props => (
    <div data-testid="data-partners-filter-nested-select">
        <button
            type="button"
            aria-label="Open data partners menu"
            data-testid="data-partners-filter-open-menu"
            onClick={props.onMenuOpen}
        />
        <button
            type="button"
            aria-label="Select single data partner"
            data-testid="data-partners-filter-set-single"
            onClick={() =>
                props.updateSector([
                    {
                        groupLabel: 'group-a',
                        label: 'partner-a',
                        value: 'partner-a',
                    },
                ])
            }
        />
        <button
            type="button"
            aria-label="Select multiple data partners"
            data-testid="data-partners-filter-set-multiple"
            onClick={() =>
                props.updateSector([
                    {
                        groupLabel: 'group-a',
                        label: 'partner-a',
                        value: 'partner-a',
                    },
                    {
                        groupLabel: 'group-b',
                        label: 'partner-b',
                        value: 'partner-b',
                    },
                ])
            }
        />
    </div>
));

jest.mock('../../actions/filters', () => ({
    setPartnerContributorFilter: jest.fn(),
    updateCombinePartnerContributorsFilterOption: jest.fn(),
}));

jest.mock('../../actions/partnerGroupContributors', () => ({
    fetchPartnerGroupContributorsIfNeeded: jest.fn(),
}));

jest.mock('../../selectors/partnerFieldGroupsSelectors', () => ({
    getPartnerGroupsWithContributors: jest.fn(),
}));

const contributorA = {
    groupLabel: 'group-a',
    label: 'partner-a',
    value: 'partner-a',
};
const contributorB = {
    groupLabel: 'group-b',
    label: 'partner-b',
    value: 'partner-b',
};

describe('DataPartnersFilter component', () => {
    const renderComponent = ({
        selectedContributors = [],
        combinePartnerContributors = '',
        fetching = false,
        groups = [],
    } = {}) => {
        getPartnerGroupsWithContributors.mockReturnValue(groups);

        return renderWithProviders(<DataPartnersFilter />, {
            preloadedState: {
                filters: {
                    partnerContributors: selectedContributors,
                    combinePartnerContributors,
                },
                partnerGroupContributors: {
                    fetching,
                },
            },
        });
    };

    beforeEach(() => {
        jest.clearAllMocks();
        setPartnerContributorFilter.mockImplementation(payload => ({
            type: 'SET_PARTNER_CONTRIBUTOR_FILTER',
            payload,
        }));
        updateCombinePartnerContributorsFilterOption.mockImplementation(
            payload => ({
                type: 'UPDATE_COMBINE_PARTNER_CONTRIBUTORS_FILTER_OPTION',
                payload,
            }),
        );
        fetchPartnerGroupContributorsIfNeeded.mockImplementation(() => ({
            type: 'FETCH_PARTNER_GROUP_CONTRIBUTORS_IF_NEEDED',
        }));
        getPartnerGroupsWithContributors.mockReturnValue([]);
    });

    test('renders nested selector and no checkbox for one contributor', () => {
        const { getByTestId, queryByRole } = renderComponent({
            selectedContributors: [contributorA],
        });

        expect(
            getByTestId('data-partners-filter-nested-select'),
        ).toBeInTheDocument();
        expect(queryByRole('checkbox')).not.toBeInTheDocument();
    });

    test('renders checkbox for multiple contributors', () => {
        const { getByRole } = renderComponent({
            selectedContributors: [contributorA, contributorB],
        });

        expect(getByRole('checkbox')).toBeInTheDocument();
    });

    test('loads groups on mount when contributor list is not empty', () => {
        renderComponent({
            selectedContributors: [contributorA],
        });

        expect(fetchPartnerGroupContributorsIfNeeded).toHaveBeenCalledTimes(1);
    });

    test('loads groups when menu opens', () => {
        const { getByTestId } = renderComponent();

        fireEvent.click(getByTestId('data-partners-filter-open-menu'));

        expect(fetchPartnerGroupContributorsIfNeeded).toHaveBeenCalledTimes(1);
    });

    test('resets combine mode when one contributor is selected', () => {
        const { getByTestId } = renderComponent();

        fireEvent.click(getByTestId('data-partners-filter-set-single'));

        expect(updateCombinePartnerContributorsFilterOption).toHaveBeenCalledWith(
            '',
        );
        expect(setPartnerContributorFilter).toHaveBeenCalledWith([
            expect.objectContaining({ value: 'partner-a' }),
        ]);
    });

    test('does not reset combine mode when multiple contributors are selected', () => {
        const { getByTestId } = renderComponent();

        fireEvent.click(getByTestId('data-partners-filter-set-multiple'));

        expect(updateCombinePartnerContributorsFilterOption).not.toHaveBeenCalled();
        expect(setPartnerContributorFilter).toHaveBeenCalledWith([
            expect.objectContaining({ value: 'partner-a' }),
            expect.objectContaining({ value: 'partner-b' }),
        ]);
    });

    test('enables combine mode when checkbox is checked', () => {
        const { getByRole } = renderComponent({
            selectedContributors: [contributorA, contributorB],
            combinePartnerContributors: '',
        });

        fireEvent.click(getByRole('checkbox'));

        expect(updateCombinePartnerContributorsFilterOption).toHaveBeenCalledWith(
            'AND',
        );
    });

    test('clears combine mode when checkbox is unchecked', () => {
        const { getByRole } = renderComponent({
            selectedContributors: [contributorA, contributorB],
            combinePartnerContributors: 'AND',
        });

        fireEvent.click(getByRole('checkbox'));

        expect(updateCombinePartnerContributorsFilterOption).toHaveBeenCalledWith(
            '',
        );
    });
});
