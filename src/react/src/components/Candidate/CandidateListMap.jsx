import React, {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import {
    Map as ReactLeafletMap,
    TileLayer,
    CircleMarker,
    Rectangle,
} from 'react-leaflet';
import Control from 'react-leaflet-control';
import L from 'leaflet';

import 'leaflet/dist/leaflet.css';

import {
    SATELLITE_TILE_URL,
    SATELLITE_TILE_ATTRIBUTION,
} from '../ProductionLocation/ProductionLocationDetailsMap/constants';
import { initialCenter, initialZoom } from '../../util/constants.facilitiesMap';
import {
    CANDIDATE_LIST_COPY,
    CANDIDATE_STATES,
    CANDIDATE_STATE_STYLES,
} from '../../util/candidateCopy';
import { formatBbox } from '../../util/candidates';
import COLOURS from '../../util/COLOURS';
import { candidateListMapStyles } from './styles';

const AREA_STYLE = Object.freeze({
    color: COLOURS.LIGHT_BLUE,
    weight: 2,
    dashArray: '6 4',
    fillOpacity: 0.05,
});

// Drags shorter than this (in pixels) are taken as a click, not an area.
const MIN_DRAG_PX = 8;

/** "minLng,minLat,maxLng,maxLat" -> Leaflet [[south, west], [north, east]] */
export const bboxToBounds = bbox => {
    if (!bbox) return null;
    const [west, south, east, north] = bbox.split(',').map(Number);
    return [
        [south, west],
        [north, east],
    ];
};

const markerStyle = (state, selected) => {
    const stateStyle =
        CANDIDATE_STATE_STYLES[state] ||
        CANDIDATE_STATE_STYLES[CANDIDATE_STATES.UNVERIFIED];
    return {
        color: selected ? COLOURS.PURPLE : stateStyle.color,
        fillColor: stateStyle.fillColor,
        fillOpacity: selected ? 0.9 : 0.6,
        weight: selected ? 3 : 1.5,
        radius: selected ? 9 : 6,
    };
};

/**
 * Map panel of the candidate review page (OSDEV-3755): the current page's
 * centroids as dots styled by validation state, the drawn area as a
 * rectangle, and a draw mode in which a click-and-drag sets the bbox
 * filter. No candidate tile or polygon layer: the list is the data.
 */
const CandidateListMap = ({
    classes,
    rows,
    selectedOsId,
    bbox,
    onSelect,
    onBboxChange,
}) => {
    const mapRef = useRef(null);
    const [drawing, setDrawing] = useState(false);
    const [dragBounds, setDragBounds] = useState(null);
    const dragStartRef = useRef(null);
    const dragLatestRef = useRef(null);

    const getMap = () => mapRef.current && mapRef.current.leafletElement;

    const areaBounds = useMemo(() => bboxToBounds(bbox), [bbox]);

    // The dots' positions as one string, so the fit below is keyed by
    // where the dots are rather than by the rows array: a vote replaces
    // the array (the row's state and tally change in place) and must not
    // move the map.
    const pointsKey = rows
        .filter(row => row.coordinates)
        .map(row => `${row.coordinates.lat},${row.coordinates.lng}`)
        .join(';');
    const points = useMemo(
        () =>
            pointsKey
                ? pointsKey.split(';').map(pair => pair.split(',').map(Number))
                : [],
        [pointsKey],
    );

    // Fit the view to what is on screen: the drawn area when there is one,
    // otherwise the page's dots (when any row has a position).
    useEffect(() => {
        const map = getMap();
        if (!map) return;
        if (areaBounds) {
            map.fitBounds(areaBounds, { padding: [16, 16] });
            return;
        }
        if (points.length) {
            map.fitBounds(points, { padding: [24, 24], maxZoom: 13 });
        }
    }, [points, areaBounds]);

    const finishDrag = useCallback(
        (start, end) => {
            const map = getMap();
            dragStartRef.current = null;
            setDragBounds(null);
            setDrawing(false);
            if (!map || !start || !end) return;
            const startPoint = map.latLngToContainerPoint(start);
            const endPoint = map.latLngToContainerPoint(end);
            if (
                Math.abs(startPoint.x - endPoint.x) < MIN_DRAG_PX ||
                Math.abs(startPoint.y - endPoint.y) < MIN_DRAG_PX
            ) {
                return;
            }
            onBboxChange(formatBbox(L.latLngBounds(start, end)));
        },
        [onBboxChange],
    );

    // Draw mode: suspend panning and turn a drag into a rectangle.
    useEffect(() => {
        const map = getMap();
        if (!map || !drawing) return undefined;
        map.dragging.disable();
        const onDown = event => {
            // Panning is off, so nothing else stops the browser from
            // starting a text selection across the page on this drag.
            if (event.originalEvent) {
                L.DomEvent.preventDefault(event.originalEvent);
            }
            dragStartRef.current = event.latlng;
            dragLatestRef.current = event.latlng;
            setDragBounds([event.latlng, event.latlng]);
        };
        const onMove = event => {
            if (dragStartRef.current) {
                dragLatestRef.current = event.latlng;
                setDragBounds([dragStartRef.current, event.latlng]);
            }
        };
        const onUp = event => finishDrag(dragStartRef.current, event.latlng);
        // The button can be released outside the map container, where the
        // map never sees the mouseup; the drag then ends at the last point
        // the map did see.
        const onDocumentUp = () => {
            if (dragStartRef.current) {
                finishDrag(dragStartRef.current, dragLatestRef.current);
            }
        };
        map.on('mousedown', onDown);
        map.on('mousemove', onMove);
        map.on('mouseup', onUp);
        document.addEventListener('mouseup', onDocumentUp);
        return () => {
            map.off('mousedown', onDown);
            map.off('mousemove', onMove);
            map.off('mouseup', onUp);
            document.removeEventListener('mouseup', onDocumentUp);
            dragStartRef.current = null;
            dragLatestRef.current = null;
            map.dragging.enable();
        };
    }, [drawing, finishDrag]);

    return (
        <div
            className={`${classes.root} ${drawing ? classes.drawing : ''}`}
            data-testid="candidate-list-map"
        >
            <ReactLeafletMap
                ref={mapRef}
                center={[initialCenter.lat, initialCenter.lng]}
                zoom={initialZoom}
                minZoom={2}
                maxZoom={18}
                scrollWheelZoom={false}
            >
                <TileLayer
                    url={SATELLITE_TILE_URL}
                    attribution={SATELLITE_TILE_ATTRIBUTION}
                    minZoom={2}
                    maxZoom={19}
                />
                {rows
                    .filter(row => row.coordinates)
                    .map(row => (
                        <CircleMarker
                            key={row.osId}
                            center={[row.coordinates.lat, row.coordinates.lng]}
                            {...markerStyle(
                                row.validation.state,
                                row.osId === selectedOsId,
                            )}
                            onClick={() => {
                                if (!drawing) onSelect(row.osId);
                            }}
                        />
                    ))}
                {areaBounds && (
                    <Rectangle bounds={areaBounds} {...AREA_STYLE} />
                )}
                {dragBounds && (
                    <Rectangle bounds={dragBounds} {...AREA_STYLE} />
                )}
                <Control position="topright">
                    <div className={classes.controls}>
                        <Button
                            size="small"
                            variant="outlined"
                            className={classes.controlButton}
                            onClick={() => setDrawing(current => !current)}
                            data-testid="candidate-map-draw"
                        >
                            {drawing
                                ? CANDIDATE_LIST_COPY.mapDrawCancel
                                : CANDIDATE_LIST_COPY.mapDraw}
                        </Button>
                        {bbox && (
                            <Button
                                size="small"
                                variant="outlined"
                                className={classes.controlButton}
                                onClick={() => onBboxChange(null)}
                                data-testid="candidate-map-clear-area"
                            >
                                {CANDIDATE_LIST_COPY.filterAreaClear}
                            </Button>
                        )}
                    </div>
                </Control>
                <Control position="bottomleft">
                    <Typography component="span" className={classes.hint}>
                        {drawing
                            ? CANDIDATE_LIST_COPY.mapDrawHint
                            : CANDIDATE_LIST_COPY.mapLegend}
                    </Typography>
                </Control>
            </ReactLeafletMap>
        </div>
    );
};

CandidateListMap.propTypes = {
    classes: PropTypes.object.isRequired,
    rows: PropTypes.arrayOf(
        PropTypes.shape({
            osId: PropTypes.string.isRequired,
            coordinates: PropTypes.shape({
                lat: PropTypes.number,
                lng: PropTypes.number,
            }),
            validation: PropTypes.shape({ state: PropTypes.string }),
        }),
    ).isRequired,
    selectedOsId: PropTypes.string,
    bbox: PropTypes.string,
    onSelect: PropTypes.func.isRequired,
    onBboxChange: PropTypes.func.isRequired,
};

CandidateListMap.defaultProps = {
    selectedOsId: null,
    bbox: null,
};

export default withStyles(candidateListMapStyles)(CandidateListMap);
