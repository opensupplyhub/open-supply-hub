/*
 * Tests for the claims dashboard v2 data hooks (OSDEV-3355), focused
 * on response-ordering: a slow response for a previously selected
 * claim must never overwrite the currently selected claim's data.
 */
import { renderHook, act } from '@testing-library/react-hooks';

import apiRequest from '../../util/apiRequest';
import { useClaimDetail, useClaimsList } from '../../components/ClaimsV2/hooks';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn() },
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

describe('useClaimDetail', () => {
    beforeEach(() => apiRequest.get.mockReset());

    test('ignores a stale response after the selected claim changes', async () => {
        const slow = deferred();
        const fast = deferred();
        apiRequest.get
            .mockReturnValueOnce(slow.promise) // claim 1, never selected now
            .mockReturnValueOnce(fast.promise); // claim 2, current

        const { result, rerender } = renderHook(id => useClaimDetail(id), {
            initialProps: 1,
        });
        rerender(2);

        fast.resolve({ data: { id: 2 } });
        await flushPromises();
        expect(result.current.detail).toEqual({ id: 2 });

        // The stale response for claim 1 arrives last and must be dropped.
        slow.resolve({ data: { id: 1 } });
        await flushPromises();
        expect(result.current.detail).toEqual({ id: 2 });
        expect(result.current.fetching).toBe(false);
    });

    test('a stale error does not clobber the current claim', async () => {
        const slow = deferred();
        const fast = deferred();
        apiRequest.get
            .mockReturnValueOnce(slow.promise)
            .mockReturnValueOnce(fast.promise);

        const { result, rerender } = renderHook(id => useClaimDetail(id), {
            initialProps: 1,
        });
        rerender(2);

        fast.resolve({ data: { id: 2 } });
        await flushPromises();

        slow.reject(new Error('network'));
        await flushPromises();
        expect(result.current.error).toBeNull();
        expect(result.current.detail).toEqual({ id: 2 });
    });

    test('clears the detail when no claim is selected', async () => {
        apiRequest.get.mockResolvedValueOnce({ data: { id: 7 } });
        const { result, rerender } = renderHook(id => useClaimDetail(id), {
            initialProps: 7,
        });
        await flushPromises();
        expect(result.current.detail).toEqual({ id: 7 });

        rerender(null);
        await flushPromises();
        expect(result.current.detail).toBeNull();
        expect(apiRequest.get).toHaveBeenCalledTimes(1);
    });
});

describe('useClaimsList', () => {
    beforeEach(() => apiRequest.get.mockReset());

    test('refetchClaims issues a new request', async () => {
        apiRequest.get
            .mockResolvedValueOnce({ data: [{ id: 1 }] })
            .mockResolvedValueOnce({ data: [{ id: 1 }, { id: 2 }] });

        const { result } = renderHook(() => useClaimsList());
        await flushPromises();
        expect(result.current.claims).toHaveLength(1);

        act(() => result.current.refetchClaims());
        await flushPromises();
        expect(result.current.claims).toHaveLength(2);
        expect(apiRequest.get).toHaveBeenCalledTimes(2);
    });
});
