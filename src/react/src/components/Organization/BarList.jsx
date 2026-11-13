import React from 'react';

import { barPercent } from './utils';
import styles from './styles';

/*
 * A horizontal bar per row, each as long as its value relative to the
 * largest. One measure per chart and the number printed beside every
 * bar, so it reads without a legend or an axis.
 */
const BarList = ({ title, rows, emptyText = 'Nothing to show yet.' }) => {
    const max = rows.reduce((largest, row) => Math.max(largest, row.value), 0);

    return (
        <div style={styles.card}>
            <h4 style={styles.chartTitle}>{title}</h4>
            {rows.length === 0 && <p style={styles.meta}>{emptyText}</p>}
            {rows.map(row => (
                <div key={row.label} style={styles.barRow}>
                    <span style={styles.barLabel} title={row.label}>
                        {row.label}
                    </span>
                    <div style={styles.barTrack}>
                        <div
                            style={{
                                ...styles.barFill,
                                width: `${barPercent(row.value, max)}%`,
                            }}
                        />
                    </div>
                    <span style={styles.barValue}>{row.value}</span>
                </div>
            ))}
        </div>
    );
};

export default BarList;
