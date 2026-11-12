/*
 * Tests for the organization data hooks: a missing organization is a
 * value, not an error; a URL that is not ready yet sends nothing; and
 * a slow response for an earlier URL never overwrites a newer one.
 */
import { renderHook, act } from '@testing-library/react-hooks';

import apiRequest from '../../util/apiRequest';
import {
    useApiGet,
    useCurrentOrganization,
    useOrganizationAction,
    useOrganizationInvitations,
} from '../../components/Organization/hooks';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn(), post: jest.fn() },
}));

const deferred = () => {
    let resolve;
    let reject;
    const promise = new Promise((res, rej) => {
        resolve = res;
        reject = rej;
    });
    return { promise, resolve, reject };
};

const flushPromises = () => act(() => Promise.resolve());

describe('useCurrentOrganization', () => {
    beforeEach(() => apiRequest.get.mockReset());

    test('returns the organization', async () => {
        apiRequest.get.mockResolvedValue({
            data: { uuid: 'abc', name: 'Brand', role: 'ADMIN' },
        });

        const { result } = renderHook(() => useCurrentOrganization());
        await flushPromises();

        expect(apiRequest.get).toHaveBeenCalledWith(
            '/api/organizations/current/',
        );
        expect(result.current.organization.name).toBe('Brand');
        expect(result.current.loaded).toBe(true);
        expect(result.current.error).toBeNull();
    });

    test('treats 404 as belonging to no organization, not as an error', async () => {
        apiRequest.get.mockRejectedValue({ response: { status: 404 } });

        const { result } = renderHook(() => useCurrentOrganization());
        await flushPromises();

        expect(result.current.organization).toBeNull();
        expect(result.current.loaded).toBe(true);
        expect(result.current.error).toBeNull();
    });

    test('reports any other failure', async () => {
        apiRequest.get.mockRejectedValue({
            response: { status: 500, data: {} },
        });

        const { result } = renderHook(() => useCurrentOrganization());
        await flushPromises();

        expect(result.current.loaded).toBe(false);
        expect(result.current.error).toBe(
            'Your organization could not be loaded.',
        );
    });
});

describe('useOrganizationInvitations', () => {
    beforeEach(() => apiRequest.get.mockReset());

    test('sends nothing for a Member, who cannot list invitations', async () => {
        const { result } = renderHook(() =>
            useOrganizationInvitations('abc', false),
        );
        await flushPromises();

        expect(apiRequest.get).not.toHaveBeenCalled();
        expect(result.current.invitations).toEqual([]);
    });

    test('fetches for an Admin', async () => {
        apiRequest.get.mockResolvedValue({ data: [{ uuid: 'i1' }] });

        const { result } = renderHook(() =>
            useOrganizationInvitations('abc', true),
        );
        await flushPromises();

        expect(apiRequest.get).toHaveBeenCalledWith(
            '/api/organizations/abc/invitations/',
        );
        expect(result.current.invitations).toEqual([{ uuid: 'i1' }]);
    });
});

describe('useApiGet', () => {
    beforeEach(() => apiRequest.get.mockReset());

    test('ignores a stale response after the url changes', async () => {
        const slow = deferred();
        const fast = deferred();
        apiRequest.get
            .mockReturnValueOnce(slow.promise)
            .mockReturnValueOnce(fast.promise);

        const { result, rerender } = renderHook(url => useApiGet(url), {
            initialProps: '/first/',
        });
        rerender('/second/');

        fast.resolve({ data: { page: 2 } });
        await flushPromises();
        expect(result.current.data).toEqual({ page: 2 });

        slow.resolve({ data: { page: 1 } });
        await flushPromises();
        expect(result.current.data).toEqual({ page: 2 });
    });

    test('refetch requests the same url again', async () => {
        apiRequest.get.mockResolvedValue({ data: [] });

        const { result } = renderHook(() => useApiGet('/again/'));
        await flushPromises();
        act(() => result.current.refetch());
        await flushPromises();

        expect(apiRequest.get).toHaveBeenCalledTimes(2);
    });
});

describe('useOrganizationAction', () => {
    test('keeps the reason the API gave when an action is refused', async () => {
        const { result } = renderHook(() => useOrganizationAction());
        const refusal = Object.assign(new Error('Bad Request'), {
            response: {
                data: { email: ['The organization has no free seat.'] },
            },
        });
        const refused = () => Promise.reject(refusal);

        await act(async () => {
            await result.current.run(refused).catch(() => {});
        });

        expect(result.current.actionError).toBe(
            'The organization has no free seat.',
        );
        expect(result.current.acting).toBe(false);
    });

    test('resolves with the response data on success', async () => {
        const { result } = renderHook(() => useOrganizationAction());
        let data;

        await act(async () => {
            data = await result.current.run(() =>
                Promise.resolve({ data: { email: 'a@b.example' } }),
            );
        });

        expect(data).toEqual({ email: 'a@b.example' });
        expect(result.current.actionError).toBeNull();
    });
});
