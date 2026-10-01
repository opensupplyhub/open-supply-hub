/* eslint-env jest */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import VerificationPanel from '../../components/ClaimsV2/VerificationPanel';

const baseDetail = {
    facility: {
        properties: { name: 'Arthur Metz', address: '102 rue du GdG' },
    },
    contact_person: 'Camille',
    job_title: 'Quality Manager',
    email: 'c@example.com',
};

describe('VerificationPanel claimant account row', () => {
    it('falls back to the contributor account name when company_name is blank', () => {
        // New-flow claims never set company_name — the account name is
        // the only organization the claimant stated.
        render(
            <VerificationPanel
                detail={{
                    ...baseDetail,
                    company_name: '',
                    contributor: { name: 'Les Grands Chais de France' },
                }}
                review={null}
                onShowDocument={() => {}}
            />,
        );
        expect(
            screen.getByText('Les Grands Chais de France'),
        ).toBeInTheDocument();
    });

    it('prefers the claim-stated company_name when present', () => {
        render(
            <VerificationPanel
                detail={{
                    ...baseDetail,
                    company_name: 'Arthur Metz SARL',
                    contributor: { name: 'Les Grands Chais de France' },
                }}
                review={null}
                onShowDocument={() => {}}
            />,
        );
        expect(screen.getByText('Arthur Metz SARL')).toBeInTheDocument();
        expect(
            screen.queryByText('Les Grands Chais de France'),
        ).not.toBeInTheDocument();
    });
});
