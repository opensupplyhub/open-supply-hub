import React from 'react';
import { fireEvent } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import PartnerSectionItem from '../../components/ProductionLocation/PartnerSection/PartnerSectionItem/PartnerSectionItem';

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
    partnerFieldGroups: {
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

    test('shows "Open" label when section is closed', () => {
        const { getByText } = renderComponent();
        expect(getByText('Open')).toBeInTheDocument();
    });

    test('shows "Close" label when section is open', () => {
        const { getByText } = renderComponent(
            { group: makeGroup({ uuid: 'open-1' }) },
            {
                partnerFieldGroups: {
                    scrollTargetId: null,
                    openSectionIds: { 'open-1': true },
                },
            },
        );
        expect(getByText('Close')).toBeInTheDocument();
    });

    test('toggles section when header is clicked', () => {
        const { getByRole, getByText } = renderComponent();

        expect(getByText('Open')).toBeInTheDocument();
        fireEvent.click(getByRole('button'));
        expect(getByText('Close')).toBeInTheDocument();
    });

    test('renders description when provided', () => {
        const { getByText } = renderComponent(
            { group: makeGroup({ uuid: 'desc-1', description: '<b>Note</b>' }) },
            {
                partnerFieldGroups: {
                    scrollTargetId: null,
                    openSectionIds: { 'desc-1': true },
                },
            },
        );
        expect(getByText('Note')).toBeInTheDocument();
    });
});
