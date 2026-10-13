/* eslint-env jest */

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import VerificationPanel from '../../components/ClaimsV2/VerificationPanel';

const baseDetail = {
    facility: {
        properties: { name: 'Example Winery', address: '1 Example Street' },
    },
    contact_person: 'Sam Example',
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
                    contributor: { name: 'Example Holdings' },
                }}
                review={null}
                onShowDocument={() => {}}
            />,
        );
        expect(
            screen.getByText('Example Holdings'),
        ).toBeInTheDocument();
    });

    it('prefers the claim-stated company_name when present', () => {
        render(
            <VerificationPanel
                detail={{
                    ...baseDetail,
                    company_name: 'Example Winery SARL',
                    contributor: { name: 'Example Holdings' },
                }}
                review={null}
                onShowDocument={() => {}}
            />,
        );
        expect(screen.getByText('Example Winery SARL')).toBeInTheDocument();
        expect(
            screen.queryByText('Example Holdings'),
        ).not.toBeInTheDocument();
    });
});
