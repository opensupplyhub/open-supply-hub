import React, { useState } from 'react';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import { useOrganizationAction, organizationApi } from './hooks';
import { ROLES, roleLabel } from './utils';
import { formatDate } from '../../util/util';
import { DATE_FORMATS } from '../../util/constants';
import styles from './styles';

/*
 * The organization's members. Everyone sees the list; an Admin can
 * change roles and remove members, and anyone can leave. Removing or
 * leaving asks for a second click, because it cannot be undone from
 * here: the person has to be invited again.
 */
const OrganizationMembers = ({
    organization,
    members,
    fetching,
    error,
    onChanged,
}) => {
    const { run, acting, actionError } = useOrganizationAction();
    const [confirmingUUID, setConfirmingUUID] = useState(null);
    const isAdmin = organization.role === ROLES.ADMIN;

    const act = request =>
        run(request)
            .then(() => {
                setConfirmingUUID(null);
                onChanged();
            })
            .catch(() => {});

    const renderRole = member => {
        if (!isAdmin || member.is_self) return roleLabel(member.role);

        return (
            <Select
                value={member.role}
                disabled={acting}
                onChange={event =>
                    act(() =>
                        organizationApi.changeRole(
                            organization.uuid,
                            member.uuid,
                            event.target.value,
                        ),
                    )
                }
                inputProps={{ 'aria-label': `Role of ${member.email}` }}
            >
                <MenuItem value={ROLES.ADMIN}>
                    {roleLabel(ROLES.ADMIN)}
                </MenuItem>
                <MenuItem value={ROLES.MEMBER}>
                    {roleLabel(ROLES.MEMBER)}
                </MenuItem>
            </Select>
        );
    };

    const renderActions = member => {
        if (!isAdmin && !member.is_self) return null;
        const label = member.is_self ? 'Leave' : 'Remove';

        if (confirmingUUID !== member.uuid) {
            return (
                <Button
                    size="small"
                    disabled={acting}
                    onClick={() => setConfirmingUUID(member.uuid)}
                >
                    {label}
                </Button>
            );
        }

        return (
            <>
                <Button
                    size="small"
                    color="secondary"
                    variant="contained"
                    disabled={acting}
                    onClick={() =>
                        act(() =>
                            organizationApi.removeMember(
                                organization.uuid,
                                member.uuid,
                            ),
                        )
                    }
                >
                    Confirm {label.toLowerCase()}
                </Button>{' '}
                <Button
                    size="small"
                    disabled={acting}
                    onClick={() => setConfirmingUUID(null)}
                >
                    Cancel
                </Button>
            </>
        );
    };

    return (
        <div style={styles.section} data-testid="organization-members">
            <h3 style={styles.sectionTitle}>Members</h3>
            <p style={styles.sectionHint}>
                Each member keeps their own account and contributor profile.
                Contributions already recorded for the organization stay with it
                when a member leaves.
            </p>
            {error && <p style={styles.error}>{error}</p>}
            {actionError && <p style={styles.error}>{actionError}</p>}
            {fetching && !members.length ? (
                <CircularProgress />
            ) : (
                <div style={styles.tableWrapper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Email</TableCell>
                                <TableCell>Contributor profile</TableCell>
                                <TableCell>Role</TableCell>
                                <TableCell>Joined</TableCell>
                                <TableCell />
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {members.map(member => (
                                <TableRow key={member.uuid}>
                                    <TableCell>
                                        {member.email}
                                        {member.is_self ? ' (you)' : ''}
                                    </TableCell>
                                    <TableCell>
                                        {member.contributor_name}
                                    </TableCell>
                                    <TableCell>{renderRole(member)}</TableCell>
                                    <TableCell>
                                        {formatDate(
                                            member.joined_at,
                                            DATE_FORMATS.LONG,
                                        )}
                                    </TableCell>
                                    <TableCell>
                                        {renderActions(member)}
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

export default OrganizationMembers;
