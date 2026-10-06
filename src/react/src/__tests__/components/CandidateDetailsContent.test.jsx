import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import { render, screen } from '@testing-library/react';

import ProductionLocationDetailsContent from '../../components/ProductionLocation/ProductionLocationDetailsContent/ProductionLocationDetailsContent';

jest.mock(
    '../../components/ProductionLocation/ProductionLocationDetailsMap/ProductionLocationDetailsMap',
    () => () => <div data-testid="details-map" />,
);
jest.mock('../../components/Candidate/CandidateValidationPanel', () => ({
    __esModule: true,
    default: ({ candidate, variant }) => (
        <div
            data-testid="candidate-validation-panel"
            data-os-id={candidate.osId}
            data-variant={variant}
        />
    ),
    PANEL_VARIANTS: { OVERLAY: 'overlay', INLINE: 'inline' },
}));
jest.mock(
    '../../components/ProductionLocation/Heading/ClaimFlag/ClaimFlag',
    () => () => <div data-testid="claim-banner" />,
);
jest.mock(
    '../../components/ProductionLocation/Heading/ClosureStatus/ClosureStatus',
    () => () => null,
);
jest.mock(
    '../../components/ProductionLocation/Heading/DataSourcesInfo/DataSourcesInfo',
    () => () => <div data-testid="understanding-data-sources-section" />,
);
jest.mock(
    '../../components/ProductionLocation/ProductionLocationDetailsGeneralFields/ProductionLocationDetailsGeneralFields',
    () => () => <div data-testid="production-location-details-general-fields" />,
);
jest.mock(
    '../../components/ProductionLocation/ClaimSection/ClaimDataContainer/ClaimDataContainer',
    () => () => <div data-testid="operational-details-section" />,
);
jest.mock(
    '../../components/ProductionLocation/PartnerSection/PartnerDataContainer/PartnerDataContainer',
    () => () => <div data-testid="spotlight-section" />,
);
jest.mock(
    '../../components/ProductionLocation/Heading/OsIdBadge/OsIdBadge',
    () => ({ osId }) => <div data-testid="os-id">{osId}</div>,
);

const OS_ID = 'US2026ABCDEF1234';

const candidateFeature = {
    id: OS_ID,
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [-79.1, 35.1] },
    properties: {
        os_id: OS_ID,
        name: '',
        address: '',
        country_name: 'United States',
        is_candidate: true,
        candidate: {
            source: 'Earth Genome',
            confidence: 0.91,
            external_id: 'eg-42',
            created_at: '2026-09-01T00:00:00Z',
            validation: {
                state: 'unverified',
                tally: { confirmed: 0, not_a_facility: 0 },
                your_vote: null,
                voting_open: true,
            },
            suggested_matches: [],
        },
    },
};

const facilityFeature = {
    id: 'US2020XYZ',
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [-79.1, 35.1] },
    properties: {
        os_id: 'US2020XYZ',
        name: 'Real Mill',
        address: '1 Mill Rd',
        is_candidate: false,
    },
};

const renderContent = data =>
    render(
        <MemoryRouter>
            <ProductionLocationDetailsContent data={data} />
        </MemoryRouter>,
    );

describe('ProductionLocationDetailsContent for candidates', () => {
    it('renders the candidate page: placeholder title, badge, provenance, inline panel', () => {
        renderContent(candidateFeature);

        expect(screen.getByTestId('candidate-details-content')).toBeInTheDocument();
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
            'Unnamed location (satellite-detected)',
        );
        expect(screen.getByTestId('candidate-badge')).toBeInTheDocument();
        expect(screen.getByTestId('candidate-state-chip')).toHaveTextContent(
            'Unverified',
        );
        const provenance = screen.getByTestId('candidate-provenance');
        expect(provenance).toHaveTextContent('Source: Earth Genome');
        expect(provenance).toHaveTextContent('Confidence: 91%');
        expect(provenance).toHaveTextContent('External ID: eg-42');
        expect(screen.getByTestId('os-id')).toHaveTextContent(OS_ID);

        const panel = screen.getByTestId('candidate-validation-panel');
        expect(panel).toHaveAttribute('data-os-id', OS_ID);
        expect(panel).toHaveAttribute('data-variant', 'inline');
        expect(screen.getByTestId('details-map')).toBeInTheDocument();
    });

    it('hides the sections that assume a confirmed facility', () => {
        renderContent(candidateFeature);

        expect(screen.queryByTestId('claim-banner')).not.toBeInTheDocument();
        expect(
            screen.queryByTestId('operational-details-section'),
        ).not.toBeInTheDocument();
        expect(screen.queryByTestId('spotlight-section')).not.toBeInTheDocument();
        expect(
            screen.queryByTestId('production-location-details-general-fields'),
        ).not.toBeInTheDocument();
        expect(
            screen.queryByTestId('understanding-data-sources-section'),
        ).not.toBeInTheDocument();
    });

    it('renders the normal page for a confirmed facility', () => {
        renderContent(facilityFeature);

        expect(
            screen.queryByTestId('candidate-details-content'),
        ).not.toBeInTheDocument();
        expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
            'Real Mill',
        );
        expect(screen.getByTestId('claim-banner')).toBeInTheDocument();
        expect(
            screen.getByTestId('production-location-details-general-fields'),
        ).toBeInTheDocument();
        expect(
            screen.queryByTestId('candidate-validation-panel'),
        ).not.toBeInTheDocument();
    });
});
