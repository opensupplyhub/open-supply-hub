import React, { useEffect, useMemo, useRef } from 'react';
import { arrayOf, func, object, string } from 'prop-types';
import {
    CircleMarker,
    Map as ReactLeafletMap,
    Tooltip,
    ZoomControl,
} from 'react-leaflet';
import ReactLeafletGoogleLayer from 'react-leaflet-google-layer';
import L from 'leaflet';

import { SupplyChainLinks } from './EmbedSupplyChainLayer';
import { DEFAULT_COUNTRY_CODE, SILVER_MAP_STYLE } from '../util/constants';
import {
    GOOGLE_CLIENT_SIDE_API_KEY,
    initialCenter,
    initialZoom,
} from '../util/constants.facilitiesMap';

const styles = {
    map: {
        height: '340px',
        width: '100%',
        marginTop: '8px',
        border: '1px solid rgb(214, 216, 221)',
    },
};

const DOT_COLOR = '#5b6b8c';
const SELECTED_RING = '#0d1128';

// The contributor's facilities as dots. There can be thousands, so they are
// only drawn again when the list itself changes, not on every edit.
function Dots({ locations, onClick }) {
    return locations.map(location => (
        <CircleMarker
            key={location.os_id}
            center={[location.lat, location.lng]}
            radius={5}
            color="#ffffff"
            weight={1}
            fillColor={DOT_COLOR}
            fillOpacity={0.85}
            onClick={() => onClick(location)}
        >
            <Tooltip direction="top">
                {location.name}
                {location.country_name ? ` · ${location.country_name}` : ''}
            </Tooltip>
        </CircleMarker>
    ));
}

Dots.propTypes = {
    locations: arrayOf(object).isRequired,
    onClick: func.isRequired,
};

const FacilityDots = React.memo(Dots);

/*
The map in the supply chain builder: every one of the contributor's
facilities as a dot, with the chain being built drawn on top. Clicking a
facility reports it through `onLocationClick`.
*/
function EmbeddedMapSupplyChainMap({
    chain,
    locations,
    selectedId,
    onLocationClick,
}) {
    const mapRef = useRef(null);

    // The dots keep one click handler for their whole life; it always calls
    // the latest `onLocationClick`.
    const latestClick = useRef(onLocationClick);
    latestClick.current = onLocationClick;
    const handleClick = useMemo(
        () => location => latestClick.current(location),
        [],
    );

    const byId = useMemo(() => {
        const lookup = {};
        locations.forEach(location => {
            lookup[location.os_id] = location;
        });
        return lookup;
    }, [locations]);

    // Start on the chain when there is one, otherwise on all the facilities.
    useEffect(() => {
        const map = mapRef.current && mapRef.current.leafletElement;
        if (!map || !locations.length) return;
        const inChain = chain.nodes
            .map(node => byId[node.os_id])
            .filter(Boolean);
        const shown = inChain.length ? inChain : locations;
        map.fitBounds(
            L.latLngBounds(shown.map(({ lat, lng }) => [lat, lng])).pad(0.2),
            { maxZoom: 8 },
        );
        // Only when the facilities arrive, not on every edit of the chain.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [locations]);

    const positions = {};
    chain.nodes.forEach(node => {
        const location = byId[node.os_id];
        if (location) positions[node.os_id] = [location.lat, location.lng];
    });

    return (
        <ReactLeafletMap
            ref={mapRef}
            center={initialCenter}
            zoom={initialZoom}
            minZoom={1}
            renderer={L.canvas()}
            style={styles.map}
            zoomControl={false}
            worldCopyJump
        >
            <ReactLeafletGoogleLayer
                googleMapsLoaderConf={{
                    KEY: GOOGLE_CLIENT_SIDE_API_KEY,
                    REGION: DEFAULT_COUNTRY_CODE,
                    VERSION: '3.57',
                }}
                type="roadmap"
                styles={SILVER_MAP_STYLE}
                continuousWorld
                minZoom={1}
                zIndex={1}
            />
            <ZoomControl position="bottomright" />
            <FacilityDots locations={locations} onClick={handleClick} />
            <SupplyChainLinks
                links={chain.links}
                positions={positions}
                color={chain.color}
            />
            {chain.nodes
                .filter(node => positions[node.os_id])
                .map(node => {
                    const isSelected = node.os_id === selectedId;
                    return (
                        <CircleMarker
                            key={`${node.os_id}-${isSelected}`}
                            center={positions[node.os_id]}
                            radius={isSelected ? 12 : 9}
                            color={isSelected ? SELECTED_RING : '#ffffff'}
                            weight={isSelected ? 4 : 2.5}
                            fillColor={chain.color}
                            fillOpacity={1}
                            onClick={() => handleClick(byId[node.os_id])}
                        >
                            <Tooltip direction="top">
                                {node.stage ? `${node.stage}: ` : ''}
                                {node.name || node.os_id}
                            </Tooltip>
                        </CircleMarker>
                    );
                })}
        </ReactLeafletMap>
    );
}

EmbeddedMapSupplyChainMap.defaultProps = {
    selectedId: null,
};

EmbeddedMapSupplyChainMap.propTypes = {
    chain: object.isRequired,
    locations: arrayOf(object).isRequired,
    selectedId: string,
    onLocationClick: func.isRequired,
};

export default EmbeddedMapSupplyChainMap;
