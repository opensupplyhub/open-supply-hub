import React from 'react';

import ModerationExistingOsIdContent from '../../components/Dashboard/ModerationExistingOsIdContent';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

jest.mock('../../components/Dashboard/ModerationLocationMatchListItem', () => () => (
    <div data-testid="moderation-location-match-list-item" />
));

describe('ModerationExistingOsIdContent component', () => {
    const mockConfirmPotentialMatch = jest.fn();

    const defaultProps = {
        classes: {
            loaderStyles: 'loaderStyles',
            emptyBlockStyles: 'emptyBlockStyles',
            emptyTextStyle: 'emptyTextStyle',
        },
        location: {
            fetching: false,
            data: null,
        },
        moderation: {
            status: 'PENDING',
            fetching: false,
        },
        actions: {
            confirmPotentialMatch: mockConfirmPotentialMatch,
        },
        isDisabled: false,
    };

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <ModerationExistingOsIdContent {...defaultProps} {...props} />,
        );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders loading indicator when existing location is fetching', () => {
        const { getByTestId, queryByTestId } = renderComponent({
            location: {
                fetching: true,
                data: null,
            },
        });

        expect(
            getByTestId('moderation-existing-osid-loader'),
        ).toBeInTheDocument();
        expect(
            queryByTestId('moderation-location-match-list-item'),
        ).not.toBeInTheDocument();
    });

    test('renders match list item when location data exists', () => {
        const locationData = {
            os_id: 'US2020123ABC',
            name: 'Test Location',
            address: '123 Main St',
            claim_status: 'claimed',
        };

        const { getByTestId } = renderComponent({
            location: {
                fetching: false,
                data: locationData,
            },
            isDisabled: true,
        });

        expect(
            getByTestId('moderation-location-match-list-item'),
        ).toBeInTheDocument();
    });

    test('renders empty state when no location data exists and not fetching', () => {
        const { getByTestId, queryByTestId } = renderComponent({
            location: {
                fetching: false,
                data: null,
            },
        });

        expect(
            getByTestId('moderation-existing-osid-empty-state'),
        ).toBeInTheDocument();
        expect(
            getByTestId('moderation-existing-osid-empty-text'),
        ).toBeInTheDocument();
        expect(
            queryByTestId('moderation-location-match-list-item'),
        ).not.toBeInTheDocument();
    });
});
