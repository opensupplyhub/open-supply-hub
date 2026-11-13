import React, { useEffect, useState } from 'react';
import { array, object, string } from 'prop-types';
import { connect } from 'react-redux';
import {
    CircleMarker,
    Marker,
    Polyline,
    Tooltip,
    withLeaflet,
} from 'react-leaflet';
import L from 'leaflet';

import {
    findEmbedSupplyChain,
    getEmbedSupplyChains,
} from '../util/embeddedMap';

const arrowIcon = (color, degrees) =>
    L.divIcon({
        className: '',
        iconSize: [14, 14],
        html: `<div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-bottom:13px solid ${color};transform:rotate(${degrees}deg)"></div>`,
    });

/*
A line with an arrow from each supplier to the location it supplies.
`positions` maps each location's OS ID to its [lat, lng]; a link to a
location without a position is not drawn.
*/
function ChainLinks({ links, positions, color, leaflet }) {
    const map = leaflet && leaflet.map;
    // Arrow angles are measured on screen, so they are redrawn after a zoom.
    const [, setZoomTick] = useState(0);

    useEffect(() => {
        if (!map) return undefined;
        const redraw = () => setZoomTick(tick => tick + 1);
        map.on('zoomend', redraw);
        return () => map.off('zoomend', redraw);
    }, [map]);

    if (!map) return null;

    return (
        <>
            {links.map(([supplier, customer]) => {
                const from = positions[supplier];
                const to = positions[customer];
                if (!from || !to) return null;
                const a = map.latLngToLayerPoint(from);
                const b = map.latLngToLayerPoint(to);
                const degrees =
                    (Math.atan2(b.x - a.x, -(b.y - a.y)) * 180) / Math.PI;
                const middle = map.layerPointToLatLng([
                    a.x + (b.x - a.x) * 0.55,
                    a.y + (b.y - a.y) * 0.55,
                ]);
                return (
                    <React.Fragment key={`${supplier}-${customer}`}>
                        <Polyline
                            positions={[from, to]}
                            color={color}
                            weight={3}
                            opacity={0.9}
                            interactive={false}
                        />
                        <Marker
                            position={middle}
                            icon={arrowIcon(color, degrees)}
                            interactive={false}
                        />
                    </React.Fragment>
                );
            })}
        </>
    );
}

ChainLinks.propTypes = {
    links: array.isRequired,
    positions: object.isRequired,
    color: string.isRequired,
    leaflet: object.isRequired,
};

export const SupplyChainLinks = withLeaflet(ChainLinks);

/*
Draws the supply chain a visitor is following on an embedded map: a line
with an arrow from each supplier to the location it supplies, and a marker
on each location. Fits the map to the chain when one is chosen.
*/
function EmbedSupplyChainLayer({ chain, leaflet }) {
    const map = leaflet && leaflet.map;

    const chainId = chain ? chain.id : null;
    useEffect(() => {
        if (map && chain && chain.nodes.length) {
            map.fitBounds(
                L.latLngBounds(chain.nodes.map(n => [n.lat, n.lng])).pad(0.3),
                { maxZoom: 8 },
            );
        }
        // Fit only when a different chain is chosen.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [chainId, map]);

    if (!chain || !map) return null;

    const position = {};
    chain.nodes.forEach(node => {
        position[node.os_id] = [node.lat, node.lng];
    });

    return (
        <>
            <SupplyChainLinks
                links={chain.links}
                positions={position}
                color={chain.color}
            />
            {chain.nodes.map(node => (
                <CircleMarker
                    key={node.os_id}
                    center={[node.lat, node.lng]}
                    radius={10}
                    color="#ffffff"
                    weight={2.5}
                    fillColor={chain.color}
                    fillOpacity={1}
                >
                    <Tooltip direction="top">
                        {node.stage ? `${node.stage}: ` : ''}
                        {node.name}
                    </Tooltip>
                </CircleMarker>
            ))}
        </>
    );
}

EmbedSupplyChainLayer.propTypes = {
    chain: object,
    leaflet: object.isRequired,
};

EmbedSupplyChainLayer.defaultProps = {
    chain: null,
};

function mapStateToProps({
    embeddedMap: { embed, config },
    filters: { embedSupplyChainId },
}) {
    return {
        chain: findEmbedSupplyChain(
            getEmbedSupplyChains(embed, config),
            embedSupplyChainId,
        ),
    };
}

export default connect(mapStateToProps)(withLeaflet(EmbedSupplyChainLayer));
