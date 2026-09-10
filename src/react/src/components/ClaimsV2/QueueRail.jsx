import React, { useState } from 'react';
import Typography from '@material-ui/core/Typography';

import { CLAIM_STAGES } from './stageUtils';
import {
    STAGE_ORDER,
    SORT_ORDERS,
    ALL_REGIONS,
    claimAgeDays,
} from './railUtils';
import styles from './styles';

/*
 * Stage-grouped queue rail (OSDEV-3356): search (`/` focuses), region
 * filter, oldest/newest sort toggle, collapsible stage sections, and
 * per-claim age/waiting badges. Selection and keyboard navigation are
 * owned by the dashboard; this component just renders and reports
 * clicks. Visual spec: the prototype's rail.
 */

const STAGE_HEADINGS = Object.freeze({
    [CLAIM_STAGES.NEW]: 'New — needs review',
    [CLAIM_STAGES.AWAITING]: 'Awaiting claimant',
    [CLAIM_STAGES.OVERDUE]: 'Reply overdue — decide',
});

const STAGE_ACCENTS = Object.freeze({
    [CLAIM_STAGES.NEW]: styles.stageAccentNew,
    [CLAIM_STAGES.AWAITING]: styles.stageAccentAwaiting,
    [CLAIM_STAGES.OVERDUE]: styles.stageAccentOverdue,
});

function RailCard({ claim, isSelected, onSelect, now }) {
    const { stageInfo } = claim;
    const showWaiting =
        stageInfo.stage !== CLAIM_STAGES.NEW &&
        stageInfo.waitingBusinessDays > 0;

    return (
        <button
            type="button"
            style={{
                ...styles.railCard,
                ...(isSelected ? styles.railCardSelected : {}),
            }}
            onClick={() => onSelect(claim.id)}
            aria-current={isSelected ? 'true' : undefined}
        >
            <div>{claim.facility_name}</div>
            <div style={styles.railCardMeta}>
                #{claim.id} · {claim.facility_country_name} ·{' '}
                {claimAgeDays(claim.created_at, now)}d old
                {showWaiting && (
                    <span style={styles.waitingBadge}>
                        {stageInfo.waitingBusinessDays}bd waiting
                    </span>
                )}
            </div>
        </button>
    );
}

export default function QueueRail({
    groups,
    visibleCount,
    selectedClaimID,
    onSelect,
    query,
    onQueryChange,
    region,
    onRegionChange,
    regions,
    sort,
    onToggleSort,
    searchInputRef,
    now,
}) {
    const [collapsed, setCollapsed] = useState({});

    const toggleSection = stage =>
        setCollapsed(prev => ({ ...prev, [stage]: !prev[stage] }));

    return (
        <nav style={styles.rail} aria-label="Pending claims queue">
            <input
                ref={searchInputRef}
                type="search"
                value={query}
                placeholder="Search claims ( / )"
                aria-label="Search claims"
                style={styles.railSearch}
                onChange={event => onQueryChange(event.target.value)}
            />
            <div style={styles.railControls}>
                <select
                    value={region}
                    aria-label="Filter by region"
                    style={styles.railSelect}
                    onChange={event => onRegionChange(event.target.value)}
                >
                    {regions.map(name => (
                        <option key={name} value={name}>
                            {name}
                        </option>
                    ))}
                </select>
                <button
                    type="button"
                    style={styles.railSortButton}
                    onClick={onToggleSort}
                >
                    {sort === SORT_ORDERS.OLDEST
                        ? 'Sorted: oldest first ⇅'
                        : 'Sorted: newest first ⇅'}
                </button>
            </div>
            <Typography variant="body1" gutterBottom>
                {visibleCount} pending claim(s)
                {region !== ALL_REGIONS || query ? ' (filtered)' : ''}
            </Typography>
            {STAGE_ORDER.map(stage => {
                const stageClaims = groups[stage] || [];
                const isCollapsed = !!collapsed[stage];
                return (
                    <section key={stage}>
                        <button
                            type="button"
                            style={{
                                ...styles.stageHead,
                                ...STAGE_ACCENTS[stage],
                            }}
                            onClick={() => toggleSection(stage)}
                            aria-expanded={!isCollapsed}
                        >
                            {STAGE_HEADINGS[stage]}
                            <span style={styles.stageCount}>
                                {stageClaims.length}
                                {isCollapsed ? ' ▸' : ' ▾'}
                            </span>
                        </button>
                        {!isCollapsed &&
                            stageClaims.map(claim => (
                                <RailCard
                                    key={claim.id}
                                    claim={claim}
                                    isSelected={claim.id === selectedClaimID}
                                    onSelect={onSelect}
                                    now={now}
                                />
                            ))}
                        {!isCollapsed && stageClaims.length === 0 && (
                            <div style={styles.stageEmpty}>None</div>
                        )}
                    </section>
                );
            })}
            <div style={styles.kbdHint}>
                ↓/↑ or J/K next / previous · / to search
            </div>
        </nav>
    );
}
