import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import FacilityDetailsClaimFlag from '../../components/FacilityDetailsClaimFlag';

describe('FacilityDetailsClaimFlag', () => {
    const defaultProps = {
        osId: 'id_221kjaksiie',
        isClaimed: false,
        isPending: false,
        isEmbed: false,
    };

    test('it renders without crashing', () => {
        const isClaimed = true;

        renderWithProviders(
            <Router>
                <FacilityDetailsClaimFlag
                    {...defaultProps}
                    isClaimed={isClaimed}
                />
            </Router>,
        );

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toBeInTheDocument();
    });

    test('facility has been claimed', () => {
        const isClaimed = true;
        const text =
            'This production location has been claimed by an owner or manager';

        renderWithProviders(
            <Router>
                <FacilityDetailsClaimFlag
                    {...defaultProps}
                    isClaimed={isClaimed}
                />
            </Router>,
        );

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('facility has not been claimed', () => {
        const text = 'This production location has not been claimed';

        renderWithProviders(
            <Router>
                <FacilityDetailsClaimFlag {...defaultProps} />
            </Router>,
        );

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('pending claim for facility ', () => {
        const isPending = true;
        const text = 'There is a pending claim for this production location';

        renderWithProviders(
            <Router>
                <FacilityDetailsClaimFlag
                    {...defaultProps}
                    isPending={isPending}
                />
            </Router>,
        );

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('facility claim should not be rendered', () => {
        const isEmbed = true;

        renderWithProviders(
            <Router>
                <FacilityDetailsClaimFlag {...defaultProps} isEmbed={isEmbed} />
            </Router>,
        );

        const banner = screen.queryByTestId('claim-banner');

        expect(banner).not.toBeInTheDocument();
    });
});
