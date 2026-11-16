import React from 'react';
import { func, object } from 'prop-types';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';

import {
    embedHeadingFont,
    getChainGroups,
    getSafeProductUrl,
    themeEmbedStyle,
} from '../util/embeddedMap';
import {
    makeFacilityDetailLink,
    getFilteredSearchForEmbed,
} from '../util/util';

const makeStyles = theme => {
    const accent =
        themeEmbedStyle(theme).accentColor || theme.palette.primary.main;
    return {
        root: {
            fontFamily: theme.typography.fontFamily,
            overflow: 'auto',
            height: '100%',
        },
        header: {
            padding: '16px 20px',
            borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
        },
        name: {
            fontFamily: embedHeadingFont(theme),
            fontSize: '26px',
            fontWeight: 700,
            margin: 0,
        },
        description: {
            margin: '6px 0 0',
            fontSize: '16px',
        },
        productLink: {
            display: 'inline-block',
            marginTop: '8px',
            fontWeight: 700,
            color: accent,
        },
        back: {
            marginTop: '10px',
            padding: 0,
            border: 0,
            background: 'none',
            fontFamily: 'inherit',
            fontSize: '14px',
            textDecoration: 'underline',
            cursor: 'pointer',
        },
        group: {
            padding: '8px 20px',
            background: 'rgba(0, 0, 0, 0.04)',
            fontSize: '12px',
            fontWeight: 700,
            letterSpacing: '0.06em',
            textTransform: 'uppercase',
        },
        node: {
            display: 'block',
            padding: '12px 20px',
            borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
            color: '#191919',
            textDecoration: 'none',
        },
        stage: {
            fontSize: '12px',
            fontWeight: 700,
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            color: 'rgba(0, 0, 0, 0.6)',
        },
        nodeName: {
            display: 'block',
            fontFamily: embedHeadingFont(theme),
            fontSize: '20px',
            fontWeight: 700,
        },
        osId: {
            fontWeight: 700,
            color: accent,
        },
        supplies: {
            marginTop: '2px',
            fontSize: '14px',
            color: 'rgba(0, 0, 0, 0.7)',
        },
    };
};

/*
The list an embedded map shows while a visitor follows a supply chain: the
chain's name, description and product link, then its locations from the
start of the chain to the end. Each location opens its facility details.
*/
function EmbedSupplyChainList({ chain, onClose, classes }) {
    const productUrl = getSafeProductUrl(chain.product_url);

    return (
        <div className={classes.root} data-testid="embed-supply-chain-list">
            <div className={classes.header}>
                <h2 className={classes.name}>{chain.name}</h2>
                {chain.description ? (
                    <p className={classes.description}>{chain.description}</p>
                ) : null}
                {productUrl ? (
                    <a
                        className={classes.productLink}
                        href={productUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        View this product
                    </a>
                ) : null}
                <div>
                    <button
                        type="button"
                        className={classes.back}
                        onClick={onClose}
                    >
                        Show all facilities
                    </button>
                </div>
            </div>
            {getChainGroups(chain).map(group => (
                <div key={group.label}>
                    <div className={classes.group}>{group.label}</div>
                    {group.nodes.map(node => (
                        <Link
                            key={node.os_id}
                            className={classes.node}
                            to={{
                                pathname: makeFacilityDetailLink(node.os_id),
                                search: getFilteredSearchForEmbed(
                                    window.location.search,
                                ),
                                state: { panMapToFacilityDetails: true },
                            }}
                        >
                            {node.stage ? (
                                <span className={classes.stage}>
                                    {node.stage}
                                </span>
                            ) : null}
                            <span className={classes.nodeName}>
                                {node.name}
                            </span>
                            <span className={classes.osId}>
                                OS ID: {node.os_id}
                            </span>
                            <div>
                                {node.address}
                                {node.country_name
                                    ? `, ${node.country_name}`
                                    : ''}
                            </div>
                            {node.supplies.length ? (
                                <div className={classes.supplies}>
                                    Supplies {node.supplies.join(', ')}
                                </div>
                            ) : null}
                        </Link>
                    ))}
                </div>
            ))}
        </div>
    );
}

EmbedSupplyChainList.propTypes = {
    chain: object.isRequired,
    onClose: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeStyles)(EmbedSupplyChainList);
