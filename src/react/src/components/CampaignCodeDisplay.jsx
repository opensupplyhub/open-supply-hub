import React, { useState } from 'react';
import { string, bool } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { toast } from 'react-toastify';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import InfoIcon from '@material-ui/icons/Info';

import CopyLinkIcon from './CopyLinkIcon';
import COLOURS from '../util/COLOURS';

const styles = {
    container: {
        backgroundColor: '#F8F9FA',
        border: '1px solid #E5E8EB',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '24px',
    },
    header: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: '12px',
        gap: '8px',
    },
    title: {
        fontWeight: '900',
        fontSize: '14px',
        letterSpacing: '0.5px',
        lineHeight: '14px',
        textTransform: 'uppercase',
        color: '#191919',
        margin: 0,
    },
    validationBadge: {
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        fontSize: '12px',
        fontWeight: '600',
        color: COLOURS.GREEN,
    },
    codeContainer: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '16px',
    },
    codeDisplay: {
        backgroundColor: '#FFFFFF',
        border: '2px solid #E5E8EB',
        borderRadius: '6px',
        padding: '12px 16px',
        fontFamily: 'Monaco, Consolas, "Lucida Console", monospace',
        fontSize: '18px',
        fontWeight: '700',
        letterSpacing: '1px',
        color: '#1C1B1F',
        minWidth: '120px',
        textAlign: 'center',
    },
    copyButton: {
        backgroundColor: COLOURS.NAVY_BLUE,
        color: '#FFFFFF',
        borderRadius: '6px',
        padding: '8px 12px',
        fontSize: '14px',
        fontWeight: '600',
        textTransform: 'none',
        minWidth: '80px',
        '&:hover': {
            backgroundColor: '#5A4FCF',
        },
    },
    description: {
        fontSize: '14px',
        lineHeight: '20px',
        color: '#6B7280',
        margin: '0 0 12px 0',
    },
    helpText: {
        display: 'flex',
        alignItems: 'flex-start',
        gap: '8px',
        backgroundColor: '#EFF6FF',
        border: '1px solid #DBEAFE',
        borderRadius: '6px',
        padding: '12px',
        fontSize: '13px',
        lineHeight: '18px',
        color: '#374151',
    },
    infoIcon: {
        fontSize: '16px',
        color: '#3B82F6',
        marginTop: '1px',
        flexShrink: 0,
    },
};

function CampaignCodeDisplay({ campaignCode, isValid, showDescription }) {
    const [recentlyCopied, setRecentlyCopied] = useState(false);

    const handleCopy = () => {
        toast('Campaign code copied to clipboard!');
        setRecentlyCopied(true);
        setTimeout(() => setRecentlyCopied(false), 2000);
    };

    if (!campaignCode) {
        return null;
    }

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <h3 style={styles.title}>Campaign Code</h3>
                {isValid && (
                    <div style={styles.validationBadge}>
                        <CheckCircleIcon style={{ fontSize: '14px' }} />
                        <span>Valid</span>
                    </div>
                )}
            </div>

            {showDescription && (
                <Typography style={styles.description}>
                    Use this code to track supplier engagement in your campaigns
                    and generate branded facility claim links.
                </Typography>
            )}

            <div style={styles.codeContainer}>
                <div style={styles.codeDisplay}>{campaignCode}</div>

                <CopyToClipboard text={campaignCode} onCopy={handleCopy}>
                    <Tooltip
                        title={recentlyCopied ? 'Copied!' : 'Copy to clipboard'}
                        placement="top"
                    >
                        <Button
                            variant="contained"
                            style={styles.copyButton}
                            startIcon={<CopyLinkIcon color="#FFFFFF" />}
                            disabled={recentlyCopied}
                        >
                            {recentlyCopied ? 'Copied!' : 'Copy'}
                        </Button>
                    </Tooltip>
                </CopyToClipboard>
            </div>

            {showDescription && (
                <div style={styles.helpText}>
                    <InfoIcon style={styles.infoIcon} />
                    <div>
                        <strong>How to use:</strong>
                        <br />
                        • Contact OS Hub staff to set up supplier engagement
                        campaigns
                        <br />
                        • Provide this code when requesting campaign link
                        generation
                        <br />• Track campaign performance through weekly
                        reports
                    </div>
                </div>
            )}
        </div>
    );
}

CampaignCodeDisplay.defaultProps = {
    campaignCode: null,
    isValid: false,
    showDescription: true,
};

CampaignCodeDisplay.propTypes = {
    campaignCode: string,
    isValid: bool,
    showDescription: bool,
};

export default CampaignCodeDisplay;
