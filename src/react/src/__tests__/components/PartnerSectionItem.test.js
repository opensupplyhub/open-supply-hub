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
});
