import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';

import {
    UnwrappedCandidatePolygonsLayer as CandidatePolygonsLayer,
    buildCandidatesRequestURL,
} from '../../components/Candidate/CandidatePolygonsLayer';
import apiRequest from '../../util/apiRequest';

jest.mock('../../util/apiRequest', () => ({
    __esModule: true,
    default: { get: jest.fn() },
}));

jest.mock('leaflet', () => ({
    circleMarker: jest.fn(() => ({})),
    DomEvent: { stopPropagation: jest.fn() },
}));

const layerHandlers = [];

jest.mock('react-leaflet', () => ({
    withLeaflet: Component => Component,
    GeoJSON: ({ data, onEachFeature }) => {
        data.features.forEach(feature => {
            const handlers = {};
            const layer = {
                setStyle: jest.fn(),
                bindTooltip: jest.fn(),
                on: (event, handler) => {
                    handlers[event] = handler;
                },
            };
            onEachFeature(feature, layer);
            layerHandlers.push({ feature, handlers, layer });
        });
        return (
            <div data-testid="candidate-geojson" data-count={data.features.length} />
        );
    },
}));

const makeBounds = () => ({
    getWest: () => -79.2,
    getSouth: () => 35.1,
    getEast: () => -79.1,
    getNorth: () => 35.2,
});

const makeMap = (zoom = 15) => {
    const handlers = {};
    return {
        getZoom: () => zoom,
        getBounds: makeBounds,
        on: jest.fn((event, handler) => {
            handlers[event] = handler;
        }),
        off: jest.fn(),
        trigger: event => handlers[event] && handlers[event](),
    };
};

const feature = (osId, state) => ({
    type: 'Feature',
    id: osId,
    geometry: {
        type: 'Polygon',
        coordinates: [
            [
                [-79.15, 35.15],
                [-79.14, 35.15],
                [-79.14, 35.16],
                [-79.15, 35.15],
            ],
        ],
    },
    properties: {
        os_id: osId,
        confidence: 0.8,
        source: 'Earth Genome',
        state,
        tally: { confirmed: 0, not_a_facility: 0 },
        centroid: { lat: 35.15, lng: -79.145 },
    },
});

const collection = features => ({ type: 'FeatureCollection', features });

const EXPECTED_URL =
    '/api/v1/production-locations/candidates/?bbox=-79.2,35.1,-79.1,35.2&limit=200';

describe('CandidatePolygonsLayer', () => {
    beforeEach(() => {
        layerHandlers.length = 0;
        jest.useFakeTimers('modern');
    });

    afterEach(() => {
        jest.useRealTimers();
        jest.clearAllMocks();
    });

    it('builds the bbox URL from the map viewport', () => {
        expect(buildCandidatesRequestURL(makeMap(15))).toBe(EXPECTED_URL);
        expect(buildCandidatesRequestURL(makeMap(11))).toBeNull();
        expect(buildCandidatesRequestURL(null)).toBeNull();
    });

    it('fetches the viewport on mount and renders the features', async () => {
        apiRequest.get.mockResolvedValue({
            data: collection([
                feature('US1', 'unverified'),
                feature('US2', 'disputed'),
            ]),
        });
        const map = makeMap(15);

        render(<CandidatePolygonsLayer leaflet={{ map }} />);

        expect(apiRequest.get).toHaveBeenCalledTimes(1);
        expect(apiRequest.get).toHaveBeenCalledWith(
            EXPECTED_URL,
            expect.objectContaining({ signal: expect.anything() }),
        );
        await waitFor(() =>
            expect(screen.getByTestId('candidate-geojson')).toHaveAttribute(
                'data-count',
                '2',
            ),
        );
        expect(map.on).toHaveBeenCalledWith('moveend', expect.any(Function));
        // Styling + state label applied per feature.
        expect(layerHandlers[0].layer.setStyle).toHaveBeenCalledWith(
            expect.objectContaining({ dashArray: '6 4' }),
        );
        expect(layerHandlers[1].layer.bindTooltip).toHaveBeenCalledWith(
            'Disputed',
            expect.any(Object),
        );
    });

    it('does not request when zoomed out below the minimum zoom', () => {
        const map = makeMap(10);

        const { container } = render(
            <CandidatePolygonsLayer leaflet={{ map }} />,
        );

        expect(apiRequest.get).not.toHaveBeenCalled();
        expect(container).toBeEmptyDOMElement();
    });

    it('debounces moveend and aborts the stale request', async () => {
        apiRequest.get.mockResolvedValue({ data: collection([]) });
        const map = makeMap(15);
        render(<CandidatePolygonsLayer leaflet={{ map }} />);
        expect(apiRequest.get).toHaveBeenCalledTimes(1);
        const firstSignal = apiRequest.get.mock.calls[0][1].signal;

        act(() => {
            map.trigger('moveend');
            map.trigger('moveend');
            map.trigger('moveend');
        });
        expect(apiRequest.get).toHaveBeenCalledTimes(1);

        act(() => {
            jest.advanceTimersByTime(350);
        });

        expect(apiRequest.get).toHaveBeenCalledTimes(2);
        expect(firstSignal.aborted).toBe(true);
        expect(apiRequest.get.mock.calls[1][1].signal.aborted).toBe(false);
    });

    it('calls onCandidateClick with the feature properties', async () => {
        apiRequest.get.mockResolvedValue({
            data: collection([feature('US1', 'confirmed')]),
        });
        const onCandidateClick = jest.fn();

        render(
            <CandidatePolygonsLayer
                leaflet={{ map: makeMap(16) }}
                onCandidateClick={onCandidateClick}
            />,
        );
        await waitFor(() =>
            expect(screen.getByTestId('candidate-geojson')).toBeInTheDocument(),
        );

        layerHandlers[0].handlers.click({ originalEvent: {} });

        expect(onCandidateClick).toHaveBeenCalledWith(
            expect.objectContaining({ os_id: 'US1', state: 'confirmed' }),
        );
    });

    it('removes the listener and aborts on unmount', () => {
        apiRequest.get.mockReturnValue(new Promise(() => {}));
        const map = makeMap(15);
        const { unmount } = render(
            <CandidatePolygonsLayer leaflet={{ map }} />,
        );
        const { signal } = apiRequest.get.mock.calls[0][1];

        unmount();

        expect(map.off).toHaveBeenCalledWith('moveend', expect.any(Function));
        expect(signal.aborted).toBe(true);
    });
});
