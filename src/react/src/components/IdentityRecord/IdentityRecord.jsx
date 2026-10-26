import React, { useEffect, useState } from 'react';
import { withRouter } from 'react-router';
import { Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';

import apiRequest from '../../util/apiRequest';
import { makeGetIdentityRecordURL } from '../../util/util';
import {
    asText,
    failureMessage,
    formatAddress,
    getClaims,
    getOperator,
    getProcessCategories,
    getSubject,
} from './recordFields';
import identityRecordStyles from './styles';

/*
 * The page a registered OS ID resolves to (FR-13, scope doc 2.6).
 *
 * Two things govern the whole layout. The record is the issuer's view of
 * the facility, not Open Supply Hub's, so the issuer is named throughout
 * and nothing here is merged into our own facility fields. And the record
 * is fetched live on every view rather than stored (NFR-04), so a loading
 * state and an honest failure state are not edge cases, they are two of
 * the three normal outcomes.
 */
/*
 * The three outcomes of fetching the record, plus the state it starts in.
 * Named rather than written as bare strings at each comparison, so a typo
 * is a reference error here instead of a branch that silently never runs.
 */
export const STATUS = Object.freeze({
    LOADING: 'loading',
    READY: 'ready',
    UNAVAILABLE: 'unavailable',
    ERROR: 'error',
});

export const IdentityRecord = ({ classes, match }) => {
    const osID = match?.params?.osID;
    const [state, setState] = useState({ status: STATUS.LOADING });

    useEffect(() => {
        let active = true;

        // Nothing to fetch without an identifier. This sets the failure
        // state rather than only returning, because the initial state is
        // LOADING and leaving it there would spin indefinitely.
        if (!osID) {
            setState({ status: STATUS.ERROR });
            return undefined;
        }

        setState({ status: STATUS.LOADING });

        apiRequest
            .get(makeGetIdentityRecordURL(osID))
            .then(({ data }) => {
                if (!active) {
                    return;
                }
                setState(
                    data.available
                        ? { status: STATUS.READY, data }
                        : {
                              status: STATUS.UNAVAILABLE,
                              reason: data.reason,
                          },
                );
            })
            .catch(() => {
                if (active) {
                    setState({ status: STATUS.ERROR });
                }
            });

        return () => {
            active = false;
        };
    }, [osID]);

    // Omitted when there is no identifier: a link to /facilities/undefined
    // is worse than no link at all.
    const locationLink = osID ? (
        <Link to={`/facilities/${osID}`} className={classes.locationLink}>
            View the Open Supply Hub production location
        </Link>
    ) : null;

    if (state.status === STATUS.LOADING) {
        return (
            <div className={classes.root}>
                <div className={classes.centered}>
                    <CircularProgress />
                    <Typography className={classes.loadingText}>
                        Fetching the record from its issuer
                    </Typography>
                </div>
            </div>
        );
    }

    /*
     * The degraded state is a page rather than a redirect to the facility
     * profile. Redirecting is a smaller surface, but it would silently
     * hand the visitor something other than what they followed the
     * identifier for, and they would have no way to tell that a record
     * exists. AC#2 asks for the location to stay reachable, which it does,
     * from here.
     */
    if (state.status !== STATUS.READY) {
        const message =
            state.status === STATUS.ERROR
                ? 'The record could not be loaded.'
                : failureMessage(state.reason);

        return (
            <div className={classes.root}>
                <Paper className={classes.unavailable}>
                    <Typography variant="title" className={classes.heading}>
                        This record is not available right now
                    </Typography>
                    <Typography className={classes.unavailableText}>
                        {message}
                    </Typography>
                    {locationLink && (
                        <Typography className={classes.unavailableText}>
                            {locationLink}
                        </Typography>
                    )}
                </Paper>
            </div>
        );
    }

    const { data } = state;
    const { credential } = data;
    const subject = getSubject(credential);
    const address = formatAddress(subject.address);
    // Every value below comes from the issuer unmapped, so each one is
    // coerced to text before it reaches JSX. React throws on an object
    // child, and the boundary that would catch it wraps the whole app.
    const country =
        asText(subject.countryOfOperation?.countryName) ||
        asText(subject.countryOfOperation?.countryCode);
    const name = asText(subject.name);
    const registeredId = asText(subject.registeredId);
    const categories = getProcessCategories(credential);
    const claims = getClaims(credential);
    const operator = getOperator(credential);

    return (
        <div className={classes.root}>
            <Typography className={classes.attribution}>
                This record was issued by {data.issuer}. It is shown as the
                issuer published it and is not part of Open Supply Hub&rsquo;s
                own record of this location.
            </Typography>

            <Paper className={classes.card}>
                <Typography variant="headline" className={classes.name}>
                    {name || 'Digital Facility Record'}
                </Typography>

                <dl className={classes.fields}>
                    {address && (
                        <>
                            <dt className={classes.term}>Address</dt>
                            <dd className={classes.detail}>{address}</dd>
                        </>
                    )}
                    {country && (
                        <>
                            <dt className={classes.term}>
                                Country of operation
                            </dt>
                            <dd className={classes.detail}>{country}</dd>
                        </>
                    )}
                    {registeredId && (
                        <>
                            <dt className={classes.term}>
                                Issuer&rsquo;s identifier
                            </dt>
                            <dd className={classes.detail}>{registeredId}</dd>
                        </>
                    )}
                    {operator && (
                        <>
                            <dt className={classes.term}>Operated by</dt>
                            <dd className={classes.detail}>{operator}</dd>
                        </>
                    )}
                    {categories.length > 0 && (
                        <>
                            <dt className={classes.term}>Process</dt>
                            <dd className={classes.detail}>
                                {categories.join(', ')}
                            </dd>
                        </>
                    )}
                    <dt className={classes.term}>Open Supply Hub ID</dt>
                    <dd className={classes.detail}>{data.os_id}</dd>
                </dl>
            </Paper>

            {claims.length > 0 && (
                <Paper className={classes.card}>
                    <Typography variant="title" className={classes.heading}>
                        Claims on this record
                    </Typography>
                    <Typography className={classes.caveat}>
                        These are statements made on the record by its issuer.
                        Each one carries its own status below.
                    </Typography>
                    <ul className={classes.claims}>
                        {claims.map(claim => (
                            <li key={claim.key} className={classes.claim}>
                                <span className={classes.claimName}>
                                    {claim.name}
                                </span>
                                {claim.scores.length > 0 && (
                                    <span className={classes.claimScore}>
                                        {claim.scores.join(', ')}
                                    </span>
                                )}
                                {claim.claimDate && (
                                    <span className={classes.claimDate}>
                                        {claim.claimDate}
                                    </span>
                                )}
                            </li>
                        ))}
                    </ul>
                </Paper>
            )}

            <Paper className={classes.card}>
                <Typography variant="title" className={classes.heading}>
                    Where this came from
                </Typography>
                <dl className={classes.fields}>
                    <dt className={classes.term}>Issuer</dt>
                    <dd className={classes.detail}>{data.issuer}</dd>
                    <dt className={classes.term}>Record type</dt>
                    <dd className={classes.detail}>{data.record_type}</dd>
                    <dt className={classes.term}>Resolver</dt>
                    <dd className={classes.detail}>
                        <a
                            href={data.resolver_uri}
                            className={classes.externalLink}
                            rel="noopener noreferrer"
                            target="_blank"
                        >
                            {data.resolver_uri}
                        </a>
                    </dd>
                    {data.document_uri && (
                        <>
                            <dt className={classes.term}>Signed credential</dt>
                            <dd className={classes.detail}>
                                <a
                                    href={data.document_uri}
                                    className={classes.externalLink}
                                    rel="noopener noreferrer"
                                    target="_blank"
                                >
                                    View the signed credential
                                </a>
                            </dd>
                        </>
                    )}
                </dl>
                {/*
                 * Said plainly because the distinction matters. We decode
                 * the credential, we do not check its signature, so this
                 * page must not imply the record has been verified.
                 */}
                <Typography className={classes.caveat}>
                    Open Supply Hub stores only a link to this record and
                    fetches it each time this page is opened. The signature on
                    the credential is not checked here; follow the link above to
                    verify it with the issuer.
                </Typography>
            </Paper>

            <Typography className={classes.footerLink}>
                {locationLink}
            </Typography>
        </div>
    );
};

export default withRouter(withStyles(identityRecordStyles)(IdentityRecord));
