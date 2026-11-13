import React from 'react';
import { node, object, oneOf, oneOfType, number, string } from 'prop-types';
import isNil from 'lodash/isNil';
import { withStyles } from '@material-ui/core/styles';

import {
    DISPLAY_AS_OPTIONS,
    DISPLAY_AS_TEXT,
    splitTagValues,
    themeEmbedStyle,
    truncateBlurb,
} from '../util/embeddedMap';

const makeStyles = theme => {
    const accent =
        themeEmbedStyle(theme).accentColor || theme.palette.primary.main;
    return {
        root: {
            fontFamily: theme.typography.fontFamily,
            fontSize: '16px',
            fontWeight: 500,
            marginTop: '4px',
        },
        label: {
            color: 'rgba(0, 0, 0, 0.6)',
        },
        tag: {
            display: 'inline-block',
            margin: '2px 4px 0 0',
            padding: '0 8px',
            border: `1px solid ${accent}`,
            borderRadius: '10px',
            color: accent,
            fontSize: '14px',
            fontWeight: 700,
        },
        blurb: {
            fontFamily: theme.typography.fontFamily,
            margin: '6px 0 0',
            padding: '4px 10px',
            borderLeft: `3px solid ${accent}`,
            background: 'rgba(0, 0, 0, 0.03)',
            fontStyle: 'italic',
            fontSize: '15px',
            fontWeight: 500,
        },
        blurbLabel: {
            display: 'block',
            fontStyle: 'normal',
            fontSize: '11px',
            fontWeight: 700,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
            color: 'rgba(0, 0, 0, 0.6)',
        },
    };
};

/*
One contributor field on a facility in an embedded map, shown the way the
contributor chose on the Embed settings screen: as plain text, as tags, or as
a blurb. Values are rendered as text, never as HTML.
*/
function EmbedFieldValue({ classes, label, value, displayAs }) {
    if (isNil(value) || String(value).trim() === '') {
        return null;
    }

    if (displayAs === 'blurb') {
        return (
            <div className={classes.blurb} data-testid="embed-field-blurb">
                <span className={classes.blurbLabel}>{label}</span>
                {truncateBlurb(value)}
            </div>
        );
    }

    if (displayAs === 'tags') {
        return (
            <div className={classes.root} data-testid="embed-field-tags">
                <span className={classes.label}>{label}: </span>
                {splitTagValues(value).map(tag => (
                    <span key={tag} className={classes.tag}>
                        {tag}
                    </span>
                ))}
            </div>
        );
    }

    return (
        <div className={classes.root} data-testid="embed-field-text">
            <span className={classes.label}>{label}: </span>
            {String(value)}
        </div>
    );
}

EmbedFieldValue.propTypes = {
    classes: object.isRequired,
    label: node.isRequired,
    value: oneOfType([string, number]),
    displayAs: oneOf(DISPLAY_AS_OPTIONS.map(option => option.value)),
};

EmbedFieldValue.defaultProps = {
    value: null,
    displayAs: DISPLAY_AS_TEXT,
};

export default withStyles(makeStyles)(EmbedFieldValue);
