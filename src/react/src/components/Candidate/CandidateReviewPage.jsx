import React, { useCallback, useEffect, useMemo, useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import ChevronLeft from '@material-ui/icons/ChevronLeft';
import ChevronRight from '@material-ui/icons/ChevronRight';

import CandidateBadge from './CandidateBadge';
import CandidateListFilters from './CandidateListFilters';
import CandidateListMap from './CandidateListMap';
import CandidateListTable from './CandidateListTable';
import CandidateLoginDialog from './CandidateLoginDialog';
import CandidateValidationPanel, {
    PANEL_VARIANTS,
} from './CandidateValidationPanel';
import { LIST_STATUS, useCandidateList } from './listHooks';
import { CANDIDATE_LIST_COPY } from '../../util/candidateCopy';
import {
    CANDIDATE_LIST_PAGE_SIZE,
    candidateListQueryFromSearch,
    candidateListQueryToSearch,
} from '../../util/candidates';
import { authLoginFormRoute } from '../../util/constants';
import { candidateReviewPageStyles } from './styles';

const ROBOTS_META_ID = 'candidate-review-robots';

/**
 * The SPA has no server-rendered head, so the noindex for this route is
 * added to the document head while the page is mounted (the API answers
 * X-Robots-Tag: noindex for the data itself).
 */
const useNoIndex = () => {
    useEffect(() => {
        if (typeof document === 'undefined') return undefined;
        const meta = document.createElement('meta');
        meta.setAttribute('name', 'robots');
        meta.setAttribute('content', 'noindex');
        meta.id = ROBOTS_META_ID;
        document.head.appendChild(meta);
        return () => {
            if (meta.parentNode) meta.parentNode.removeChild(meta);
        };
    }, []);
};

/**
 * /candidates (OSDEV-3755): every satellite-detected candidate, filtered,
 * sorted and paged from the OSDEV-3754 list endpoint, with the existing
 * validation panel inline so a reviewer can vote through a page. The
 * query lives in the URL search string (same names as the API), so a
 * sorted, filtered view can be shared.
 *
 * Flag gating is the route's job (Routes.jsx wraps this in FeatureFlag);
 * login gating is here: anonymous visitors see the login prompt and no
 * list request is sent.
 */
export const CandidateReviewPage = ({
    classes,
    history,
    location,
    user,
    sessionFetching,
}) => {
    useNoIndex();
    const query = useMemo(() => candidateListQueryFromSearch(location.search), [
        location.search,
    ]);
    const sessionPending =
        !!sessionFetching || !user || typeof user.isAnon !== 'boolean';
    const isAnon = sessionPending ? null : user.isAnon;
    const enabled = isAnon === false;

    const {
        rows,
        count,
        status,
        refetch,
        updateRowValidation,
    } = useCandidateList(query, { enabled });

    const [selectedOsId, setSelectedOsId] = useState(null);
    // The seed handed to the panel is fixed when a row is opened: the row
    // itself is updated in place after each vote, and re-seeding the panel
    // from that would refetch the detail and reset its status line.
    const [panelSeed, setPanelSeed] = useState(null);
    const [loginPromptOpen, setLoginPromptOpen] = useState(true);

    const setQuery = useCallback(
        (changes, { resetPage = true } = {}) => {
            const next = {
                ...query,
                ...changes,
                page: resetPage ? 1 : changes.page || query.page,
            };
            history.replace({
                pathname: location.pathname,
                search: candidateListQueryToSearch(next),
            });
        },
        [history, location.pathname, query],
    );

    const selectRow = useCallback(
        osId => {
            const row = rows.find(item => item.osId === osId) || null;
            setSelectedOsId(row ? row.osId : null);
            setPanelSeed(row);
        },
        [rows],
    );

    const closePanel = useCallback(() => {
        setSelectedOsId(null);
        setPanelSeed(null);
    }, []);

    // A new page or filter set drops the selection: its row is no longer
    // on screen.
    useEffect(() => {
        closePanel();
    }, [location.search, closePanel]);

    const selectedIndex = rows.findIndex(row => row.osId === selectedOsId);
    const stepTo = index => {
        if (index >= 0 && index < rows.length) selectRow(rows[index].osId);
    };

    const handleValidationChange = useCallback(
        validation => {
            if (selectedOsId) updateRowValidation(selectedOsId, validation);
        },
        [selectedOsId, updateRowValidation],
    );

    const totalPages = Math.max(1, Math.ceil(count / CANDIDATE_LIST_PAGE_SIZE));

    const renderStatus = () => {
        if (status === LIST_STATUS.PAGE_PAST_END) {
            return (
                <Paper elevation={0} className={classes.status}>
                    <Typography className={classes.statusText}>
                        {CANDIDATE_LIST_COPY.pagePastEnd}
                    </Typography>
                    <Button
                        variant="outlined"
                        onClick={() => setQuery({ page: 1 })}
                        data-testid="candidate-list-first-page"
                    >
                        {CANDIDATE_LIST_COPY.backToFirstPage}
                    </Button>
                </Paper>
            );
        }
        if (status === LIST_STATUS.ERROR) {
            return (
                <Paper elevation={0} className={classes.status}>
                    <Typography className={classes.statusText}>
                        {CANDIDATE_LIST_COPY.loadError}
                    </Typography>
                    <Button variant="outlined" onClick={refetch}>
                        {CANDIDATE_LIST_COPY.retry}
                    </Button>
                </Paper>
            );
        }
        if (status === LIST_STATUS.READY && rows.length === 0) {
            return (
                <Paper elevation={0} className={classes.status}>
                    <Typography
                        className={classes.statusText}
                        data-testid="candidate-list-empty"
                    >
                        {CANDIDATE_LIST_COPY.empty}
                    </Typography>
                </Paper>
            );
        }
        return null;
    };

    const header = (
        <header className={classes.header}>
            <div>
                <CandidateBadge />
            </div>
            <h1 className={classes.title}>{CANDIDATE_LIST_COPY.title}</h1>
            <Typography component="p" className={classes.intro}>
                {CANDIDATE_LIST_COPY.intro}
            </Typography>
        </header>
    );

    if (sessionPending) {
        return (
            <div className={classes.root} data-testid="candidate-review-page">
                {header}
                <div className={classes.status}>
                    <CircularProgress />
                </div>
            </div>
        );
    }

    if (isAnon) {
        return (
            <div className={classes.root} data-testid="candidate-review-page">
                {header}
                <Paper elevation={0} className={classes.loginNote}>
                    <Typography data-testid="candidate-review-login-note">
                        {CANDIDATE_LIST_COPY.loginNote}
                    </Typography>
                    <Button
                        variant="contained"
                        color="primary"
                        href={authLoginFormRoute}
                    >
                        Log In
                    </Button>
                </Paper>
                <CandidateLoginDialog
                    open={loginPromptOpen}
                    onClose={() => setLoginPromptOpen(false)}
                />
            </div>
        );
    }

    const statusBlock = renderStatus();

    return (
        <div className={classes.root} data-testid="candidate-review-page">
            {header}
            <div className={classes.layout}>
                <div className={classes.rail}>
                    <CandidateListFilters query={query} onChange={setQuery} />
                </div>
                <div className={classes.main}>
                    <div className={classes.topRow}>
                        <div className={classes.mapColumn}>
                            <CandidateListMap
                                rows={rows}
                                selectedOsId={selectedOsId}
                                bbox={query.bbox}
                                onSelect={selectRow}
                                onBboxChange={bbox => setQuery({ bbox })}
                            />
                        </div>
                        {panelSeed && (
                            <div
                                className={classes.panelColumn}
                                data-testid="candidate-review-panel"
                            >
                                <div className={classes.panelNav}>
                                    <Button
                                        size="small"
                                        variant="outlined"
                                        disabled={selectedIndex <= 0}
                                        onClick={() =>
                                            stepTo(selectedIndex - 1)
                                        }
                                        data-testid="candidate-panel-previous"
                                    >
                                        <ChevronLeft fontSize="small" />
                                        {CANDIDATE_LIST_COPY.panelPrevious}
                                    </Button>
                                    <Button
                                        size="small"
                                        variant="outlined"
                                        disabled={
                                            selectedIndex < 0 ||
                                            selectedIndex >= rows.length - 1
                                        }
                                        onClick={() =>
                                            stepTo(selectedIndex + 1)
                                        }
                                        data-testid="candidate-panel-next"
                                    >
                                        {CANDIDATE_LIST_COPY.panelNext}
                                        <ChevronRight fontSize="small" />
                                    </Button>
                                    <Typography
                                        component="span"
                                        className={classes.panelPosition}
                                        data-testid="candidate-panel-position"
                                    >
                                        {CANDIDATE_LIST_COPY.panelPosition(
                                            selectedIndex + 1,
                                            rows.length,
                                        )}
                                    </Typography>
                                </div>
                                <div className={classes.panelPaper}>
                                    <CandidateValidationPanel
                                        candidate={panelSeed}
                                        variant={PANEL_VARIANTS.INLINE}
                                        onClose={closePanel}
                                        onValidationChange={
                                            handleValidationChange
                                        }
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                    <div className={classes.summaryRow}>
                        <Typography
                            component="span"
                            className={classes.summary}
                            data-testid="candidate-list-summary"
                        >
                            {status === LIST_STATUS.LOADING && '…'}
                            {status === LIST_STATUS.READY &&
                                CANDIDATE_LIST_COPY.countSummary(
                                    count,
                                    query.page,
                                    totalPages,
                                )}
                        </Typography>
                    </div>
                    {statusBlock}
                    {(rows.length > 0 || status === LIST_STATUS.LOADING) && (
                        <CandidateListTable
                            rows={rows}
                            count={count}
                            page={query.page}
                            sort={query.sort}
                            loading={status === LIST_STATUS.LOADING}
                            selectedOsId={selectedOsId}
                            onSelect={selectRow}
                            onSortChange={sort => setQuery({ sort })}
                            onPageChange={page =>
                                setQuery({ page }, { resetPage: false })
                            }
                        />
                    )}
                </div>
            </div>
        </div>
    );
};

CandidateReviewPage.propTypes = {
    classes: PropTypes.object.isRequired,
    history: PropTypes.shape({ replace: PropTypes.func.isRequired }).isRequired,
    location: PropTypes.shape({
        pathname: PropTypes.string.isRequired,
        search: PropTypes.string,
    }).isRequired,
    user: PropTypes.shape({ isAnon: PropTypes.bool }),
    sessionFetching: PropTypes.bool,
};

CandidateReviewPage.defaultProps = {
    user: null,
    sessionFetching: false,
};

const mapStateToProps = ({ auth }) => ({
    user: auth && auth.user ? auth.user.user : null,
    sessionFetching: !!(auth && auth.session && auth.session.fetching),
});

export default withRouter(
    connect(mapStateToProps)(
        withStyles(candidateReviewPageStyles)(CandidateReviewPage),
    ),
);
