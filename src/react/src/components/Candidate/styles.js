import COLOURS from '../../util/COLOURS';
import { getTypographyStyles } from '../../util/typographyStyles';
import {
    CANDIDATE_BADGE_COLOURS,
    CANDIDATE_STATE_CHIP_COLOURS,
    CANDIDATE_STATES,
} from '../../util/candidateCopy';

// Interim visuals, flagged for Design review (OSDEV-3192).
const stateChip = state => ({
    backgroundColor: CANDIDATE_STATE_CHIP_COLOURS[state].background,
    color: CANDIDATE_STATE_CHIP_COLOURS[state].text,
});

export const candidateBadgeStyles = theme => {
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        badge: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: spacing * 0.5,
            padding: `${spacing * 0.25}px ${spacing}px`,
            borderRadius: 12,
            border: `1px solid ${CANDIDATE_BADGE_COLOURS.border}`,
            backgroundColor: CANDIDATE_BADGE_COLOURS.background,
            color: CANDIDATE_BADGE_COLOURS.text,
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
        }),
        badgeIcon: Object.freeze({
            fontSize: 14,
        }),
        stateChip: Object.freeze({
            display: 'inline-block',
            padding: `${spacing * 0.25}px ${spacing}px`,
            borderRadius: 12,
            fontSize: '0.75rem',
            fontWeight: 600,
            whiteSpace: 'nowrap',
        }),
        stateUnverified: stateChip(CANDIDATE_STATES.UNVERIFIED),
        stateDisputed: stateChip(CANDIDATE_STATES.DISPUTED),
        stateConfirmed: stateChip(CANDIDATE_STATES.CONFIRMED),
        stateRetirementPending: stateChip(CANDIDATE_STATES.RETIREMENT_PENDING),
    });
};

export const candidateHeadingStyles = theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing,
            padding: `0 ${spacing * 2.5}px ${spacing * 2}px 0`,
        }),
        badgeRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: spacing,
        }),
        provenance: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.95rem',
        }),
        provenanceItem: Object.freeze({
            display: 'inline',
            '& + &::before': {
                content: '" · "',
            },
        }),
        provenanceLabel: Object.freeze({
            fontWeight: 600,
            color: theme.palette.text.primary,
        }),
        note: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.9rem',
            fontStyle: 'italic',
        }),
    });
};

export const candidateValidationPanelStyles = theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        root: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: COLOURS.WHITE,
            overflow: 'hidden',
        }),
        overlay: Object.freeze({
            position: 'absolute',
            top: spacing,
            right: spacing,
            zIndex: 1000,
            width: 300,
            maxWidth: 'calc(100% - 16px)',
            maxHeight: 'calc(100% - 16px)',
            overflowY: 'auto',
            borderRadius: 6,
            boxShadow: '0 4px 16px rgba(0,0,0,0.18)',
        }),
        inline: Object.freeze({
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            width: '100%',
        }),
        header: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: spacing,
            padding: `${spacing * 1.5}px ${spacing * 2}px`,
            backgroundColor: COLOURS.AMBER_50,
            borderBottom: `1px solid ${COLOURS.AMBER_300}`,
        }),
        headerText: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 0.5,
            flex: 1,
            minWidth: 0,
        }),
        title: Object.freeze({
            fontSize: '1rem',
            fontWeight: 600,
            lineHeight: 1.3,
            color: theme.palette.text.primary,
        }),
        intro: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.85rem',
            lineHeight: 1.4,
        }),
        closeButton: Object.freeze({
            marginTop: -spacing * 0.5,
            marginRight: -spacing,
        }),
        section: Object.freeze({
            padding: `${spacing * 1.5}px ${spacing * 2}px`,
            borderBottom: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 0.75,
        }),
        sectionLast: Object.freeze({
            borderBottom: 'none',
        }),
        metaRow: Object.freeze({
            fontSize: '0.8rem',
            color: theme.palette.text.secondary,
        }),
        metaLabel: Object.freeze({
            fontWeight: 600,
            color: theme.palette.text.primary,
        }),
        stateRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: spacing,
        }),
        tally: Object.freeze({
            fontSize: '0.85rem',
            fontWeight: 500,
            color: theme.palette.text.primary,
        }),
        tallyDisputed: Object.freeze({
            color: COLOURS.PURPLE_TEXT,
            fontWeight: 600,
        }),
        stateDescription: Object.freeze({
            fontSize: '0.8rem',
            color: theme.palette.text.secondary,
        }),
        voteButtons: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 0.75,
        }),
        voteButton: Object.freeze({
            justifyContent: 'flex-start',
            textAlign: 'left',
            textTransform: 'none',
            fontSize: '0.875rem',
            fontWeight: 500,
            padding: `${spacing}px ${spacing * 1.5}px`,
            borderRadius: 4,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            backgroundColor: COLOURS.WHITE,
            color: theme.palette.text.primary,
            '&:hover': {
                backgroundColor: COLOURS.HOVER_GREY,
            },
        }),
        voteButtonSelected: Object.freeze({
            borderColor: COLOURS.NEAR_BLACK,
            backgroundColor: COLOURS.NEAR_BLACK,
            color: COLOURS.WHITE,
            '&:hover': {
                backgroundColor: COLOURS.DARK_SLATE_GREY,
            },
            '&$voteButtonDisabled': {
                backgroundColor: COLOURS.DARK_GREY,
                color: COLOURS.WHITE,
            },
        }),
        voteButtonDisabled: Object.freeze({}),
        voteButtonIcon: Object.freeze({
            fontSize: 18,
            marginRight: spacing,
        }),
        yourVoteTag: Object.freeze({
            marginLeft: 'auto',
            fontSize: '0.7rem',
            fontWeight: 600,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            opacity: 0.85,
        }),
        statusText: Object.freeze({
            fontSize: '0.8rem',
            color: theme.palette.text.secondary,
        }),
        statusClosed: Object.freeze({
            color: COLOURS.GREEN_TEXT,
            fontWeight: 600,
        }),
        statusRetired: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            fontWeight: 600,
        }),
        statusError: Object.freeze({
            color: COLOURS.MATERIAL_RED,
        }),
        matchesTitle: Object.freeze({
            fontSize: '0.8rem',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            color: theme.palette.text.secondary,
        }),
        matchesList: Object.freeze({
            listStyle: 'none',
            margin: 0,
            padding: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing,
        }),
        matchItem: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
        }),
        matchName: Object.freeze({
            fontSize: '0.875rem',
            fontWeight: 500,
            color: COLOURS.NAVY_BLUE,
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            },
        }),
        matchMeta: Object.freeze({
            fontSize: '0.75rem',
            color: theme.palette.text.secondary,
        }),
        knowLink: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: spacing * 0.5,
            fontSize: '0.875rem',
            fontWeight: 600,
            color: COLOURS.NAVY_BLUE,
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            },
        }),
        knowHint: Object.freeze({
            fontSize: '0.75rem',
            color: theme.palette.text.secondary,
        }),
        loading: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            padding: spacing,
        }),
    });
};
