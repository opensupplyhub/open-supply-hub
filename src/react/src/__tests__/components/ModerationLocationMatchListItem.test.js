import React from 'react';
import { MemoryRouter } from 'react-router-dom';

import ModerationLocationMatchListItem from '../../components/Dashboard/ModerationLocationMatchListItem';
import renderWithProviders from '../../util/testUtils/renderWithProviders';

const mockModerationMatchConfirmButton = jest.fn();

jest.mock('../../components/Dashboard/ModerationMatchConfirmButton', () => props => {
    mockModerationMatchConfirmButton(props);
    return (
        <div
            data-testid="moderation-match-confirm-button-mock"
            data-aria-label={props.ariaLabel}
        />
    );
});

describe('ModerationLocationMatchListItem component', () => {
    const mockConfirmPotentialMatch = jest.fn();

    const defaultProps = {
        classes: {
            listItemStyle: 'listItemStyle',
            listItemStyle_confirmed: 'listItemStyle_confirmed',
            listItemTextStyle: 'listItemTextStyle',
        },
        location: {
            osId: 'US2020123ABC',
            name: 'Test Location',
            address: '123 Main St',
            claimStatus: 'claimed',
        },
        match: {
            matchOsId: 'US2020123ABC',
            eventOsId: 'US2020456DEF',
        },
        moderation: {
            status: 'PENDING',
            fetching: false,
        },
        actions: {
            confirmPotentialMatch: mockConfirmPotentialMatch,
        },
        isDisabled: false,
        isConfirmed: false,
        confirmAriaLabel: 'Confirm potential match button tooltip',
    };

    const renderComponent = (props = {}) =>
        renderWithProviders(
            <MemoryRouter>
                <ModerationLocationMatchListItem
                    {...defaultProps}
                    {...props}
                />
            </MemoryRouter>,
        );

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('renders row data and link details', () => {
        const { getByTestId } = renderComponent();

        expect(
            getByTestId('moderation-location-match-list-item'),
        ).toBeInTheDocument();
        expect(getByTestId('moderation-location-match-osid')).toHaveTextContent(
            'OS ID: US2020123ABC',
        );
        expect(getByTestId('moderation-location-match-name')).toHaveTextContent(
            'Name: Test Location',
        );
        expect(
            getByTestId('moderation-location-match-address'),
        ).toHaveTextContent('Address: 123 Main St');
        expect(
            getByTestId('moderation-location-match-claim-status'),
        ).toHaveTextContent('Claimed Status: claimed');
        expect(
            getByTestId('moderation-location-match-osid-link'),
        ).toBeInTheDocument();
    });

    test('applies confirmed row class when isConfirmed is true', () => {
        const { getByTestId } = renderComponent({ isConfirmed: true });

        expect(
            getByTestId('moderation-location-match-list-item'),
        ).toHaveClass('listItemStyle');
        expect(
            getByTestId('moderation-location-match-list-item'),
        ).toHaveClass('listItemStyle_confirmed');
    });

    test('forwards expected props to ModerationMatchConfirmButton', () => {
        const { getByTestId } = renderComponent({
            isDisabled: true,
            confirmAriaLabel: 'Confirm existing OS ID button tooltip',
        });

        expect(
            getByTestId('moderation-match-confirm-button-mock'),
        ).toBeInTheDocument();
        expect(
            getByTestId('moderation-match-confirm-button-mock'),
        ).toHaveAttribute(
            'data-aria-label',
            'Confirm existing OS ID button tooltip',
        );
        expect(mockModerationMatchConfirmButton).toHaveBeenCalledWith(
            expect.objectContaining({
                classes: defaultProps.classes,
                match: defaultProps.match,
                moderation: defaultProps.moderation,
                actions: defaultProps.actions,
                isDisabled: true,
                ariaLabel: 'Confirm existing OS ID button tooltip',
            }),
        );
    });
});
