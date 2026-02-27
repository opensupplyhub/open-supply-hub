import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ProductionLocationClaimFlag from '../../components/ProductionLocation/Heading/ClaimFlag/ClaimFlag';

describe('ProductionLocation ClaimFlag', () => {
    const defaultProps = {
        osId: 'US202510850SQCV',
        isClaimed: false,
        isPending: false,
        isEmbed: false,
    };

    test('renders without crashing', () => {
        renderWithProviders(
            <Router>
                <ProductionLocationClaimFlag
                    {...defaultProps}
                    isClaimed={true}
                />
            </Router>,
        );

        const banner = screen.getByTestId('claim-banner');
        expect(banner).toBeInTheDocument();
    });

    test('shows CLAIMED PROFILE when claimed', () => {
        renderWithProviders(
            <Router>
                <ProductionLocationClaimFlag
                    {...defaultProps}
                    isClaimed={true}
                />
            </Router>,
        );

        const banner = screen.getByTestId('claim-banner');
        expect(banner).toHaveTextContent('CLAIMED PROFILE');
    });

    test('shows unclaimed message when not claimed', () => {
        renderWithProviders(
            <Router>
                <ProductionLocationClaimFlag {...defaultProps} />
            </Router>,
        );

        const banner = screen.getByTestId('claim-banner');
        expect(banner).toHaveTextContent(
            'This production location has not been claimed',
        );
    });

    test('shows claim link when not claimed and not pending', () => {
        renderWithProviders(
            <Router>
                <ProductionLocationClaimFlag {...defaultProps} />
            </Router>,
        );

        const link = screen.getByRole('link', {
            name: /I want to claim this production location/i,
        });
        expect(link).toBeInTheDocument();
    });

    test('shows pending claim message when pending', () => {
        renderWithProviders(
            <Router>
                <ProductionLocationClaimFlag
                    {...defaultProps}
                    isPending={true}
                />
            </Router>,
        );

        const banner = screen.getByTestId('claim-banner');
        expect(banner).toHaveTextContent(
            'There is a pending claim for this production location',
        );
    });

    test('returns null when embed is true', () => {
        renderWithProviders(
            <Router>
                <ProductionLocationClaimFlag
                    {...defaultProps}
                    isEmbed={true}
                />
            </Router>,
        );

        const banner = screen.queryByTestId('claim-banner');
        expect(banner).not.toBeInTheDocument();
    });

    test('shows claimed-by line when claimed with contributor and date', () => {
        const claimInfo = {
            contributor: { name: 'Acme Corp' },
            approved_at: '2023-06-15T12:00:00Z',
        };

        renderWithProviders(
            <Router>
                <ProductionLocationClaimFlag
                    {...defaultProps}
                    isClaimed={true}
                    claimInfo={claimInfo}
                />
            </Router>,
        );

        expect(screen.getByText(/Claimed by/)).toBeInTheDocument();
        expect(screen.getByText(/Acme Corp/)).toBeInTheDocument();
    });
});
