import React from 'react';
import { fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import PartnerSectionItem from '../../components/ProductionLocation/PartnerSection/PartnerSectionItem/PartnerSectionItem';
import { sendLocationPartnerBetaFeedbackLinkClick } from '../../util/analytics/gaCustomEvents';

jest.mock('../../util/analytics/gaCustomEvents', () => ({
    ...jest.requireActual('../../util/analytics/gaCustomEvents'),
    sendLocationPartnerBetaFeedbackLinkClick: jest.fn(),
}));

const makeGroup = (overrides = {}) => ({
    uuid: 'group-1',
    name: 'Test Group',
    icon_file: null,
    helper_text: '<p>Helper</p>',
    description: '',
    partnerFields: [{ fieldName: 'field-1', label: 'Field 1' }],
    ...overrides,
});

const defaultState = {
    facilities: { singleFacility: { data: null } },
    sectionNavigation: {
        scrollTargetId: null,
        openSectionIds: {},
    },
};

const renderComponent = (props = {}, stateOverrides = {}) =>
    renderWithProviders(
        <PartnerSectionItem
            group={makeGroup()}
            partnerFields={[]}
            {...props}
        />,
        {
            preloadedState: { ...defaultState, ...stateOverrides },
        },
    );

describe('PartnerSectionItem component', () => {
    test('renders the group name', () => {
        const { getByText } = renderComponent();
        expect(getByText('Test Group')).toBeInTheDocument();
    });

    test('shows ExpandMore icon when section is closed', () => {
        const { getByTestId, queryByTestId } = renderComponent();
        expect(getByTestId('partner-section-expand-more')).toBeInTheDocument();
        expect(
            queryByTestId('partner-section-expand-less'),
        ).not.toBeInTheDocument();
    });

    test('shows ExpandLess icon when section is open', () => {
        const { getByTestId, queryByTestId } = renderComponent(
            { group: makeGroup({ uuid: 'open-1' }) },
            {
                sectionNavigation: {
                    scrollTargetId: null,
                    openSectionIds: { 'open-1': true },
                },
            },
        );
        expect(getByTestId('partner-section-expand-less')).toBeInTheDocument();
        expect(
            queryByTestId('partner-section-expand-more'),
        ).not.toBeInTheDocument();
    });

    test('toggles section when header is clicked', () => {
        const { getByRole, getByTestId, queryByTestId } = renderComponent();

        expect(getByTestId('partner-section-expand-more')).toBeInTheDocument();
        expect(
            queryByTestId('partner-section-expand-less'),
        ).not.toBeInTheDocument();
        fireEvent.click(getByRole('button'));
        expect(getByTestId('partner-section-expand-less')).toBeInTheDocument();
        expect(
            queryByTestId('partner-section-expand-more'),
        ).not.toBeInTheDocument();
    });

    test('renders description when provided', () => {
        const { getByText } = renderComponent(
            { group: makeGroup({ uuid: 'desc-1', description: '<b>Note</b>' }) },
            {
                sectionNavigation: {
                    scrollTargetId: null,
                    openSectionIds: { 'desc-1': true },
                },
            },
        );
        expect(getByText('Note')).toBeInTheDocument();
    });

    describe('Why beta card (OSDEV-3778)', () => {
        const openState = uuid => ({
            sectionNavigation: {
                scrollTargetId: null,
                openSectionIds: { [uuid]: true },
            },
        });

        test('renders the card when a field in the group is beta', () => {
            const { getByRole } = renderComponent(
                {
                    group: makeGroup({
                        uuid: 'beta-1',
                        partnerFields: [
                            { fieldName: 'plain', label: 'Plain', beta: false },
                            { fieldName: 'provisional', label: 'Provisional', beta: true },
                        ],
                    }),
                },
                openState('beta-1'),
            );

            expect(
                getByRole('heading', { name: 'Why beta?', level: 4 }),
            ).toBeInTheDocument();
        });

        test('reports the admin-set label of the beta field in the suggestions GA event', () => {
            sendLocationPartnerBetaFeedbackLinkClick.mockClear();
            const entry = {
                id: 1,
                value: { raw_value: 'x' },
                contributor_name: 'HeatWatch',
                contributor_id: 7,
                created_at: '2026-08-25T00:00:00Z',
                updated_at: '2026-08-25T00:00:00Z',
                is_verified: false,
                // The label set in the Django admin, unlike the
                // title-cased field name preparePartnerFields derives.
                label: 'Temperature & humidity',
                beta: true,
            };
            const { getByRole } = renderComponent(
                {
                    group: makeGroup({
                        uuid: 'beta-2',
                        name: 'Environment & Climate',
                        partnerFields: [
                            {
                                fieldName: 'heatwatch',
                                label: 'Heatwatch',
                                beta: true,
                                formatValue: value => value.raw_value,
                            },
                        ],
                    }),
                },
                {
                    ...openState('beta-2'),
                    facilities: {
                        singleFacility: {
                            data: {
                                properties: {
                                    os_id: 'IN2019083ABCDEF',
                                    partner_fields: { heatwatch: [entry] },
                                },
                            },
                        },
                    },
                },
            );

            fireEvent.click(getByRole('link', { name: 'Send us your suggestions' }));

            expect(sendLocationPartnerBetaFeedbackLinkClick).toHaveBeenCalledWith(
                expect.objectContaining({
                    partnerGroup: 'Environment & Climate',
                    osId: 'IN2019083ABCDEF',
                    partnerFieldName: 'Temperature & humidity',
                }),
            );
        });

        test('renders no card when no field in the group is beta', () => {
            const { queryByRole } = renderComponent(
                {
                    group: makeGroup({
                        uuid: 'plain-1',
                        partnerFields: [
                            { fieldName: 'plain', label: 'Plain', beta: false },
                            { fieldName: 'other', label: 'Other' },
                        ],
                    }),
                },
                openState('plain-1'),
            );

            expect(
                queryByRole('heading', { name: 'Why beta?', level: 4 }),
            ).not.toBeInTheDocument();
        });
    });
});
