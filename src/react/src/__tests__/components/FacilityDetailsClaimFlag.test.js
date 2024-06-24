import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import FacilityDetailsClaimFlag from '../../components/FacilityDetailsClaimFlag';


function renderComponent(props = {}) {
    const defaultProps = {
        osId: 'id_221kjaksiie',
        isClaimed: false,
        isPending: false,
        isEmbed: false,
    };

    render(
        <Router>
            <FacilityDetailsClaimFlag
                {...defaultProps} {...props}
            />
        </Router>,
    );
}

describe('FacilityDetailsClaimFlag', () => {
    test('it renders without crashing', () => {
        const isClaimed = true;

        renderComponent({ isClaimed })

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toBeInTheDocument();
    });

    test('facility has been claimed', () => {
        const isClaimed = true;
        const text =
            'This production location has been claimed by an owner or manager';

        renderComponent({ isClaimed })

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('facility has not been claimed', () => {
        const text = 'This production location has not been claimed';

        renderComponent()

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('pending claim for facility ', () => {
        const isPending = true;
        const text = 'There is a pending claim for this production location';

        renderComponent({ isPending })

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('facility claim should not be rendered', () => {
        const isEmbed = true;

        renderComponent({ isEmbed })

        const banner = screen.queryByTestId('claim-banner');

        expect(banner).not.toBeInTheDocument();
    });
});
