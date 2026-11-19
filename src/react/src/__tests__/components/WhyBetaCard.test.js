import React from 'react';
import { fireEvent, screen } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import WhyBetaCard from '../../components/ProductionLocation/PartnerSection/WhyBetaCard/WhyBetaCard';
import { BETA_CHIP_TEXT } from '../../components/Shared/BetaChip/BetaChip';
import {
    WHY_BETA_TITLE,
    WHY_BETA_BODY,
    WHY_BETA_LINK_TEXT,
    WHY_BETA_LINK_HREF,
} from '../../components/ProductionLocation/PartnerSection/WhyBetaCard/constants';
import { listUploadTroubleshootingEmail } from '../../util/constants';
import {
    GA_LINK_PLACEMENT,
    sendLocationPartnerBetaFeedbackLinkClick,
} from '../../util/analytics/gaCustomEvents';

jest.mock('../../util/analytics/gaCustomEvents', () => ({
    ...jest.requireActual('../../util/analytics/gaCustomEvents'),
    sendLocationPartnerBetaFeedbackLinkClick: jest.fn(),
}));

const gaSpotlightContext = {
    partner_group: 'Environment & Climate',
    os_id: 'IN2019083ABCDEF',
    partner_field_name: 'Temperature & humidity',
};

describe('WhyBetaCard component', () => {
    beforeEach(() => {
        sendLocationPartnerBetaFeedbackLinkClick.mockClear();
    });

    test('renders the chip, title, body and suggestions link', () => {
        renderWithProviders(<WhyBetaCard />);

        expect(
            screen.getByRole('heading', { name: WHY_BETA_TITLE, level: 4 }),
        ).toBeInTheDocument();
        expect(screen.getByText(BETA_CHIP_TEXT)).toBeInTheDocument();
        expect(screen.getByText(WHY_BETA_BODY)).toBeInTheDocument();

        const link = screen.getByRole('link', { name: WHY_BETA_LINK_TEXT });
        expect(link).toHaveAttribute('href', WHY_BETA_LINK_HREF);
    });

    test('the suggestions link opens an email to the shared support address', () => {
        expect(WHY_BETA_LINK_HREF).toBe(
            `mailto:${listUploadTroubleshootingEmail}?subject=Spotlight%20beta%20data%20feedback`,
        );
    });

    test('a click on the suggestions link sends the beta feedback GA event', () => {
        renderWithProviders(
            <WhyBetaCard gaSpotlightContext={gaSpotlightContext} />,
        );

        fireEvent.click(screen.getByRole('link', { name: WHY_BETA_LINK_TEXT }));

        expect(sendLocationPartnerBetaFeedbackLinkClick).toHaveBeenCalledWith({
            partnerGroup: 'Environment & Climate',
            linkPlacement: GA_LINK_PLACEMENT.WHY_BETA_CARD,
            destinationUrl: WHY_BETA_LINK_HREF,
            osId: 'IN2019083ABCDEF',
            partnerFieldName: 'Temperature & humidity',
            // The viewer id hook is mocked to null in setupTests.js.
            viewerUserId: null,
        });
    });

    test('sends no GA event without a Spotlight context', () => {
        renderWithProviders(<WhyBetaCard />);

        fireEvent.click(screen.getByRole('link', { name: WHY_BETA_LINK_TEXT }));

        expect(sendLocationPartnerBetaFeedbackLinkClick).not.toHaveBeenCalled();
    });
});
