import React, { useState } from 'react';
import Button from '@material-ui/core/Button';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import { useOrganizationAction, organizationApi } from './hooks';
import { ROLES } from './utils';
import styles from './styles';

/*
 * Admin only: existing OS Hub accounts that use the Admin's own email
 * domain and are not in an organization, each with a one-click
 * invitation as a Member. Nothing is rendered when there are none, or
 * when the Admin's address is on a public mail provider.
 */
const DomainAccounts = ({ organization, domain, accounts, onInvited }) => {
    const { run, acting, actionError } = useOrganizationAction();
    const [sentTo, setSentTo] = useState(null);

    if (!domain || accounts.length === 0) return null;

    const invite = email => {
        setSentTo(null);
        run(() =>
            organizationApi.invite(organization.uuid, email, ROLES.MEMBER),
        )
            .then(invitation => {
                setSentTo(invitation.email);
                onInvited();
            })
            .catch(() => {});
    };

    return (
        <div style={styles.section} data-testid="organization-domain-accounts">
            <h3 style={styles.sectionTitle}>Colleagues already on OS Hub</h3>
            <p style={styles.sectionHint}>
                These accounts use an @{domain} address and are not in an
                organization. Inviting one adds them as a Member once they
                accept.
            </p>
            {actionError && <p style={styles.error}>{actionError}</p>}
            {sentTo && <p style={styles.meta}>Invitation sent to {sentTo}.</p>}
            <div style={styles.tableWrapper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Email</TableCell>
                            <TableCell>Contributor profile</TableCell>
                            <TableCell />
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {accounts.map(account => (
                            <TableRow key={account.email}>
                                <TableCell>{account.email}</TableCell>
                                <TableCell>
                                    {account.contributor_name || ''}
                                </TableCell>
                                <TableCell>
                                    <Button
                                        size="small"
                                        disabled={acting}
                                        onClick={() => invite(account.email)}
                                    >
                                        Invite
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
};

export default DomainAccounts;
