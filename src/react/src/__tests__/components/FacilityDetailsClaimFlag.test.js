import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { render, screen } from '@testing-library/react';
import FacilityDetailsClaimFlag from '../../components/FacilityDetailsClaimFlag';


function renderComponent({ osId, isClaimed, isPending, isEmbed }) {
    render(
        <Router>
            <FacilityDetailsClaimFlag
                osId={osId}
                isClaimed={isClaimed}
                isPending={isPending}
                isEmbed={isEmbed}
            />
        </Router>,
    );
}

describe('FacilityDetailsClaimFlag', () => {
    test('it renders without crashing', () => {
        const osId = 'id_221kjaksiie';
        const isClaimed = true;
        const isPending = false;
        const isEmbed = false;

        renderComponent({ osId, isClaimed, isPending, isEmbed })

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toBeInTheDocument();
    });

    test('facility has been claimed', () => {
        const osId = 'id_221kjaksiie';
        const isClaimed = true;
        const isPending = false;
        const isEmbed = false;
        const text =
            'This production location has been claimed by an owner or manager';

        renderComponent({ osId, isClaimed, isPending, isEmbed })

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('facility has not been claimed', () => {
        const osId = 'id_221kjaksiie';
        const isClaimed = false;
        const isPending = false;
        const isEmbed = false;
        const text = 'This production location has not been claimed';

        renderComponent({ osId, isClaimed, isPending, isEmbed })

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('pending claim for facility ', () => {
        const osId = 'id_221kjaksiie';
        const isClaimed = false;
        const isPending = true;
        const isEmbed = false;
        const text = 'There is a pending claim for this production location';

        renderComponent({ osId, isClaimed, isPending, isEmbed })

        const banner = screen.getByTestId('claim-banner');

        expect(banner).toHaveTextContent(text);
    });

    test('facility claim should not be rendered', () => {
        const osId = 'id_221kjaksiie';
        const isClaimed = false;
        const isPending = true;
        const isEmbed = true;

        renderComponent({ osId, isClaimed, isPending, isEmbed })

        const banner = screen.queryByTestId('claim-banner');

        expect(banner).not.toBeInTheDocument();
    });
});
