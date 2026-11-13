import React from 'react';
import { arrayOf, shape, string } from 'prop-types';
import { connect } from 'react-redux';

import {
    embedDrawsDots,
    getEmbedColorLabel,
    getEmbedColorLegend,
    getEmbedSpotlight,
    getSpotlightRingColor,
    getSpotlightTileKey,
} from '../util/embeddedMap';

const styles = {
    legend: {
        background: 'white',
        border: '1px solid rgb(13, 17, 40)',
        padding: '8px 12px',
        fontSize: '14px',
        maxWidth: '220px',
    },
    title: {
        fontWeight: 700,
        marginBottom: '4px',
    },
    row: {
        display: 'flex',
        alignItems: 'center',
        padding: '1px 0',
    },
    swatch: {
        width: '12px',
        height: '12px',
        borderRadius: '50%',
        marginRight: '8px',
        flex: 'none',
        border: '1px solid rgb(13, 17, 40)',
    },
};

/*
The key to the marker colors on an embedded map whose contributor colors
markers by one of their fields. Renders nothing on any other map.
*/
function EmbedColorLegend({ label, legend, spotlightRingColor }) {
    if (!legend.length && !spotlightRingColor) return null;

    return (
        <div style={styles.legend} data-testid="embed-color-legend">
            {legend.length ? <div style={styles.title}>{label}</div> : null}
            {legend.map(({ value, color }) => (
                <div key={value} style={styles.row}>
                    <span style={{ ...styles.swatch, background: color }} />
                    {value}
                </div>
            ))}
            {spotlightRingColor ? (
                <div style={styles.row}>
                    <span
                        style={{
                            ...styles.swatch,
                            background: 'none',
                            border: `3px solid ${spotlightRingColor}`,
                        }}
                    />
                    Has Spotlight data
                </div>
            ) : null}
        </div>
    );
}

EmbedColorLegend.propTypes = {
    label: string,
    legend: arrayOf(shape({ value: string, color: string })),
    spotlightRingColor: string,
};

EmbedColorLegend.defaultProps = {
    label: '',
    legend: [],
    spotlightRingColor: '',
};

function mapStateToProps({ embeddedMap: { embed, config }, featureFlags }) {
    const embedConfig = embed ? config : null;
    // Only dots can be ringed, so the legend only mentions the ring when the
    // map draws its facilities as dots.
    const drawsDots = embedDrawsDots(embed, featureFlags);
    return {
        label: getEmbedColorLabel(embedConfig),
        legend: getEmbedColorLegend(embedConfig),
        spotlightRingColor:
            drawsDots &&
            getSpotlightTileKey(getEmbedSpotlight(!!embed, config))
                ? getSpotlightRingColor(config)
                : '',
    };
}

export default connect(mapStateToProps)(EmbedColorLegend);
