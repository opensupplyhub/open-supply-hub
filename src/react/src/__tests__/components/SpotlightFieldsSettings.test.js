import React from 'react';
import { screen, waitFor, fireEvent } from '@testing-library/react';

import renderWithProviders from '../../util/testUtils/renderWithProviders';
import SpotlightFieldsSettings from '../../components/SpotlightFieldsSettings';
import {
    validateSpotlightInternalName,
    validateSpotlightDisplayName,
    getSpotlightFieldStatus,
} from '../../util/spotlightFields';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest');
jest.mock('react-toastify', () => ({ toast: { error: jest.fn() } }));

const baseSummary = {
    go_live_date: null,
    go_live_pending: false,
    can_control_visibility: false,
    available_in_api: true,
    available_in_data_downloads: true,
    fields: [],
};

const field = (overrides = {}) => ({
    name: 'certification_status',
    display_name: 'Certification Status',
    approved: true,
    active: false,
    ...overrides,
});

describe('Spotlight name rules', () => {
    it('accepts lowercase names with underscores', () => {
        expect(validateSpotlightInternalName('certification_status')).toBeNull();
        expect(validateSpotlightInternalName('scope_3')).toBeNull();
    });

    it('rejects uppercase, spaces, dashes, leading digits and long names', () => {
        ['Certification', 'has space', 'dash-ed', '1abc', 'a'.repeat(51)].forEach(
            bad => expect(validateSpotlightInternalName(bad)).toMatch(/internal name/i),
        );
        expect(validateSpotlightInternalName('')).toMatch(/enter/i);
    });

    it('limits the display name to 50 characters', () => {
        expect(validateSpotlightDisplayName('Certification Status')).toBeNull();
        expect(validateSpotlightDisplayName('x'.repeat(51))).toMatch(/50/);
        expect(validateSpotlightDisplayName('   ')).toMatch(/enter/i);
    });

    it('describes each status in plain words', () => {
        expect(getSpotlightFieldStatus(field({ approved: false }))).toBe(
            'Waiting for approval',
        );
        expect(getSpotlightFieldStatus(field())).toBe('Approved, inactive');
        expect(getSpotlightFieldStatus(field({ active: true }))).toBe('Active');
    });
});

describe('SpotlightFieldsSettings', () => {
    beforeEach(() => {
        jest.resetAllMocks();
    });

    it('shows the naming rules and an empty state', async () => {
        apiRequest.get.mockResolvedValue({ data: baseSummary });
        renderWithProviders(<SpotlightFieldsSettings />);
        expect(
            await screen.findByText(/You have not added any fields yet/i),
        ).toBeInTheDocument();
        expect(screen.getByText(/lowercase letters, numbers/i)).toBeInTheDocument();
    });

    it('blocks a bad internal name with a clear message and does not post', async () => {
        apiRequest.get.mockResolvedValue({ data: baseSummary });
        renderWithProviders(<SpotlightFieldsSettings />);
        await screen.findByText(/Add a field/i);
        fireEvent.change(screen.getByLabelText(/Internal name/i), {
            target: { value: 'Bad Name' },
        });
        fireEvent.change(screen.getByLabelText(/Display name/i), {
            target: { value: 'Bad Name' },
        });
        fireEvent.click(screen.getByRole('button', { name: /Submit field/i }));
        expect(
            await screen.findByText(/must use only lowercase letters/i),
        ).toBeInTheDocument();
        expect(apiRequest.post).not.toHaveBeenCalled();
    });

    it('posts a valid field and shows the pending-approval message', async () => {
        apiRequest.get.mockResolvedValue({ data: baseSummary });
        apiRequest.post.mockResolvedValue({
            data: {
                ...baseSummary,
                message: 'Thanks! Your new fields are inactive until approved.',
                fields: [field({ approved: false })],
            },
        });
        renderWithProviders(<SpotlightFieldsSettings />);
        await screen.findByText(/Add a field/i);
        fireEvent.change(screen.getByLabelText(/Internal name/i), {
            target: { value: 'certification_status' },
        });
        fireEvent.change(screen.getByLabelText(/Display name/i), {
            target: { value: 'Certification Status' },
        });
        fireEvent.click(screen.getByRole('button', { name: /Submit field/i }));
        await waitFor(() =>
            expect(apiRequest.post).toHaveBeenCalledWith(
                '/api/spotlight-fields/',
                {
                    name: 'certification_status',
                    display_name: 'Certification Status',
                },
            ),
        );
        expect(await screen.findByText(/inactive until approved/i)).toBeInTheDocument();
        expect(screen.getByText('Waiting for approval')).toBeInTheDocument();
    });

    it('lets a partner switch an approved field on', async () => {
        apiRequest.get.mockResolvedValue({
            data: { ...baseSummary, fields: [field()] },
        });
        apiRequest.patch.mockResolvedValue({
            data: { ...baseSummary, fields: [field({ active: true })] },
        });
        renderWithProviders(<SpotlightFieldsSettings />);
        const toggle = await screen.findByLabelText(/Active: certification_status/i);
        expect(toggle).not.toBeDisabled();
        fireEvent.click(toggle);
        await waitFor(() =>
            expect(apiRequest.patch).toHaveBeenCalledWith(
                '/api/spotlight-fields/certification_status/',
                { active: true },
            ),
        );
    });

    it('disables the switch for unapproved fields and before the go-live date', async () => {
        apiRequest.get.mockResolvedValue({
            data: {
                ...baseSummary,
                go_live_date: '2099-01-01',
                go_live_pending: true,
                fields: [
                    field({ name: 'waiting', approved: false }),
                    field({ name: 'approved_one' }),
                ],
            },
        });
        renderWithProviders(<SpotlightFieldsSettings />);
        expect(
            await screen.findByLabelText(/Active: waiting/i),
        ).toBeDisabled();
        expect(screen.getByLabelText(/Active: approved_one/i)).toBeDisabled();
        expect(screen.getByText(/Go-live date: 2099-01-01/i)).toBeInTheDocument();
    });

    it('has no delete control and shows visibility only when permitted', async () => {
        apiRequest.get.mockResolvedValue({
            data: { ...baseSummary, fields: [field()] },
        });
        const { unmount } = renderWithProviders(<SpotlightFieldsSettings />);
        await screen.findByText(/Your fields/i);
        expect(screen.queryByText(/delete/i, { selector: 'button' })).toBeNull();
        expect(screen.queryByText(/Show in the API/i)).toBeNull();
        unmount();

        apiRequest.get.mockResolvedValue({
            data: { ...baseSummary, can_control_visibility: true },
        });
        renderWithProviders(<SpotlightFieldsSettings />);
        expect(await screen.findByText(/Show in the API/i)).toBeInTheDocument();
    });
});
