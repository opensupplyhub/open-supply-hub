import React, { useEffect, useState } from 'react';
import { arrayOf, bool, func, number, string } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';

import apiRequest from '../util/apiRequest';
import { makeEmbedSpotlightOptionsURL } from '../util/util';
import { toggleSpotlightGroup } from '../util/embeddedMap';

const styles = {
    section: {
        marginTop: '30px',
    },
    sectionHeader: {
        color: 'rgb(0, 0, 0)',
        fontSize: '24px',
        margin: '10px 0',
    },
    subHeader: {
        color: 'rgb(0, 0, 0)',
        fontSize: '18px',
        fontWeight: 700,
        margin: '20px 0 2px',
    },
    summary: {
        margin: '12px 0',
        padding: '10px 12px',
        background: 'white',
        border: '1px solid rgb(214, 216, 221)',
    },
    checkbox: {
        color: 'rgb(0, 0, 0)',
    },
    group: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    count: {
        fontSize: '13px',
        color: 'rgba(0, 0, 0, 0.6)',
        whiteSpace: 'nowrap',
    },
    hint: {
        fontSize: '13px',
        color: 'rgba(0, 0, 0, 0.6)',
    },
};

const locations = count => `${count} ${count === 1 ? 'location' : 'locations'}`;

/*
Lets a contributor choose whether their embedded map shows Spotlight data,
from OS Hub's data partners: which kinds, whether locations that have it are
ringed on the map, and whether visitors can filter by it.
*/
function EmbeddedMapSpotlightConfig({
    showSpotlight,
    setShowSpotlight,
    spotlightHighlight,
    setSpotlightHighlight,
    spotlightFilter,
    setSpotlightFilter,
    spotlightGroups,
    setSpotlightGroups,
    shownCount,
}) {
    const [options, setOptions] = useState(null);
    const [loadError, setLoadError] = useState(false);

    useEffect(() => {
        apiRequest
            .get(makeEmbedSpotlightOptionsURL())
            .then(({ data }) => setOptions(data))
            .catch(() => setLoadError(true));
    }, []);

    if (loadError) {
        return (
            <div style={styles.section}>
                <Typography style={styles.sectionHeader}>Spotlight</Typography>
                <Typography>
                    Spotlight data could not be loaded. Reload the page to try
                    again.
                </Typography>
            </div>
        );
    }

    const groups = options ? options.groups : [];
    const noneAvailable = !!options && !groups.length;

    // Turning Spotlight on for the first time shows every kind of data.
    const toggleShow = checked => {
        setShowSpotlight(checked);
        if (checked && !spotlightGroups.length) {
            setSpotlightGroups(groups.map(group => group.uuid));
        }
    };

    return (
        <div style={styles.section}>
            <Typography style={styles.sectionHeader}>Spotlight</Typography>
            {options && (
                <Typography style={styles.summary}>
                    <strong>{options.count}</strong> of your {options.total}{' '}
                    locations have Spotlight data. Your map currently shows it
                    for <strong>{shownCount}</strong>.
                </Typography>
            )}
            {noneAvailable && (
                <Typography style={styles.hint}>
                    There is no Spotlight data to show yet.
                </Typography>
            )}
            <div>
                <FormControlLabel
                    label="Show Spotlight data on my map"
                    control={
                        <Checkbox
                            checked={showSpotlight}
                            disabled={!options || noneAvailable}
                            onChange={e => toggleShow(e.target.checked)}
                            style={styles.checkbox}
                        />
                    }
                />
            </div>
            <div>
                <FormControlLabel
                    label="Ring locations that have Spotlight data"
                    control={
                        <Checkbox
                            checked={showSpotlight && spotlightHighlight}
                            disabled={!showSpotlight}
                            onChange={e =>
                                setSpotlightHighlight(e.target.checked)
                            }
                            style={styles.checkbox}
                        />
                    }
                />
            </div>
            <div>
                <FormControlLabel
                    label="Offer Spotlight as a filter"
                    control={
                        <Checkbox
                            checked={showSpotlight && spotlightFilter}
                            disabled={!showSpotlight}
                            onChange={e => setSpotlightFilter(e.target.checked)}
                            style={styles.checkbox}
                        />
                    }
                />
            </div>
            {groups.length ? (
                <>
                    <Typography style={styles.subHeader}>
                        Data to show
                    </Typography>
                    <Typography style={styles.hint}>
                        Each kind of partner data, and how many of your
                        locations have it.
                    </Typography>
                    {groups.map(group => (
                        <div key={group.uuid} style={styles.group}>
                            <FormControlLabel
                                label={group.name}
                                control={
                                    <Checkbox
                                        checked={
                                            showSpotlight &&
                                            spotlightGroups.includes(group.uuid)
                                        }
                                        disabled={!showSpotlight}
                                        onChange={e =>
                                            setSpotlightGroups(
                                                toggleSpotlightGroup(
                                                    spotlightGroups,
                                                    group.uuid,
                                                    e.target.checked,
                                                ),
                                            )
                                        }
                                        style={styles.checkbox}
                                    />
                                }
                            />
                            <span style={styles.count}>
                                {locations(group.count)}
                            </span>
                        </div>
                    ))}
                </>
            ) : null}
        </div>
    );
}

EmbeddedMapSpotlightConfig.defaultProps = {
    spotlightGroups: [],
    shownCount: 0,
};

EmbeddedMapSpotlightConfig.propTypes = {
    showSpotlight: bool.isRequired,
    setShowSpotlight: func.isRequired,
    spotlightHighlight: bool.isRequired,
    setSpotlightHighlight: func.isRequired,
    spotlightFilter: bool.isRequired,
    setSpotlightFilter: func.isRequired,
    spotlightGroups: arrayOf(string),
    setSpotlightGroups: func.isRequired,
    shownCount: number,
};

export default EmbeddedMapSpotlightConfig;
