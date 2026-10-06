import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';
import { GeoJSON, withLeaflet } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import debounce from 'lodash/debounce';

import apiRequest from '../../util/apiRequest';
import {
    CANDIDATE_LAYER_DEBOUNCE_MS,
    CANDIDATE_LAYER_LIMIT,
    formatBbox,
    getCandidateStyle,
    makeCandidatesBboxURL,
    shouldFetchCandidates,
} from '../../util/candidates';
import { CANDIDATE_STATE_LABELS } from '../../util/candidateCopy';

const EMPTY = Object.freeze({ type: 'FeatureCollection', features: [] });

/**
 * Builds the bbox request for the map's current viewport, or null when the
 * map is zoomed out past CANDIDATE_LAYER_MIN_ZOOM.
 */
export const buildCandidatesRequestURL = map => {
    if (!map || !shouldFetchCandidates(map.getZoom())) return null;
    return makeCandidatesBboxURL(
        formatBbox(map.getBounds()),
        CANDIDATE_LAYER_LIMIT,
    );
};

/**
 * Satellite-detected candidate footprints for the current viewport
 * (OSDEV-3247). Fetches GET /api/v1/production-locations/candidates/?bbox=
 * on load and after each (debounced) moveend, cancelling any in-flight
 * request, and renders polygons/points styled by validation state:
 * unverified dashed, disputed dotted purple, confirmed solid green,
 * retirement_pending as disputed plus a label. Interim visuals, OSDEV-3192.
 */
const CandidatePolygonsLayer = ({
    leaflet,
    onCandidateClick,
    selectedOsId,
    refreshKey,
}) => {
    const map = leaflet ? leaflet.map : null;
    const [collection, setCollection] = useState(EMPTY);
    const [version, setVersion] = useState(0);
    const controllerRef = useRef(null);
    const clickRef = useRef(onCandidateClick);
    clickRef.current = onCandidateClick;

    useEffect(() => {
        if (!map) return undefined;

        const load = () => {
            if (controllerRef.current) {
                controllerRef.current.abort();
                controllerRef.current = null;
            }
            const url = buildCandidatesRequestURL(map);
            if (!url) {
                setCollection(EMPTY);
                return;
            }
            const controller = new AbortController();
            controllerRef.current = controller;
            apiRequest
                .get(url, { signal: controller.signal })
                .then(({ data }) => {
                    if (controller.signal.aborted) return;
                    controllerRef.current = null;
                    setCollection(
                        data && Array.isArray(data.features) ? data : EMPTY,
                    );
                    setVersion(current => current + 1);
                })
                .catch(err => {
                    if (axios.isCancel(err) || controller.signal.aborted) {
                        return;
                    }
                    controllerRef.current = null;
                    // eslint-disable-next-line no-console
                    console.error('Candidate layer fetch failed:', err);
                });
        };

        const debouncedLoad = debounce(load, CANDIDATE_LAYER_DEBOUNCE_MS);
        load();
        map.on('moveend', debouncedLoad);

        return () => {
            map.off('moveend', debouncedLoad);
            debouncedLoad.cancel();
            if (controllerRef.current) {
                controllerRef.current.abort();
                controllerRef.current = null;
            }
        };
    }, [map, refreshKey]);

    if (!collection.features.length) return null;

    const styleFor = feature =>
        getCandidateStyle(feature.properties.state, {
            selected:
                !!selectedOsId && feature.properties.os_id === selectedOsId,
        });

    const onEachFeature = (feature, layer) => {
        const base = styleFor(feature);
        const hover = getCandidateStyle(feature.properties.state, {
            hover: true,
            selected:
                !!selectedOsId && feature.properties.os_id === selectedOsId,
        });
        if (layer.setStyle) layer.setStyle(base);
        const label = CANDIDATE_STATE_LABELS[feature.properties.state];
        if (label && layer.bindTooltip) {
            layer.bindTooltip(label, { sticky: true, direction: 'top' });
        }
        layer.on('mouseover', () => layer.setStyle && layer.setStyle(hover));
        layer.on('mouseout', () => layer.setStyle && layer.setStyle(base));
        layer.on('click', event => {
            if (event && event.originalEvent && L.DomEvent) {
                L.DomEvent.stopPropagation(event);
            }
            if (clickRef.current) clickRef.current(feature.properties);
        });
    };

    const pointToLayer = (feature, latlng) =>
        L.circleMarker(latlng, { radius: 8, ...styleFor(feature) });

    return (
        <GeoJSON
            key={`candidates-${version}-${selectedOsId || ''}`}
            data={collection}
            style={styleFor}
            onEachFeature={onEachFeature}
            pointToLayer={pointToLayer}
        />
    );
};

CandidatePolygonsLayer.propTypes = {
    leaflet: PropTypes.shape({ map: PropTypes.object }),
    onCandidateClick: PropTypes.func,
    selectedOsId: PropTypes.string,
    refreshKey: PropTypes.number,
};

CandidatePolygonsLayer.defaultProps = {
    leaflet: null,
    onCandidateClick: null,
    selectedOsId: null,
    refreshKey: 0,
};

export { CandidatePolygonsLayer as UnwrappedCandidatePolygonsLayer };

export default withLeaflet(CandidatePolygonsLayer);
