import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';

import CandidateListMap from '../../components/Candidate/CandidateListMap';

jest.mock('leaflet', () => ({
    DomEvent: { preventDefault: jest.fn() },
    latLngBounds: (start, end) => ({
        getWest: () => Math.min(start.lng, end.lng),
        getSouth: () => Math.min(start.lat, end.lat),
        getEast: () => Math.max(start.lng, end.lng),
        getNorth: () => Math.max(start.lat, end.lat),
    }),
}));

jest.mock('react-leaflet-control', () => ({
    __esModule: true,
    default: ({ children }) => <div>{children}</div>,
}));

// A stand-in Leaflet map: records fitBounds calls and lets a test fire the
// mouse events the draw mode listens for.
const makeMap = () => {
    const handlers = {};
    return {
        fitBounds: jest.fn(),
        dragging: { enable: jest.fn(), disable: jest.fn() },
        on: (event, handler) => {
            handlers[event] = handler;
        },
        off: event => {
            delete handlers[event];
        },
        // Pixels == degrees * 100, enough to tell a click from a drag.
        latLngToContainerPoint: ({ lat, lng }) => ({
            x: lng * 100,
            y: -lat * 100,
        }),
        fire: (event, latlng) =>
            handlers[event] && handlers[event]({ latlng, originalEvent: {} }),
        has: event => Boolean(handlers[event]),
    };
};

let mockMap;

jest.mock('react-leaflet', () => {
    const ReactModule = jest.requireActual('react');
    return {
        // eslint-disable-next-line react/prop-types
        Map: ReactModule.forwardRef(({ children }, ref) => {
            ReactModule.useImperativeHandle(ref, () => ({
                leafletElement: mockMap,
            }));
            return <div data-testid="leaflet-map">{children}</div>;
        }),
        TileLayer: () => null,
        CircleMarker: ({ center, onClick }) => (
            <button
                type="button"
                data-testid="dot"
                data-center={center.join(',')}
                aria-label={center.join(',')}
                onClick={onClick}
            />
        ),
        Rectangle: ({ bounds }) => (
            <div data-testid="rectangle" data-bounds={JSON.stringify(bounds)} />
        ),
    };
});

const row = (osId, lat, lng, state = 'unverified') => ({
    osId,
    coordinates: lat === null ? null : { lat, lng },
    validation: { state },
});

const renderMap = (props = {}) => {
    const onSelect = jest.fn();
    const onBboxChange = jest.fn();
    const utils = render(
        <CandidateListMap
            rows={[row('A', 10, 20), row('B', 11, 21)]}
            selectedOsId={null}
            bbox={null}
            onSelect={onSelect}
            onBboxChange={onBboxChange}
            {...props}
        />,
    );
    return { ...utils, onSelect, onBboxChange };
};

beforeEach(() => {
    mockMap = makeMap();
});

describe('CandidateListMap', () => {
    it('fits the page once and not again when a vote replaces the rows', () => {
        const { rerender } = renderMap();
        expect(mockMap.fitBounds).toHaveBeenCalledTimes(1);
        expect(mockMap.fitBounds.mock.calls[0][0]).toEqual([
            [10, 20],
            [11, 21],
        ]);

        // Same dots, new array with one row's validation changed in place.
        rerender(
            <CandidateListMap
                rows={[row('A', 10, 20, 'confirmed'), row('B', 11, 21)]}
                selectedOsId="A"
                bbox={null}
                onSelect={jest.fn()}
                onBboxChange={jest.fn()}
            />,
        );
        expect(mockMap.fitBounds).toHaveBeenCalledTimes(1);

        // A different page refits.
        rerender(
            <CandidateListMap
                rows={[row('C', 30, 40)]}
                selectedOsId={null}
                bbox={null}
                onSelect={jest.fn()}
                onBboxChange={jest.fn()}
            />,
        );
        expect(mockMap.fitBounds).toHaveBeenCalledTimes(2);
    });

    it('does not fit the map when no row on the page has a position', () => {
        renderMap({ rows: [row('A', null), row('B', null)] });
        expect(mockMap.fitBounds).not.toHaveBeenCalled();
        expect(screen.queryAllByTestId('dot')).toHaveLength(0);
    });

    it('fits the drawn area instead of the dots when there is one', () => {
        renderMap({ bbox: '20,10,21,11' });
        expect(mockMap.fitBounds).toHaveBeenCalledTimes(1);
        expect(mockMap.fitBounds.mock.calls[0][0]).toEqual([
            [10, 20],
            [11, 21],
        ]);
    });

    it('finishes a drag released outside the map at the last point it saw', () => {
        const { onBboxChange } = renderMap();
        fireEvent.click(screen.getByTestId('candidate-map-draw'));
        expect(mockMap.dragging.disable).toHaveBeenCalled();

        act(() => {
            mockMap.fire('mousedown', { lat: 10, lng: 20 });
            mockMap.fire('mousemove', { lat: 12, lng: 23 });
        });
        expect(screen.getByTestId('rectangle')).toBeInTheDocument();

        // Released over the page, not the map.
        act(() => {
            fireEvent.mouseUp(document.body);
        });
        expect(onBboxChange).toHaveBeenCalledWith('20,10,23,12');
        expect(screen.queryByTestId('rectangle')).not.toBeInTheDocument();
        // Draw mode is over: the map listeners are gone and panning is back.
        expect(mockMap.has('mousedown')).toBe(false);
        expect(mockMap.dragging.enable).toHaveBeenCalled();

        // A later mouseup on the page does nothing.
        act(() => {
            fireEvent.mouseUp(document.body);
        });
        expect(onBboxChange).toHaveBeenCalledTimes(1);
    });

    it('treats a short drag as a click and sets no area', () => {
        const { onBboxChange } = renderMap();
        fireEvent.click(screen.getByTestId('candidate-map-draw'));
        act(() => {
            mockMap.fire('mousedown', { lat: 10, lng: 20 });
            mockMap.fire('mouseup', { lat: 10.01, lng: 20.01 });
        });
        expect(onBboxChange).not.toHaveBeenCalled();
    });

    it('selects a row from its dot when not drawing', () => {
        const { onSelect } = renderMap();
        fireEvent.click(screen.getAllByTestId('dot')[1]);
        expect(onSelect).toHaveBeenCalledWith('B');
    });
});
