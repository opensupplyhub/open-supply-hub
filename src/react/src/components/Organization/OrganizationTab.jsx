import React from 'react';
import { Link } from 'react-router-dom';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';

import PendingInvitations from './PendingInvitations';
import OrganizationMembers from './OrganizationMembers';
import OrganizationInvitations from './OrganizationInvitations';
import OrganizationContributions from './OrganizationContributions';
import OnboardingChecklist from './OnboardingChecklist';
import DomainAccounts from './DomainAccounts';
import {
    useCurrentOrganization,
    useMyInvitations,
    useOrganizationMembers,
    useOrganizationInvitations,
    useOrganizationOnboarding,
    useOrganizationDomainAccounts,
} from './hooks';
import { ROLES, roleLabel, seatsLabel } from './utils';
import { organizationDashboardRoute } from '../../util/constants';
import styles from './styles';

/*
 * The body of the My Organization page (see OrganizationPage), which
 * is reached from the account menu in the navbar.
 *
 * An organization is a group of existing accounts that the Open Supply
 * Hub team sets up; nobody creates one here. The page shows the
 * invitations waiting for the signed-in user, and, for a member, the
 * organization: its people, its invitations (Admins only) and what its
 * members submitted. The paid dashboard is linked when OS Hub has
 * switched it on for the organization.
 */
const OrganizationTab = () => {
    const {
        organization,
        loaded,
        error,
        refetch: refetchOrganization,
    } = useCurrentOrganization();
    const {
        invitations: myInvitations,
        refetch: refetchMyInvitations,
    } = useMyInvitations();

    const organizationUUID = organization ? organization.uuid : null;
    const isAdmin = Boolean(organization && organization.role === ROLES.ADMIN);

    const {
        members,
        fetching: fetchingMembers,
        error: membersError,
        refetch: refetchMembers,
    } = useOrganizationMembers(organizationUUID);
    const {
        invitations,
        error: invitationsError,
        refetch: refetchInvitations,
    } = useOrganizationInvitations(organizationUUID, isAdmin);

    const { progress, refetch: refetchProgress } = useOrganizationOnboarding(
        organizationUUID,
    );
    const {
        domain,
        accounts: domainAccounts,
        refetch: refetchDomainAccounts,
    } = useOrganizationDomainAccounts(organizationUUID, isAdmin);

    const refetchAll = () => {
        refetchOrganization();
        refetchMyInvitations();
    };

    // Seat usage lives on the organization, so anything that changes
    // members or invitations refreshes it too.
    const refetchPeople = () => {
        refetchOrganization();
        refetchMembers();
        refetchInvitations();
        refetchProgress();
        refetchDomainAccounts();
    };

    if (error) return <p style={styles.error}>{error}</p>;
    if (!loaded) return <CircularProgress />;

    return (
        <div style={styles.root} data-testid="organization-tab">
            <PendingInvitations
                invitations={myInvitations}
                onAnswered={refetchAll}
            />
            {!organization && (
                <div style={styles.emptyState}>
                    You don&apos;t belong to an organization. Organizations are
                    set up by the Open Supply Hub team. Once yours exists, one
                    of its Admins can invite you using the email address of this
                    account, and the invitation will appear here.
                </div>
            )}
            {organization && (
                <>
                    <div style={styles.headerRow}>
                        <div>
                            <h2 style={styles.organizationName}>
                                {organization.name}
                            </h2>
                            <p style={styles.meta}>
                                <span style={styles.chip}>
                                    {roleLabel(organization.role)}
                                </span>{' '}
                                {seatsLabel(
                                    organization.seats_used,
                                    organization.seat_limit,
                                )}
                            </p>
                            {(organization.legal_name ||
                                organization.parent_entity_name) && (
                                <p
                                    style={styles.meta}
                                    data-testid="organization-entity-names"
                                >
                                    {[
                                        organization.legal_name &&
                                            `Legal name: ${organization.legal_name}`,
                                        organization.parent_entity_name &&
                                            `Part of: ${organization.parent_entity_name}`,
                                    ]
                                        .filter(Boolean)
                                        .join(' · ')}
                                </p>
                            )}
                        </div>
                        {organization.dashboard_enabled ? (
                            <Button
                                variant="contained"
                                color="primary"
                                component={Link}
                                to={organizationDashboardRoute}
                            >
                                Open dashboard
                            </Button>
                        ) : (
                            <p style={styles.meta}>
                                The organization dashboard is a paid add-on.
                                Contact Open Supply Hub to switch it on.
                            </p>
                        )}
                    </div>
                    <OnboardingChecklist
                        progress={progress}
                        isAdmin={isAdmin}
                    />
                    <OrganizationMembers
                        organization={organization}
                        members={members}
                        fetching={fetchingMembers}
                        error={membersError}
                        onChanged={refetchPeople}
                    />
                    {isAdmin && (
                        <OrganizationInvitations
                            organization={organization}
                            invitations={invitations}
                            error={invitationsError}
                            onChanged={refetchPeople}
                        />
                    )}
                    {isAdmin && (
                        <DomainAccounts
                            organization={organization}
                            domain={domain}
                            accounts={domainAccounts}
                            onInvited={refetchPeople}
                        />
                    )}
                    <OrganizationContributions organization={organization} />
                </>
            )}
        </div>
    );
};

export default OrganizationTab;
