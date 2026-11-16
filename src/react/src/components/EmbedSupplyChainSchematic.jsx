import React from 'react';
import { func, object, string } from 'prop-types';

import { getSchematicLayout } from '../util/embeddedMap';

const INK = 'rgb(13, 17, 40)';
const LINE = 'rgb(190, 194, 204)';
const MUTED = 'rgba(0, 0, 0, 0.6)';

const styles = {
    scroll: {
        overflowX: 'auto',
    },
    empty: {
        fontSize: '13px',
        color: MUTED,
    },
};

/*
A supply chain without the geography, read left to right: its locations in
columns from the start of the chain to the end, with an arrow from each
supplier to each location it supplies. With `onSelect`, a location can be
clicked (or chosen with the keyboard) to select it.
*/
function EmbedSupplyChainSchematic({ chain, selectedId, onSelect }) {
    if (!chain.nodes.length) {
        return (
            <div style={styles.empty}>
                The schematic appears once the chain has a location.
            </div>
        );
    }

    const { width, height, headers, boxes, edges, box } = getSchematicLayout(
        chain,
    );
    const markerId = `chain-arrow-${chain.id || 'new'}`;

    return (
        <div style={styles.scroll}>
            <svg
                viewBox={`0 0 ${width} ${height}`}
                style={{
                    display: 'block',
                    width: '100%',
                    maxWidth: `${width}px`,
                    minWidth: `${Math.min(width, 420)}px`,
                }}
                role="img"
                aria-label={`Schematic of ${chain.name || 'the supply chain'}`}
            >
                <defs>
                    <marker
                        id={markerId}
                        markerWidth="8"
                        markerHeight="8"
                        refX="1"
                        refY="4"
                        orient="auto"
                    >
                        <path d="M0 0 L8 4 L0 8 Z" fill={chain.color} />
                    </marker>
                </defs>
                {headers.map(header => (
                    <text
                        key={header.label}
                        x={header.x}
                        y="12"
                        fill={MUTED}
                        fontSize="10"
                        fontWeight="600"
                        letterSpacing="0.08em"
                    >
                        {header.label.toUpperCase()}
                    </text>
                ))}
                {edges.map(edge => (
                    <path
                        key={edge.key}
                        d={edge.d}
                        fill="none"
                        stroke={chain.color}
                        strokeWidth="2"
                        markerEnd={`url(#${markerId})`}
                    />
                ))}
                {boxes.map(item => {
                    const isSelected = item.osId === selectedId;
                    const interactive = onSelect
                        ? {
                              role: 'button',
                              tabIndex: 0,
                              'aria-pressed': isSelected,
                              'aria-label': item.fullName,
                              style: { cursor: 'pointer' },
                              onClick: () => onSelect(item.osId),
                              onKeyDown: event => {
                                  if (
                                      event.key === 'Enter' ||
                                      event.key === ' '
                                  ) {
                                      event.preventDefault();
                                      onSelect(item.osId);
                                  }
                              },
                          }
                        : {};
                    return (
                        <g key={item.osId} {...interactive}>
                            <title>{item.fullName}</title>
                            <rect
                                x={item.x}
                                y={item.y}
                                width={box.width}
                                height={box.height}
                                rx="4"
                                fill="white"
                                stroke={isSelected ? INK : LINE}
                                strokeWidth={isSelected ? 2 : 1}
                            />
                            <text
                                x={item.x + 8}
                                y={item.y + 16}
                                fontSize="11.5"
                                fontWeight="600"
                                fill={INK}
                            >
                                {item.name}
                            </text>
                            <text
                                x={item.x + 8}
                                y={item.y + 30}
                                fontSize="10.5"
                                fill={MUTED}
                            >
                                {item.sub}
                            </text>
                        </g>
                    );
                })}
            </svg>
        </div>
    );
}

EmbedSupplyChainSchematic.defaultProps = {
    selectedId: null,
    onSelect: null,
};

EmbedSupplyChainSchematic.propTypes = {
    chain: object.isRequired,
    selectedId: string,
    onSelect: func,
};

export default EmbedSupplyChainSchematic;
