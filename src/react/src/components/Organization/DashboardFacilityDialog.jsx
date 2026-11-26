import React from 'react';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';

import { useDashboardFacility } from './hooks';
import { claimedDataRows } from './utils';
import { formatDate, makeFacilityDetailLink } from '../../util/util';
import { DATE_FORMATS } from '../../util/constants';
import styles from './styles';

const DetailRow = ({ label, value }) => (
    <div style={styles.detailRow}>
        <span style={styles.detailLabel}>{label}</span>
        <span>{value}</span>
    </div>
);

/*
 * One submitted production location: who in the organization submitted
 * it and when, and the data its claimant added. Only what the public
 * profile shows is returned by the API, so nothing private appears.
 */
const DashboardFacilityDialog = ({ organizationUUID, osID, onClose }) => {
    const { facility, fetching, error } = useDashboardFacility(
        organizationUUID,
        osID,
    );
    const claimRows = facility ? claimedDataRows(facility.claim) : [];

    return (
        <Dialog open={Boolean(osID)} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                {facility ? facility.name : 'Production location'}
            </DialogTitle>
            <DialogContent>
                {fetching && <CircularProgress />}
                {error && <p style={styles.error}>{error}</p>}
                {facility && !fetching && (
                    <>
                        <DetailRow label="OS ID" value={facility.os_id} />
                        <DetailRow label="Address" value={facility.address} />
                        <DetailRow
                            label="Country"
                            value={facility.country_name}
                        />

                        <h4 style={styles.detailHeading}>
                            Submitted by your organization
                        </h4>
                        {facility.submissions.map(submission => (
                            <DetailRow
                                key={submission.submission_id}
                                label={formatDate(
                                    submission.submitted_at,
                                    DATE_FORMATS.LONG,
                                )}
                                value={`${
                                    submission.submitted_by
                                        ? submission.submitted_by
                                              .contributor_name
                                        : 'Unknown'
                                }${
                                    submission.list
                                        ? `, list "${submission.list.name}"`
                                        : ', single contribution'
                                }`}
                            />
                        ))}

                        <h4 style={styles.detailHeading}>Claimed data</h4>
                        {!facility.is_claimed && (
                            <p style={styles.meta}>
                                This production location has not been claimed.
                            </p>
                        )}
                        {facility.is_claimed && (
                            <>
                                <DetailRow
                                    label="Claimed on"
                                    value={
                                        facility.claimed_at
                                            ? formatDate(
                                                  facility.claimed_at,
                                                  DATE_FORMATS.LONG,
                                              )
                                            : ''
                                    }
                                />
                                {claimRows.map(row => (
                                    <DetailRow
                                        key={row.label}
                                        label={row.label}
                                        value={row.value}
                                    />
                                ))}
                            </>
                        )}
                    </>
                )}
            </DialogContent>
            <DialogActions>
                {facility && (
                    <Button
                        color="primary"
                        href={makeFacilityDetailLink(facility.os_id)}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Open public profile
                    </Button>
                )}
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
};

export default DashboardFacilityDialog;
