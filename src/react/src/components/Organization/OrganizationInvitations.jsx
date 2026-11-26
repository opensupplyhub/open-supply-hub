import React, { useState } from 'react';
import Button from '@material-ui/core/Button';
import MenuItem from '@material-ui/core/MenuItem';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';

import { useOrganizationAction, organizationApi } from './hooks';
import { ROLES, roleLabel } from './utils';
import { formatDate } from '../../util/util';
import { DATE_FORMATS } from '../../util/constants';
import styles from './styles';

/*
 * Admin only: invite an existing OS Hub account by its email, and
 * revoke invitations that are still waiting. When the email cannot be
 * invited the API says why (no confirmed account, already in an
 * organization, no free seat) and that reason is shown as it is.
 */
const OrganizationInvitations = ({
    organization,
    invitations,
    error,
    onChanged,
}) => {
    const {
        run,
        acting,
        actionError,
        clearActionError,
    } = useOrganizationAction();
    const [email, setEmail] = useState('');
    const [role, setRole] = useState(ROLES.MEMBER);
    const [sentTo, setSentTo] = useState(null);

    const invite = event => {
        event.preventDefault();
        setSentTo(null);
        run(() => organizationApi.invite(organization.uuid, email, role))
            .then(invitation => {
                setSentTo(invitation.email);
                setEmail('');
                onChanged();
            })
            .catch(() => {});
    };

    const revoke = invitationUUID =>
        run(() =>
            organizationApi.revokeInvitation(organization.uuid, invitationUUID),
        )
            .then(onChanged)
            .catch(() => {});

    return (
        <div style={styles.section} data-testid="organization-invitations">
            <h3 style={styles.sectionTitle}>Invite people</h3>
            <p style={styles.sectionHint}>
                Enter the email of someone who already has an OS Hub account. If
                they don&apos;t have one yet, ask them to register and confirm
                their email first.
            </p>
            <form style={styles.inviteForm} onSubmit={invite}>
                <TextField
                    id="organization-invite-email"
                    label="Email"
                    type="email"
                    required
                    value={email}
                    style={styles.inviteEmailField}
                    onChange={event => {
                        setEmail(event.target.value);
                        clearActionError();
                    }}
                />
                <TextField
                    id="organization-invite-role"
                    select
                    label="Role"
                    value={role}
                    onChange={event => setRole(event.target.value)}
                >
                    <MenuItem value={ROLES.MEMBER}>
                        {roleLabel(ROLES.MEMBER)}
                    </MenuItem>
                    <MenuItem value={ROLES.ADMIN}>
                        {roleLabel(ROLES.ADMIN)}
                    </MenuItem>
                </TextField>
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={acting || !email}
                >
                    Send invitation
                </Button>
            </form>
            {actionError && <p style={styles.error}>{actionError}</p>}
            {error && <p style={styles.error}>{error}</p>}
            {sentTo && <p style={styles.meta}>Invitation sent to {sentTo}.</p>}
            {invitations.length > 0 && (
                <div style={styles.tableWrapper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Invited</TableCell>
                                <TableCell>Role</TableCell>
                                <TableCell>Sent</TableCell>
                                <TableCell>Expires</TableCell>
                                <TableCell />
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {invitations.map(invitation => (
                                <TableRow key={invitation.uuid}>
                                    <TableCell>{invitation.email}</TableCell>
                                    <TableCell>
                                        {roleLabel(invitation.role)}
                                    </TableCell>
                                    <TableCell>
                                        {formatDate(
                                            invitation.created_at,
                                            DATE_FORMATS.LONG,
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        {formatDate(
                                            invitation.expires_at,
                                            DATE_FORMATS.LONG,
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        <Button
                                            size="small"
                                            disabled={acting}
                                            onClick={() =>
                                                revoke(invitation.uuid)
                                            }
                                        >
                                            Revoke
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            )}
        </div>
    );
};

export default OrganizationInvitations;
