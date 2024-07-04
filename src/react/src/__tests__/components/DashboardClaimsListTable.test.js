import React from 'react';
import { Router, Route } from 'react-router-dom';
import { render, fireEvent, waitFor, screen, act } from '@testing-library/react';
import history from '../../util/history';
import DashboardClaimsListTable from '../../components/DashboardClaimsListTable';

const data = [
    {
        "id": 184,
        "created_at": "2024-06-14T10:45:53.857805Z",
        "updated_at": "2024-06-14T13:25:49.835368Z",
        "claim_decision": "2024-06-14T13:25:49.835368Z",
        "contributor_id": 1002,
        "os_id": "TR2024425AKVM2E",
        "contributor_name": "Contributor B",
        "facility_name": "Facility Beta",
        "facility_address": "456 Beta Avenue, Beta City, Türkiye",
        "facility_country_name": "Türkiye",
        "status": "APPROVED"
    },
    {
        "id": 45,
        "created_at": "2024-06-13T05:38:41.859592Z",
        "updated_at": "2024-06-13T05:38:41.859607Z",
        "claim_decision": null,
        "contributor_id": 1003,
        "os_id": "UK2661125AKVMHV",
        "contributor_name": "Contributor C",
        "facility_name": "Facility Gamma",
        "facility_address": "789 Gamma Road, Gamma City, United Kingdom",
        "facility_country_name": "United Kingdom",
        "status": "PENDING"
    },
    {
        "id": 24,
        "created_at": "2024-06-13T00:48:46.677503Z",
        "updated_at": "2024-06-13T00:48:46.677518Z",
        "claim_decision": null,
        "contributor_id": 1004,
        "os_id": "CN3023325AKVMQ3",
        "contributor_name": "Contributor D",
        "facility_name": "Facility Delta",
        "facility_address": "101 Delta Blvd, Delta City, Delta Country",
        "facility_country_name": "China",
        "status": "PENDING"
    },
    {
        "id": 12,
        "created_at": "2024-06-15T04:52:16.352025Z",
        "updated_at": "2024-06-15T04:52:16.352040Z",
        "claim_decision": "2024-06-15T04:52:16.352040Z",
        "contributor_id": 1001,
        "os_id": "CN2021177AKVM66",
        "contributor_name": "Contributor A",
        "facility_name": "Facility Alpha",
        "facility_address": "123 Alpha Street, Alpha City, China",
        "facility_country_name": "China",
        "status": "REVOKED"
    },
    {
        "id": 3,
        "created_at": "2024-06-13T00:24:49.566190Z",
        "updated_at": "2024-06-13T00:24:49.566204Z",
        "claim_decision": "2024-06-13T00:24:49.566204Z",
        "contributor_id": 1005,
        "os_id": "SP2421145AKVMH4",
        "contributor_name": "Contributor E",
        "facility_name": "Facility Epsilon",
        "facility_address": "202 Epsilon Parkway, Epsilon City, Spain",
        "facility_country_name": "Spain",
        "status": "DENIED"
    },
    {
        "id": 20,
        "created_at": "2024-06-15T04:58:23.352025Z",
        "updated_at": "2024-06-15T05:23:10.352040Z",
        "claim_decision": "2024-06-15T05:23:10.352040Z",
        "contributor_id": 1006,
        "os_id": "DM5021177DCET89",
        "contributor_name": "contributor b (lowercase test)",
        "facility_name": "facility beta (lowercase test)",
        "facility_address": "123 BetaLowerCase Street, BetaLowerCase City, Greece",
        "facility_country_name": "Greece",
        "status": "REVOKED"
    },
];

describe('DashboardClaimsListTable component', () => {
    let handleSortClaimsMock;

    beforeEach(() => {
        handleSortClaimsMock = jest.fn();

        render(
            <Router history={history}>
                <Route>
                    <DashboardClaimsListTable data={data} handleSortClaims={handleSortClaimsMock} />
                </Route>
            </Router>
        );
    });

    it('sort by claim id in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Claim ID'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].id).toBe(3);
            expect(sortedData[sortedData.length - 1].id).toBe(184);
        });
    });

    it('sort by facility name in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Facility Name'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].facility_name).toBe('Facility Alpha');
            expect(sortedData[1].facility_name).toBe('Facility Beta');
            expect(sortedData[2].facility_name).toBe('facility beta (lowercase test)');
            expect(sortedData[sortedData.length - 1].facility_name).toBe('Facility Gamma');
        });
    });

    it('sort by organization name in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Organization Name'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].contributor_name).toBe('Contributor A');
            expect(sortedData[1].contributor_name).toBe('Contributor B');
            expect(sortedData[2].contributor_name).toBe('contributor b (lowercase test)');
            expect(sortedData[sortedData.length - 1].contributor_name).toBe('Contributor E');
        });
    });

    it('sort by country in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Country'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].facility_country_name).toBe('China');
            expect(sortedData[sortedData.length - 1].facility_country_name).toBe('United Kingdom');
        });
    });

    it('sort by country in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Country'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].facility_country_name).toBe('China');
            expect(sortedData[sortedData.length - 1].facility_country_name).toBe('United Kingdom');
        });
    });

    it('sort by creation date in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Created'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].created_at).toBe('2024-06-13T00:24:49.566190Z');
            expect(sortedData[sortedData.length - 1].created_at).toBe('2024-06-15T04:58:23.352025Z');
        });
    });

    it('sort by last updated date in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Last Updated'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].updated_at).toBe('2024-06-13T00:24:49.566204Z');
            expect(sortedData[sortedData.length - 1].updated_at).toBe('2024-06-15T05:23:10.352040Z');
        });
    });

    it('sort by status in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Status'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].status).toBe('APPROVED');
            expect(sortedData[sortedData.length - 1].status).toBe('REVOKED');
        });
    });

    it('sort by claim decision in ascending order', async () => {
        act(() => {
            fireEvent.click(screen.getByText('Claim Decision'));
        });

        await waitFor(() => {
            expect(handleSortClaimsMock).toHaveBeenCalled();
            const sortedData = handleSortClaimsMock.mock.calls[0][0];
            expect(sortedData[0].claim_decision).toBe('2024-06-13T00:24:49.566204Z');
            expect(sortedData[sortedData.length - 1].claim_decision).toBe(null);
        });
    });
});
