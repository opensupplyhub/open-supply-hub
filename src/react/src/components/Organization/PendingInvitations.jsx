import React from 'react';
import Button from '@material-ui/core/Button';

import { useOrganizationAction, organizationApi } from './hooks';
import { roleLabel } from './utils';
import { formatDate } from '../../util/util';
import { DATE_FORMATS } from '../../util/constants';
import styles from './styles';

/*
 * The invitations waiting for the signed-in user's answer. Accepting
 * creates the membership; the organization then sees the lists,
 * contributions and claims this account has submitted, so the card
 * says so before the user decides.
 */
const PendingInvitations = ({ invitations, onAnswered }) => {
    const { run, acting, actionError } = useOrganizationAction();

    if (!invitations.length) return null;

    const answer = request =>
        run(request)
            .then(onAnswered)
            .catch(() => {});

    return (
        <div style={styles.section} data-testid="pending-invitations">
            <h3 style={styles.sectionTitle}>Invitations</h3>
            {invitations.map(invitation => (
                <div key={invitation.uuid} style={styles.invitationCard}>
                    <div>
                        <strong>{invitation.invited_by_email}</strong> invited
                        you to join{' '}
                        <strong>{invitation.organization_name}</strong> as{' '}
                        {roleLabel(invitation.role)}.
                    </div>
                    <p style={styles.meta}>
                        If you accept, the organization can see the lists,
                        contributions and claims you have submitted, including
                        earlier ones. Your account, contributor profile and
                        public attribution do not change. The invitation expires
                        on{' '}
                        {formatDate(invitation.expires_at, DATE_FORMATS.LONG)}.
                    </p>
                    <div style={styles.actionsRow}>
                        <Button
                            variant="contained"
                            color="primary"
                            disabled={acting}
                            onClick={() =>
                                answer(() =>
                                    organizationApi.acceptInvitation(
                                        invitation.uuid,
                                    ),
                                )
                            }
                        >
                            Accept
                        </Button>
                        <Button
                            variant="outlined"
                            disabled={acting}
                            onClick={() =>
                                answer(() =>
                                    organizationApi.declineInvitation(
                                        invitation.uuid,
                                    ),
                                )
                            }
                        >
                            Decline
                        </Button>
                    </div>
                </div>
            ))}
            {actionError && <p style={styles.error}>{actionError}</p>}
        </div>
    );
};

export default PendingInvitations;
