import React from 'react';
import { fireEvent, waitFor } from '@testing-library/react';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import ClaimInfoSection from '../../components/InitialClaimFlow/ClaimIntro/ClaimInfoSection';

describe('ClaimInfoSection component', () => {
    const renderComponent = () => renderWithProviders(<ClaimInfoSection />);

    test('renders without crashing', () => {
        renderComponent();
    });

    describe('Step 1 - Eligibility rendering', () => {
        test('displays Step 1 title', () => {
            const { getByText } = renderComponent();

            expect(getByText('Confirm Your Eligibility')).toBeInTheDocument();
        });

        test('displays eligibility requirements', () => {
            const { getByText } = renderComponent();

            expect(
                getByText(/Claim requests must be submitted by a current employee/)
            ).toBeInTheDocument();
            expect(
                getByText(/If you're not an owner or manager/)
            ).toBeInTheDocument();
        });
    });

    describe('Step 2 - Prove Your Name and Role rendering', () => {
        test('displays Step 2 title', () => {
            const { getByText } = renderComponent();

            expect(getByText('Prove Your Name and Role')).toBeInTheDocument();
        });

        test('displays OPTIONS list', () => {
            const { getByText } = renderComponent();

            expect(
                getByText(/Company website showing your name and role/)
            ).toBeInTheDocument();
            expect(getByText(/Employee ID badge/)).toBeInTheDocument();
            expect(getByText(/Employment letter/)).toBeInTheDocument();
        });

        test('displays employee examples for Step 2', () => {
            const { getAllByAltText } = renderComponent();

            expect(
                getAllByAltText('Example employee ID badge')[0]
            ).toBeInTheDocument();
            expect(
                getAllByAltText('Example employment letter')[0]
            ).toBeInTheDocument();
            expect(
                getAllByAltText('Example business card')[0]
            ).toBeInTheDocument();
        });
    });

    describe('Step 3 - Prove Your Company Name and Address rendering', () => {
        test('displays Step 3 title', () => {
            const { getByText } = renderComponent();

            expect(
                getByText('Prove Your Company Name and Address')
            ).toBeInTheDocument();
        });

        test('displays company verification OPTIONS', () => {
            const { getByText } = renderComponent();

            expect(getByText(/Business registration/)).toBeInTheDocument();
            expect(getByText(/Business license/)).toBeInTheDocument();
            expect(getByText(/Utility bill/)).toBeInTheDocument();
        });

        test('displays NOTE about company name and address', () => {
            const { getByText } = renderComponent();

            expect(
                getByText(/The document must show the same company name and address/)
            ).toBeInTheDocument();
        });

        test('displays company examples for Step 3', () => {
            const { getAllByAltText } = renderComponent();

            expect(
                getAllByAltText('Example business registration certificate')[0]
            ).toBeInTheDocument();
            expect(
                getAllByAltText('Example business license')[0]
            ).toBeInTheDocument();
            expect(
                getAllByAltText('Example utility bill')[0]
            ).toBeInTheDocument();
        });
    });

    describe('Step 4 and 5 - Maximum Value section rendering', () => {
        test('displays Maximum Value badge', () => {
            const { getByText } = renderComponent();

            expect(getByText('Maximum Value')).toBeInTheDocument();
        });

        test('displays Step 4 - Add Key Details', () => {
            const { getByText } = renderComponent();

            expect(getByText(/Add Key Details:/)).toBeInTheDocument();
            expect(
                getByText(/Provide information about the production location/)
            ).toBeInTheDocument();
        });

        test('displays Step 5 - Get a Credible and Confirmed Profile', () => {
            const { getByText } = renderComponent();

            expect(getByText(/Get a Credible and Confirmed Profile:/)).toBeInTheDocument();
            expect(
                getByText(/After the claim is approved, you get a credible/)
            ).toBeInTheDocument();
        });
    });

    describe('Important Note rendering', () => {
        test('displays important warning box', () => {
            const { getByText } = renderComponent();

            expect(getByText('IMPORTANT!')).toBeInTheDocument();
            expect(
                getByText(/Any documentation appearing to be forged/)
            ).toBeInTheDocument();
        });

        test('displays info icon in warning box', () => {
            const { container } = renderComponent();

            const svgIcons = container.querySelectorAll('svg');
            expect(svgIcons.length).toBeGreaterThan(0);
        });
    });

    describe('Image Dialog functionality', () => {
        test('opens dialog when example image is clicked', async () => {
            const { getAllByAltText, getByRole } = renderComponent();

            const exampleImage = getAllByAltText('Example employee ID badge')[0];
            const imageButton = exampleImage.closest('button');

            fireEvent.click(imageButton);

            await waitFor(() => {
                const dialog = getByRole('dialog');
                expect(dialog).toBeInTheDocument();
            });
        });

        test('displays image in dialog when opened', async () => {
            const { getAllByAltText } = renderComponent();

            const exampleImage = getAllByAltText('Example employee ID badge')[0];
            const imageButton = exampleImage.closest('button');

            fireEvent.click(imageButton);

            await waitFor(() => {
                const dialogImages = getAllByAltText('Example employee ID badge');

                expect(dialogImages.length).toBeGreaterThan(1);
            });
        });
    });

    describe('External link', () => {
        test('displays learn more link', () => {
            const { getByText } = renderComponent();

            const link = getByText('Learn more about claiming your production location');
            expect(link).toBeInTheDocument();
            expect(link.tagName).toBe('A');
            expect(link).toHaveAttribute('href', 'https://info.opensupplyhub.org/resources/claim-a-facility');
            expect(link).toHaveAttribute('target', '_blank');
        });
    });
});
