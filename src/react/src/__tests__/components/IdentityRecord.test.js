import React from 'react';
import { Router } from 'react-router-dom';
import { screen, waitFor } from '@testing-library/react';

import history from '../../util/history';
import renderWithProviders from '../../util/testUtils/renderWithProviders';
import { IdentityRecord } from '../../components/IdentityRecord/IdentityRecord';
import {
    asText,
    failureMessage,
    formatAddress,
    getClaims,
    getOperator,
    getProcessCategories,
} from '../../components/IdentityRecord/recordFields';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest');

const OS_ID = 'XX2000001AAAAA5';

const CREDENTIAL = {
    type: ['VerifiableCredential', 'DigitalFacilityRecord'],
    issuer: { id: 'did:web:issuer.example.org' },
    credentialSubject: {
        name: 'Example Facility',
        registeredId: 'REC-00000001',
        countryOfOperation: { countryCode: 'XX', countryName: 'Exampleland' },
        address: {
            streetAddress: '1 Example Road',
            addressLocality: 'Example City',
            postalCode: '00000',
            addressCountry: { countryName: 'Exampleland' },
        },
        processCategory: [{ code: 'Manufacturing', name: 'Manufacturing' }],
        relatedParty: [
            { role: 'operator', party: { name: 'Example Operator' } },
        ],
        performanceClaim: [
            {
                id: 'urn:example:claim:1',
                name: 'Self-Declared Country of Origin',
                claimDate: '2026-09-04',
                claimedPerformance: [{ score: { code: 'Declared' } }],
            },
        ],
    },
};

const AVAILABLE = {
    os_id: OS_ID,
    available: true,
    resolver_uri: 'https://resolver.test-issuer.example/records/REC-00000001',
    document_uri: 'https://documents.test-issuer.example/doc.json',
    record_type: 'untp:DigitalFacilityRecord',
    issuer: 'did:web:issuer.example.org',
    credential: CREDENTIAL,
};

const renderPage = () =>
    renderWithProviders(
        <Router history={history}>
            <IdentityRecord
                classes={{}}
                match={{ params: { osID: OS_ID } }}
            />
        </Router>,
    );

describe('IdentityRecord page', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders the record, attributed to its issuer', async () => {
        apiRequest.get.mockResolvedValue({ data: AVAILABLE });

        renderPage();

        await waitFor(() =>
            expect(screen.getByText('Example Facility')).toBeInTheDocument(),
        );

        expect(
            screen.getByText(/1 Example Road, Example City/),
        ).toBeInTheDocument();
        expect(screen.getAllByText(/did:web:issuer.example.org/).length)
            .toBeGreaterThan(0);
        expect(
            screen.getByText('View the signed credential'),
        ).toBeInTheDocument();
    });

    it('never claims the credential has been verified', async () => {
        /*
         * We decode the credential without checking its signature, so the
         * page must not imply otherwise. This is the assertion that stops
         * someone adding a reassuring word later.
         */
        apiRequest.get.mockResolvedValue({ data: AVAILABLE });

        renderPage();

        await waitFor(() =>
            expect(screen.getByText('Example Facility')).toBeInTheDocument(),
        );

        expect(
            screen.getByText(/signature on the credential is not checked/i),
        ).toBeInTheDocument();
        expect(screen.queryByText(/\bverified\b/i)).not.toBeInTheDocument();
    });

    it('shows a loading state while the record is fetched', () => {
        apiRequest.get.mockReturnValue(new Promise(() => {}));

        renderPage();

        expect(
            screen.getByText(/Fetching the record from its issuer/i),
        ).toBeInTheDocument();
    });

    it('shows an honest degraded state that keeps the location reachable',
        async () => {
            apiRequest.get.mockResolvedValue({
                data: { os_id: OS_ID, available: false, reason: 'timeout' },
            });

            renderPage();

            await waitFor(() =>
                expect(
                    screen.getByText(/not available right now/i),
                ).toBeInTheDocument(),
            );

            expect(
                screen.getByText(/did not respond in time/i),
            ).toBeInTheDocument();
            expect(
                screen.getByText(/View the Open Supply Hub production/i),
            ).toBeInTheDocument();
        });

    it('distinguishes an unregistered identifier from a failure',
        async () => {
            apiRequest.get.mockResolvedValue({
                data: {
                    os_id: OS_ID,
                    available: false,
                    reason: 'not_registered',
                },
            });

            renderPage();

            await waitFor(() =>
                expect(
                    screen.getByText(/No record is registered/i),
                ).toBeInTheDocument(),
            );
        });

    it('handles the request itself failing', async () => {
        apiRequest.get.mockRejectedValue(new Error('network'));

        renderPage();

        await waitFor(() =>
            expect(
                screen.getByText(/could not be loaded/i),
            ).toBeInTheDocument(),
        );
    });
});

describe('identityRecord helpers', () => {
    it('formats an address from the parts that are present', () => {
        expect(
            formatAddress({
                streetAddress: '1 Example Road',
                addressLocality: 'Example City',
            }),
        ).toBe('1 Example Road, Example City');

        expect(formatAddress({})).toBeNull();
        expect(formatAddress(null)).toBeNull();
    });

    it('surfaces each claim score rather than dropping it', () => {
        /*
         * Every claim on the pilot records is self-declared. Showing the
         * claim without its score would read as an assessment result,
         * which would overstate what the issuer is saying.
         */
        const claims = getClaims(CREDENTIAL);

        expect(claims).toHaveLength(1);
        expect(claims[0].scores).toEqual(['Declared']);
        expect(claims[0].claimDate).toBe('2026-09-04');
    });

    it('reads the operator and process categories', () => {
        expect(getOperator(CREDENTIAL)).toBe('Example Operator');
        expect(getProcessCategories(CREDENTIAL)).toEqual(['Manufacturing']);
    });

    it('copes with a record missing every optional section', () => {
        const bare = { credentialSubject: { name: 'Bare' } };

        expect(getClaims(bare)).toEqual([]);
        expect(getProcessCategories(bare)).toEqual([]);
        expect(getOperator(bare)).toBeNull();
    });

    /*
     * The backend checks only that the document is an object carrying
     * credentialSubject, so every shape below is one an issuer can
     * legally publish. A throw here would be caught by the boundary
     * wrapping the whole application, not just this page, so the
     * visitor would lose the site rather than the record.
     */
    it('does not throw on singular values where a list is expected', () => {
        const compacted = {
            credentialSubject: {
                name: 'Compacted',
                // JSON-LD collapses one-element lists to a bare object.
                processCategory: { name: 'Manufacturing' },
                relatedParty: { role: 'operator', party: { name: 'Solo' } },
                performanceClaim: {
                    name: 'Only claim',
                    claimedPerformance: { score: { code: 'Declared' } },
                    conformityTopic: { name: 'Labour' },
                    referenceCriteria: { name: 'Hours' },
                },
            },
        };

        expect(getProcessCategories(compacted)).toEqual(['Manufacturing']);
        expect(getOperator(compacted)).toBe('Solo');

        const claims = getClaims(compacted);
        expect(claims).toHaveLength(1);
        expect(claims[0].name).toBe('Only claim');
        expect(claims[0].scores).toEqual(['Declared']);
        expect(claims[0].topics).toEqual(['Labour']);
        expect(claims[0].criteria).toEqual(['Hours']);
    });

    it('drops object-valued scalars rather than rendering them', () => {
        const languageTagged = {
            credentialSubject: {
                // A value object is legal JSON-LD, and React throws on
                // an object child.
                name: { '@value': 'Acme', '@language': 'en' },
                processCategory: ['Weaving'],
                performanceClaim: [
                    { name: { '@value': 'Odd' }, claimDate: {} },
                ],
            },
        };

        expect(asText(languageTagged.credentialSubject.name)).toBeNull();

        const claims = getClaims(languageTagged);
        expect(claims[0].name).toBe('Claim');
        expect(claims[0].claimDate).toBeNull();
    });

    it('reads an address sent as a string or as a list', () => {
        expect(formatAddress('1 Example Road, Example City')).toBe(
            '1 Example Road, Example City',
        );
        expect(
            formatAddress([{ streetAddress: '2 Example Road' }]),
        ).toBe('2 Example Road');
        expect(formatAddress({ streetAddress: { '@value': 'x' } })).toBeNull();
    });

    it('survives a credentialSubject sent as a list', () => {
        const listed = { credentialSubject: [{ name: 'Listed' }] };

        expect(getClaims(listed)).toEqual([]);
        expect(getProcessCategories(listed)).toEqual([]);
        expect(getOperator(listed)).toBeNull();
    });

    it('gives a specific message per failure reason', () => {
        expect(failureMessage('encrypted')).toMatch(/encrypted/i);
        expect(failureMessage('not_registered')).toMatch(/No record/i);
        expect(failureMessage('something_new')).toMatch(
            /temporarily unavailable/i,
        );
    });
});
