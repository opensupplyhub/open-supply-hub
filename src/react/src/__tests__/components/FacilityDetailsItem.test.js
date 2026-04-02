import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import FacilityDetailsItem from '../../components/FacilityDetailsItem';

const renderItem = (props = {}) =>
    render(<FacilityDetailsItem label="Test Label" primary="Test Value" {...props} />);

const renderItemWithRouter = (props = {}) =>
    render(
        <MemoryRouter>
            <FacilityDetailsItem label="Test Label" primary="Test Value" {...props} />
        </MemoryRouter>,
    );

describe('FacilityDetailsItem component', () => {
    describe('basic rendering', () => {
        test('renders label and primary value', () => {
            renderItem();

            expect(screen.getByText('Test Label')).toBeInTheDocument();
            expect(screen.getByText('Test Value')).toBeInTheDocument();
        });

        test('does not render "more" button when there is no additional content', () => {
            renderItem({ additionalContent: [] });

            expect(screen.queryByRole('button')).not.toBeInTheDocument();
        });

        test('renders singular "more entry" button for one additional item', () => {
            renderItem({
                additionalContent: [{ primary: 'Second Value' }],
            });

            expect(
                screen.getByRole('button', { name: /1 more entry/i }),
            ).toBeInTheDocument();
        });

        test('renders plural "more entries" button for multiple additional items', () => {
            renderItem({
                additionalContent: [
                    { primary: 'Second Value' },
                    { primary: 'Third Value' },
                ],
            });

            expect(
                screen.getByRole('button', { name: /2 more entries/i }),
            ).toBeInTheDocument();
        });

        test('hides "more" button when embed is true', () => {
            renderItem({
                additionalContent: [{ primary: 'Second Value' }],
                embed: true,
            });

            expect(screen.queryByRole('button')).not.toBeInTheDocument();
        });
    });

    describe('TitledDrawer (default behaviour, customDrawer=false)', () => {
        test('does not open TitledDrawer before button click', () => {
            renderItem({
                additionalContent: [{ primary: 'Second Value' }],
            });

            expect(
                screen.queryByTestId('contributions-drawer'),
            ).not.toBeInTheDocument();
        });

        test('opens TitledDrawer when the "more" button is clicked', () => {
            renderItem({
                additionalContent: [{ primary: 'Second Value' }],
            });

            fireEvent.click(
                screen.getByRole('button', { name: /1 more entry/i }),
            );

            expect(screen.getByText('Second Value')).toBeInTheDocument();
        });

        test('closes TitledDrawer when the Close button inside it is clicked', () => {
            renderItem({
                additionalContent: [{ primary: 'Second Value' }],
            });

            fireEvent.click(
                screen.getByRole('button', { name: /1 more entry/i }),
            );
            expect(screen.getByText('Second Value')).toBeInTheDocument();

            fireEvent.click(screen.getByRole('button', { name: /close/i }));
            expect(screen.queryByText('Second Value')).not.toBeInTheDocument();
        });
    });

    describe('ContributionsDrawer (customDrawer=true)', () => {
        const promotedContribution = {
            value: 'Promoted Value',
            sourceName: 'Contributor A',
            date: '2025-01-01T00:00:00Z',
            userId: 10,
        };

        const additionalContribution = {
            value: 'Additional Value',
            sourceName: 'Contributor B',
            date: '2025-02-01T00:00:00Z',
            userId: 11,
        };

        test('does not render ContributionsDrawer before button click', () => {
            renderItemWithRouter({
                additionalContent: [{ primary: 'Extra' }],
                customDrawer: true,
                drawerPromotedContribution: promotedContribution,
                drawerContributions: [],
            });

            expect(
                screen.queryByTestId('contributions-drawer'),
            ).not.toBeInTheDocument();
        });

        test('opens ContributionsDrawer when the "more" button is clicked', () => {
            renderItemWithRouter({
                additionalContent: [{ primary: 'Extra' }],
                customDrawer: true,
                drawerFieldName: 'Climate Data',
                drawerPromotedContribution: promotedContribution,
                drawerContributions: [],
            });

            fireEvent.click(
                screen.getByRole('button', { name: /1 more entry/i }),
            );

            expect(
                screen.getByTestId('contributions-drawer'),
            ).toBeInTheDocument();
        });

        test('passes drawerFieldName to ContributionsDrawer', () => {
            renderItemWithRouter({
                label: 'Fallback Label',
                additionalContent: [{ primary: 'Extra' }],
                customDrawer: true,
                drawerFieldName: 'Climate Data',
                drawerPromotedContribution: promotedContribution,
                drawerContributions: [],
            });

            fireEvent.click(
                screen.getByRole('button', { name: /1 more entry/i }),
            );

            expect(
                screen.getByTestId('contributions-drawer-title'),
            ).toBeInTheDocument();
        });

        test('falls back to label when drawerFieldName is not provided', () => {
            renderItemWithRouter({
                label: 'Fallback Label',
                additionalContent: [{ primary: 'Extra' }],
                customDrawer: true,
                drawerPromotedContribution: promotedContribution,
                drawerContributions: [],
            });

            fireEvent.click(
                screen.getByRole('button', { name: /1 more entry/i }),
            );

            expect(
                screen.getByTestId('contributions-drawer'),
            ).toBeInTheDocument();
        });

        test('renders contribution cards for drawerContributions inside drawer', () => {
            renderItemWithRouter({
                additionalContent: [{ primary: 'Extra' }],
                customDrawer: true,
                drawerPromotedContribution: promotedContribution,
                drawerContributions: [additionalContribution],
            });

            fireEvent.click(
                screen.getByRole('button', { name: /1 more entry/i }),
            );

            expect(
                screen.getByTestId('contributions-drawer-list'),
            ).toBeInTheDocument();
        });

        test('does not use ContributionsDrawer when there is no additional content', () => {
            renderItemWithRouter({
                additionalContent: [],
                customDrawer: true,
                drawerPromotedContribution: promotedContribution,
                drawerContributions: [],
            });

            expect(screen.queryByRole('button')).not.toBeInTheDocument();
            expect(
                screen.queryByTestId('contributions-drawer'),
            ).not.toBeInTheDocument();
        });
    });
});
